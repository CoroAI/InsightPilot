
# InsightPilot Architecture

## Overview

InsightPilot is a modular, service-oriented AI agent backend built with FastAPI, LangChain, and LangGraph. It automates the collection of business/process/data requests, orchestrates intelligent agents, gathers datasets, and generates actionable reports using a variety of AI models. The architecture is designed for scalability, extensibility, and future public deployment.

---

## Layered Architecture

### 1. API Layer
**Responsibility:**
- Exposes RESTful endpoints for user requests, data retrieval, and reporting.
- Handles authentication, request validation, and error management.
- Provides interactive OpenAPI documentation for developers.

**Example:**
- `/collect`: Accepts a business/process/data request and triggers agent workflows.
- `/report/{id}`: Returns a generated report for a specific request.

### 2. Service Layer
**Responsibility:**
- Implements business logic and orchestrates agent workflows.
- Manages request lifecycle, validation, and coordination between agents and integrations.
- Handles data transformation, aggregation, and post-processing.

**Example:**
- Validates incoming requests, selects appropriate agents, and manages workflow execution.

### 3. Agent Layer
**Responsibility:**
- Defines LangChain/LangGraph agents for intelligent data gathering, enrichment, and summarization.
- Supports multi-step, graph-based workflows for complex business processes.
- Integrates tools (web search, LLMs, custom APIs) for advanced reasoning.

**Example:**
- An agent that uses DuckDuckGo search, queries Ollama for LLM inference, and summarizes results for reporting.

### 4. Integrations Layer
**Responsibility:**
- Connects to external AI models and APIs (Ollama, HuggingFace, OpenAI, etc.).
- Manages model selection, API calls, and result caching.
- Ensures secure, scalable, and configurable model access.

**Example:**
- Integration module for running local LLMs via Ollama or fetching embeddings from HuggingFace.

### 5. Models Layer
**Responsibility:**
- Defines Pydantic schemas for request/response validation and internal data structures.
- Ensures type safety, serialization, and documentation of data contracts.

**Example:**
- `ReportRequest`, `DatasetSummary`, `AgentResult` schemas.

### 6. Utils Layer
**Responsibility:**
- Provides reusable helper functions for logging, formatting, error handling, and more.
- Centralizes common utilities to reduce code duplication.

**Example:**
- Logging setup, data formatting utilities, error response helpers.

---

## Data Flow & Workflow Example

1. **User submits a request** via the API (e.g., business process to analyze).
2. **API Layer** validates and forwards the request to the Service Layer.
3. **Service Layer** selects and orchestrates the appropriate Agent workflow.
4. **Agent Layer** executes a multi-step process:
    - Searches the web for relevant data (DuckDuckGo).
    - Queries LLMs (Ollama, HuggingFace, OpenAI) for analysis/summarization.
    - Aggregates and formats results.
5. **Integrations Layer** manages external model/API calls and caches results.
6. **Models Layer** ensures all data is validated and serialized for response.
7. **Utils Layer** logs workflow steps and handles errors.
8. **API Layer** returns the final structured dataset/report to the user.

---

## Extensibility & Scalability

- **Add new agents:** Create new modules in `app/agents` for custom workflows.
- **Integrate new models:** Extend `app/integrations` to support additional AI APIs or local models.
- **Expand business logic:** Add new services in `app/services` for specialized processes.
- **Testing:** Use `tests/` for unit/integration tests to ensure reliability.
- **Frontend:** Ready for future web/mobile frontend integration via API.
- **Deployment:** Supports Docker, Conda, and cloud-native deployment strategies.

---

## Deployment Considerations

- **Environment Management:** Use Conda and pip for reproducible environments.
- **Secrets & Config:** Store sensitive data in `.env` files and use environment variables for model endpoints.
- **Scalability:** Deploy with Docker, Kubernetes, or serverless platforms for horizontal scaling.
- **Security:** Implement authentication, authorization, and secure API access.

---

## Example Advanced Workflow

> **Scenario:** A user requests a market analysis report for a specific industry.

1. API receives the request and validates input.
2. Service layer triggers a LangGraph workflow:
    - Step 1: DuckDuckGo agent searches for recent news and datasets.
    - Step 2: Ollama agent summarizes findings using a local LLM.
    - Step 3: HuggingFace agent extracts key trends and statistics.
    - Step 4: Results are aggregated and formatted.
3. Integrations layer manages model calls and caches results.
4. Models layer validates and serializes the final report.
5. API returns the report to the user.

---

## References & Further Reading
- [FastAPI Architecture](https://fastapi.tiangolo.com/)
- [LangChain Concepts](https://python.langchain.com/docs/)
- [LangGraph Workflows](https://blog.langchain.dev/langgraph-intro/)
- [Ollama Model Management](https://ollama.com/library)
- [Service-Oriented Architecture](https://martinfowler.com/articles/microservices.html)

---
For more, see `learning.md`, `setup.md`, and `references.md` in the docs folder.
