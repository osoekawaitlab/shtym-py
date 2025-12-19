# Development Guide

This guide covers the development workflow for shtym contributors.

## Prerequisites

- Python 3.10 or later
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver

## Development Setup

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

### 2. Clone the Repository

```bash
git clone https://github.com/osoekawaitlab/shtym-py.git
cd shtym-py
```

### 3. Install Dependencies

```bash
# Install development dependencies
uv sync --group dev

# Install with Ollama support
uv pip install -e ".[ollama]" --group dev

# Install documentation dependencies
uv sync --group docs
```

## Project Structure

```text
shtym-py/
├── src/shtym/              # Source code
│   ├── domain/             # Domain layer (business logic)
│   ├── infrastructure/     # Infrastructure layer (external integrations)
│   ├── application.py      # Application layer (orchestration)
│   ├── cli.py              # Presentation layer (CLI interface)
│   └── exceptions.py       # Exception hierarchy
├── tests/
│   ├── unit/               # Unit tests (mocked dependencies)
│   ├── e2e/                # End-to-end tests (with cassettes)
│   └── fixtures/           # Test fixtures and cassettes
├── docs/
│   ├── adr/                # Architecture Decision Records
│   └── architecture/       # Architecture documentation
├── noxfile.py              # Task automation
└── pyproject.toml          # Project configuration
```

### Architecture Layers

Shtym follows a layered architecture (see [ADR-0003](adr/0003-adopt-layered-architecture.md)):

- **Presentation Layer** (`cli.py`): Command-line interface
- **Application Layer** (`application.py`): Business logic orchestration
- **Domain Layer** (`domain/`): Core business concepts (Profile, Processor protocols)
- **Infrastructure Layer** (`infrastructure/`): External system integrations (file I/O, LLM clients)

For detailed architecture documentation, see [Architecture Overview](architecture/overview.md).

## Running Tests

