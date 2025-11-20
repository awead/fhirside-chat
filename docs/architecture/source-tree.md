# Source Tree

This document describes the project structure and organization of the FHIRside Chat codebase.

## Project Overview

FHIRside Chat is a Python 3.13 FastAPI application that provides an AI-powered chat interface to FHIR data using PydanticAI agents with Azure OpenAI and Aidbox MCP integration.

---

## Directory Structure

```
fhirside-chat/
├── .bmad-core/              # BMad workflow configuration (gitignored except config)
├── .github/                 # GitHub Actions and chat modes
├── aidbox/                  # Aidbox FHIR server configuration
├── docs/                    # Project documentation
│   ├── architecture/        # Architecture documentation
│   ├── design/              # Design system artifacts
│   ├── epics/               # Epic documents
│   ├── qa/                  # QA documentation (future)
│   └── stories/             # User story documents
├── src/                     # Application source code
│   ├── ai/                  # AI agents and telemetry
│   └── models/              # Pydantic data models
├── tests/                   # Test suite
│   ├── ai/                  # AI module tests
│   └── models/              # Model tests
├── tmp/                     # Temporary files (gitignored)
├── .env                     # Environment variables (gitignored)
├── .gitignore               # Git ignore rules
├── .python-version          # Python version specification
├── .tool-versions           # Tool version specifications (asdf)
├── docker-compose.yaml      # Docker services orchestration
├── env-sample.txt           # Example environment variables
├── pyproject.toml           # Project metadata and dependencies
├── README.md                # Project documentation
└── uv.lock                  # Dependency lock file (uv package manager)
```

---

## Core Directories

### `src/` - Application Source Code

Main application code organized by concern:

```
src/
├── __init__.py              # Package initialization (exports app)
├── app.py                   # FastAPI application and endpoints
├── ai/                      # AI agent logic
│   ├── __init__.py
│   ├── agents.py            # PydanticAI agent definitions
│   └── telemetry.py         # OpenTelemetry instrumentation setup
└── models/                  # Data models
    ├── __init__.py
    └── clinical_history.py  # Patient history request/response models
```

#### Key Files

**`src/app.py`**
- FastAPI application factory (`create_app()`)
- API endpoints (`/chat`, `/patient`, `/ws`)
- Request/response models (`ChatRequest`, `ChatResponse`)
- `ChatService` for in-memory session management
- Logging configuration

**`src/ai/agents.py`**
- `chat_agent()` - General chat agent with MCP access
- `patient_history_agent()` - Specialized patient history generation agent
- Shared MCP server connection configuration
- Azure OpenAI client setup

**`src/ai/telemetry.py`**
- OpenTelemetry configuration
- OTLP exporter setup (Jaeger)
- `instrumentation()` function for agent observability

**`src/models/clinical_history.py`**
- `PatientHistoryRequest` - Input model for patient endpoint
- `PatientClinicalHistory` - Structured output model for patient history

---

### `tests/` - Test Suite

Test suite mirrors `src/` structure:

```
tests/
├── __init__.py
├── test_app.py              # API endpoint tests
├── ai/
│   ├── __init__.py
│   ├── test_agents.py       # Agent initialization tests
│   └── test_telemetry.py    # Telemetry setup tests
└── models/
    ├── __init__.py
    └── test_clinical_history.py  # Model validation tests
```

**Test Conventions:**
- Test files named `test_<module>.py`
- Test functions named `test_<feature>_<scenario>()`
- Use `@pytest.mark.asyncio` for async tests
- Mock external dependencies (OpenAI, MCP, Aidbox)

---

### `docs/` - Documentation

Comprehensive project documentation:

