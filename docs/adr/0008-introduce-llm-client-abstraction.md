# ADR 0008: Introduce LLM Client Abstraction

## Status

Accepted

## Date

2025-12-02

## Context

Issue #5 introduces LLM-based filtering using Ollama. Future requirements include support for multiple LLM providers (OpenAI, Claude, etc.).

Without abstraction, domain layer would directly depend on Ollama-specific APIs (`ollama.Client`, `Message`, `ResponseError`), making provider switching difficult and leaking infrastructure details into domain logic.

## Decision

Introduce `LLMClient` protocol in domain layer and `OllamaLLMClient` in infrastructure layer.

```text
domain/
  llm_client.py     # LLMClient protocol
  filter.py         # LLMFilter depends on LLMClient

infrastructure/
  ollama_client.py  # OllamaLLMClient implements LLMClient
```

LLMFilter (domain) depends on LLMClient protocol (domain). OllamaLLMClient (infrastructure) implements the protocol. Application layer injects client into filter.

## Rationale

- **Dependency Inversion**: Domain depends on abstraction, not concrete infrastructure
- **Extensibility**: Adding providers requires only new infrastructure implementation, zero domain changes
- **Testing**: Domain tests mock simple protocol; infrastructure tests verify real integrations
- **Encapsulation**: Provider-specific details (auth, message formats, errors) isolated in infrastructure

## Implications

### Positive Implications

- Adding new providers requires no domain changes
- Domain tests use simple mocks
- Provider complexity isolated in infrastructure

### Concerns

- Adds one layer of indirection (mitigation: negligible performance impact)
- Simple interface may not expose advanced features (mitigation: extend protocol when needed)

## Alternatives

### Ollama Direct in Domain Layer

- **Cons**: Domain depends on infrastructure; adding providers requires domain changes
- **Reason for rejection**: Multiple provider support is planned

### Strategy Pattern with Provider Enum

- **Cons**: Violates Open/Closed; provider logic mixed in domain
- **Reason for rejection**: Doesn't scale

### Abstract Base Class

- **Cons**: Requires inheritance; less flexible than Protocol
- **Reason for rejection**: Protocol is more Pythonic

## References

- [Issue #5: Add LLM-based filtering with Ollama](https://github.com/osoekawaitlab/shtym-py/issues/5)
- [ADR-0003: Adopt Layered Architecture](./0003-adopt-layered-architecture.md)
- [ADR-0007: Introduce Filter Abstraction for Output Processing](./0007-introduce-filter-abstraction-for-output-processing.md)
- [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)
