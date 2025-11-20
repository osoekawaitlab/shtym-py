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