```
docs/
├── architecture/            # Technical architecture
│   ├── coding-standards.md  # Coding standards and practices
│   ├── high-level-architecture.md  # System architecture overview
│   ├── index.md             # Architecture documentation index
│   ├── introduction.md      # Architecture introduction
│   ├── next-steps.md        # Future architecture considerations
│   ├── source-tree.md       # This file
│   └── tech-stack.md        # Technology stack details
├── design/                  # Design system (for frontend)
│   ├── accessibility-checklist.md  # WCAG compliance checklist
│   ├── component-library.md        # UI component reference
│   ├── tailwind-config.md          # TailwindCSS configuration
│   └── wireframes.md               # UI wireframes
├── epics/                   # Epic documents
│   ├── epic-001-patient-history-enhancement.md
│   └── epic-002-frontend-chat-interface.md
└── stories/                 # User story documents
    ├── story-001-patient-history-endpoint.md
    ├── story-002-telemetry-api-endpoint.md
    ├── story-003-react-chat-foundation.md
    ├── story-004-chat-ui-enhancement.md
    └── story-005-telemetry-visualization-panel.md
```

---

### `aidbox/` - FHIR Server Configuration

Aidbox containerization and initialization:

```
aidbox/
├── Dockerfile               # Aidbox container configuration
└── init-bundle.json         # Initial FHIR data bundle
```

**Purpose:**
- Custom Aidbox Docker image
- Seed FHIR data for development/testing
- MCP server endpoint configuration

---

### `.bmad-core/` - BMad Workflow System

BMad methodology configuration (mostly gitignored except `core-config.yaml`):

```
.bmad-core/
├── core-config.yaml         # Project configuration for BMad agents
├── agents/                  # Agent persona definitions
├── checklists/              # Quality checklists
├── data/                    # Knowledge base documents
├── tasks/                   # Workflow task definitions
└── templates/               # Document templates
```

**Note:** Only `core-config.yaml` is version controlled. Other BMad files are team-specific.

---

## Configuration Files

### `pyproject.toml`

Primary project configuration:

```toml
[project]
name = "fhirside-chat"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [...]        # Production dependencies

[dependency-groups]
dev = [...]                 # Development dependencies

[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]
```

**Sections:**
- `[project]` - Package metadata and production dependencies
- `[dependency-groups]` - Development dependencies (pytest, ruff, etc.)
- `[build-system]` - Build tool configuration (setuptools)
- `[tool.setuptools]` - Package discovery configuration

### `docker-compose.yaml`

Multi-container development environment:

```yaml
services:
  aidbox:           # FHIR server with MCP support
  aidbox-db:        # PostgreSQL for Aidbox
  jaeger:           # Distributed tracing backend
```

**Services:**
- `aidbox` - FHIR R4 server with MCP endpoint (port 8080)
- `aidbox-db` - PostgreSQL 17 database (port 5432)
- `jaeger` - Jaeger UI (port 16686) and OTLP collector (ports 4317/4318)

### `.env` (gitignored)

Environment variables for configuration:

```bash
# Azure OpenAI
OPENAI_API_KEY=...
OPENAI_API_ENDPOINT=...
OPENAI_API_VERSION=...
OPENAI_MODEL=...

# Aidbox
AIDBOX_LICENSE_KEY=...
```

See `env-sample.txt` for template.

### `uv.lock`

Dependency lock file (managed by `uv`):
- Exact versions of all dependencies
- Transitive dependencies
- Cross-platform compatibility

---

## Import Patterns

### Absolute Imports (Preferred)

```python
from src.ai.agents import chat_agent, patient_history_agent
from src.models.clinical_history import PatientHistoryRequest
```

### Relative Imports (Within Package)

```python
from .ai.agents import chat_agent
from .models.clinical_history import PatientHistoryRequest
```

### Import Organization (Managed by Ruff)

```python
from fastapi import FastAPI
import logging
from typing import Dict, List

from pydantic import BaseModel
from opentelemetry import trace

from src.ai.agents import chat_agent
from src.models.schemas import Model
```

1. Standard library
2. Third-party packages
3. Local application imports

---

## File Naming Conventions

