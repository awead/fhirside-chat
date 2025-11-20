# Coding Standards

This document defines the coding standards and practices for the FHIRside Chat project.

## Core Principles

1. **No Comments Unless Absolutely Necessary** - Code should be self-documenting through clear naming and structure. Only add comments when the code cannot be made clearer through refactoring.
2. **Minimal Documentation** - Only public methods require docstrings. Private methods (starting with `_`) should not have docstrings unless performing complex or unusual operations. Never add docstrings to tests - test function names should be sufficient.
3. **SOLID Principles** - Follow Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion principles
4. **Small, Focused Units** - Avoid long files and large classes. Keep functions and classes tightly scoped with single responsibilities
5. **Dependency Injection** - Use dependency injection to separate concerns and enable testing. Pass dependencies explicitly rather than creating them internally
6. **Type Safety** - Extensive use of Python type hints with strict mode
7. **Async-First** - Prefer async/await for I/O operations
8. **Fail Fast** - Validate early, raise exceptions clearly

---

## Python Standards

### Language Version
- **Python 3.13+** required
- Use modern Python 3.13 features where appropriate
- Type hints are mandatory for all function signatures

### Code Style
- **Formatter:** ruff (configured in `pyproject.toml`)
- **Linter:** ruff (replaces flake8, black, isort)
- **Line Length:** 100 characters (ruff default)
- **Imports:** Organized automatically by ruff (stdlib, third-party, local)

### Type Hints
```python
from typing import Dict, List, Optional
from pydantic import BaseModel

async def process_message(session_id: str, message: str) -> str:
    ...

def get_session(session_id: str) -> Optional[Dict[str, List[str]]]:
    """Retrieve session data by session ID.

    Args:
        session_id: Unique session identifier.

    Returns:
        Session data as a dictionary, or None if not found.
    """
```

### Docstrings
Use **Google-style docstrings** for public APIs:

```python
def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured application instance with routes and middleware.

    Raises:
        RuntimeError: If required environment variables are missing.
    """
```

**Do NOT add docstrings for:**
- Private methods (prefixed with `_`) unless they perform complex or unusual operations
- Simple property getters/setters
- Obvious one-liners
- Test functions (test names should be self-documenting)

**Exception for complex private methods:**
```python
def _calculate_complex_metric(data: List[Dict]) -> float:
    """Calculate weighted average with exponential decay.

    This uses a custom algorithm for time-series weighting that may not be
    immediately obvious from the code alone.

    Args:
        data: Time-series data points with timestamps.

    Returns:
        Weighted average value.
    """
```

### No Comments Rule

**Only add comments when absolutely necessary.** Comments should explain *why*, not *what*.

❌ **Bad - Obvious comment:**
```python
session_id = request.session_id

output = await agent.run(prompt)
```

❌ **Bad - Comment instead of refactoring:**
```python
if x > 0 and x < 100 and status == "active":
    ...
```

✅ **Good - Refactor for clarity:**
```python
def is_valid_active_session(x: int, status: str) -> bool:
    return 0 < x < 100 and status == "active"

if is_valid_active_session(x, status):
    ...
```

✅ **Acceptable - Explains non-obvious why:**
```python
await asyncio.sleep(0.1)
```

**When comments are acceptable:**
- Explaining non-obvious algorithms or business logic
- Documenting workarounds for external library bugs
- Noting TODOs with ticket references
- Explaining performance optimizations

Code clarity comes from:
- Descriptive variable names
- Small, focused functions
- Clear control flow
- Proper abstractions
- Dependency injection

---

## Dependency Management

### Package Manager
- **Primary:** `uv` (fast, modern)
- **Fallback:** `pip` (standard)
- **Dependencies:** Defined in `pyproject.toml`

### Dependency Groups
```toml
[project]
dependencies = [...]  # Production dependencies

[dependency-groups]
dev = [...]  # Development tools (pytest, ruff, ipython)
```

### Adding Dependencies
```bash
uv add package-name
uv add --dev pytest-plugin
```

---

## SOLID Principles

Follow SOLID principles to maintain clean, maintainable code:

### 1. Single Responsibility Principle (SRP)
Each class/function should have one reason to change.

❌ **Bad - Multiple responsibilities:**
```python
class ChatService:
    def process_message(self, message: str) -> str:
        self._validate_message(message)
        self._log_message(message)
        response = self._call_llm(message)
        self._save_to_database(response)
        return response
```

