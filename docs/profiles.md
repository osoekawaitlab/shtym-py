# Profiles

Profiles allow you to define custom output transformation behaviors for different use cases. Instead of relying solely on environment variables, you can create named profiles with specific LLM settings and prompt templates.

## What Are Profiles?

A profile is a named configuration that defines:

- **System prompt template**: Context and instructions for the LLM (recommended: keep concise)
- **User prompt template**: Template for command output and user message
- **LLM settings**: Model name and server URL to use
- **Processing behavior**: How command output should be transformed

Profiles enable you to:

- Use different LLM models for different tasks (e.g., fast model for summaries, powerful model for analysis)
- Apply task-specific prompts (e.g., "summarize", "translate", "extract errors")
- Switch between configurations without changing environment variables

## Profile Configuration File

Profiles are defined in a TOML file located at:

```bash
~/.config/shtym/profiles.toml
```

If this file doesn't exist, shtym uses the built-in default profile that reads from environment variables (see [Configuration](configuration.md)).

## Basic Profile Syntax

A profile definition has the following structure:

```toml
[profiles.<profile_name>]
type = "llm"
version = 1
system_prompt_template = "<system instructions>"
user_prompt_template = "<user message template>"

[profiles.<profile_name>.llm_settings]
model_name = "<model name>"
base_url = "<ollama server URL>"
```

### Fields

- **`type`**: Must be `"llm"` (currently the only supported type)
- **`version`**: Profile schema version (currently `1`, optional with default)
- **`system_prompt_template`**: Template for system prompt (sets LLM context)
    - Available variables: `$command`, `$stdout`, `$stderr`
    - **Best practice**: Keep concise; avoid `$stdout` for long outputs
    - Example: `"You are summarizing output from: $command"`
- **`user_prompt_template`**: Template for user message (contains command output)
    - Available variables: `$command`, `$stdout`, `$stderr`
    - Example: `"Output:\n$stdout\n\nErrors:\n$stderr"`
- **`model_name`**: Ollama model to use (e.g., `"gpt-oss:20b"`, `"llama2"`)
- **`base_url`**: Ollama server URL (e.g., `"http://localhost:11434"`)

## Creating Profiles

### Example: Summary Profile

Create a profile for summarizing command output:

```toml
[profiles.summary]
type = "llm"
system_prompt_template = "Summarize output from: $command"
user_prompt_template = "Provide a 2-3 sentence summary.\n\n$stdout"

[profiles.summary.llm_settings]
model_name = "gpt-oss:20b"
base_url = "http://localhost:11434"
```

Usage:

```bash
stym run --profile summary pytest tests/
```

### Example: Error Extraction Profile

Create a profile that extracts only errors:

```toml
[profiles.errors]
type = "llm"
system_prompt_template = "Extract errors from: $command"
user_prompt_template = "List only the errors.\n\nOutput:\n$stdout\n\nErrors:\n$stderr"

[profiles.errors.llm_settings]
model_name = "gpt-oss:120b"  # Use more powerful model for accuracy
base_url = "http://localhost:11434"
```

Usage:

```bash
stym run --profile errors npm run build
```

### Example: Translation Profile

Create a profile for translating output to another language:

```toml
[profiles.translate-ja]
type = "llm"
system_prompt_template = "Translate to Japanese: $command"
user_prompt_template = "$stdout"

[profiles.translate-ja.llm_settings]
model_name = "llama2"
base_url = "http://localhost:11434"
```

Usage:

```bash
stym run --profile translate-ja echo "Hello, world!"
```

## Multiple Profiles

You can define multiple profiles in the same file:

```toml
[profiles.summary]
type = "llm"
system_prompt_template = "Summarize: $command"
user_prompt_template = "$stdout"

[profiles.summary.llm_settings]
model_name = "gpt-oss:20b"
base_url = "http://localhost:11434"

[profiles.detailed]
type = "llm"
system_prompt_template = "Provide detailed analysis: $command"
user_prompt_template = "$stdout"

[profiles.detailed.llm_settings]
model_name = "gpt-oss:120b"
base_url = "http://localhost:11434"

[profiles.fast]
type = "llm"
system_prompt_template = "Quick summary: $command"
user_prompt_template = "$stdout"

[profiles.fast.llm_settings]
model_name = "gemma3:4b"
base_url = "http://localhost:11434"
```

Switch between profiles using `--profile`:

```bash
# Use fast profile for quick feedback
stym run --profile fast pytest tests/

# Use detailed profile for thorough analysis
stym run --profile detailed ruff check .
```

## Overriding the Default Profile

The default profile is used when `--profile` is not specified:

```bash
# Uses default profile
stym run pytest tests/
```

By default, this uses the built-in profile that reads from environment variables. You can override it by defining a `default` profile in `profiles.toml`:

```toml
[profiles.default]
type = "llm"
system_prompt_template = "Summarize concisely: $command"
user_prompt_template = "$stdout"

[profiles.default.llm_settings]
model_name = "gpt-oss:20b"
base_url = "http://localhost:11434"
```

After defining this, `stym run` without `--profile` will use your custom default settings instead of environment variables.

## Using Profiles

### Specify Profile Explicitly

```bash
# Use named profile
stym run --profile summary pytest tests/

# Use default profile (explicit)
stym run --profile default ruff check .
```

### Use Default Profile Implicitly

```bash
# Uses default profile (from profiles.toml or built-in)
stym run pytest tests/
```

### Profile Selection Priority

