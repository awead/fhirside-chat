# FHIRside Chat Brownfield Enhancement Architecture

## Introduction

This document outlines the architectural approach for enhancing FHIRside Chat with **automated patient clinical history generation**. Its primary goal is to serve as the guiding architectural blueprint for AI-driven development of the new `/patient` endpoint while ensuring seamless integration with the existing system.

**Relationship to Existing Architecture:**
This document supplements the existing project architecture by defining how the new patient history generation feature will integrate with current chat agent systems. The enhancement extends PydanticAI agent capabilities and introduces structured clinical data output while maintaining compatibility with existing FastAPI patterns, Aidbox MCP integration, and OpenTelemetry observability.

### Existing Project Analysis

#### Current Project State

- **Primary Purpose:** Real-time chat interface to FHIR data via AI agent with MCP integration
- **Current Tech Stack:** Python 3.13, FastAPI, PydanticAI, Azure OpenAI, Aidbox FHIR Server, PostgreSQL, Docker
- **Architecture Style:** Modular monolith with async event-driven components, RESTful API + WebSocket support
- **Deployment Method:** Docker Compose orchestration with separate services (API, Aidbox, Jaeger, PostgreSQL)

#### Available Documentation

- `README.md` - Configuration and usage guide with service startup instructions
- `pyproject.toml` - Dependency management and project metadata
- `docker-compose.yaml` - Infrastructure orchestration definitions
- In-code documentation for AI agents, telemetry, and chat service

#### Identified Constraints

- **In-memory session storage only** - No persistent chat history (current limitation, future enhancement planned)
- **No persistence layer** - SQLModel definitions exist but database integration deferred to future enhancement
- **Azure OpenAI dependency** - Requires active API endpoint and key configuration
- **Aidbox license requirement** - Commercial FHIR server with licensing constraints
- **MCP Server SSE protocol** - Fixed integration pattern via Server-Sent Events at `http://localhost:8080/sse`
- **Single generic agent** - Current `chat_agent()` handles all interactions; new patient agent will extend this pattern
- **Stateless patient history generation** - No caching or idempotency for v1; each request generates fresh output

### Change Log

| Change | Date | Version | Description | Author |
|--------|------|---------|-------------|--------|
| Initial draft | 2025-11-14 | 0.1 | Created brownfield architecture for patient history generation endpoint | Winston (Architect) |

## Enhancement Scope and Integration Strategy

### Enhancement Overview

**Enhancement Type:** New API Endpoint with Specialized AI Agent
**Scope:** Add POST `/patient` endpoint for automated clinical history generation from FHIR data
**Integration Impact:** Low - extends existing patterns without modifying current chat functionality

### Integration Approach

**Code Integration Strategy:**
- New `patient_history_agent()` function in `src/ai/agents.py` extending existing agent pattern
- New endpoint handler in `src/app.py` following existing FastAPI async patterns
- Reuse existing MCP server connection (`MCPServerSSE`) and OpenAI client configuration
- New request/response models in `src/models/` for patient history API contract

**Database Integration:**
- No database persistence required for this enhancement (future scope)
- Stateless endpoint design - each request generates fresh clinical history
- Existing `Patient` SQLModel will be enhanced for structured output schema only

**API Integration:**
- Reuses existing Aidbox MCP endpoint (`http://localhost:8080/sse`)
- Reuses existing Azure OpenAI configuration (endpoint, key, model, API version)
- No changes to existing `/chat` or `/ws` endpoints

**UI Integration:**
- Backend-only enhancement - no UI changes required
- JSON response format enables future frontend integration (separate concern)

### Compatibility Requirements

**Existing API Compatibility:**
- Zero impact on existing `/chat` POST endpoint
- Zero impact on existing `/ws` WebSocket endpoint
- New endpoint follows FastAPI conventions (async handlers, Pydantic models)

**Database Schema Compatibility:**
- No schema changes required
- `Patient` SQLModel enhanced but not persisted (preparation for future persistence)

**UI/UX Consistency:**
- N/A - Backend API only; frontend is separate concern

**Performance Impact:**
- New endpoint creates additional OpenAI API calls (cost consideration)
- MCP queries to Aidbox may be extensive depending on patient data volume
- OpenTelemetry spans will track patient history generation performance
- No impact on existing chat endpoint performance (separate code paths)

