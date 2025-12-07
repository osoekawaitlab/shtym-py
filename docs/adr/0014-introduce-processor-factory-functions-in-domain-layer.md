# ADR 0014: Introduce Processor Factory Functions in Domain Layer

## Status

Accepted

## Date

2025-12-08

## Context

Application layer needs to create Processors from Profiles. The creation logic involves:
- Retrieving Profile from repository
- Handling ProfileNotFoundError
- Creating Processor from Profile via ProcessorFactory
- Wrapping Processor with fallback logic
- Handling ProcessorCreationError

Without domain-level factory functions, this complex creation logic would be duplicated across multiple places (CLI, tests, future API layer).

## Decision

Introduce two factory functions in domain layer:

```python
# domain/processor.py
def create_processor_with_fallback(
    profile: Profile, processor_factory: ProcessorFactory
) -> Processor:
    """Create processor with automatic fallback to PassThroughProcessor."""

def create_processor_from_profile_name(
    profile_name: str,
    profile_repository: ProfileRepository,
    processor_factory: ProcessorFactory,
) -> Processor:
    """Create processor from profile name with automatic fallback."""
```

## Rationale

- **Single Responsibility**: Each function handles one creation scenario
- **Reusability**: Application, CLI, and tests can use same creation logic
- **Domain logic in domain layer**: Fallback decision is business logic, not application orchestration
- **Dependency injection**: Functions accept repository and factory as parameters, enabling testability

## Implications

### Positive Implications

- Application layer simplified to single function call
- Consistent fallback behavior across all entry points
- Easy to test creation logic in isolation
- Clear extension point for future Processor creation variations

### Concerns

- Domain layer now depends on ProfileRepository abstraction (mitigation: repository is domain abstraction, this is acceptable)
- Factory functions increase domain layer API surface (mitigation: only two focused functions, both essential)

## Alternatives

### Application Layer Handles Creation

Place creation logic in Application.create() method.

**Pros**: Simpler domain layer, orchestration in application layer

**Cons**: Cannot reuse creation logic in CLI or other contexts; tests must test through Application

**Reason for rejection**: Creation logic is business rule (when to fallback), belongs in domain

### Builder Pattern

Use builder pattern for Processor creation.

**Pros**: Fluent API, can chain configuration

**Cons**: Overkill for two simple creation scenarios; more complex than needed

**Reason for rejection**: Factory functions provide sufficient flexibility with less ceremony

## References

- [Issue #10: Introduce default profile concept](https://github.com/osoekawaitlab/shtym-py/issues/10)
- [ADR-0011: Silent Fallback on Profile Not Found](./0011-silent-fallback-on-profile-not-found.md)
- [ADR-0012: Adopt Repository Pattern for Profile Access](./0012-adopt-repository-pattern-for-profile-access.md)
