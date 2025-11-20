# ADR 0002: Use argparse for CLI Implementation

## Status

Accepted

## Date

2025-11-20

## Context

Following ADR-0001's decision to keep stdout clean, shtym needs a CLI argument parsing library. Python offers several options including the standard library's argparse, and third-party libraries like click and typer that provide rich terminal UI features.

The tool's design philosophy emphasizes simplicity and minimal dependencies. Since shtym's primary function is piping input through AI summarization, the CLI surface area is intentionally small. Complex interactive features, auto-completion, or rich formatting would not align with the clean stdout principle established in ADR-0001.

## Decision

Use argparse from Python's standard library for CLI argument parsing.

## Rationale

- **Zero external dependencies**: argparse is part of Python's standard library, requiring no additional packages
- **Sufficient functionality**: Provides all necessary features (flags, options, help text, subcommands if needed)
- **No rich UI features**: Lack of built-in colors, prompts, and progress bars aligns with ADR-0001's philosophy
- **Simplicity**: Straightforward API without magic decorators or complex abstractions
- **Stability**: Part of the standard library with guaranteed long-term support
- **Predictability**: Well-documented behavior, no surprises from framework-specific conventions

## Implications

### Positive Implications

- No dependency management overhead
- Works out-of-the-box in any Python environment
- Lightweight CLI with minimal overhead
- Clear, explicit argument definitions without decorators
- Easy to test with standard mocking techniques
- Reduces package size and installation complexity

### Concerns

- Manual help text formatting (mitigation: acceptable trade-off for simplicity)
- No built-in shell completion (mitigation: can add via argcomplete if needed, but likely unnecessary for our simple CLI)
- More verbose than decorator-based frameworks (mitigation: explicit is better than implicit, aids readability)

## Alternatives

### Click

A popular third-party CLI framework with decorator-based API.

- **Pros**: Elegant decorator syntax, rich ecosystem, wide adoption
- **Cons**: External dependency, includes rich terminal features we don't need (colors, prompts, progress bars), adds framework magic
- **Reason for rejection**: Adds unnecessary dependency and features that contradict ADR-0001's clean output philosophy

### Typer

Modern CLI framework built on top of Click with type hints.

- **Pros**: Type-safe, modern Python syntax, automatic help generation from type hints
- **Cons**: External dependency, even heavier than Click (depends on Click + rich), includes rich terminal UI we don't want
- **Reason for rejection**: Same concerns as Click, plus additional dependency weight and unwanted UI features

### Python Fire

Automatically generates CLIs from Python objects.

- **Pros**: Zero boilerplate, automatic CLI generation
- **Cons**: External dependency, magic behavior, less explicit control, harder to understand CLI structure
- **Reason for rejection**: Too much magic, lack of explicit control contradicts our simplicity goal

## Future Direction

This decision is expected to remain stable. Potential triggers for revisiting:

- **Complex subcommand structure emerges**: If shtym grows to require many subcommands with nested options, a richer framework might become beneficial (unlikely given the tool's focused scope)
- **Shell completion becomes essential**: If users strongly request shell completion, we could add argcomplete as an optional dependency
- **Standard library evolution**: If argparse gains significant improvements or a better alternative enters the standard library

For now, argparse provides everything needed for shtym's straightforward CLI.

## References

- [ADR-0001: Keep stdout Clean for AI and Human Consumption](./0001-keep-stdout-clean-for-ai-and-human-consumption.md)
- [Python argparse documentation](https://docs.python.org/3/library/argparse.html)
- [PEP 389: argparse - New Command Line Parsing Module](https://peps.python.org/pep-0389/)
