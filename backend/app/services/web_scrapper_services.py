#!/usr/bin/env python3
"""
scrape_to_rag.py

Scrape HTML + PDFs -> Clean -> Chunk -> Embed -> FAISS -> RAG (HuggingFace)

Usage:
    python scrape_to_rag.py "business summary here"

Notes:
- Recommended to run in a virtualenv and install the requirements below.
- Works on CPU; GPU will speed up embedding and generation if available.
- Large PDFs are streamed and parsed page-by-page to avoid OOM.
"""

import sys
import os
import logging
import time
import pickle
from typing import List, Dict, Tuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from charset_normalizer import from_bytes
import fitz  # PyMuPDF
import pandas as pd
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, pipeline

# -------------------- Config --------------------
EMBED_MODEL = "all-MiniLM-L6-v2"       # small/faster embedder
GEN_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"  # replace if unavailable locally
FAISS_INDEX_PATH = "faiss_index.bin"
META_PATH = "faiss_meta.pkl"
CSV_OUTPUT = "scraped_dataset.csv"

# chunk config (approx by characters; ~500-800 chars ≈ 100-200 tokens)
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

# network / scraping
REQUEST_TIMEOUT = 12
MAX_BYTES_TO_READ = 8 * 1024 * 1024  # 8 MB per resource (safety)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
             "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"

# RAG
TOP_K = 4

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("scrape_to_rag")

# -------------------- Utilities --------------------
def safe_get(url: str, timeout=REQUEST_TIMEOUT):
    """Fetch resource with streaming, return raw bytes or None."""
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    try:
        with requests.get(url, headers=headers, timeout=timeout, stream=True) as r:
            r.raise_for_status()
            total = 0
            chunks = []
            for chunk in r.iter_content(chunk_size=64 * 1024):
                if chunk:
                    chunks.append(chunk)
                    total += len(chunk)
                    if total > MAX_BYTES_TO_READ:
                        logger.warning("Reached max read bytes for %s — stopping stream", url)
                        break
            return b"".join(chunks), r.headers.get("Content-Type", "")
    except Exception as e:
        logger.warning("Failed to GET %s -> %s", url, e)
        return None, None

def detect_encoding_and_decode(raw_bytes: bytes) -> str:
    """Use charset_normalizer to detect encoding then decode."""
    if not raw_bytes:
        return ""
    try:
        results = from_bytes(raw_bytes)
        best = results.best()
        if best:
            return best.output_string()
    except Exception:
        pass
    # fallback
    try:
        return raw_bytes.decode("utf-8", errors="replace")
    except Exception:
        return raw_bytes.decode("latin-1", errors="replace")

# -------------------- Parsers --------------------
def parse_html_text(html_text: str) -> Tuple[str, str]:
    """Return (title, main_text)."""
    soup = BeautifulSoup(html_text, "html.parser")
    # Remove unwanted tags
    for s in soup(["script", "style", "header", "footer", "noscript", "svg", "iframe"]):
        s.decompose()
    title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"
    paragraphs = soup.find_all("p")
    texts = [p.get_text(separator=" ", strip=True) for p in paragraphs if p.get_text(strip=True)]
    # fallback to body text if paragraphs are missing
    if not texts:
        body = soup.get_text(separator=" ", strip=True)
        main = " ".join([s.strip() for s in body.splitlines() if s.strip()])[:20000]
    else:
        main = " ".join([t for t in texts if len(t) > 40])
    return title, main

def parse_pdf_bytes(pdf_bytes: bytes) -> Tuple[str, str]:
    """Extract text from PDF bytes using PyMuPDF (fitz). Returns (title, text)."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        texts = []
        # attempt to get title from metadata
        meta = doc.metadata
        title = meta.get("title") or meta.get("title", "") or "PDF Document"
        for page in doc:
            # extract text page by page
            text = page.get_text("text")
            if text:
                texts.append(text.strip())
            # small memory relief
        combined = "\n".join(texts)
        return title if title else "PDF Document", combined
    except Exception as e:
        logger.warning("PDF parse failed: %s", e)
        return "PDF Document", ""

# -------------------- Cleaning & Chunking --------------------
def clean_text(s: str) -> str:
    if not s:
        return ""
    s = s.replace("\r", " ").replace("\n", " ")
    s = " ".join(s.split())
    return s.strip()

def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Chunk by characters with overlap."""
    if not text:
        return []
    text = clean_text(text)
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(start + size, L)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == L:
            break
        start = max(0, end - overlap)
    return chunks