### Python Modules
- `lowercase_with_underscores.py`
- Examples: `app.py`, `agents.py`, `clinical_history.py`

### Test Files
- `test_<module>.py`
- Examples: `test_app.py`, `test_agents.py`

### Documentation
- `kebab-case.md`
- Examples: `tech-stack.md`, `coding-standards.md`, `source-tree.md`

### Configuration
- Standard names: `pyproject.toml`, `docker-compose.yaml`, `.gitignore`

---

## Entry Points

### API Server

```bash
uvicorn src:app --host 0.0.0.0 --port 8000 --reload

uv run uvicorn src:app --host 0.0.0.0 --port 8000 --reload
```

**Application:** `src/__init__.py` exports `app` from `src.app`

### Docker Services

```bash
docker compose up -d
docker compose down
```

**Services:** Aidbox, PostgreSQL, Jaeger

### Tests

```bash
pytest
pytest --cov=src tests/
pytest tests/ai/test_agents.py
```

### Linting/Formatting

```bash
ruff check .
ruff format .
```

---

## Module Responsibilities

### `src/app.py`
**Responsibility:** API layer and application configuration
- FastAPI application factory
- HTTP endpoints
- WebSocket endpoint
- Request/response models
- Error handling

### `src/ai/agents.py`
**Responsibility:** AI agent definitions and MCP integration
- PydanticAI agent creation
- MCP server connection
- Azure OpenAI client setup
- System prompts

### `src/ai/telemetry.py`
**Responsibility:** Observability and instrumentation
- OpenTelemetry configuration
- OTLP exporter setup
- Tracer provider initialization

### `src/models/clinical_history.py`
**Responsibility:** Data models for patient history feature
- Request/response schemas
- Pydantic model definitions
- Field validation

---

## Build Artifacts

### Generated Files (Gitignored)

```
__pycache__/             # Python bytecode cache
*.pyc                    # Compiled Python files
.pytest_cache/           # Pytest cache
.ruff_cache/             # Ruff cache
.coverage                # Coverage data
htmlcov/                 # Coverage HTML report
fhirside_chat.egg-info/  # Build metadata
dist/                    # Distribution packages
```

### Temporary Files

```
tmp/                     # Scratch files (gitignored)
.ai/                     # AI agent debug logs (gitignored)
```

---

## Future Directories (Planned)

Based on Stories 003-005, the following structure will be added:

```
frontend/                # React + Vite frontend application
├── src/
│   ├── components/
│   │   ├── chat/
│   │   └── telemetry/
│   ├── services/
│   ├── types/
│   ├── utils/
│   ├── App.tsx
│   └── main.tsx
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

**Note:** Frontend structure follows Story 003-005 specifications in `docs/stories/`.

---

## Key Architectural Patterns

### Modular Monolith
- Single Python application
- Organized by concern (ai, models, app)
- Clear separation of responsibilities

### Async-First
- All I/O operations use async/await
- FastAPI with async handlers
- PydanticAI async agents

### Type-Safe
- Pydantic models at API boundaries
- Python type hints throughout
- Strict type checking

### Observable
- OpenTelemetry spans for all operations
- Structured logging with context
- Jaeger UI for debugging

### Testable
- Test suite mirrors source structure
- Mocking for external dependencies
- High test coverage (80%+ target)

---

## Development Workflow

1. **Start Services:** `docker compose up -d`
2. **Start API:** `uv run uvicorn src:app --reload`
3. **Run Tests:** `pytest`
4. **Lint:** `ruff check .`
5. **Format:** `ruff format .`
6. **View Traces:** http://localhost:16686 (Jaeger UI)
7. **API Docs:** http://localhost:8000/docs (Swagger UI)

---

## References

- **Coding Standards:** `docs/architecture/coding-standards.md`
- **Tech Stack:** `docs/architecture/tech-stack.md`
- **High-Level Architecture:** `docs/architecture/high-level-architecture.md`
- **README:** `README.md`
