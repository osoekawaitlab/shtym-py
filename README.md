# shtym

AI-powered summary filter that distills any command's output.

## Overview

Shtym is a command wrapper designed to reduce context size for both human users and AI coding agents. It wraps command execution and currently passes output through unchanged (with future AI summarization planned).

## Installation

```bash
pip install shtym
```

## Usage

Wrap any command with `stym run`:

```bash
# Run tests
stym run pytest tests/

# Run linter
stym run ruff check .

# Build project
stym run npm run build

# Any command with options
stym run ls -la

# Pipe output to other commands
stym run pytest tests/ | grep FAILED
```

## Key Features

- **Exit code inheritance**: Shtym preserves the wrapped command's exit code, making it CI/CD friendly
- **Clean stdout**: Output contains only command results, no progress indicators or metadata
- **Transparent wrapper**: Works seamlessly with existing workflows and scripts

## Design Philosophy

Shtym follows Unix conventions for command wrappers (like `sudo`, `timeout`, `time`):

- Executes commands as subprocesses
- Inherits and propagates exit codes exactly
- Maintains clean stdout for composability
- Enables reliable integration with automated workflows

## Development

For development documentation, see:

- [Architecture Overview](https://osoekawaitlab.github.io/shtym-py/architecture/overview/)

## License

MIT
