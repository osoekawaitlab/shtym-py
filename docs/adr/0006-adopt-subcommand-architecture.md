# ADR 0006: Adopt Subcommand Architecture

## Status

Accepted

## Date

2025-11-21

## Context

Shtym's CLI was initially designed as a simple wrapper: `stym command args`. While this works for the basic pass-through functionality, future LLM integration will require additional commands for configuration and status checking.

With a simple wrapper design, commands like `stym status` would be ambiguous:

- Does it execute a command named "status"?
- Does it show shtym's LLM status?

This ambiguity becomes critical when planning for future features:

- `stym status` - Check LLM connection, API key validity, usage quota
- `stym config` - View or modify configuration (API keys, default model)
- `stym models` - List available LLM models

Without a clear subcommand structure, these would either:

1. Require awkward flag syntax (`stym --status`, `stym --config`)
2. Use reserved word lists (fragile, prevents wrapping commands with those names)
3. Be impossible to implement without breaking changes

This decision must be made **before the first release** because changing from `stym command` to `stym run command` later would be a breaking change for all users.

## Decision

Adopt a subcommand architecture using argparse subparsers:

```bash
stym run <command> [args...]     # Execute and filter command
stym status                      # (Future) Check LLM status
stym config [options]            # (Future) Manage configuration
stym models                      # (Future) List available models
```

## Rationale

**Extensibility for LLM integration:**

- Clear namespace for shtym operations vs wrapped commands
- No ambiguity: `stym status` always means shtym's status, never a command named "status"
- Natural place for future subcommands without breaking changes

**Industry standard pattern:**

- `git commit`, `docker run`, `kubectl get` - all use subcommands
- `gh pr create`, `cargo build` - modern CLIs follow this pattern
- Users familiar with these tools will immediately understand shtym's structure

**Prevents future breaking changes:**

- Adding `stym status` later would break users running `stym status` expecting command execution
- Changing from `stym pytest` to `stym run pytest` would break all existing scripts and documentation
- Must decide now, before first release and user adoption

**Explicit is better than implicit:**

- `stym run pytest` clearly indicates "run this command through shtym"
- No magic reserved words or special parsing rules
- Easier to explain and document

## Implications

### Positive Implications

- Future-proof: can add `status`, `config`, `models` without breaking changes
- Clear separation: shtym commands vs wrapped commands
- Industry-standard pattern: familiar to users
- Enables rich CLI features: help for each subcommand, subcommand-specific options
- Testable: each subcommand can be tested independently

### Concerns

- Slightly more typing: `stym run pytest` vs `stym pytest` (mitigation: users can create shell aliases if desired: `alias sr='stym run'`)
- Breaking change from current development version (mitigation: no released version yet, no users affected)

## Alternatives

### Simple Wrapper (No Subcommands)

Keep `stym command args` pattern, add shtym operations as flags.

- **Pros**: Shortest syntax for command execution
- **Cons**: Awkward operation syntax (`stym --status`), limited extensibility, confusing help output
- **Reason for rejection**: Cannot support rich LLM features without awkward UX

### Reserved Word List

Use `stym command` but treat certain words (status, config, etc.) as special.

- **Pros**: Short command execution syntax
- **Cons**: Cannot wrap commands named "status", "config", etc.; fragile (must maintain reserved list); confusing ("why doesn't `stym status` work?")
- **Reason for rejection**: Too many edge cases and user confusion

### Auto-Detection

Detect whether argument is a shtym subcommand or external command.

- **Pros**: "Smart" behavior
- **Cons**: Magic behavior, ambiguity (what if someone creates a command named "status"?), hard to predict
- **Reason for rejection**: Explicit is better than implicit; too much magic

## Future Direction

This subcommand structure is foundational and should remain stable. Expected future subcommands:

**Planned:**

- `stym status` - LLM connection and usage status
- `stym config` - Configuration management
- `stym models` - List and manage available models

**Possible:**

- `stym history` - Command execution history
- `stym explain` - Explain previous command output
- `stym debug` - Debug mode with verbose logging

**Triggers for revisiting:**

- If `stym run` becomes overwhelming majority of usage and other subcommands rarely used (could add `run` as default, but keep subcommand structure)
- If user feedback strongly prefers shorter syntax despite tradeoffs (could add shell completion to make `stym run` typing easier)

For now, explicit subcommand architecture provides the best balance of clarity, extensibility, and future-proofing.

## References

- [Issue #3: Implement basic pass-through mode](https://github.com/osoekawaitlab/shtym-py/issues/3)
- [ADR-0002: Use argparse for CLI Implementation](./0002-use-argparse-for-cli-implementation.md)
- [Git Subcommands](https://git-scm.com/docs/git#_git_commands)