## Tech Stack

### Existing Technology Stack

| Category | Current Technology | Version | Usage in Enhancement | Notes |
|----------|-------------------|---------|---------------------|-------|
| **Language** | Python | 3.13 | All new code | Maintained |
| **Web Framework** | FastAPI | 0.115.0+ | New `/patient` endpoint | Async pattern maintained |
| **AI Framework** | PydanticAI | 1.0.15+ | New patient history agent | Core framework for agent creation |
| **LLM Provider** | Azure OpenAI | API 2024-12-01-preview | Clinical history generation | Existing client and model reused |
| **OpenAI SDK** | openai | 1.6.0+ | Client integration | Existing configuration |
| **MCP Integration** | fastmcp | 2.0.0+ | FHIR data retrieval | Existing SSE connection reused |
| **FHIR Server** | Aidbox | Latest | Patient data source via MCP | No changes required |
| **Data Validation** | Pydantic (via PydanticAI) | Bundled | Request/response models, JSON parsing | Enhanced for clinical data |
| **Data Models** | SQLModel | 0.0.27+ | Patient output schema | Enhanced but not persisted |
| **Observability** | OpenTelemetry | 1.37.0+ | Tracing new endpoint | Existing instrumentation extended |
| **Tracing Backend** | Jaeger | Latest | Performance monitoring | No changes required |
| **Database** | PostgreSQL | 17 | Not used in this enhancement | Ready for future persistence |
| **Orchestration** | Docker Compose | N/A | No changes | Existing services maintained |
| **ASGI Server** | Uvicorn | 0.32.0+ | Serving new endpoint | No changes required |

### New Technology Additions

**No new technologies required for this enhancement.**

All necessary capabilities are provided by the existing stack:
- PydanticAI handles structured output via `result_type` parameter with native JSON parsing
- FastAPI supports additional endpoints without framework changes
- Existing MCP and OpenAI integrations are sufficient for clinical data retrieval
- Existing Azure OpenAI model configuration reused (model variance deferred to future enhancement)
- SQLModel can model clinical history schema without persistence layer

## Data Models and Schema Changes

### Design Philosophy: Progressive Complexity

**v1 Approach:** Start with a simplified, narrative-focused model that leverages LLM strengths (natural language generation) while providing basic structured data. This approach:
- Reduces implementation complexity and time-to-value
- Minimizes LLM output validation failures
- Enables rapid iteration on prompt design
- Provides a foundation for future enhancement with detailed structured models

**Future Evolution:** v2 can introduce detailed nested models for specific FHIR resources (Condition, Medication, Observation, etc.) based on validated use cases and user feedback.

### New Data Models

#### PatientHistoryRequest

**Purpose:** Input model for POST `/patient` endpoint
**Integration:** Validates incoming requests, provides type safety for endpoint handler

**Implementation:**
```python
from uuid import UUID
from pydantic import BaseModel

class PatientHistoryRequest(BaseModel):
    patient_id: UUID
```

**Key Attributes:**
- `patient_id: UUID` - FHIR Patient resource identifier from Aidbox (e.g., `Patient/{uuid}`)

**Design Notes:**
- Single-field model for v1; extensible for future query parameters (e.g., `date_range`, `include_resources`)
- UUID type provides validation and type safety
- Maps directly to Aidbox Patient/{id} resource pattern

---

#### PatientClinicalHistory

**Purpose:** Output schema for patient clinical history response; serves as PydanticAI agent `result_type`
**Integration:** Defines structured JSON response format; guides LLM output generation

**Implementation:**
```python
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field

class PatientClinicalHistory(BaseModel):
    patient_id: UUID = Field(description="Patient identifier from request")
    patient_name: str = Field(description="Patient's full name")
    date_of_birth: Optional[str] = Field(None, description="Patient DOB (YYYY-MM-DD format)")

    clinical_summary: str = Field(
        description="Comprehensive narrative clinical history synthesized by LLM"
    )

    key_conditions: List[str] = Field(
        default_factory=list,
        description="List of significant diagnosed conditions (plain text)"
    )

    active_medications: List[str] = Field(
        default_factory=list,
        description="List of current medications (plain text with dosage)"
    )

    recent_encounters: List[str] = Field(
        default_factory=list,
        description="Recent clinical encounters (plain text summaries)"
    )

    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of history generation"
    )
```

