
# InsightPilot

InsightPilot is a modular AI Agent backend designed for automated data collection, reporting, and business process support. Built with FastAPI, LangChain, and LangGraph, it provides a scalable, service-oriented foundation for intelligent data workflows and future integrations with open-source and commercial AI models.

## Application Overview

InsightPilot enables users to submit business, process, or data requests. The backend orchestrates AI agents to collect relevant datasets, generate summaries, and produce actionable reports. The architecture is designed for extensibility, allowing easy integration of new models (Ollama, HuggingFace, OpenAI) and future frontend interfaces.

## Features
- Modular, service-oriented architecture for maintainability and scalability
- Agent-driven data collection and reporting workflows
- Ready for integration with Ollama, HuggingFace, OpenAI, and other models
- Extensible for future frontend and public deployment
- Clear documentation and code structure for onboarding and collaboration

## Folder Structure
- `backend/`: FastAPI backend and agent logic
- `frontend/`: Placeholder for future frontend
- `docs/`: Architecture and documentation

## Development Process

### 1. Project Setup
- Clone the repository and set up a Python virtual environment.
- Install dependencies listed in `backend/requirements.txt` (FastAPI, LangChain, LangGraph, etc.).
- Configure environment variables in `.env` for secrets and model endpoints.

### 2. Architecture
- **API Layer:** Exposes endpoints for user requests and data retrieval.
- **Service Layer:** Implements business logic, agent orchestration, and data collection workflows.
- **Agent Layer:** Defines LangChain/LangGraph agents for intelligent data gathering and reporting.
- **Integrations:** Connects to external AI models (Ollama, HuggingFace, OpenAI).
- **Models:** Pydantic schemas for data validation and serialization.
- **Utils:** Helper functions for logging, formatting, and common tasks.

### 3. Workflow
1. User submits a business/process/data request via API.
2. Service layer validates and processes the request.
3. Agent layer orchestrates AI agents (LangChain/LangGraph) to collect data and generate summaries.
4. Integrations layer fetches data from external models as needed.
5. Results are returned to the user as structured datasets, summaries, or reports.

### 4. Extensibility
- Add new agents by creating modules in `backend/app/agents`.
- Integrate new models by extending `backend/app/integrations`.
- Expand business logic in `backend/app/services`.
- Future frontend can be added in the `frontend/` folder.

### 5. Testing & Documentation
- Write unit and integration tests in `backend/tests`.
- Document code with PEP 257-compliant docstrings and update `docs/architecture.md` for architectural changes.

## Getting Started

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run the FastAPI backend:
   ```bash
   uvicorn backend.app.main:app --reload
   ```
4. Access API docs at `http://localhost:8000/docs`

## Contributing

See `docs/architecture.md` for design details. Please follow code style and documentation standards. PRs and issues are welcome!
