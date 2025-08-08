from backend.app.services.web_scrapper_services import *

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