**Key Attributes:**
- `patient_id: UUID` - Echo of input for traceability
- `patient_name: str` - Patient's full name from FHIR Patient resource
- `date_of_birth: Optional[str]` - DOB if available
- `clinical_summary: str` - **Primary value:** LLM-generated comprehensive narrative history
- `key_conditions: List[str]` - Simple string list of conditions (e.g., "Type 2 Diabetes Mellitus", "Hypertension")
- `active_medications: List[str]` - Simple string list with dosages (e.g., "Metformin 500mg twice daily")
- `recent_encounters: List[str]` - Encounter summaries (e.g., "2025-10-15: Annual wellness visit")
- `generated_at: datetime` - Generation timestamp for debugging/logging

**Design Rationale:**

1. **Narrative-first approach:** The `clinical_summary` field is the primary output. LLMs excel at synthesizing information into coherent narratives, making this the highest-value field.

2. **Simple string lists:** Instead of complex nested models (`List[Condition]` with codes, statuses, dates), use plain text strings. This:
   - Reduces LLM schema validation failures
   - Simplifies prompt engineering
   - Provides immediate value without FHIR complexity
   - Can be enhanced to structured models in v2

3. **Optional demographic fields:** Graceful handling of incomplete FHIR data (real-world constraint)

4. **Default factories for lists:** Ensures lists are never `None`, simplifying consumer code

**Relationships:**
- **With Existing:** References same `patient_id` as existing `Patient` SQLModel (no FK relationship in stateless v1)
- **With New:** Standalone model; no nested dependencies in v1

---

### Schema Integration Strategy

**Database Changes Required:**
- **New Tables:** None (stateless v1)
- **Modified Tables:** None
- **New Indexes:** None
- **Migration Strategy:** N/A for v1

**Backward Compatibility:**
- Existing `Patient` SQLModel in `src/models/patient.py` remains unchanged
- New models will be in `src/models/clinical_history.py` - separate file for clear separation of concerns
- When persistence is added in future, `PatientClinicalHistory` can be evolved into a table model or stored as JSONB

**Model Organization:**
```
src/models/
├── __init__.py
├── patient.py              # Existing: Patient SQLModel (for future persistence)
└── clinical_history.py     # New: PatientHistoryRequest, PatientClinicalHistory
```

**Future Evolution Path (v2+):**

When real-world usage validates the need for detailed structured data:

1. **Add nested models:** Introduce `Condition`, `Medication`, `Observation` models with FHIR codes
2. **Enhance prompt:** Update agent instructions to populate detailed schema
3. **Maintain backward compatibility:** Keep v1 fields, add v2 fields as optional
4. **Version API response:** Consider `/patient?version=2` or accept header negotiation

---

### Data Quality and Error Handling

**Graceful Degradation Strategy:**

Given the simplified model design, error handling is straightforward:

- **Missing data:** Lists default to empty `[]`, optional fields to `None`
- **LLM validation failures:** Pydantic validation catches schema mismatches; retry logic can be added
- **Incomplete FHIR data:** Prompt instructs LLM to work with available data and note gaps in `clinical_summary`

**Error Response (separate from success model):**
```python
class PatientHistoryError(BaseModel):
    patient_id: UUID
    error: str
    error_code: str  # e.g., "PATIENT_NOT_FOUND", "MCP_TIMEOUT", "LLM_GENERATION_FAILED"
```

HTTP status codes:
- `200 OK`: Successful generation (even if data is sparse)
- `404 Not Found`: Patient ID doesn't exist in Aidbox
- `500 Internal Server Error`: MCP or LLM failure
- `422 Unprocessable Entity`: Invalid request (bad UUID format)

## Component Architecture

### Overview

The enhancement introduces two primary new components while reusing existing infrastructure:

1. **`patient_history_agent()`** - Specialized PydanticAI agent with clinical history prompt
2. **`POST /patient` endpoint** - FastAPI handler orchestrating agent execution

All new components follow existing architectural patterns (async handlers, instrumentation, error handling).

