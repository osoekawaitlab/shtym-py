# ADR 0003: Adopt Layered Architecture

## Status

Accepted

## Date

2025-11-21

## Context

Shtym needs to implement subprocess execution and output handling for pass-through mode (Issue #3), with future expansion to LLM integration. The current flat module structure (cli.py, core.py) lacks clear separation of concerns, which will make future LLM integration and testing more difficult.

A clear architectural pattern is needed to:

- Separate I/O concerns from business logic
- Enable easy testing without actual I/O operations
- Provide clear boundaries for future LLM integration
- Maintain code organization as functionality grows

## Decision

Adopt a layered architecture with four distinct layers:

```text
src/shtym/
├── _version.py           # Version constant
├── __init__.py           # Package exports
├── cli.py                # Presentation Layer
├── application.py        # Application Layer
├── domain.py             # Domain Layer
└── infrastructure/       # Infrastructure Layer
    ├── __init__.py
    └── stdio.py          # stdout writing
```

**Layer responsibilities:**

- **Presentation Layer** (cli.py): CLI argument parsing, error handling, user-facing messages
- **Application Layer** (application.py): Orchestration of domain and infrastructure components
- **Domain Layer** (domain.py): Core text processing logic (pass-through, future LLM summarization)
- **Infrastructure Layer** (infrastructure/): External I/O operations (stdio, future LLM API clients)

## Rationale

- **Testability**: Each layer can be tested independently. Infrastructure I/O can be mocked in unit tests
- **Separation of concerns**: Clear boundaries between user interface, orchestration, business logic, and external dependencies
- **Future LLM integration**: LLM clients will naturally fit in infrastructure layer alongside stdio
- **Maintainability**: Changes to I/O mechanisms or CLI don't affect business logic
- **Standard pattern**: Layered architecture is well-understood and documented
- **Lightweight**: Only four layers, avoiding over-engineering for small project

## Implications

### Positive Implications

- Unit tests can focus on pure logic without I/O
- Infrastructure components are swappable (e.g., different LLM providers)
- Clear mental model for future contributors
- Dependency flow is explicit (presentation → application → domain ← infrastructure)
- Easy to add new infrastructure adapters (file I/O, network, etc.)

### Concerns

- Slightly more files than flat structure (mitigation: only 3-4 additional modules, manageable)
- Requires discipline to maintain layer boundaries (mitigation: documented in ADR, enforced in code review)
- Possible over-engineering for simple pass-through (mitigation: pattern pays off immediately when LLM integration begins)

## Alternatives

### Flat Module Structure

Keep current flat structure with cli.py and core.py.

- **Pros**: Fewer files, simpler initial setup
- **Cons**: Tight coupling between I/O and logic, hard to test, unclear where to add LLM clients
- **Reason for rejection**: Technical debt accumulates quickly; refactoring later is harder than starting with clear structure

### Hexagonal Architecture (Ports and Adapters)

Use ports (interfaces) and adapters pattern.

- **Pros**: Maximum flexibility, very testable, clear boundaries
- **Cons**: More abstract, requires interfaces/protocols for every boundary, overhead for small project
- **Reason for rejection**: Too much ceremony for current needs; layered architecture provides similar benefits with less complexity

### MVC Pattern

Adopt Model-View-Controller pattern.

- **Pros**: Well-known web pattern
- **Cons**: Designed for UI interactions, not for CLI command wrapper tools; controller/view distinction unclear for CLI
- **Reason for rejection**: Not a natural fit for CLI command wrapper tools

## Future Direction

The layered architecture should remain stable through LLM integration. Potential triggers for revisiting:

- **Infrastructure layer grows too large**: If we add many infrastructure adapters (multiple LLM providers, various I/O sources), consider splitting into subdirectories (infrastructure/llm/, infrastructure/io/)
- **Cross-cutting concerns emerge**: If we need logging, metrics, or tracing across all layers, consider aspect-oriented patterns or middleware
- **Domain logic becomes complex**: If text processing logic grows significantly, consider splitting domain.py into multiple modules or introducing domain-driven design patterns

For now, this lightweight four-layer structure provides the right balance of organization and simplicity.

## References

- [Issue #3: Implement basic pass-through mode](https://github.com/osoekawaitlab/shtym-py/issues/3)
- [ADR-0001: Keep stdout Clean for AI and Human Consumption](./0001-keep-stdout-clean-for-ai-and-human-consumption.md)
- [Layered Architecture Pattern](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/ch01.html)
