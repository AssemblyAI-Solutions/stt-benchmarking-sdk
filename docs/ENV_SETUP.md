# Environment Configuration Setup

## AssemblyAI API Key for LLM Vibe Eval

The SDK uses the AssemblyAI LLM Gateway for qualitative "vibe eval" assessments. Your API key is loaded securely from a `.env` file.

## Quick Setup

### 1. Get Your API Key

Sign up at https://www.assemblyai.com to obtain your API key.

### 2. Create .env File

The `.env` file should be in your **project root** (same directory as `README.md`), not inside the virtual environment:

```bash
# From project root (stt-benchmarking-sdk/)
cp .env.example .env
```

**Directory structure:**
```
stt-benchmarking-sdk/          # Project root
├── .env                        # Your API key (git ignored) ← HERE
├── .env.example                # Template (safe to commit)
├── venv/                       # Virtual environment (git ignored)
├── src/
├── examples/
└── README.md
```

### 3. Add Your API Key

Edit the `.env` file and replace `your_api_key_here` with your actual key:

```
ASSEMBLYAI_API_KEY=your_actual_api_key_here
```

**Important:** The `.env` file stays in the project root and works with any virtual environment.

### 4. Verify Setup

The SDK automatically loads your API key when you initialize the `LLMEvaluator`:

```python
from stt_benchmarking import LLMEvaluator

# API key is loaded from .env automatically
evaluator = LLMEvaluator()

# Or pass explicitly (not recommended)
evaluator = LLMEvaluator(api_key="your-key")
```

## Security Notes

- **Never commit `.env` to git** - The file is already in `.gitignore`
- **Keep `.env.example`** - Share this template file, not the actual `.env`
- **Rotate keys if exposed** - If you accidentally commit your key, regenerate it immediately

## Alternative: Environment Variables

If you prefer not to use `.env` files, you can set the environment variable directly:

**Linux/macOS:**
```bash
export ASSEMBLYAI_API_KEY='your-api-key-here'
python your_script.py
```

**Windows (PowerShell):**
```powershell
$env:ASSEMBLYAI_API_KEY='your-api-key-here'
python your_script.py
```

**Windows (CMD):**
```cmd
set ASSEMBLYAI_API_KEY=your-api-key-here
python your_script.py
```

## Troubleshooting

### Error: "AssemblyAI API key required"

**Cause:** No API key found in `.env` or environment variables

**Solution:**
1. Verify `.env` file exists in project root
2. Check file contains: `ASSEMBLYAI_API_KEY=your_key`
3. Ensure no spaces around the `=` sign
4. Try restarting your terminal/IDE

### Error: "401 Unauthorized"

**Cause:** Invalid or expired API key

**Solution:**
1. Verify your API key is correct
2. Check you copied the entire key (no spaces/truncation)
3. Regenerate key from AssemblyAI dashboard if needed

## Best Practices

1. **Use .env for development** - Easiest for local work
2. **Use environment variables for production** - Set in deployment platform
3. **Use different keys for dev/prod** - Helps track usage and isolate issues
4. **Add .env to .gitignore** - Already done in this project
5. **Document in README** - Include setup instructions for collaborators
