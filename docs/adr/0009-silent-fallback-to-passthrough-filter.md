# ADR 0009: Silent Fallback to PassThrough Filter on Model Unavailability

## Status

Accepted (Amended 2025-12-06)

## Date

2025-12-04

## Context

Issue #7 adds environment variable support for LLM model configuration (`SHTYM_LLM_SETTINGS__MODEL`).

When the specified model is unavailable (not installed in Ollama, typo in model name, etc.), the application must decide whether to fail with an error or continue execution.

Current implementation: `Application.create()` checks `OllamaLLMClient.is_available()`. If `False`, it silently falls back to `PassThroughFilter`.

## Decision

When configured LLM model is unavailable, silently fall back to `PassThroughFilter` without warnings or errors.

```python
@classmethod
def create(cls, command: list[str]) -> "Application":
    try:
        llm_client = OllamaLLMClient.create()
        if llm_client.is_available():
            filter = LLMFilter(llm_client=llm_client)
        else:
            filter = PassThroughFilter()
    except ImportError:
        filter = PassThroughFilter()
    return cls(command=command, filter=filter)
```

## Rationale

- **Graceful degradation**: User can continue work even when LLM unavailable
- **Zero-configuration default**: Works without Ollama installation
- **No interruption**: No manual intervention required when model missing
- **Consistent behavior**: Same fallback mechanism for all unavailability scenarios

## Implications

### Positive Implications

- Application never fails due to LLM configuration issues
- Smooth user experience in environments without LLM access
- No breaking changes when upgrading models or switching environments

### Concerns

- Silent errors hide configuration mistakes (mitigation: add logging in future to warn when falling back to PassThroughFilter)
- Unexpected behavior when user expects LLM filtering but gets raw output (mitigation: add `--verbose` flag to show fallback notifications)
- Difficult debugging without indication that fallback occurred (mitigation: add `stym doctor` command to validate LLM configuration)

## Alternatives

### Fail with Error on Model Unavailability

**Behavior**: Exit with error message when model unavailable.

**Pros**:
- User immediately aware of configuration issues
- Explicit failure easier to debug than silent fallback

**Cons**:
- Breaks zero-configuration experience
- Requires manual intervention for every configuration issue
- Inconsistent with graceful degradation philosophy

**Reason for rejection**: Prioritize availability over strict validation in initial implementation.

### Warn but Continue

**Behavior**: Print warning to stderr, then fall back to PassThroughFilter.

**Pros**:
- User notified of fallback
- Still allows continued execution

**Cons**:
- Warning noise in logs/CI environments
- May be ignored or filtered out
- Complicates testing (need to assert stderr)

**Reason for rejection**: Defer notification mechanism to future enhancement. Current simple behavior easier to test and reason about.

## Future Direction

### Follow-up Actions

1. **Add structured logging**: Implement logging framework to warn when falling back to PassThroughFilter
2. **Add verbose mode**: Implement `--verbose` flag to show fallback notifications
3. **Add diagnostic command**: Implement `stym doctor` command to validate LLM configuration and report issues
4. **Add strict mode**: Implement `--strict-llm` flag to fail fast when model unavailable

### Triggers for Revisiting

This decision should be reconsidered when:

- Users report confusion about unexpected passthrough behavior
- Multiple bug reports about model configuration typos go unnoticed
- CI/CD pipelines require explicit validation of LLM availability
- Production deployments need guaranteed LLM filtering (no silent fallback)

## References

- [Issue #7: Allow LLM model configuration via environment variable](https://github.com/osoekawaitlab/shtym-py/issues/7)
- [ADR-0007: Introduce Filter Abstraction for Output Processing](./0007-introduce-filter-abstraction-for-output-processing.md)
- [ADR-0008: Introduce LLM Client Abstraction](./0008-introduce-llm-client-abstraction.md)

## Amendment (2025-12-06)

### What Changed

The term "Filter" used throughout this ADR has been renamed to "Processor":

- "PassThrough Filter" → "PassThrough Processor"
- "LLMFilter" → "LLMProcessor"

### Reason for Amendment

The term "Filter" strongly implies **reduction or removal**, but shtym's transformation capabilities extend beyond reduction. "Processor" is a more neutral and accurate term for output transformation.

See ADR-0013 for detailed rationale.

### Impact on Original ADR

**Unchanged:**

- The decision to silently fall back when model is unavailable remains valid
- The graceful degradation philosophy is unchanged
- Future direction (logging, verbose mode, doctor command) remains applicable

**Changed:**

- Terminology only: "Filter" → "Processor" throughout the codebase and documentation