1. **`--profile` option**: If specified, uses the named profile from `profiles.toml`
2. **Default profile in `profiles.toml`**: If `[profiles.default]` exists, uses it when `--profile` is not specified
3. **Built-in default**: Uses environment variables (`SHTYM_LLM_SETTINGS__*`) as fallback

## Graceful Degradation

Following shtym's philosophy of graceful degradation:

- **Missing profile file**: Falls back to built-in default (environment variables)
- **Invalid TOML syntax**: Behaves as if no profiles are defined (silent fallback)
- **Profile not found**: Falls back to PassThrough mode (no error)
- **Model unavailable**: Falls back to PassThrough mode (outputs original command result)

This ensures shtym never fails due to configuration issues.

## Best Practices

### 1. Use Descriptive Profile Names

```toml
# Good: Clear purpose
[profiles.test-summary]
[profiles.error-extractor]
[profiles.translate-ja]

# Avoid: Unclear purpose
[profiles.profile1]
[profiles.temp]
```

### 2. Match Model Power to Task Complexity

```toml
# Simple summarization: Use faster model
[profiles.quick-summary]
type = "llm"
system_prompt_template = "One sentence summary: $command"
user_prompt_template = "$stdout"
[profiles.quick-summary.llm_settings]
model_name = "gemma3:4b"

# Complex analysis: Use powerful model
[profiles.deep-analysis]
type = "llm"
system_prompt_template = "Comprehensive analysis: $command"
user_prompt_template = "Provide recommendations.\n\n$stdout"
[profiles.deep-analysis.llm_settings]
model_name = "gpt-oss:120b"
```

### 3. Keep Prompts Focused

```toml
# Good: Specific instruction
system_prompt_template = "Extract error messages and line numbers: $command"
user_prompt_template = "$stdout"

# Avoid: Too vague
system_prompt_template = "Do something with this: $command"
user_prompt_template = "$stdout"
```

### 4. Test Profiles Before Committing

```bash
# Create test profile
echo '[profiles.test]
type = "llm"
system_prompt_template = "Test: $command"
user_prompt_template = "$stdout"
[profiles.test.llm_settings]
model_name = "gpt-oss:20b"
base_url = "http://localhost:11434"' >> ~/.config/shtym/profiles.toml

# Test it
stym run --profile test echo "Hello, world!"
```

## Troubleshooting

### Profile Not Working

**Symptom**: Profile seems ignored; output is not transformed

**Possible causes**:

1. TOML syntax error → Check file with TOML validator
2. Profile name mismatch → Verify `--profile` matches `[profiles.<name>]`
3. Ollama server not running → Start Ollama: `ollama serve`
4. Model not available → Pull model: `ollama pull <model_name>`

**Debug steps**:

```bash
# Verify TOML syntax
python3 - <<'PY'
import sys
from pathlib import Path
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
with open(Path.home() / ".config" / "shtym" / "profiles.toml", "rb") as f:
    tomllib.load(f)
print("OK")
PY

# Check Ollama server
curl http://localhost:11434/api/tags

# Test with built-in default
stym run echo "test"
```

### Profile File Location

**Linux/macOS**: `~/.config/shtym/profiles.toml`

**Example**:

```bash
# Create directory if it doesn't exist
mkdir -p ~/.config/shtym

# Edit profiles
nano ~/.config/shtym/profiles.toml
```

### Viewing Active Configuration

Currently shtym does not have a command to show active profiles. This may be added in a future version.

## Examples

### CI/CD Profile

For continuous integration environments where you want concise summaries:

```toml
[profiles.ci]
type = "llm"
system_prompt_template = "Summarize test results, highlight failures: $command"
user_prompt_template = "$stdout"

[profiles.ci.llm_settings]
model_name = "gpt-oss:20b"
base_url = "http://ci-ollama.internal:11434"
```

Usage in CI:

```bash
stym run --profile ci pytest --verbose tests/
```

### Development Profile

For local development with detailed feedback:

```toml
[profiles.dev]
type = "llm"
system_prompt_template = "Analyze and suggest improvements: $command"
user_prompt_template = "$stdout"

[profiles.dev.llm_settings]
model_name = "gpt-oss:120b"
base_url = "http://localhost:11434"
```

### Multilingual Support

Define profiles for different languages:

```toml
[profiles.ja]
type = "llm"
system_prompt_template = "以下の出力を日本語で要約してください: $command"
user_prompt_template = "$stdout"

[profiles.ja.llm_settings]
model_name = "gpt-oss:20b"
base_url = "http://localhost:11434"

[profiles.en]
type = "llm"
system_prompt_template = "Summarize the following output in English: $command"
user_prompt_template = "$stdout"

[profiles.en.llm_settings]
model_name = "gpt-oss:20b"
base_url = "http://localhost:11434"
```

## Future Enhancements

The profile system will continue to evolve. Planned features include:

- **Environment variable expansion**: Use `${VAR_NAME}` syntax in profiles for secrets and per-environment values
- **Project-local profiles**: Place profiles in `.shtym/profiles.toml` for team-shared configurations
- **Additional LLM providers**: OpenAI, Anthropic (Claude), Azure OpenAI Service support
- **Azure Key Vault integration**: Fetch secrets using `akv://vault-name/secret-name` URI scheme via envresolve

See the [Roadmap](roadmap.md) for details and priorities.

## See Also

- [Configuration](configuration.md) - Environment variable configuration
- [Roadmap](roadmap.md) - Planned features and enhancements
- [Development Guide](development.md) - Contributing to shtym
- [Architecture Overview](architecture/overview.md) - Design decisions behind profiles
