# ADR 0007: Introduce Filter Abstraction for Output Processing

## Status

Accepted

## Date

2025-11-21

## Context

Shtym is implementing basic pass-through mode (Issue #3) with the understanding that LLM-based output filtering will be added in the near future. The initial implementation could directly pass subprocess output to stdout, but this approach would require significant refactoring when adding LLM integration.

Key considerations:

- Current requirement: Pass subprocess output through unchanged
- Future requirement: Filter output through LLM for summarization
- Goal: Minimize code changes when adding LLM integration
- Constraint: Avoid over-engineering for hypothetical requirements

The question is whether to introduce an abstraction layer now or refactor later when LLM integration is implemented.

## Decision

Introduce a `Filter` protocol and implement `PassThroughFilter` immediately, even though current behavior requires no transformation.

**Architecture:**

```python
# Domain layer - Filter protocol
class Filter(Protocol):
    def filter(self, text: str) -> str: ...

# Domain layer - PassThroughFilter implementation
class PassThroughFilter:
    def filter(self, text: str) -> str:
        return text

# Application layer - process_command uses Filter
def process_command(
    command: list[str], text_filter: Filter
) -> ProcessedCommandResult:
    result = run_command(command)
    filtered_output = text_filter.filter(result.stdout)
    return ProcessedCommandResult(filtered_output, result.returncode)

# Presentation layer - CLI instantiates filter
def main() -> None:
    # ...
    text_filter = PassThroughFilter()
    result = process_command(args.command, text_filter)
    write_stdout(result.filtered_output)
```

## Rationale

**Minimizes future LLM integration changes:**

Adding LLM filtering will only require:

1. Implementing `LLMFilter` class with `filter(text: str) -> str` method
2. Changing CLI to instantiate `LLMFilter` instead of `PassThroughFilter`
3. Adding LLM configuration (API keys, model selection, etc.)

No changes needed to:

- `process_command` function
- Test infrastructure
- Exit code handling
- Core command execution logic

**Follows Dependency Injection pattern:**

- `process_command` depends on abstraction (`Filter` protocol), not concrete implementation
- Makes testing trivial - can inject mock filters with predictable behavior
- Presentation layer controls which filter to use based on configuration

**Adheres to SOLID principles:**

- **Open/Closed**: Can add new filter types without modifying `process_command`
- **Liskov Substitution**: Any `Filter` implementation works identically from caller's perspective
- **Dependency Inversion**: Application layer depends on domain abstraction, not infrastructure implementation

**Minimal current overhead:**

`PassThroughFilter` is trivial (~3 lines) and has zero performance impact. The abstraction adds clarity even for pass-through behavior: the code explicitly shows "we're applying a filter, which happens to pass through unchanged" rather than implicitly passing stdout.

**Clear extension point:**

The `Filter` protocol serves as documentation: "This is where output transformation happens." Future developers immediately understand where LLM integration belongs.

## Implications

### Positive Implications

- **Smooth LLM integration**: Adding `LLMFilter` is straightforward - implement protocol and swap in CLI
- **Testability**: Can test filters independently; can test `process_command` with mock filters
- **Flexibility**: Easy to support multiple filter types (pass-through, LLM summarization, custom filters)
- **Separation of concerns**: Output transformation logic separated from command execution
- **Type safety**: Protocol provides IDE autocomplete and type checking

### Concerns

- **Slight complexity increase**: Adds abstraction layer for currently-trivial behavior (mitigation: abstraction is minimal and will pay off immediately when LLM integration begins)
- **Indirection**: One extra function call (`filter.filter()`) in execution path (mitigation: negligible performance impact, clarity benefit outweighs cost)

## Alternatives

### Direct stdout Pass-Through

Pass subprocess stdout directly to `write_stdout` without filter abstraction.

```python
def main() -> None:
    result = run_command(args.command)
    write_stdout(result.stdout)
    sys.exit(result.returncode)
```

- **Pros**: Simplest possible implementation, zero abstraction overhead
- **Cons**: LLM integration requires modifying `run_command`, CLI logic, and all tests; no clear extension point
- **Reason for rejection**: Known future requirement (LLM integration) makes abstraction worthwhile immediately

### Conditional Filter Application

Check flag/config and conditionally apply filter.

```python
def process_command(command, use_llm=False):
    result = run_command(command)
    if use_llm:
        return llm_filter(result.stdout)
    return result.stdout
```

- **Pros**: No protocol needed, logic in one place
- **Cons**: Violates Open/Closed Principle; adding new filter types requires modifying `process_command`; harder to test
- **Reason for rejection**: Doesn't scale to multiple filter types; protocol-based approach is cleaner

### Strategy Pattern with Base Class

Use abstract base class instead of Protocol.

```python
class Filter(ABC):
    @abstractmethod
    def filter(self, text: str) -> str: ...
```

- **Pros**: Enforces implementation via ABC; similar to Protocol approach
- **Cons**: Requires inheritance; Protocol is more Pythonic for duck typing; heavier-weight
- **Reason for rejection**: Protocol provides same benefits with lighter syntax; aligns with Python typing best practices

## Future Direction

This abstraction should remain stable through LLM integration and beyond. Potential triggers for revisiting:

- **Multiple transformation steps**: If we need chaining (e.g., LLM summarization → Markdown formatting → Syntax highlighting), consider Composite Pattern or pipeline approach
- **Streaming output**: If we need to filter output as it streams (not batch), consider async generators or streaming protocols
- **Context-aware filtering**: If filters need access to command context (working directory, environment, history), consider enriching Filter protocol with context parameter

For now, the simple `filter(text: str) -> str` interface provides exactly what's needed for both pass-through and LLM summarization.

## References

- [Issue #3: Implement basic pass-through mode](https://github.com/osoekawaitlab/shtym-py/issues/3)
- [ADR-0003: Adopt Layered Architecture](./0003-adopt-layered-architecture.md)
- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy)
- [Dependency Injection Principle](https://en.wikipedia.org/wiki/Dependency_injection)
