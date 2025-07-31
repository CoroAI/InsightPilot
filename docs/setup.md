# Environment Setup & Troubleshooting

## Setting Up Your Development Environment

1. **Install Conda (Recommended):**
   - [Miniconda Download](https://docs.conda.io/en/latest/miniconda.html)
2. **Create Environment:**
   ```bash
   conda env create -f backend/environment.yml
   conda activate insightpilot
   ```
3. **Install Additional Dependencies (if needed):**
   ```bash
   pip install -r backend/requirements.txt
   ```
4. **Configure Environment Variables:**
   - Copy `.env.example` to `.env` and update secrets, endpoints, etc.
5. **Run Backend:**
   ```bash
   uvicorn app.main:app --reload
   ```

## Troubleshooting
- If you encounter package conflicts, update `environment.yml` and `requirements.txt` to match versions.
- For Python version issues, ensure Conda is using Python 3.13 (check with `python --version`).
- For FastAPI errors, see [FastAPI Troubleshooting](https://fastapi.tiangolo.com/tutorial/debugging/).
- For LangChain/agent errors, see [LangChain Docs](https://python.langchain.com/docs/).

## Useful Links
- [Conda User Guide](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html)
- [Uvicorn Docs](https://www.uvicorn.org/)
