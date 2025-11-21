# ADR 0004: Do Not Implement Stdin Pipe Mode

## Status

Accepted

## Date

2025-11-21

## Context

When designing shtym's invocation pattern, there are two common approaches for wrapping command-line tools:

1. **Pipe mode**: `command | shtym` - reads from stdin, writes to stdout
2. **Wrapper mode**: `shtym command args` - executes command as subprocess

The pipe mode (`command | shtym`) appears natural for Unix pipeline tools and aligns with the "filter" concept. However, this approach has a fundamental technical limitation that conflicts with critical development workflow requirements.

## Decision

Do NOT implement stdin pipe mode (`command | shtym`). Shtym will exclusively use wrapper mode (`shtym command args`).

## Rationale

**Technical constraint - Exit code inheritance:**

In development workflows, exit codes are critical for:

- CI/CD pipeline control (fail on test failures)
- Build automation (stop on compilation errors)
- Developer scripts (conditional execution based on success/failure)
- Shell scripting (`set -e` to fail on errors)

**Pipe mode limitation:**

```bash
pytest tests/ | stym
echo $?  # Always returns stym's exit code, not pytest's
```

When using pipes, the shell pipeline's exit code is determined by the last command (`stym`), not the piped command (`pytest`). There is no standard mechanism for `stym` to access `pytest`'s exit code in this scenario.

While `$PIPESTATUS` or `set -o pipefail` can provide workarounds, they:

- Require users to remember special shell features
- Don't work consistently across shells (bash vs zsh vs fish)
- Add cognitive overhead and documentation burden
- Break the principle of least surprise

**Wrapper mode advantage:**

```bash
stym run pytest tests/
echo $?  # Returns pytest's exit code
```

Wrapper mode executes the command as a subprocess, captures its exit code via `subprocess.run()`, and propagates it via `sys.exit(child_returncode)`. This works reliably and requires no special user knowledge.

**Unix precedent:**

Standard Unix wrapper commands use this pattern:

- `sudo command` - inherits exit code
- `timeout command` - inherits exit code
- `time command` - inherits exit code
- `nice command` - inherits exit code

**Composability is preserved:**

Users can still pipe shtym's output:

```bash
stym run pytest tests/ | grep "FAILED"
stym run npm test | tee output.txt
```

The wrapper pattern doesn't sacrifice composability; it enhances it by adding exit code reliability.

## Implications

### Positive Implications

- Exit codes work correctly without special shell configuration
- Matches Unix wrapper command conventions
- No documentation needed for `$PIPESTATUS` workarounds
- Works identically across all shells
- Integrates seamlessly with CI/CD systems
- Composable with pipes while preserving exit codes

### Concerns

- Deviates from traditional "filter" mental model (mitigation: wrapper is more accurate for our use case)
- Users familiar with `command | filter` pattern may expect pipe mode (mitigation: clear documentation and error messages)
- Cannot process pre-existing piped input like `cat file | stym` (mitigation: not a target use case; use `stym run cat file` instead)

## Alternatives

### Implement Pipe Mode Only

Use `command | stym` pattern exclusively.

- **Pros**: Familiar Unix filter pattern, simple mental model
- **Cons**: Cannot inherit exit codes, breaks CI/CD workflows, requires shell-specific workarounds
- **Reason for rejection**: Exit code inheritance is non-negotiable for development tool integration

### Implement Both Modes

Support both `command | stym` and `stym run command` with auto-detection.

- **Pros**: Maximum flexibility, supports both use cases
- **Cons**: Complex implementation, confusing UX (which mode is active?), pipe mode still can't solve exit code problem, doubles testing surface area
- **Reason for rejection**: Pipe mode provides no benefits over wrapper mode while adding complexity

### Use Special Flags for Exit Code

Implement pipe mode with `--exit-code=FILE` to write exit code separately.

- **Pros**: Solves exit code problem while keeping pipe mode
- **Cons**: Extremely awkward UX, requires temp files, fragile, no Unix precedent for this pattern
- **Reason for rejection**: Trading one problem for multiple worse problems

## Future Direction

This decision is expected to remain stable. Potential triggers for revisiting:

- **New shell features**: If future shells provide standard mechanisms for filters to access piped command exit codes (unlikely; would break 50 years of Unix convention)
- **User demand**: If significant user feedback requests pipe mode despite exit code limitations (would require clear documentation of the tradeoff)

For now, wrapper mode provides all benefits of pipe mode plus exit code inheritance, making it strictly superior for our use case.

## References

- [ADR-0001: Keep stdout Clean for AI and Human Consumption](./0001-keep-stdout-clean-for-ai-and-human-consumption.md) (Amended to use wrapper pattern)
- [ADR-0005: Inherit Child Process Exit Codes](./0005-inherit-child-process-exit-codes.md)
- [Unix Pipe Documentation](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html#tag_18_09)
