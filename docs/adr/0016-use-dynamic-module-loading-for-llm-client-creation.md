# ADR 0016: Use Dynamic Module Loading for LLM Client Creation

## Status

Accepted

## Date

2025-12-08

## Context

LLMProcessor requires an LLMClient (e.g., OllamaLLMClient) to function. The ollama library is an optional dependency - users may not have it installed if they don't use LLM features.

Without guards, importing infrastructure code would fail with ImportError when ollama is not installed, breaking the entire application even for users who only want PassThroughProcessor.

## Decision

Use importlib for dynamic module loading in LLMClientFactory.

```python
# infrastructure/llm_clients/factory.py
class LLMClientFactory:
    def create(self, profile: BaseLLMClientSettings) -> LLMClient:
        if isinstance(profile, OllamaLLMClientSettings):
            try:
                ollama_client_module = importlib.import_module(
                    "shtym.infrastructure.llm_clients.ollama_client"
                )
                return ollama_client_module.OllamaLLMClient.create(settings=profile)
            except ImportError as e:
                raise LLMModuleNotFoundError("ollama") from e
```

## Rationale

- **Graceful degradation**: Application works without ollama library installed
- **Delayed import**: Only imports LLM modules when actually needed
- **Clear error messages**: LLMModuleNotFoundError provides actionable feedback
- **Zero-configuration default**: PassThroughProcessor users don't need LLM dependencies

## Implications

### Positive Implications

- Application installable and usable without LLM dependencies
- LLM features opt-in via optional dependency group
- Clear error when LLM requested but dependencies missing
- Follows principle of "fail late" for optional features

### Concerns

- Dynamic imports harder to trace statically (mitigation: only used in factory, well-documented)
- Type checkers may not catch import errors (mitigation: tests cover import failure scenarios)
- Slightly more complex than static imports (mitigation: complexity isolated in factory)

## Alternatives

### Static Imports with Try/Except at Module Level

Import ollama at module top level, wrap in try/except.

```python
try:
    from ollama import Client
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
```

**Pros**: Simpler, checked once at import time

**Cons**: Fails entire module if import fails; cannot provide user-facing error at usage time

**Reason for rejection**: Want to provide clear error message when user tries to use LLM, not when module loads

### Optional Dependency with Runtime Check

Make ollama required dependency, check availability at runtime.

**Pros**: Simplest implementation, static imports

**Cons**: Forces all users to install ollama even if not using LLM features

**Reason for rejection**: Violates zero-configuration principle for PassThrough users

### Plugin Architecture

Use plugin system to load LLM clients dynamically.

**Pros**: Maximum flexibility, extensible

**Cons**: Over-engineered for current needs; adds significant complexity

**Reason for rejection**: importlib provides sufficient flexibility with minimal overhead

## References

- [Issue #10: Introduce default profile concept](https://github.com/osoekawaitlab/shtym-py/issues/10)
- [ADR-0009: Silent Fallback to PassThrough Processor on Model Unavailability](./0009-silent-fallback-to-passthrough-filter.md)
- [Python importlib documentation](https://docs.python.org/3/library/importlib.html)
