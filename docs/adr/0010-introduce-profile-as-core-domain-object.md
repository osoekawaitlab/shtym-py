# ADR 0010: Introduce Profile as Core Domain Object

## Status

Accepted

## Date

2025-12-05

## Context

The application transforms command output using LLM. Users need a way to configure transformation behavior (prompt style, output format, LLM settings).

Currently, the application makes filter selection decisions internally without user control.

## Decision

Introduce "Profile" as a core domain concept. A profile represents a named configuration for output transformation.

## Rationale

- Users think in terms of transformation modes ("summarize briefly", "explain in detail", "extract errors"), not technical filter implementations
- Configuration naturally groups into reusable named profiles
- Profiles provide a stable user-facing abstraction independent of implementation changes

## Implications

### Positive Implications

- Clear vocabulary for discussing transformation configuration
- Natural extension point for user-defined transformation behaviors
- Decouples user intent from technical implementation

### Concerns

- Additional abstraction layer (mitigation: profiles match user mental model, not artificial complexity)

## Alternatives

### Direct Filter Configuration

Let users directly configure filters and LLM clients.

**Pros**: No intermediate abstraction

**Cons**: Exposes implementation details; users must understand filter architecture; configuration becomes fragile as implementation evolves

**Reason for rejection**: User-facing API should reflect user concepts, not internal architecture

## References

- [Issue #10: Introduce default profile concept](https://github.com/osoekawaitlab/shtym-py/issues/10)
- [ADR-0003: Adopt Layered Architecture](./0003-adopt-layered-architecture.md)