✅ **Good - Separated concerns:**
```python
class MessageValidator:
    def validate(self, message: str) -> None:
        ...

class LLMClient:
    async def generate(self, prompt: str) -> str:
        ...

class ChatService:
    def __init__(self, validator: MessageValidator, llm: LLMClient):
        self._validator = validator
        self._llm = llm

    async def process(self, message: str) -> str:
        self._validator.validate(message)
        return await self._llm.generate(message)
```

### 2. Open/Closed Principle
Open for extension, closed for modification.

Use dependency injection and protocols/abstract base classes to allow extension without modification.

### 3. Liskov Substitution Principle
Subtypes must be substitutable for their base types.

### 4. Interface Segregation Principle
Many specific interfaces are better than one general-purpose interface.

### 5. Dependency Inversion Principle
Depend on abstractions, not concretions.

---

## Dependency Injection

Use dependency injection to:
- Separate concerns
- Enable testing with mocks
- Make dependencies explicit
- Reduce coupling

### Constructor Injection (Preferred)

```python
class ChatService:
    def __init__(
        self,
        agent_factory: Callable[[], Agent],
        validator: MessageValidator
    ):
        self._agent_factory = agent_factory
        self._validator = validator

    async def process(self, message: str) -> str:
        self._validator.validate(message)
        async with self._agent_factory() as agent:
            result = await agent.run(message)
            return result.output
```

### FastAPI Dependency Injection

```python
from fastapi import Depends

def get_chat_service() -> ChatService:
    return ChatService(
        agent_factory=chat_agent,
        validator=MessageValidator()
    )

@app.post("/chat")
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    output = await service.process(request.message)
    return ChatResponse(session_id=request.session_id, output=output)
```

### Testing with Dependency Injection

```python
@pytest.mark.asyncio
async def test_chat_service_with_mock():
    mock_agent = AsyncMock()
    mock_agent.run.return_value = Mock(output="test response")

    service = ChatService(
        agent_factory=lambda: mock_agent,
        validator=MessageValidator()
    )

    result = await service.process("test message")
    assert result == "test response"
```

---

## File and Class Size Guidelines

Keep files and classes small and focused:

### File Size
- **Target:** < 300 lines per file
- **Maximum:** 500 lines per file
- **If exceeded:** Split into multiple files by concern

### Class Size
- **Target:** < 200 lines per class
- **Maximum:** 300 lines per class
- **If exceeded:** Extract responsibilities into separate classes

### Function Size
- **Target:** < 30 lines per function
- **Maximum:** 50 lines per function
- **If exceeded:** Extract helper functions

### When to Split

❌ **Bad - Large class with multiple concerns:**
```python
class ChatService:
    def process_message(self, message: str) -> str: ...
    def validate_message(self, message: str) -> bool: ...
    def log_message(self, message: str) -> None: ...
    def save_history(self, message: str) -> None: ...
    def load_history(self, session_id: str) -> List[str]: ...
    def format_response(self, response: str) -> str: ...
```

✅ **Good - Separated into focused classes:**
```python
class MessageValidator:
    def validate(self, message: str) -> None: ...

class ChatHistory:
    def save(self, session_id: str, message: str) -> None: ...
    def load(self, session_id: str) -> List[str]: ...

class ResponseFormatter:
    def format(self, response: str) -> str: ...

class ChatService:
    def __init__(
        self,
        validator: MessageValidator,
        history: ChatHistory,
        formatter: ResponseFormatter
    ):
        ...

    async def process(self, session_id: str, message: str) -> str:
        self._validator.validate(message)
        self._history.save(session_id, message)
        response = await self._generate_response(message)
        return self._formatter.format(response)
```

---

## FastAPI Standards

### Application Structure
- Single `create_app()` factory function
- Routes defined as decorated functions
- Dependency injection for shared services

### Endpoint Patterns
```python
@app.post("/endpoint", response_model=ResponseModel)
async def endpoint_handler(req: RequestModel) -> ResponseModel:
    """Brief description of endpoint purpose.

    Args:
        req: Request payload.

    Returns:
        ResponseModel: Response payload.

    Raises:
        HTTPException: 404 if not found, 500 on internal error.
    """
    try:
        result = await some_async_operation(req)
        return result
    except SpecificError as e:
        logger.error("descriptive_error", extra={"context": str(e)})
        raise HTTPException(status_code=500, detail="User-friendly message")
```

