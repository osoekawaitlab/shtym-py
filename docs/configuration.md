# Configuration

Shtym uses environment variables for configuration.

## Environment Variables

### `SHTYM_LLM_SETTINGS__BASE_URL`

**Description**: Ollama server URL

**Default**: `http://localhost:11434`

**Example**:
```bash
export SHTYM_LLM_SETTINGS__BASE_URL=http://ollama.example.com:11434
```

---

### `SHTYM_LLM_SETTINGS__MODEL`

**Description**: Ollama model name to use for output summarization

**Default**: `gpt-oss:20b`

**Example**:
```bash
export SHTYM_LLM_SETTINGS__MODEL=llama2
```

**Notes**:
- Empty strings or whitespace-only values are treated as unset (falls back to default)
- If the specified model is not available in Ollama, shtym silently falls back to PassThrough mode
