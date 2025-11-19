# Tech Stack

This is the **definitive technology selection section**. All technologies are specified with exact versions to ensure consistency across development and deployment environments.

## Cloud Infrastructure

- **Provider:** Local Development (Docker Compose)
- **Key Services:**
  - Docker Engine for container orchestration
  - Aidbox FHIR Server (containerized)
  - PostgreSQL 17 (containerized for Aidbox data storage)
  - Jaeger (containerized for distributed tracing)
- **Deployment Regions:** Localhost only (production deployment TBD)
- **Notes:** Current architecture targets local development; cloud provider selection (AWS, Azure, GCP) and production deployment strategy are future considerations

## Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|-----------|---------|---------|-----------|
| **Language** | Python | 3.13 | Primary development language | Latest stable Python with modern type hints, async improvements, better performance; team expertise |
| **Runtime** | Python Runtime | 3.13+ | Application execution environment | Native async/await support, extensive ecosystem for AI/ML libraries |
| **Web Framework** | FastAPI | 0.115.0+ | RESTful API & WebSocket server | Async-first design, automatic OpenAPI docs, excellent performance, native Pydantic integration |
| **ASGI Server** | Uvicorn | 0.32.0+ | Production-grade ASGI server | High performance, auto-reload for development, standard for FastAPI deployments |
| **AI Framework** | PydanticAI | 1.0.15+ | AI agent orchestration & LLM integration | Type-safe agent definitions, structured outputs via Pydantic, tool integration, built-in observability hooks |
| **LLM Provider** | Azure OpenAI | API 2024-12-01-preview | Language model inference | Enterprise support, HIPAA-eligible, consistent model behavior, specific API version tested |
| **OpenAI SDK** | openai | 1.6.0+ | Azure OpenAI client library | Official SDK, async support, streaming capabilities, Azure-specific authentication |
| **MCP Integration** | fastmcp | 2.0.0+ | Model Context Protocol client | Enables AI agents to use MCP tools, SSE transport support, Aidbox integration |
| **FHIR Server** | Aidbox | Latest | FHIR R4 data storage & MCP provider | Commercial FHIR server with MCP support, comprehensive FHIR implementation, PostgreSQL-backed |
| **Database** | PostgreSQL | 17 | Aidbox data persistence | Industry-standard RDBMS, excellent JSONB support for FHIR resources, proven reliability |
| **Data Validation** | Pydantic | Bundled with PydanticAI | Request/response models, type validation | Automatic JSON schema generation, validation at API boundaries, type safety |
| **Data Models** | SQLModel | 0.0.27+ | Future persistence layer (models defined but not used) | Pydantic + SQLAlchemy integration, prepared for future database persistence |
| **Observability - API** | OpenTelemetry API | 1.37.0+ | Tracing abstraction layer | Vendor-neutral observability, standardized span/trace concepts |
| **Observability - SDK** | OpenTelemetry SDK | 1.37.0+ | Trace collection & export | Implements OTLP protocol, exports to Jaeger, auto-instrumentation for FastAPI |
| **Observability - Exporter** | OTLP gRPC Exporter | 1.37.0+ | Trace export to Jaeger | Efficient binary protocol for trace data |
| **Tracing Backend** | Jaeger | Latest | Distributed tracing UI & storage | Industry-standard tracing solution, excellent UI for debugging AI agent flows |
| **Rich Console** | rich | 13.0.0+ | Enhanced terminal output | Better debugging experience, formatted logs in development |
| **Container Orchestration** | Docker Compose | 3.8+ | Multi-container development environment | Manages Aidbox, PostgreSQL, Jaeger services; simple local setup |
| **Package Manager** | uv | Latest | Fast Python package & environment manager | Significantly faster than pip, lockfile support, modern dependency resolution |
| **Testing Framework** | pytest | 8.4.2+ | Unit & integration testing | Industry standard, excellent async support, rich plugin ecosystem |
| **Async Testing** | pytest-asyncio | 1.2.0+ | Async test support | Enables testing of async FastAPI handlers and agents |
| **Test Coverage** | pytest-cov | 7.0.0+ | Code coverage measurement | Integrated with pytest, generates coverage reports |
| **Linting/Formatting** | ruff | 0.13.3+ | Fast Python linter & formatter | Extremely fast, replaces multiple tools (black, flake8, isort), configured in pyproject.toml |
| **Interactive Shell** | IPython | 9.6.0+ | Enhanced REPL for development | Better debugging experience, auto-completion, magic commands |
