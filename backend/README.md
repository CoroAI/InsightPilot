
# InsightPilot Backend

This backend is built with FastAPI, LangChain, and LangGraph. It provides service-oriented APIs for AI agent-driven data collection, reporting, and business process automation.

## Folder Structure

```
backend/
│
├── app/
│   ├── api/           # API route definitions, organized by feature/service
│   ├── core/          # Core settings, configuration, and startup logic
│   ├── models/        # Pydantic schemas for data validation and serialization
│   ├── services/      # Business logic, orchestration, and workflows
│   ├── agents/        # LangChain/LangGraph agent definitions and workflows
│   ├── integrations/  # Model integrations (Ollama, HuggingFace, OpenAI, etc.)
│   ├── utils/         # Utility functions and helpers
│   ├── main.py        # FastAPI application entrypoint
│   └── __init__.py
├── tests/             # Unit and integration tests for backend modules
├── requirements.txt   # Python dependencies
└── README.md          # Backend documentation
```

### Folder Details
- **app/api/**: Contains all API route definitions, grouped by functionality (e.g., data, reports, agents).
- **app/core/**: Handles configuration, environment variables, and application startup/shutdown events.
- **app/models/**: Defines Pydantic models for request/response validation and internal data structures.
- **app/services/**: Implements business logic, orchestrates agent workflows, and manages data collection/reporting processes.
- **app/agents/**: Contains LangChain/LangGraph agent classes and workflows for intelligent data gathering and summarization.
- **app/integrations/**: Integrates external AI models and APIs (Ollama, HuggingFace, OpenAI, etc.).
- **app/utils/**: Provides reusable utility functions (logging, formatting, etc.).
- **app/main.py**: The main FastAPI application file, where routers and middleware are registered.
- **tests/**: Test suite for backend modules, services, and agents.

## Setup Instructions

1. **Create a Python virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables:**
   - Copy `.env.example` to `.env` and update secrets, model endpoints, etc.
4. **Run the FastAPI backend:**
   ```bash
   uvicorn app.main:app --reload
   ```
5. **Access API docs:**
   - Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive documentation.

## Architecture Overview

InsightPilot backend is designed with a modular, service-oriented architecture:

- **API Layer:** Exposes endpoints for user requests, data retrieval, and reporting.
- **Service Layer:** Implements business logic, orchestrates agent workflows, and manages data collection/reporting.
- **Agent Layer:** Defines LangChain/LangGraph agents for intelligent data gathering, summarization, and reporting.
- **Integrations Layer:** Connects to external AI models and APIs (Ollama, HuggingFace, OpenAI).
- **Models Layer:** Pydantic schemas for data validation and serialization.
- **Utils Layer:** Helper functions for logging, formatting, and common tasks.

### Workflow
1. User submits a business/process/data request via API.
2. Service layer validates and processes the request.
3. Agent layer orchestrates AI agents to collect data and generate summaries.
4. Integrations layer fetches data from external models as needed.
5. Results are returned to the user as structured datasets, summaries, or reports.

### Extensibility
- Add new agents in `app/agents/`.
- Integrate new models in `app/integrations/`.
- Expand business logic in `app/services/`.
- Write tests in `tests/`.

For more details, see the main project `README.md` and `docs/architecture.md`.
