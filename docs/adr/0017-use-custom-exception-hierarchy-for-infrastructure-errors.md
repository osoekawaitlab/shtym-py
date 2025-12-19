# ADR 0017: Use Custom Exception Hierarchy for Infrastructure Errors

## Status

Accepted

## Date

2025-12-16

## Context

Infrastructure layer components interact with external systems such as file systems, networks, and configuration parsers. These operations can fail for various reasons (file not found, permission denied, network timeout, parse errors).

Python provides built-in exceptions like `FileNotFoundError`, `OSError`, and `ValueError` that can be raised directly. However, using Python built-in exceptions directly in the infrastructure layer creates inconsistency when some infrastructure components use domain-specific exceptions while others use built-ins.

This inconsistency makes error handling less uniform and harder to reason about. Callers need to catch both built-in exceptions and domain-specific exceptions, and it's unclear which layer is responsible for which error type.

## Decision

All infrastructure layer errors must extend `ShtymInfrastructureError`, which itself extends the base `ShtymError` exception class.

Infrastructure components must catch Python built-in exceptions (such as `FileNotFoundError`, `OSError`, `ValueError`) at the boundary and re-raise them as domain-specific exceptions that extend `ShtymInfrastructureError`.

## Rationale

**Consistency**: All infrastructure errors follow the same pattern, making error handling uniform across the codebase.

**Clear layer boundaries**: The exception hierarchy explicitly marks which errors come from which architectural layer. Infrastructure errors are distinguishable from domain errors and application errors.

**Simplified error handling**: Callers can catch `ShtymInfrastructureError` to handle all infrastructure failures without needing to know about specific Python built-in exceptions.

**Extensibility**: New infrastructure error types can be added by extending `ShtymInfrastructureError`, maintaining consistency as the system evolves.

## Implications

### Positive Implications

- Exception hierarchy clearly reflects architectural layers
- Error handling code is more consistent and predictable
- Infrastructure errors can be handled uniformly by upper layers
- New contributors can easily understand which exceptions belong to which layer

### Concerns

- Adds boilerplate code to catch and re-raise built-in exceptions (mitigation: consistent pattern makes copy-paste straightforward; future helper utilities can reduce boilerplate if needed)
- Each new infrastructure component needs to define its own exception class (mitigation: clear naming convention and template pattern; existing examples serve as reference)
- Exception chaining must be used (`raise ... from e`) to preserve original error information (mitigation: linters and code review enforce proper chaining; tests verify stack traces)

## Alternatives

### Use Python Built-in Exceptions Directly

Allow infrastructure components to raise Python built-in exceptions like `FileNotFoundError`, `OSError`, `ValueError` without wrapping them.

**Pros**: Simpler implementation with no wrapper exceptions needed; less boilerplate code

**Cons**: Creates inconsistency when some components use domain exceptions; makes layer boundaries unclear; callers must know about both built-in and custom exceptions

**Reason for rejection**: Inconsistent with existing domain-specific exceptions like ProfileParserError; violates layered architecture principle

### Mix Built-in and Custom Exceptions Based on Error Type

Allow some exceptions to be built-ins (e.g., file errors) while others are custom (e.g., parsing errors).

**Pros**: Flexible approach; uses built-ins where they fit naturally

**Cons**: Creates confusion about which errors use which pattern; inconsistent error handling across infrastructure layer; unclear guidelines for contributors

**Reason for rejection**: Consistency is more valuable than flexibility; uniform pattern easier to understand and maintain

### Create Exception Wrappers Only at Application Boundaries

Let infrastructure layer raise built-in exceptions; convert to custom exceptions only at application entry points.

**Pros**: Minimal boilerplate in infrastructure layer; conversion logic centralized

**Cons**: Pushes error handling responsibility to application layer; doesn't clearly separate infrastructure concerns; leaks implementation details across layers

**Reason for rejection**: Violates separation of concerns; each layer should own its error types

## Future Direction

As new infrastructure components are added (network clients, database adapters, external API integrations), each must define its own exception class extending `ShtymInfrastructureError`.

If exception handling becomes overly verbose, consider introducing helper utilities to reduce boilerplate while maintaining the custom exception hierarchy.

## References

- ADR-0003: Adopt Layered Architecture - establishes the infrastructure layer
- Python Exception Hierarchy: <https://docs.python.org/3/library/exceptions.html>
