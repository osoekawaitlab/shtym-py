# Architecture Overview

This document provides a high-level overview of architectural decisions made for the shtym project.

## Architecture Decision Records

### [ADR-0001: Keep stdout Clean for AI and Human Consumption](../adr/0001-keep-stdout-clean-for-ai-and-human-consumption.md)

**Status**: Accepted | **Date**: 2025-11-20

Keep stdout exclusively for AI-generated summaries, directing all other output to stderr for clean consumption by humans and AI agents.

---

### [ADR-0002: Use argparse for CLI Implementation](../adr/0002-use-argparse-for-cli-implementation.md)

**Status**: Accepted | **Date**: 2025-11-20

Use Python's standard library argparse for CLI parsing to maintain zero external dependencies and align with the clean output philosophy.

---

### [ADR-0003: Adopt Layered Architecture](../adr/0003-adopt-layered-architecture.md)

**Status**: Accepted | **Date**: 2025-11-21

Adopt a four-layer architecture (Presentation, Application, Domain, Infrastructure) to separate concerns, enable testing, and prepare for future LLM integration.

---

### [ADR-0004: Do Not Implement Stdin Pipe Mode](../adr/0004-do-not-implement-stdin-pipe-mode.md)

**Status**: Accepted | **Date**: 2025-11-21

Use wrapper mode (`stym run command`) instead of pipe mode (`command | stym`) to enable exit code inheritance, which is critical for CI/CD integration.

---

### [ADR-0005: Inherit Child Process Exit Codes](../adr/0005-inherit-child-process-exit-codes.md)

**Status**: Accepted | **Date**: 2025-11-21

Shtym must inherit and propagate the child process exit code exactly as-is, following Unix wrapper command conventions (sudo, timeout, time) for seamless CI/CD integration.

---

### [ADR-0006: Adopt Subcommand Architecture](../adr/0006-adopt-subcommand-architecture.md)

**Status**: Accepted | **Date**: 2025-11-21

Adopt subcommand architecture (`stym run`, `stym status`, `stym config`) to enable future features without breaking changes or command ambiguity.

---

### [ADR-0007: Introduce Filter Abstraction for Output Processing](../adr/0007-introduce-filter-abstraction-for-output-processing.md)

**Status**: Accepted | **Date**: 2025-11-21

Introduce Filter protocol with PassThroughFilter implementation now to minimize code changes when adding LLM integration, following Dependency Injection and SOLID principles.

---

### [ADR-0008: Introduce LLM Client Abstraction](../adr/0008-introduce-llm-client-abstraction.md)

**Status**: Accepted (Amended 2025-12-08) | **Date**: 2025-12-02

Introduce LLMClient protocol as internal infrastructure abstraction and OllamaLLMClient implementation to decouple LLM processor from specific providers. Amendment clarifies LLMClient belongs in infrastructure layer, not domain layer.

---

### [ADR-0009: Silent Fallback to PassThrough Filter on Model Unavailability](../adr/0009-silent-fallback-to-passthrough-filter.md)

**Status**: Accepted | **Date**: 2025-12-04

When configured LLM model is unavailable, silently fall back to PassThroughFilter without warnings or errors, prioritizing graceful degradation and zero-configuration experience over strict validation.

---

### [ADR-0010: Introduce Profile as Core Domain Object](../adr/0010-introduce-profile-as-core-domain-object.md)

**Status**: Accepted | **Date**: 2025-12-05

Introduce "Profile" as a core domain concept representing a named configuration for output transformation, providing a stable user-facing abstraction independent of implementation changes.

---

### [ADR-0011: Silent Fallback on Profile Not Found](../adr/0011-silent-fallback-on-profile-not-found.md)

**Status**: Accepted | **Date**: 2025-12-05

When requested profile does not exist, silently fall back to PassThroughFilter without warnings or errors, consistent with ADR-0009's graceful degradation pattern.

---

### [ADR-0012: Adopt Repository Pattern for Profile Access](../adr/0012-adopt-repository-pattern-for-profile-access.md)

**Status**: Accepted | **Date**: 2025-12-05

Use Repository pattern for profile access to separate profile retrieval logic from application business logic, enabling testability and future storage backend flexibility.

---

### [ADR-0013: Rename Filter to Processor](../adr/0013-rename-filter-to-processor.md)

**Status**: Accepted | **Date**: 2025-12-06

Rename "Filter" to "Processor" to better reflect the abstraction's purpose of transforming output (expansion, conversion, translation) rather than only filtering/reducing it.

---

### [ADR-0014: Introduce Processor Factory Functions in Domain Layer](../adr/0014-introduce-processor-factory-functions-in-domain-layer.md)

**Status**: Accepted | **Date**: 2025-12-08

Introduce domain-level factory functions (create_processor_with_fallback, create_processor_from_profile_name) to centralize processor creation logic and ensure consistent fallback behavior across all entry points.

---

### [ADR-0015: Adopt Factory Pattern for Profile-to-Processor Conversion](../adr/0015-adopt-factory-pattern-for-profile-to-processor-conversion.md)

**Status**: Accepted | **Date**: 2025-12-08

Introduce ProcessorFactory protocol in domain layer and ConcreteProcessorFactory in infrastructure layer to decouple profile configuration from processor instantiation, following dependency inversion principle.

---

### [ADR-0016: Use Dynamic Module Loading for LLM Client Creation](../adr/0016-use-dynamic-module-loading-for-llm-client-creation.md)

**Status**: Accepted | **Date**: 2025-12-08

Use importlib for dynamic module loading in LLMClientFactory to enable graceful degradation when optional LLM dependencies are not installed, supporting zero-configuration usage of PassThroughProcessor.

---

### [ADR-0017: Use Custom Exception Hierarchy for Infrastructure Errors](../adr/0017-use-custom-exception-hierarchy-for-infrastructure-errors.md)

**Status**: Accepted | **Date**: 2025-12-16

All infrastructure layer errors must extend ShtymInfrastructureError to ensure consistent error handling, clear layer boundaries, and uniform exception patterns across the codebase.

---