### Request/Response Models
- Use Pydantic `BaseModel` for all request/response types
- Add `Field()` descriptions for OpenAPI documentation
- Validate strictly at API boundaries

```python
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    session_id: str = Field(description="Unique session identifier")
    message: str = Field(description="User message text")
```

### Error Handling
- Catch specific exceptions
- Log with structured context (`logger.error()` with `extra={}`)
- Raise `HTTPException` with appropriate status codes:
  - `400`: Bad request (client error)
  - `404`: Resource not found
  - `422`: Validation error (Pydantic handles automatically)
  - `500`: Internal server error

---

## Async/Await Standards

### When to Use Async
- **Always:** For I/O operations (HTTP, database, file I/O)
- **Always:** For PydanticAI agents (use `async with agent()`)
- **Never:** For CPU-bound operations

### Async Patterns
```python
async with resource() as r:
    result = await r.operation()

results = await asyncio.gather(
    operation1(),
    operation2()
)
```

### Context Managers
Prefer `async with` for resource management:
```python
async with chat_agent() as agent:
    result = await agent.run(prompt)
```

---

## Testing Standards

### Framework
- **pytest** for all tests
- **pytest-asyncio** for async tests
- **pytest-cov** for coverage reporting

### Test Organization
```
tests/
├── __init__.py
├── test_app.py           # API endpoint tests
├── ai/
│   ├── test_agents.py    # Agent tests
│   └── test_telemetry.py # Telemetry tests
└── models/
    └── test_clinical_history.py  # Model tests
```

### Test Naming
- Test files: `test_<module>.py`
- Test functions: `test_<feature>_<scenario>()`
- **No docstrings for tests** - test names should be self-documenting

```python
def test_chat_endpoint_returns_response_for_valid_request():
    ...

def test_chat_endpoint_raises_422_for_invalid_session_id():
    ...

@pytest.mark.asyncio
async def test_agent_run_with_mocked_llm_returns_expected_output():
    ...
```

### Test Structure

Use descriptive test names instead of docstrings:

```python
@pytest.mark.asyncio
async def test_endpoint_returns_same_session_id_as_request():
    request = ChatRequest(session_id="test-123", message="Hello")

    response = await chat_endpoint(request)

    assert response.session_id == "test-123"
    assert len(response.output) > 0
```

### Test Organization with Dependency Injection

```python
@pytest.fixture
def mock_validator():
    return Mock(spec=MessageValidator)

@pytest.fixture
def mock_llm():
    mock = AsyncMock(spec=LLMClient)
    mock.generate.return_value = "test response"
    return mock

@pytest.mark.asyncio
async def test_chat_service_uses_validator(mock_validator, mock_llm):
    service = ChatService(validator=mock_validator, llm=mock_llm)

    await service.process("test message")

    mock_validator.validate.assert_called_once_with("test message")
```

### Coverage Requirements
- **Target:** 80%+ coverage for new code
- **Run:** `pytest --cov=src tests/`
- **Exceptions:** Skip coverage for:
  - `__init__.py` files with only imports
  - Development scripts

---

## PydanticAI Standards

### Agent Creation
```python
from pydantic_ai import Agent

def agent_name() -> Agent[ReturnType]:
    """Create agent with specific purpose.

    Returns:
        Agent configured for specific task.
    """
    model = OpenAIChatModel(...)
    system_prompt = """Clear instructions..."""

    return Agent(
        model,
        result_type=ReturnType,
        system_prompt=system_prompt,
        toolsets=[mcp_server],
        instrument=instrumentation()
    )
```

### Agent Usage
```python
async with agent_name() as agent:
    result = await agent.run(prompt)
    output = result.output
```

### Structured Outputs
Use Pydantic models as `result_type` for structured LLM responses:
```python
class AgentOutput(BaseModel):
    field1: str
    field2: List[str]

agent = Agent(model, result_type=AgentOutput, ...)
```

---

## Logging Standards

### Logger Setup
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Structured Logging
Use `extra` for context:
```python
logger.info("operation_success", extra={
    "session_id": session_id,
    "duration_ms": duration
})

logger.error("operation_failed", extra={
    "session_id": session_id,
    "error": str(error)
})
```

