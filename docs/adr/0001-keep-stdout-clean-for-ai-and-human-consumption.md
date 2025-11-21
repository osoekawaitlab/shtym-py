# ADR 0001: Keep stdout Clean for AI and Human Consumption

## Status

Accepted (Amended 2025-11-21)

## Date

2025-11-20

## Context

The shtym tool is designed as a command-line filter that summarizes input using AI. Its primary purpose is to reduce context size for both human users and AI coding agents working in terminal environments. Users need to pipe command output through shtym and receive only the essential summary without any visual clutter or formatting.

In modern development workflows, AI coding agents are increasingly consuming command-line output programmatically. Additionally, humans often need to copy-paste terminal output or chain commands together. Any extra formatting, progress indicators, or decorative elements in stdout would interfere with these use cases and defeat the purpose of context reduction.

## Decision

Keep stdout exclusively for AI-generated summaries. All other output (progress indicators, error messages, logging, metadata) must go to stderr or other channels.

## Rationale

- **Context reduction goal**: Adding any extra formatting to stdout would contradict the core purpose of reducing context size
- **AI agent compatibility**: AI coding agents can cleanly consume stdout without parsing decorative elements
- **Unix philosophy**: Following the principle that stdout carries the primary data output while stderr carries metadata
- **Composability**: Users can reliably pipe shtym output to other commands or redirect it to files
- **Copy-paste friendliness**: Humans can directly use the stdout content without manual cleanup

## Implications

### Positive Implications

- Clean integration with Unix pipes and redirections
- AI coding agents can parse output without special handling
- Predictable behavior: stdout always contains exactly the summary
- No dependency on terminal capabilities or detection logic
- Users can easily capture only the summary: `command | shtym > summary.txt`

### Concerns

- Users won't see progress indicators in stdout (mitigation: use stderr for progress)
- Debugging information must go to stderr (mitigation: implement proper logging levels)
- May feel "bare" compared to modern CLI tools with rich formatting (mitigation: this is intentional for our use case)

## Alternatives

### Rich CLI with formatting controls

Using libraries like rich or colorama to provide formatted output with an option to disable it.

- **Pros**: Better visual experience for interactive use, can show progress elegantly
- **Cons**: Adds complexity, requires terminal detection, users must remember to use `--plain` flags, increases dependencies
- **Reason for rejection**: Goes against the core philosophy of simplicity and context reduction

### JSON output mode

Wrapping the summary in JSON with metadata fields.

- **Pros**: Machine-readable, can include metadata
- **Cons**: Increases output size, requires parsing, defeats context reduction purpose
- **Reason for rejection**: Contradicts the goal of minimal context; metadata can go to stderr if needed

### Mixed output with delimiters

Using special delimiters to separate summary from other information in stdout.

- **Pros**: Can include both summary and metadata in one stream
- **Cons**: Users must parse delimiters, still increases output size, fragile
- **Reason for rejection**: Adds unnecessary complexity and increases context size

## Future Direction

This decision is foundational and unlikely to change. However, we should:

- Implement proper stderr logging for progress and debug information
- Consider environment variables or config files for verbosity control (affecting stderr only)
- Document this design choice clearly for users and contributors
- Revisit if a compelling use case emerges that requires stdout metadata (trigger: multiple user requests for structured output)

## References

- [Unix Philosophy: "Write programs that do one thing and do it well"](https://en.wikipedia.org/wiki/Unix_philosophy)

## Amendment (2025-11-21)

### What Changed

The original ADR assumed pipe-based usage where users pipe command output into shtym:

- **Original assumption**: `pytest tests/ | stym`
- **Amended to**: `stym run pytest tests/` (wrapper pattern with subcommand)

The core principle of keeping stdout clean remains unchanged. Only the invocation pattern has changed from pipe-based to wrapper-based.

### Reason for Amendment

Exit code inheritance is a critical requirement for development workflows. When tests fail, build commands error, or linters find issues, the command must exit with a non-zero status to integrate properly with CI/CD pipelines and developer scripts.

Technical constraint:

- **Pipe pattern** (`command | stym`): The wrapper process cannot access the exit code of the piped command. The pipeline's exit code would always be shtym's exit code, losing the original command's status.
- **Wrapper pattern** (`stym run command args`): The wrapper can execute the command as a subprocess, capture its exit code, and propagate it via `sys.exit(child_exit_code)`.

Unix precedent: Standard Unix wrapper commands (sudo, timeout, time) all inherit their child process exit codes. This is the established pattern for command wrappers.

### Impact on Original ADR

**Unchanged:**

- Clean stdout principle: stdout still contains only the primary data (command output or AI summary)
- stderr for metadata: progress indicators and errors still go to stderr
- Composability: shtym output can still be piped to other commands (`stym run pytest | grep ERROR`)
- Unix philosophy: still doing one thing well with clean interfaces

**Changed:**

- Invocation pattern: wrapper style instead of pipe style
- Data flow: shtym executes the command rather than reading from stdin
- Exit code: properly inherited from child process

**Compatibility note:**
The wrapper pattern is more composable than originally described. Users can still pipe shtym's output:

```bash
stym run pytest tests/ | grep "FAILED"
stym run npm test | tee test-output.txt
```

The clean stdout principle enables these compositions while also preserving exit codes.