---

### New Components

#### Patient History Agent (`src/ai/agents.py`)

**Responsibility:** Generate structured clinical histories from FHIR data via MCP queries

**Integration Points:**
- Existing `MCPServerSSE` connection to Aidbox
- Existing `AsyncAzureOpenAI` client configuration
- Existing `instrumentation()` for OpenTelemetry tracing

**Implementation Pattern:**
```python
def patient_history_agent() -> Agent[PatientClinicalHistory]:
    """
    Creates a PydanticAI agent specialized for patient clinical history generation.

    Uses custom system prompt to:
    1. Query Aidbox FHIR server via MCP for patient data
    2. Retrieve related resources (Conditions, Medications, Encounters, etc.)
    3. Synthesize information into structured PatientClinicalHistory output
    """
    mcp_server = MCPServerSSE("http://localhost:8080/sse")

    client = AsyncAzureOpenAI(
        azure_endpoint=api_endpoint,
        api_version=api_version,
        api_key=api_key,
    )

    model = OpenAIChatModel(api_model, provider=OpenAIProvider(openai_client=client))

    system_prompt = """You are a clinical data analyst specializing in patient history synthesis.

Given a patient ID, you will:
1. Retrieve the Patient resource from the FHIR server using available MCP tools
2. Query for related clinical resources: Conditions, MedicationStatements, Encounters, Observations
3. Synthesize the information into a comprehensive clinical narrative
4. Extract key conditions, active medications, and recent encounters as structured lists

Guidelines:
- Prioritize recent and active clinical data
- Note any data gaps or missing information in the narrative
- Use clear, professional medical terminology
- Format dates consistently (YYYY-MM-DD)
- Include medication dosages when available
"""

    agent = Agent(
        model,
        result_type=PatientClinicalHistory,
        system_prompt=system_prompt,
        toolsets=[mcp_server],
        instrument=instrumentation()
    )

    return agent
```

**Key Interfaces:**
- **Input:** Patient UUID (passed as part of agent `run()` prompt)
- **Output:** `PatientClinicalHistory` model instance
- **Tools:** MCP server provides FHIR query capabilities via tool discovery
- **Observability:** OpenTelemetry spans track execution

**Error Handling:**
- MCP connection failures → Propagate exception to endpoint handler
- LLM generation failures → Retry logic (configurable)
- Schema validation failures → Log error, return 500

---

#### Patient History Endpoint (`src/app.py`)

**Responsibility:** HTTP interface for patient clinical history requests

**Integration Points:**
- New `patient_history_agent()` function
- Existing FastAPI application instance
- Existing error handling patterns

**Implementation Pattern:**
```python
@app.post("/patient", response_model=PatientClinicalHistory)
async def generate_patient_history(req: PatientHistoryRequest):
    """
    Generate comprehensive clinical history for a patient.

    Args:
        req: Request containing patient_id

    Returns:
        PatientClinicalHistory: Structured clinical history

    Raises:
        HTTPException(404): Patient not found in Aidbox
        HTTPException(500): MCP or LLM generation failure
    """
    try:
        async with patient_history_agent() as agent:
            prompt = f"Generate comprehensive clinical history for patient ID: {req.patient_id}"
            result = await agent.run(prompt)
            return result.output

    except PatientNotFoundException:
        raise HTTPException(status_code=404, detail=f"Patient {req.patient_id} not found")
    except Exception as e:
        # Log error with telemetry
        logger.error(f"Failed to generate history for {req.patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate clinical history")
```

**Key Interfaces:**
- **HTTP Method:** POST
- **Path:** `/patient`
- **Request Body:** `PatientHistoryRequest` JSON
- **Response:** `PatientClinicalHistory` JSON (200) or error (4xx/5xx)
- **Headers:** Standard FastAPI (Content-Type: application/json)

**Error Handling:**
- 404: Patient not found in Aidbox
- 422: Invalid request (bad UUID)
- 500: MCP connection failure, LLM generation failure, or unexpected errors
- OpenTelemetry exceptions traced automatically

---

### Component Interaction Diagram