### Log Levels
- `DEBUG`: Detailed diagnostic information
- `INFO`: Confirmation of expected behavior
- `WARNING`: Unexpected but handled situation
- `ERROR`: Serious problem, operation failed
- `CRITICAL`: System-level failure

---

## OpenTelemetry Standards

### Instrumentation
```python
from src.ai.telemetry import instrumentation

agent = Agent(
    model,
    instrument=instrumentation()
)
```

### Span Attributes
Add context to spans for debugging:
```python
span.set_attribute("session_id", session_id)
span.set_attribute("operation", "chat_message")
```

---

## File Organization

### Module Structure
```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from .ai.agents import agent_function
from .models.schemas import ModelClass
```

### Import Order (managed by ruff)
1. Standard library
2. Third-party packages
3. Local application imports

### Naming Conventions
- **Modules:** `lowercase_with_underscores.py`
- **Classes:** `PascalCase`
- **Functions:** `lowercase_with_underscores()`
- **Constants:** `UPPERCASE_WITH_UNDERSCORES`
- **Private:** `_leading_underscore`

---

## Environment Configuration

### Environment Variables
- Defined in `.env` file (gitignored)
- Example in `env-sample.txt`
- Accessed via `os.getenv()` or Pydantic Settings

### Required Variables
- `OPENAI_API_KEY`: Azure OpenAI API key
- `OPENAI_API_ENDPOINT`: Azure OpenAI endpoint URL
- `OPENAI_API_VERSION`: API version (e.g., "2024-12-01-preview")
- `OPENAI_MODEL`: Model name (e.g., "gpt-4o")
- `AIDBOX_LICENSE_KEY`: Aidbox license

---

## Code Review Checklist

Before submitting code:
- [ ] Ruff passes (`ruff check .` and `ruff format .`)
- [ ] All tests pass (`pytest`)
- [ ] Coverage ≥ 80% for new code (`pytest --cov`)
- [ ] Type hints present for all function signatures
- [ ] Only public methods have docstrings
- [ ] No docstrings on private methods (unless complex)
- [ ] No docstrings on tests
- [ ] No comments unless absolutely necessary
- [ ] SOLID principles followed
- [ ] Files < 500 lines, classes < 300 lines, functions < 50 lines
- [ ] Dependency injection used for testability
- [ ] Async/await used for I/O operations
- [ ] Error handling with specific exceptions
- [ ] Logging includes structured context

---

## Performance Guidelines

### Async Best Practices
- Use `asyncio.gather()` for parallel operations
- Avoid blocking calls in async functions
- Use `asyncio.to_thread()` for unavoidable blocking operations

### Database (Future)
- Use connection pooling
- Minimize N+1 queries
- Index foreign keys and frequently queried fields

### API Performance
- Response time target: < 5 seconds for typical chat requests
- Use pagination for large result sets
- Implement rate limiting for production

---

## Security Standards

### Input Validation
- All user input validated by Pydantic models
- UUID format validation for IDs
- String length limits for text fields

### API Keys
- Never hardcode API keys
- Use environment variables
- Never log API keys

### Error Messages
- Never expose stack traces to clients
- Log detailed errors server-side
- Return generic error messages to clients

---

## Documentation Standards

### README
- Setup instructions
- Environment variable requirements
- How to run tests
- How to start the server

### API Documentation
- Automatic via FastAPI OpenAPI
- Accessible at `/docs` (Swagger UI)
- Keep request/response models documented

### Architecture Documentation
- High-level architecture in `docs/architecture/`
- Decision records for significant choices
- Update when architecture changes

---

## Prohibited Patterns

❌ **Do Not:**
- Add comments unless absolutely necessary
- Add docstrings to private methods (unless complex operations)
- Add docstrings to test functions
- Create large classes (> 300 lines) or long files (> 500 lines)
- Instantiate dependencies inside classes (use dependency injection)
- Use wildcard imports (`from module import *`)
- Catch broad exceptions without re-raising (`except Exception: pass`)
- Use mutable default arguments (`def func(items=[]):`)
- Modify global state
- Use `print()` instead of `logger`
- Ignore type hints
- Write untested code

---

## Questions?

Refer to:
- Tech Stack: `docs/architecture/tech-stack.md`
- Source Tree: `docs/architecture/source-tree.md`
- Existing codebase for patterns