Shtym uses [nox](https://nox.thea.codes/) for task automation. All test commands use uv as the backend.

### Unit Tests Only

```bash
# With Ollama support
uv run nox -s tests_unit

# Without Ollama dependency
uv run nox -s tests_unit_no_ollama
```

### End-to-End Tests Only

```bash
uv run nox -s tests_e2e
```

### All Tests with Coverage

```bash
# Runs all tests with coverage report (requires 80% minimum coverage)
uv run nox -s tests

# Coverage reports generated:
# - Terminal: detailed coverage per file
# - HTML: htmlcov/index.html
```

### Test Across All Python Versions

```bash
# Tests on Python 3.10, 3.11, 3.12, 3.13
uv run nox -s tests_all_versions
```

### E2E Test Cassettes

E2E tests interact with external services (Ollama LLM server) using a record/replay mechanism called "cassettes". This allows tests to run without requiring a live Ollama instance.

#### What Are Cassettes?

Cassettes are JSON files that record HTTP requests and responses during test execution. They are stored in `tests/fixtures/cassettes/` and contain:

- HTTP request details (method, path, query, body, headers)
- HTTP response data (status, body, headers)

Each cassette entry is keyed by a hash of the normalized request, ensuring consistent replay of identical requests.

Example cassette location: `tests/fixtures/cassettes/test_profiles_toml/test_load_profile_from_toml_file.json`

#### Replay Mode (Default)

By default, E2E tests run in **replay mode**:

```bash
# No Ollama server needed - uses recorded cassettes
uv run pytest tests/e2e/
```

**Behavior in replay mode:**

- Tests send HTTP requests to a local mock server (pytest-httpserver)
- Mock server responds with data from cassette files
- No external dependencies required (Ollama doesn't need to be running)
- Tests run quickly and deterministically
- Cassette files must exist or tests will fail

**Use replay mode for:**

- CI/CD pipelines
- Local development without Ollama
- Fast test execution
- Reproducible test results

#### Record Mode

When tests or Ollama interactions change, cassettes must be re-recorded:

```bash
# Requires running Ollama instance with appropriate model
SHTYMTEST_RECORDER_MODE=record uv run pytest tests/e2e/
```

**Behavior in record mode:**

- Tests send HTTP requests to local mock server (pytest-httpserver)
- Mock server forwards requests to real Ollama server
- Receives responses from Ollama and records request/response pairs to cassette files
- Overwrites existing cassettes with new recordings
- Requires Ollama server running at configured URL (default: `http://localhost:11434`)

**Prerequisites for recording:**

1. Ollama server must be running: `ollama serve`
2. Required model must be available: `ollama pull gpt-oss:20b` (or configured model)
3. Environment variables set if using non-default configuration:

   ```bash
   export SHTYM_LLM_SETTINGS__BASE_URL=http://localhost:11434
   export SHTYM_LLM_SETTINGS__MODEL=gpt-oss:20b
   ```

**When to record new cassettes:**

- Adding new E2E tests that interact with Ollama
- Changing prompt templates or LLM interaction logic
- Updating to new Ollama API version
- Modifying test data that affects LLM requests

**After recording:**

- Commit the updated cassette files to version control
- Verify tests still pass in replay mode: `uv run pytest tests/e2e/`
- Review cassette diffs to ensure expected changes only

#### Auto Mode

Auto mode intelligently switches between replay and record:

```bash
# Replays from cassette when available, records when missing
SHTYMTEST_RECORDER_MODE=auto uv run pytest tests/e2e/
```

**Behavior in auto mode:**

- If cassette entry exists for a request → replay from cassette (fast, no Ollama needed)
- If cassette entry missing for a request → forward to real Ollama server and record
- Automatically creates cassettes for new tests while using existing cassettes for unchanged tests

**Use auto mode for:**

- Adding new tests incrementally (only records new interactions)
- Updating specific tests (only re-records changed interactions)
- Local development workflow (avoids repeatedly recording unchanged tests)

**Prerequisites:**

- Same as record mode: Ollama server must be running with required model

## Code Quality

### Linting

```bash
# Check code style issues
uv run nox -s lint

# Or run directly
uv run ruff check .
```

### Formatting

```bash
# Auto-format code
uv run nox -s format_code

# Or run directly
uv run ruff format .
```

### Type Checking

```bash
# Run mypy type checker
uv run nox -s mypy

# Or run directly
uv run mypy src/ tests/
```

### Configuration

- **Ruff**: Configured in `pyproject.toml` with Google-style docstrings
- **Mypy**: Strict mode enabled with comprehensive type checking
- **Pytest**: Doctest modules, strict markers, random test order

## Building Documentation

```bash
# Build documentation site
uv run nox -s docs_build

# Serve locally (not in noxfile, run directly)
uv run mkdocs serve
```

Documentation is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) and deployed to GitHub Pages.

## Coding Standards

### Exception Handling

All infrastructure errors must extend `ShtymInfrastructureError` (see [ADR-0017](adr/0017-use-custom-exception-hierarchy-for-infrastructure-errors.md)):

```python
from shtym.exceptions import ShtymInfrastructureError

class FileReadError(ShtymInfrastructureError):
    """Exception raised when file reading fails."""

    def __init__(self, message: str) -> None:
        super().__init__(f"File read error: {message}")

# Always use exception chaining
try:
    with open(path) as f:
        return f.read()
except FileNotFoundError as e:
    msg = f"File not found: {path}"
    raise FileReadError(msg) from e
```

### Silent Fallback Pattern

When resources are unavailable (missing profiles, unavailable models), silently fall back to `PassThroughProcessor` (see [ADR-0009](adr/0009-silent-fallback-to-passthrough-filter.md) and [ADR-0011](adr/0011-silent-fallback-on-profile-not-found.md)):

```python
try:
    profile = repository.get(profile_name)
except ProfileNotFoundError:
    # Silent fallback - no warnings, no errors
    return PassThroughProcessor()
```

### Dependency Injection

Use constructor injection for testability:

```python
class FileBasedProfileRepository:
    def __init__(self, file_reader: FileReader, parser: TOMLProfileParser) -> None:
        self.file_reader = file_reader
        self.parser = parser
```

### Test Organization

- **Unit tests**: Mock all external dependencies (file I/O, HTTP, LLM clients)
- **E2E tests**: Use recorded cassettes for external service interactions
- **One test per behavior**: Each test validates a single specific behavior
- **Descriptive test names**: `test_<what>_<when>_<expected>` (e.g., `test_get_profile_raises_error_when_not_found`)

## Contributing

### Before Submitting a Pull Request

1. **Run all tests**: `uv run nox -s tests`
2. **Check code quality**: `uv run nox -s lint mypy`
3. **Format code**: `uv run nox -s format_code`
4. **Update documentation**: Add ADRs for architectural decisions
5. **Write tests**: Maintain 80%+ coverage with meaningful tests

### Commit Messages

Follow conventional commit format:

- `feat: add profile loading from TOML files`
- `fix: handle file read errors gracefully`
- `test: add E2E tests for profile loading`
- `docs: update development guide`
- `refactor: extract file reading logic`

### Architecture Decision Records

Document significant architectural decisions in `docs/adr/`:

1. Use template: `docs/adr/0000-adr-template.md`
2. Number sequentially: `0018-title.md`
3. Update `docs/architecture/overview.md` with summary
4. Focus on decisions, not implementations
5. Document why alternatives were rejected

## Debugging

### Enable Verbose Logging

```bash
# Set environment variable for debug output
export SHTYM_DEBUG=1
stym run pytest tests/
```

### Inspect Test Cassettes

E2E test cassettes are stored in `tests/fixtures/cassettes/`:

```bash
# View cassette content
cat tests/fixtures/cassettes/test_profiles_toml/test_load_profile_from_toml_file.json
```

### Test Individual Files

```bash
# Run specific test file
uv run pytest tests/unit/test_application.py -v

# Run specific test function
uv run pytest tests/unit/test_application.py::test_create_application_with_default_profile -v
```

## Release Process

(To be documented when release workflow is established)

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/osoekawaitlab/shtym-py/issues)
- **Architecture**: See [Architecture Overview](architecture/overview.md) and ADRs in `docs/adr/`
- **Project Goals**: See [Home](index.md)
