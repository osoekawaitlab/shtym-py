# shtym

AI-powered summary filter that distills any command's output.

## Overview

Shtym is a command wrapper designed to reduce context size for both human users and AI coding agents. It wraps command execution and, when an LLM is available, summarizes the output; otherwise it passes output through unchanged.

## Installation

```bash
pip install shtym

# with Ollama support (requires a running Ollama instance)
pip install "shtym[ollama]"
```

## Configuration

### Basic Configuration (Environment Variables)

Configure Ollama settings using environment variables:

- `SHTYM_LLM_SETTINGS__BASE_URL`: Ollama server URL (defaults to `http://localhost:11434`)
- `SHTYM_LLM_SETTINGS__MODEL`: Model to use (defaults to `gpt-oss:20b`)

Example:

```bash
export SHTYM_LLM_SETTINGS__BASE_URL=http://localhost:11434
export SHTYM_LLM_SETTINGS__MODEL=llama2
stym run pytest tests/
```

### Advanced Configuration (Profiles)

For more control, create profiles in `~/.config/shtym/profiles.toml` with custom prompts and LLM settings:

```toml
[profiles.summary]
type = "llm"
system_prompt_template = "You are summarizing: $command"
user_prompt_template = "Output:\n$stdout"

[profiles.summary.llm_settings]
model_name = "gpt-oss:20b"
base_url = "http://localhost:11434"
```

Use profiles with the `--profile` option:

```bash
stym run --profile summary pytest tests/
```

See the [Profiles documentation](https://osoekawaitlab.github.io/shtym-py/profiles/) for more details.

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
- **Optional LLM summaries**: If Ollama is available, output is summarized by the configured model; otherwise passthrough is used automatically

## Design Philosophy

Shtym follows Unix conventions for command wrappers (like `sudo`, `timeout`, `time`):

- Executes commands as subprocesses
- Inherits and propagates exit codes exactly
- Maintains clean stdout for composability
- Enables reliable integration with automated workflows

## Documentation

- [Profiles](https://osoekawaitlab.github.io/shtym-py/profiles/) - Advanced configuration with custom profiles
- [Roadmap](https://osoekawaitlab.github.io/shtym-py/roadmap/) - Planned features and enhancements

## Development

For development documentation, see:

- [Development Guide](https://osoekawaitlab.github.io/shtym-py/development/) - Setup, testing, and contribution guidelines
- [Architecture Overview](https://osoekawaitlab.github.io/shtym-py/architecture/overview/) - Design principles and ADRs

## License

MIT
