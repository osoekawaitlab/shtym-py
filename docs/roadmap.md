# Roadmap

This document outlines planned features and enhancements for shtym. Timing and scope may change based on feedback and contributions.

## Near Term (High Priority)

### Project-Local Profile Configuration

Support profile files in project directories (e.g., `.shtym/profiles.toml`), not just `~/.config/shtym/`.

**Why**: Enable team-shared configurations committed to version control, with automatic profile discovery per project.

**Example**:

```bash
my-project/
├── .shtym/profiles.toml  # Team profiles
└── src/

cd my-project
stym run --profile team-standard pytest  # Automatically uses project profiles
```

---

### Profile Inheritance

Allow profiles to extend other profiles to reduce duplication.

**Example**:

```toml
[profiles.base-summary]
system_prompt_template = "Summarize: $command"
user_prompt_template = "$stdout"

[profiles.fast-summary]
extends = "base-summary"
[profiles.fast-summary.llm_settings]
model_name = "gemma3:4b"
```

**Why**: Maintain related profiles more easily with shared configuration.

---

### Environment Variable Expansion in Profiles

Enable `${VAR_NAME}` syntax in profile configurations to separate secrets from configuration files.

**Why**: Keep API keys and credentials out of version control while sharing profile structure with teams.

**Example**:

```toml
[profiles.openai]
type = "llm"
[profiles.openai.llm_settings]
api_key = "${OPENAI_API_KEY}"
base_url = "${OPENAI_BASE_URL:-https://api.openai.com/v1}"
```

---

### Structured Output Support

Enable LLM responses in structured formats (JSON) with schema validation.

**Why**: Make LLM outputs machine-readable for downstream processing, CI/CD integration, and programmatic analysis.

**Example**:

```toml
[profiles.test-analysis]
type = "llm"
system_prompt_template = "Analyze test results: $command"
user_prompt_template = "$stdout"
output_format = "json"
output_schema = """
{
  "type": "object",
  "properties": {
    "total_tests": {"type": "integer"},
    "passed": {"type": "integer"},
    "failed": {"type": "integer"},
    "errors": {
      "type": "array",
      "items": {"type": "string"}
    }
  }
}
"""
```

**Use cases**:

- Parse test results for CI/CD metrics
- Extract structured lint findings
- Generate machine-readable summaries for automation

---

### Template Variable Support

Enable user-defined variables in prompt templates with default values, allowing dynamic customization at runtime.

**Why**: Reuse the same profile with different parameters without creating multiple profiles. Useful for automation tools like nox.

**Example**:

```toml
[profiles.custom-summary]
type = "llm"
system_prompt_template = "Summarize from ${perspective:-general} perspective: $command"
user_prompt_template = "$stdout"
```

Usage:

```bash
# Use default value (general)
stym run --profile custom-summary pytest tests/

# Override with specific perspective
stym run --profile custom-summary --var perspective=security pytest tests/
stym run --profile custom-summary --var perspective=performance ruff check .
```

---

### Long Context Handling

Support processing large command outputs that exceed LLM context limits through chunking and hierarchical summarization.

**Why**: Enable shtym to handle real-world scenarios with massive test suites, large diffs, or extensive logs without hitting token limits.

**Example strategies**:

- Chunk large outputs and process separately
- Hierarchical summarization (summarize chunks, then summarize summaries)
- Extract critical sections (errors, failures) before processing
- Stream processing for very large outputs

**Use cases**:

- Large test suites with thousands of tests
- Extensive log files
- Large git diffs across many files
- Build outputs from complex projects

---

## Medium Term

### OpenAI API Support

Add support for OpenAI's API as an LLM provider alongside Ollama.

**Why**: Provide flexibility to use different LLM providers based on availability, cost, or performance needs.

---

### Azure Key Vault Integration

Fetch secrets from Azure Key Vault using `akv://` URI scheme (via envresolve library).

**Why**: Enterprise-grade secret management with audit trails and automatic rotation support.

**Example**:

```toml
api_key = "akv://my-vault/openai-key"
# Or with variable expansion:
api_key = "akv://${VAULT_NAME}/openai-key"
```

---

## Long Term (Lower Priority)

### Command-Specific Prompt Presets

Provide built-in optimized prompts for common development commands (pytest, ruff, git, npm, etc.) with automatic detection.

**Why**: Make it easier to get started with effective prompts without manual prompt engineering.

**Example**:

```bash
stym run pytest tests/  # Automatically uses pytest-optimized prompt
```

---

### External Prompt Import

Enable importing prompt configurations from URLs, files, or repositories.

**Why**: Share and reuse proven prompt configurations across teams and projects.

**Example**:

```bash
stym profile import https://example.com/prompts/pytest-detailed.toml
```

---

### Additional LLM Providers

Extend support to Anthropic (Claude), Azure OpenAI Service, and other major LLM providers.

**Why**: Maximize flexibility and support diverse deployment scenarios.

---

### Configuration Management Commands

Add `stym config` subcommands for validation and inspection:

- `stym config validate` - Check profile syntax and configuration
- `stym config list` - Show all available profiles
- `stym config show <profile>` - Display profile details

**Why**: Improve debugging and discoverability of profiles.

---

## Contributing

Interested in implementing a feature? Please open a [GitHub Issue](https://github.com/osoekawaitlab/shtym-py/issues) to discuss the approach before starting work.

## Feedback

Have ideas for other features? Open an issue or start a [discussion](https://github.com/osoekawaitlab/shtym-py/discussions).
