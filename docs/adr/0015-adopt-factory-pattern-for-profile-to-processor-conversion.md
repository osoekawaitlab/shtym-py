# ADR 0015: Adopt Factory Pattern for Profile-to-Processor Conversion

## Status

Accepted

## Date

2025-12-08

## Context

Profiles (domain objects) contain configuration for output transformation. Processors (infrastructure implementations) perform the actual transformation.

The application needs to convert Profile → Processor. This conversion involves:
- Type-based dispatch (LLMProfile → LLMProcessor, future profiles → other processors)
- Infrastructure-specific instantiation (LLM clients, API connections, etc.)
- Error handling for unsupported profile types

Without abstraction, domain layer would need to know about all infrastructure implementations.

## Decision

Introduce ProcessorFactory protocol in domain layer and ConcreteProcessorFactory in infrastructure layer.

```python
# domain/processor.py
class ProcessorFactory(Protocol):
    def create(self, profile: Profile) -> Processor: ...

# infrastructure/processors/factory.py
class ConcreteProcessorFactory:
    def create(self, profile: Profile) -> Processor:
        if isinstance(profile, LLMProfile):
            return LLMProcessor.create(profile=profile)
        raise ProcessorCreationError(...)
```

## Rationale

- **Dependency Inversion**: Domain depends on ProcessorFactory abstraction, not concrete implementations
- **Open/Closed**: Adding new profile types requires only new infrastructure code, no domain changes
- **Type-based dispatch**: Factory centralizes profile-type-to-processor-implementation mapping
- **Encapsulation**: Infrastructure creation details hidden from domain layer

## Implications

### Positive Implications

- Domain layer remains ignorant of infrastructure implementations
- Easy to add new profile types (OpenAI, Claude, custom processors)
- Factory is single point for processor instantiation logic
- Testable via mock factories in domain tests

### Concerns

- Adds abstraction layer between Profile and Processor (mitigation: necessary for dependency inversion)
- Factory must know all profile types (mitigation: limited to infrastructure layer, acceptable coupling)

## Alternatives

### Direct Profile-to-Processor Method

Add `to_processor()` method on Profile base class.

```python
class Profile:
    def to_processor(self) -> Processor: ...
```

**Pros**: No separate factory needed, simple API

**Cons**: Domain objects create infrastructure objects, violates layering; Profile must import infrastructure

**Reason for rejection**: Violates dependency inversion and layered architecture

### Service Locator Pattern

Use service locator to find processor for given profile.

**Pros**: Decouples profile from processor creation

**Cons**: Hidden dependencies, harder to test, anti-pattern in modern design

**Reason for rejection**: Factory pattern is more explicit and testable

## References

- [Issue #10: Introduce default profile concept](https://github.com/osoekawaitlab/shtym-py/issues/10)
- [ADR-0010: Introduce Profile as Core Domain Object](./0010-introduce-profile-as-core-domain-object.md)
- [Factory Pattern](https://refactoring.guru/design-patterns/factory-method)