```
┌─────────────────┐
│   HTTP Client   │
└────────┬────────┘
         │ POST /patient {"patient_id": "..."}
         ▼
┌─────────────────────────────────────┐
│   FastAPI App (src/app.py)          │
│   - Validate request                │
│   - Create patient_history_agent()  │
│   - Execute agent.run()             │
│   - Return PatientClinicalHistory   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   patient_history_agent()            │
│   (src/ai/agents.py)                │
│   - System prompt                   │
│   - result_type=PatientClinicalHistory│
│   - OpenTelemetry instrumentation   │
└────┬──────────────────────┬─────────┘
     │                      │
     │ Query FHIR           │ Generate
     │ via MCP tools        │ with LLM
     ▼                      ▼
┌──────────────────┐  ┌──────────────────┐
│  Aidbox MCP      │  │  Azure OpenAI    │
│  (localhost:8080)│  │  (gpt-4o)        │
└──────────────────┘  └──────────────────┘
         │                      │
         │ FHIR resources       │ Structured JSON
         ▼                      ▼
┌─────────────────────────────────────┐
│  PatientClinicalHistory JSON        │
│  {                                  │
│    "patient_id": "...",             │
│    "clinical_summary": "...",       │
│    "key_conditions": [...],         │
│    ...                              │
│  }                                  │
└─────────────────────────────────────┘
```

---

### Reused Existing Components

**No modifications required for:**

- `chat_agent()` - Remains unchanged for chat functionality
- `ChatService` - Not used by patient endpoint (stateless design)
- `instrumentation()` - Reused as-is for telemetry
- Aidbox MCP server connection - Same endpoint, same protocol
- Azure OpenAI client configuration - Same credentials, same model
- Jaeger tracing backend - Automatically receives spans from new endpoint

**This is a key architectural strength:** The enhancement is purely additive with zero modifications to existing components.

---

### Testing Strategy

**Unit Tests:**
- `test_patient_history_request_validation()` - Test UUID validation
- `test_patient_clinical_history_model()` - Test model serialization
- `test_patient_history_agent_creation()` - Test agent initialization

**Integration Tests:**
- `test_patient_endpoint_success()` - Mock MCP and LLM, verify response structure
- `test_patient_endpoint_not_found()` - Test 404 error handling
- `test_patient_endpoint_mcp_failure()` - Test MCP timeout/error handling

**End-to-End Tests (Manual):**
- Verify against real Aidbox patient data
- Test with patients having varying data completeness
- Monitor OpenTelemetry spans in Jaeger UI
- Validate LLM output quality and consistency

## API Design and Integration

### API Integration Strategy

**API Integration Strategy:** Additive - new endpoint coexists with existing `/chat` and `/ws` endpoints
**Authentication:** None for v1 (matches existing endpoints); future enhancement will add auth consistently across all endpoints
**Versioning:** Not required for v1; if needed in future, will use path versioning (`/v2/patient`) consistently with existing API

### New API Endpoint: POST /patient

**Method:** POST
**Endpoint:** `/patient`
**Purpose:** Generate comprehensive clinical history for a specified patient
**Integration:** Standalone endpoint; no dependencies on existing `/chat` or `/ws` endpoints

#### Request

