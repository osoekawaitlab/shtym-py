# ADR 0005: Inherit Child Process Exit Codes

## Status

Accepted

## Date

2025-11-21

## Context

Shtym wraps command execution to filter or summarize output. As a command wrapper, it must decide how to handle the exit code (return code) of the child process it executes.

Exit codes are fundamental to Unix command composition and automation:

- Exit code 0 indicates success
- Non-zero exit codes indicate failure (1-255)
- Scripts and CI/CD systems rely on exit codes for flow control

When shtym executes `stym pytest tests/`, there are several options for what exit code shtym itself should return.

## Decision

Shtym MUST inherit and propagate the child process exit code exactly as-is. If the child process exits with code N, shtym exits with code N.

Implementation:

```python
result = subprocess.run(command, ...)
sys.exit(result.returncode)  # Inherit exactly
```

## Rationale

**Critical for development workflows:**

Development commands have meaningful exit codes:

- `pytest tests/` → 0 if all tests pass, 1 if any test fails
- `mypy src/` → 0 if types are correct, 1 if type errors exist
- `npm test` → 0 if tests pass, non-zero if tests fail
- `make build` → 0 if build succeeds, non-zero if build fails

If shtym returned its own exit code (e.g., always 0), it would break:

- CI/CD pipelines that fail builds on test failures
- Pre-commit hooks that block commits on linter errors
- Makefiles with conditional targets
- Shell scripts using `set -e` to fail fast
- Developer muscle memory (`command && next-step`)

**Unix wrapper command convention:**

Standard Unix wrapper commands inherit child exit codes:

```bash
$ sudo false; echo $?
1  # Inherits false's exit code

$ timeout 5 false; echo $?
1  # Inherits false's exit code

$ time false; echo $?
1  # Inherits false's exit code

$ nice false; echo $?
1  # Inherits false's exit code
```

This is established Unix convention for wrapper commands. Users expect wrappers to be transparent with respect to exit codes.

**Principle of least surprise:**

Developers expect:

```bash
stym pytest tests/ && echo "Tests passed"
```

To behave identically to:

```bash
pytest tests/ && echo "Tests passed"
```

If shtym returned a different exit code, it would violate the principle of least surprise and be unusable in automated workflows.

**No loss of information:**

Shtym has no reason to override the child's exit code:

- Shtym's own errors (invalid arguments, etc.) prevent child execution, so there's no conflict
- Child execution errors are reflected in the child's exit code
- Shtym's purpose (filtering output) doesn't change the success/failure of the underlying command

## Implications

### Positive Implications

- Works seamlessly in CI/CD pipelines
- Integrates with shell scripting patterns (`&&`, `||`, `set -e`)
- Matches Unix wrapper command conventions
- Preserves all semantic information from child process
- No special documentation needed (behavior is intuitive)
- Enables `stym` to be used as a drop-in wrapper:

  ```bash
  alias pytest='stym pytest'  # Transparent wrapper
  ```

### Concerns

- If shtym itself encounters an error while the child succeeds, it cannot signal its own error via exit code (mitigation: errors that prevent output filtering prevent child execution, so no conflict exists; errors during filtering can be logged to stderr without affecting exit code)
- Edge case: if child exits with code 127 (command not found) vs shtym exits with 127, these are indistinguishable (mitigation: acceptable, as both indicate the same problem from the user's perspective)

## Alternatives

### Return Shtym's Own Exit Code

Shtym returns 0 on successful execution (child ran successfully), regardless of child exit code.

- **Pros**: Distinguishes "shtym worked" from "child worked"
- **Cons**: Breaks all CI/CD integration, violates Unix conventions, unusable in automated workflows
- **Reason for rejection**: Makes shtym unsuitable for its primary use case (development command wrapping)

### Return Combined Exit Code

Use bitwise OR or custom encoding to combine shtym's status and child's exit code.

- **Pros**: Theoretically provides both pieces of information
- **Cons**: No Unix precedent, requires custom parsing, breaks standard exit code semantics (0 = success), confusing UX
- **Reason for rejection**: Violates Unix exit code conventions; no tool expects this pattern

### Exit Code Passthrough Flag

Default to inheriting child exit code, but provide `--own-exit-code` flag to return shtym's status instead.

- **Pros**: Flexibility for edge cases
- **Cons**: Complicates UX, almost never useful, adds testing burden, invites misuse
- **Reason for rejection**: No identified use case for the flag; YAGNI (You Aren't Gonna Need It)

## Future Direction

This decision is foundational and unlikely to change. Potential triggers for revisiting:

- **Shtym processing errors**: If shtym frequently encounters errors during output processing (e.g., LLM API failures) that need to be signaled separately from child failures (mitigation: log to stderr, use non-zero exit code only if child execution is prevented)
- **Request for signal differentiation**: If users need to distinguish "child failed" from "shtym processing failed" programmatically (mitigation: stderr logging, exit codes in different ranges, or status files if truly needed)

For now, exact exit code inheritance provides the right semantics for a command wrapper and aligns with 50 years of Unix convention.

## References

- [ADR-0004: Do Not Implement Stdin Pipe Mode](./0004-do-not-implement-stdin-pipe-mode.md)
- [Exit Status (POSIX)](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html#tag_18_08)
- [Advanced Bash-Scripting Guide: Exit Codes With Special Meanings](https://tldp.org/LDP/abs/html/exitcodes.html)
