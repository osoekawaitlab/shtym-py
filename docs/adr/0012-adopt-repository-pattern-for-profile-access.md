# ADR 0012: Adopt Repository Pattern for Profile Access

## Status

Accepted

## Date

2025-12-05

## Context

ADR-0010 introduced Profile as a domain object. Profiles need to be retrieved by name and made available to the application.

Options for profile access:
1. Direct loading (Profile.load(name))
2. Service pattern (ProfileService.get(name))
3. Repository pattern (ProfileRepository.get(name))

## Decision

Use Repository pattern for profile access.

## Rationale

- **Domain-driven design**: Repository is the standard pattern for domain object lifecycle management
- **Testability**: Easy to inject mock repositories in tests
- **Clear extension point**: Future implementations can load from files, databases, or remote APIs
- **Separation of concerns**: Repository handles profile retrieval; Application handles business logic

## Implications

### Positive Implications

- Profile access logic separated from Application lifecycle
- Easy to test profile resolution independently
- Repository can be swapped for different storage backends

### Concerns

- Additional abstraction (mitigation: Repository is well-understood pattern with clear benefits)

## Alternatives

### Direct Loading

Use static method `Profile.load(name)`.

**Pros**: Simpler, fewer classes

**Cons**: Tight coupling to storage mechanism; hard to test; violates Single Responsibility Principle

**Reason for rejection**: Repository provides better separation and testability

### Service Pattern

Use `ProfileService` for profile operations.

**Pros**: Service pattern is flexible

**Cons**: Less specific than Repository; Repository is standard for domain object access

**Reason for rejection**: Repository pattern is more precise for this use case

## References

- [Issue #10: Introduce default profile concept](https://github.com/osoekawaitlab/shtym-py/issues/10)
- [ADR-0010: Introduce Profile as Core Domain Object](./0010-introduce-profile-as-core-domain-object.md)
- [Repository Pattern - Martin Fowler](https://martinfowler.com/eaaCatalog/repository.html)