```json
{
  "patient_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Validation:**
- `patient_id` must be valid UUID format
- FastAPI automatic validation via Pydantic model

#### Response (Success - 200 OK)

```json
{
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",
  "patient_name": "John Doe",
  "date_of_birth": "1975-03-15",
  "clinical_summary": "Patient is a 50-year-old male with a history of Type 2 Diabetes Mellitus diagnosed in 2018, currently managed with Metformin. Hypertension diagnosed in 2020, controlled with Lisinopril. Recent wellness visit on 2025-10-15 showed good glycemic control (HbA1c 6.8%) and blood pressure within target range (128/82 mmHg). No recent hospitalizations or emergency visits. Patient reports good medication adherence and regular exercise.",
  "key_conditions": [
    "Type 2 Diabetes Mellitus",
    "Essential Hypertension",
    "Hyperlipidemia"
  ],
  "active_medications": [
    "Metformin 500mg twice daily",
    "Lisinopril 10mg once daily",
    "Atorvastatin 20mg once daily"
  ],
  "recent_encounters": [
    "2025-10-15: Annual wellness visit - routine checkup",
    "2025-07-20: Follow-up for diabetes management",
    "2025-04-10: Lab work - HbA1c and lipid panel"
  ],
  "generated_at": "2025-11-14T10:30:00Z"
}
```

#### Response (Error - 404 Not Found)

```json
{
  "detail": "Patient 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

#### Response (Error - 422 Unprocessable Entity)

```json
{
  "detail": [
    {
      "loc": ["body", "patient_id"],
      "msg": "value is not a valid uuid",
      "type": "type_error.uuid"
    }
  ]
}
```

#### Response (Error - 500 Internal Server Error)

```json
{
  "detail": "Failed to generate clinical history"
}
```

---

## Source Tree

### Existing Project Structure

```
fhirside-chat/
├── README.md
├── pyproject.toml
├── docker-compose.yaml
├── src/
│   ├── __init__.py
│   ├── app.py                    # FastAPI application
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── agents.py             # AI agent definitions
│   │   └── telemetry.py          # OpenTelemetry setup
│   └── models/
│       ├── __init__.py
│       └── patient.py            # Patient SQLModel
├── tests/
│   ├── __init__.py
│   └── ai/
│       ├── __init__.py
│       ├── test_agents.py
│       └── test_telemetry.py
└── aidbox/
    ├── Dockerfile
    └── init-bundle.json
```

### New File Organization

```
fhirside-chat/
├── src/
│   ├── app.py                    # Modified: Add POST /patient endpoint
│   ├── ai/
│   │   └── agents.py             # Modified: Add patient_history_agent()
│   └── models/
│       ├── patient.py            # Unchanged
│       └── clinical_history.py   # NEW: PatientHistoryRequest, PatientClinicalHistory
└── tests/
    ├── models/                   # NEW: Test directory for models
    │   ├── __init__.py
    │   └── test_clinical_history.py  # NEW: Model tests
    └── test_app.py               # NEW: Endpoint integration tests
```

### Integration Guidelines

- **File Naming:** Follow existing snake_case convention (e.g., `clinical_history.py`)
- **Folder Organization:** Group by concern (models, ai, tests) matching existing structure
- **Import/Export Patterns:**
  - Expose public APIs through `__init__.py` files
  - Use absolute imports: `from src.models.clinical_history import PatientClinicalHistory`
  - Follow existing pattern in `src/ai/agents.py` for agent creation functions

---

## Infrastructure and Deployment Integration

### Existing Infrastructure

**Current Deployment:** Local development with Docker Compose; no production deployment defined yet
**Infrastructure Tools:** Docker, Docker Compose
**Environments:** Development only (localhost)

**Service Architecture:**
- `aidbox`: Aidbox FHIR server (port 8080)
- `aidbox-db`: PostgreSQL database for Aidbox (port 5432)
- `jaeger`: Jaeger tracing backend (port 16686 UI, 4317/4318 OTLP)
- FastAPI app: Runs outside Docker via `uvicorn` (port 8000)

### Enhancement Deployment Strategy

**Deployment Approach:** No infrastructure changes required

- New `/patient` endpoint is part of existing FastAPI application
- No new services or containers needed
- Same `uvicorn` startup command: `uv run uvicorn src:app --host 0.0.0.0 --port 8000 --reload`
- Same environment variables (OpenAI credentials, Aidbox license)

**Infrastructure Changes:** None

**Pipeline Integration:** N/A (no CI/CD pipeline exists yet)

### Rollback Strategy

**Rollback Method:** Git revert or branch switch

- Enhancement is purely additive; existing endpoints unaffected
- To roll back: revert commits or switch to previous git branch
- No database migrations to reverse (stateless v1)
- No infrastructure state to manage

**Risk Mitigation:**
- Feature flag pattern not needed (separate endpoint)
- Can deploy and test without impacting existing chat functionality
- OpenTelemetry traces allow debugging issues without affecting production

**Monitoring:**
- Use Jaeger UI (http://localhost:16686) to monitor new endpoint performance
- Track OpenTelemetry spans for `/patient` endpoint separately from `/chat`
- Log analysis via standard Python logging (console output in development)

---

## Coding Standards

### Existing Standards Compliance

**Code Style:** PEP 8 compliance (no explicit formatter configured, but code follows conventions)
**Linting Rules:** Ruff configured in `pyproject.toml` ([dependency-groups].dev includes `ruff>=0.13.3`)
**Testing Patterns:** pytest with pytest-asyncio for async tests; test files mirror source structure
**Documentation Style:** Docstrings in Google style; inline comments for complex logic

**Type Hints:** Extensive use of type hints with Python 3.13 features (`from __future__ import annotations`)

### Enhancement-Specific Standards

- **Pydantic Models:** Use `Field()` with descriptions for all model attributes to generate clear schemas
- **Async/Await:** All new endpoint handlers and agent operations must use `async def` and `await`
- **Error Handling:** Raise FastAPI `HTTPException` for HTTP errors; log exceptions with context before raising
- **OpenTelemetry:** Ensure all new agent functions use `instrument=instrumentation()` parameter
- **Imports:** Group imports (stdlib, third-party, local) with blank lines between groups

### Critical Integration Rules

- **Existing API Compatibility:** New endpoint must not modify existing `/chat` or `/ws` endpoint behavior
- **Database Integration:** No database operations in v1; if persistence is added later, use async SQLAlchemy patterns
- **Error Handling:** Follow existing pattern in `src/app.py` - catch exceptions, log with logger, raise HTTPException
- **Logging Consistency:** Use standard Python `logging` module; configure logger name as `fhirside_chat.{module}`

---

## Testing Strategy

### Integration with Existing Tests

**Existing Test Framework:** pytest with pytest-asyncio for async test support
**Test Organization:** Mirror source structure (`tests/ai/` for `src/ai/`, etc.)
**Coverage Requirements:** No explicit coverage target defined; aim for critical path coverage

**Existing Test Patterns:**
- Test files named `test_{module}.py`
- Async tests decorated with `@pytest.mark.asyncio`
- Fixtures used for setup/teardown
- Mocking external dependencies (MCP, OpenAI)

### New Testing Requirements

#### Unit Tests for New Components

- **Framework:** pytest + pytest-asyncio
- **Location:**
  - `tests/models/test_clinical_history.py` - Model validation tests
  - `tests/ai/test_agents.py` - Add tests for `patient_history_agent()`
  - `tests/test_app.py` - Endpoint handler tests
- **Coverage Target:** 80%+ for new code (models, agent, endpoint)
- **Integration with Existing:** Use same pytest configuration and patterns

**Key Test Cases:**
```python
# Model tests
def test_patient_history_request_valid_uuid():
    """Test PatientHistoryRequest accepts valid UUID"""

def test_patient_history_request_invalid_uuid():
    """Test PatientHistoryRequest rejects invalid UUID"""

def test_patient_clinical_history_serialization():
    """Test PatientClinicalHistory serializes to JSON correctly"""

# Agent tests
@pytest.mark.asyncio
async def test_patient_history_agent_initialization():
    """Test agent creation with correct configuration"""

# Endpoint tests
@pytest.mark.asyncio
async def test_patient_endpoint_success(mock_agent):
    """Test successful patient history generation"""

@pytest.mark.asyncio
async def test_patient_endpoint_not_found(mock_agent):
    """Test 404 response when patient not found"""
```

#### Integration Tests

- **Scope:** End-to-end flow from HTTP request to JSON response (with mocked external services)
- **Existing System Verification:** Ensure `/chat` and `/ws` endpoints still function after changes
- **New Feature Testing:** Test `/patient` endpoint with various scenarios (success, errors, edge cases)

**Mock Strategy:**
- Mock `MCPServerSSE` to simulate Aidbox responses
- Mock Azure OpenAI client to return predictable LLM outputs
- Use `pytest-mock` or `unittest.mock` for mocking

#### Regression Testing

- **Existing Feature Verification:** Run full existing test suite to ensure no regressions
- **Automated Regression Suite:** Existing pytest tests serve as regression suite
- **Manual Testing Requirements:**
  - Test existing chat endpoint with real Aidbox/OpenAI
  - Test new patient endpoint with real Aidbox/OpenAI
  - Verify OpenTelemetry traces in Jaeger for both endpoints

---

## Security Integration

### Existing Security Measures

**Authentication:** None (development environment only)
**Authorization:** None (development environment only)
**Data Protection:** HTTPS not configured (localhost HTTP only); environment variables for secrets (OpenAI API key, Aidbox license)
**Security Tools:** None explicitly configured

**Current Security Posture:** Development-grade only; not production-ready

### Enhancement Security Requirements

**New Security Measures:** None for v1 (matches existing security level)

**Integration Points:**
- New endpoint has same security posture as existing endpoints (no auth)
- When authentication is added in future, all endpoints (`/chat`, `/ws`, `/patient`) should be secured consistently
- OpenAI API key and Aidbox credentials remain in environment variables

**Compliance Requirements:**
- **HIPAA/PHI:** This application handles Protected Health Information. In production:
  - Must implement authentication and authorization
  - Must use HTTPS/TLS for all API communication
  - Must implement audit logging of PHI access
  - Must secure environment variables (secrets management)
  - **v1 is NOT HIPAA compliant** - development/testing only

### Security Testing

**Existing Security Tests:** None

**New Security Test Requirements:**
- Defer security testing until authentication is implemented
- For v1: Validate that sensitive data (OpenAI API key) is not logged or exposed in responses

**Penetration Testing:** Not applicable for v1 development environment

**Security Roadmap for Future:**
1. Implement OAuth2/JWT authentication
2. Add role-based access control (RBAC)
3. Enable HTTPS with valid certificates
4. Implement secrets management (e.g., HashiCorp Vault)
5. Add audit logging for PHI access
6. Conduct security audit and penetration testing

---

## Next Steps

### Implementation Sequence

1. **Create Data Models** (`src/models/clinical_history.py`)
   - Implement `PatientHistoryRequest` and `PatientClinicalHistory`
   - Add unit tests for model validation and serialization

2. **Create Patient History Agent** (`src/ai/agents.py`)
   - Implement `patient_history_agent()` function
   - Define system prompt for clinical history synthesis
   - Add unit tests for agent initialization

3. **Create API Endpoint** (`src/app.py`)
   - Implement `POST /patient` endpoint handler
   - Integrate with `patient_history_agent()`
   - Add integration tests

4. **Manual Testing & Iteration**
   - Test with real Aidbox patient data
   - Refine system prompt based on output quality
   - Monitor performance with Jaeger
   - Iterate on prompt and error handling

5. **Documentation**
   - Update README.md with new endpoint usage
   - Add example curl command
   - Document expected response format

### Developer Handoff

**For developers implementing this enhancement:**

1. **Read this architecture document** thoroughly, especially:
   - Data Models section (simplified v1 approach rationale)
   - Component Architecture (implementation patterns)
   - Coding Standards (consistency requirements)

2. **Start with models first:**
   - Create `src/models/clinical_history.py`
   - Implement and test `PatientHistoryRequest` and `PatientClinicalHistory`
   - Verify JSON serialization works as expected

3. **Key technical decisions to follow:**
   - Reuse existing OpenAI client configuration (don't create new credentials)
   - Reuse existing MCP connection (same SSE endpoint)
   - Follow async/await patterns consistently
   - Use existing `instrumentation()` for telemetry

4. **Integration checkpoints:**
   - After creating models: Verify they serialize correctly to JSON
   - After creating agent: Test that it initializes without errors
   - After creating endpoint: Test with mock agent before real MCP/OpenAI
   - After integration: Verify existing `/chat` endpoint still works
   - Final: Test end-to-end with real services

5. **System prompt iteration:**
   - Start with the prompt defined in Component Architecture section
   - Test with 2-3 real patients
   - Refine based on output quality (narrative clarity, data accuracy)
   - Document prompt changes in git commit messages

6. **Error handling requirements:**
   - Gracefully handle missing FHIR data (empty lists, optional fields)
   - Log all exceptions with patient_id for debugging
   - Return appropriate HTTP status codes (404, 500)
   - Ensure OpenTelemetry traces capture errors

7. **Testing requirements:**
   - Run existing test suite after each major change
   - Add new tests before implementing (TDD approach recommended)
   - Test with various patient scenarios (complete data, sparse data, no data)
   - Verify OpenTelemetry spans appear in Jaeger UI

**Existing system compatibility is paramount:** This is a brownfield enhancement. At every step, verify that existing functionality remains intact.