# -------------------- Embedding & FAISS --------------------
logger.info("Loading embedding model: %s", EMBED_MODEL)
embedder = SentenceTransformer(EMBED_MODEL)

def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    dim = embeddings.shape[1]
    # use inner product on normalized vectors => cosine similarity
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    return index

def save_faiss(index: faiss.Index, meta: List[Dict], idx_path=FAISS_INDEX_PATH, meta_path=META_PATH):
    faiss.write_index(index, idx_path)
    with open(meta_path, "wb") as f:
        pickle.dump(meta, f)
    logger.info("Saved FAISS index (%s) and metadata (%s).", idx_path, meta_path)

def load_faiss(idx_path=FAISS_INDEX_PATH, meta_path=META_PATH):
    if not os.path.exists(idx_path) or not os.path.exists(meta_path):
        return None, None
    index = faiss.read_index(idx_path)
    with open(meta_path, "rb") as f:
        meta = pickle.load(f)
    return index, meta

# -------------------- Scrape -> parse -> chunk -> embed pipeline --------------------
def process_url(url: str, business_summary: str) -> List[Dict]:
    """Return list of chunk dicts with metadata for a single URL."""
    logger.info("Processing URL: %s", url)
    raw, content_type = safe_get(url)
    if raw is None:
        logger.warning("No content for %s", url)
        return []

    # detect and decode
    text = detect_encoding_and_decode(raw)

    # branch on content-type (pdf vs html)
    lowered_ct = (content_type or "").lower()
    title, main = "No Title", ""
    if "pdf" in lowered_ct or url.lower().endswith(".pdf"):
        logger.info("Detected PDF content for %s", url)
        try:
            t, main = parse_pdf_bytes(raw)
            title = t
        except Exception as e:
            logger.warning("PDF parsing exception for %s: %s", url, e)
            return []
    else:
        title, main = parse_html_text(text)

    # if main is empty, give up
    if not main or len(main) < 50:
        logger.info("Insufficient textual content for %s (len=%d)", url, len(main))
        return []

    main = clean_text(main)
    chunks = chunk_text(main)
    out = []
    for i, c in enumerate(chunks):
        out.append({
            "url": url,
            "title": title,
            "source": urlparse(url).netloc,
            "chunk_id": f"{url}__{i}",
            "content": c,
            "business_summary": business_summary,
            "scrape_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        })
    logger.info("Created %d chunks for %s", len(out), url)
    return out

def ingest_urls(urls: List[str], business_summary: str) -> Tuple[faiss.Index, List[Dict]]:
    """Process URLs, create embeddings, and return a built FAISS index and metadata list."""
    all_chunks = []
    for u in urls:
        try:
            chunks = process_url(u, business_summary)
            all_chunks.extend(chunks)
        except Exception as e:
            logger.exception("Failed processing URL %s: %s", u, e)

    if not all_chunks:
        logger.warning("No chunks found from provided URLs.")
        return None, []

    # embed in batches
    texts = [c["content"] for c in all_chunks]
    logger.info("Creating embeddings for %d chunks...", len(texts))
    embeddings = embedder.encode(texts, convert_to_numpy=True, show_progress_bar=True, normalize_embeddings=True)

    # ensure embeddings shape
    if embeddings.ndim == 1:
        embeddings = embeddings.reshape(1, -1)

    index = build_faiss_index(embeddings.copy())
    # metadata must align with vectors order
    return index, all_chunks

# -------------------- RAG Query --------------------
logger.info("Loading generation model tokenizer and pipeline (this may be slow)...")
# we create the generation pipeline lazily (catch model unavailable)
gen_pipeline = None
gen_tokenizer = None
try:
    gen_tokenizer = AutoTokenizer.from_pretrained(GEN_MODEL)
    # device mapping: if GPU is available, pipeline will use it automatically with device_map else CPU
    gen_pipeline = pipeline("text-generation", model=GEN_MODEL, tokenizer=gen_tokenizer, device_map="auto")
except Exception as e:
    logger.warning("Could not load generation model '%s' locally: %s", GEN_MODEL, e)
    logger.info("You can still use embeddings + FAISS. To enable generation, install model or change GEN_MODEL variable.")

def rag_answer(query: str, index: faiss.Index, metadata: List[Dict], top_k: int = TOP_K) -> Dict:
    """Retrieve top_k chunks and optionally generate an answer with model."""
    if index is None or not metadata:
        return {"error": "FAISS index or metadata missing."}
    q_emb = embedder.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    faiss.normalize_L2(q_emb)
    D, I = index.search(q_emb, top_k)
    hits = []
    for score, idx in zip(D[0].tolist(), I[0].tolist()):
        if idx < 0 or idx >= len(metadata):
            continue
        md = metadata[idx].copy()
        md["score"] = float(score)
        hits.append(md)

    # Prepare context
    context = "\n\n".join([h["content"] for h in hits])
    answer = None
    if gen_pipeline:
        prompt = f"Use the following context to answer the question concisely.\n\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"
        try:
            out = gen_pipeline(prompt, max_new_tokens=200, do_sample=False)
            generated = out[0]["generated_text"]
            # remove the prompt prefix if model echoes
            answer = generated.replace(prompt, "").strip()
        except Exception as e:
            logger.warning("Generation failed: %s", e)
            answer = None

    return {"query": query, "hits": hits, "answer": answer}

# -------------------- Helper: build dataset CSV --------------------
def build_csv_from_metadata(metadata: List[Dict], csv_path: str = CSV_OUTPUT):
    if not metadata:
        logger.warning("No metadata to save to CSV.")
        return
    rows = []
    for m in metadata:
        rows.append({
            "title": m.get("title"),
            "source": m.get("source"),
            "url": m.get("url"),
            "chunk_id": m.get("chunk_id"),
            "content": m.get("content"),
            "scrape_time": m.get("scrape_time"),
        })
    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)
    logger.info("Saved CSV with %d rows to %s", len(df), csv_path)

# -------------------- Main flow --------------------
def discover_urls_from_summary(summary: str, limit: int = 8) -> List[str]:
    """Simple Google News-ish discovery using 'googlesearch' or manual seed list fallback."""
    try:
        from googlesearch import search
        query = f"{summary} site:news"
        urls = list(search(query, num_results=limit))
        logger.info("Discovered %d URLs via search.", len(urls))
        return urls
    except Exception as e:
        logger.warning("googlesearch failed: %s — falling back to empty list", e)
        return []

def main(business_summary: str):
    logger.info("Starting pipeline for summary: %s", business_summary)
    urls = discover_urls_from_summary(business_summary, limit=8)
    # allow user to pass fallback URLs if none found
    if not urls:
        logger.warning("No URLs discovered. Provide a list or check network/search config.")
        return

    index, metadata = ingest_urls(urls, business_summary)
    if index is None:
        logger.error("No index built; aborting.")
        return

    # Save index and metadata
    save_faiss(index, metadata)

    # Save CSV dataset (Kaggle-style)
    build_csv_from_metadata(metadata, CSV_OUTPUT)

    # Quick interactive query example
    example_q = "Which companies are investing in EV charging infrastructure?"
    logger.info("Running sample RAG query: %s", example_q)
    result = rag_answer(example_q, index, metadata, top_k=TOP_K)
    logger.info("RAG result: answer present=%s, hits=%d", result.get("answer") is not None, len(result.get("hits", [])))
    if result.get("answer"):
        print("\n=== RAG GENERATED ANSWER ===\n", result["answer"])

    # Print top hit summaries
    print("\nTop retrieved contexts (scores):")
    for h in result.get("hits", []):
        print(f"- ({h['score']:.3f}) {h['source']} / {h['url']} / chunk_id={h['chunk_id']}")
        print(h['content'][:300].strip(), "...\n")

if __name__ == "__main__":
    summary = "Monitor latest developments and investments in electric vehicle charging infrastructure in South Asia"
    main(summary)
