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

**Status**: Accepted | **Date**: 2025-12-02

Introduce LLMClient protocol in domain layer and OllamaLLMClient in infrastructure layer to decouple domain logic from specific LLM providers, enabling future support for OpenAI, Claude, and other providers.

---
