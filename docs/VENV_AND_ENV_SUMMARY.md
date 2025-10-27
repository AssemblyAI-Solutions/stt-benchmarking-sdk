# Virtual Environment + .env Setup Summary

## Quick Answer: How .env Works with venv

✅ **They work perfectly together!**

- `.env` file: Stays in **project root** (same level as README.md)
- `venv/` folder: Also in **project root**, contains Python packages
- Both are git-ignored (already configured in `.gitignore`)
- One `.env` works with any virtual environment

## Directory Structure

```
stt-benchmarking-sdk/          # ← Your project root (run commands here)
├── .env                        # ← Your API keys (git ignored)
├── .env.example                # ← Template (safe to commit)
├── .gitignore                  # ← Already excludes venv/ and .env
├── venv/                       # ← Virtual environment (git ignored)
│   ├── bin/                    #    (or Scripts/ on Windows)
│   ├── lib/
│   └── ...
├── src/
│   └── stt_benchmarking/
│       └── llm_eval.py         # ← Loads .env from project root
├── examples/
├── README.md
└── run_benchmark_template.py
```

## Complete Setup Flow

### First Time Setup (5 minutes)

```bash
# 1. Navigate to project
cd stt-benchmarking-sdk

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
source venv/bin/activate
# Windows: venv\Scripts\activate

# 4. Install SDK
pip install -e .

# 5. Setup .env for LLM features (optional)
cp .env.example .env
nano .env  # Add: ASSEMBLYAI_API_KEY=your_actual_key

# 6. Test it works
python examples/basic_usage.py
```

### Daily Usage

```bash
# Navigate and activate venv
cd stt-benchmarking-sdk
source venv/bin/activate  # Windows: venv\Scripts\activate

# Work on your project
python run_benchmark.py
python examples/llm_vibe_eval_example.py

# Deactivate when done
deactivate
```

## How python-dotenv Works

When you run a Python script:

```python
# In llm_eval.py:
from dotenv import load_dotenv
load_dotenv()  # Looks for .env in current directory
```

**Execution flow:**
1. You run: `python examples/llm_vibe_eval_example.py`
2. Current directory: `/path/to/stt-benchmarking-sdk/` (project root)
3. `load_dotenv()` searches for `.env` starting from current directory
4. Finds: `/path/to/stt-benchmarking-sdk/.env` ✓
5. Loads environment variables into memory
6. Your API key is available via `os.environ.get('ASSEMBLYAI_API_KEY')`

**Why it works:**
- You run scripts from project root (where `.env` is)
- `load_dotenv()` searches **current directory**, not Python installation
- Virtual environment location doesn't matter

## What's in .gitignore

Already configured (no changes needed):

```gitignore
# Line 99-105
.env          # ← Your secrets (NEVER commit)
.venv
env/
venv/         # ← Virtual environment (NEVER commit)
ENV/
env.bak/
venv.bak/
```

## Platform Differences

### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows PowerShell
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### Windows Command Prompt
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Everything else is the same!** The `.env` file works identically on all platforms.

## Common Questions

### Q: Do I need to copy .env into venv/?
**A:** No! `.env` stays in project root. `load_dotenv()` finds it automatically.

### Q: What if I create venv with a different name?
**A:** Fine! You could use `python -m venv myenv` - `.env` still works the same way.

```
project/
├── .env        ← Here
├── myenv/      ← Different name, still works!
└── src/
```

### Q: Can I use the same .env with multiple venvs?
**A:** Yes! One `.env` file works with any virtual environment setup.

```
project/
├── .env            ← Shared by all
├── venv-dev/       ← Dev environment
├── venv-test/      ← Test environment
└── venv-prod/      ← Production environment
```

### Q: Does .env work without venv?
**A:** Yes! Virtual environment is optional. `.env` works either way:

```bash
# Without venv
pip install -e .
python script.py  # ✓ Loads .env

# With venv
python -m venv venv
source venv/bin/activate
pip install -e .
python script.py  # ✓ Also loads .env
```

### Q: Do I commit .env or venv/?
**A:** **NO!** Never commit either:
- ✗ `.env` - Contains secrets (API keys)
- ✗ `venv/` - Huge, platform-specific, regenerable
- ✓ `.env.example` - Safe template to commit
- ✓ `requirements.txt` - Commit this instead of venv/

### Q: How do collaborators get the API key?
**A:** They create their own `.env`:

```bash
# Collaborator clones repo
git clone your-repo
cd stt-benchmarking-sdk

# Setup their own .env
cp .env.example .env
nano .env  # Add their own API key

# Never commit .env!
git status  # Should NOT show .env (git ignored)
```

## Verification Checklist

✓ **Is venv active?**
```bash
# Check for (venv) in prompt:
(venv) user@computer:~/project$  # ✓ Active

# Or check Python location:
which python  # macOS/Linux
where python  # Windows
# Should be in venv/bin/ or venv\Scripts\
```

✓ **Is .env in the right place?**
```bash
ls .env  # Should exist in project root
# Not in venv/!
```

✓ **Is .env loaded?**
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Key:', os.environ.get('ASSEMBLYAI_API_KEY', 'NOT FOUND')[:10] + '...')"
# Should show first 10 chars of your key
```

✓ **Are venv and .env git-ignored?**
```bash
git status
# Should NOT see venv/ or .env
# (If repo is initialized)
```

## Troubleshooting

### "Module not found" errors
**Cause:** venv not activated or SDK not installed

**Fix:**
```bash
source venv/bin/activate
pip install -e .
```

### "API key required" error
**Cause:** `.env` not found or not in project root

**Fix:**
```bash
# Check you're in project root
pwd  # Should show: /path/to/stt-benchmarking-sdk

# Check .env exists
ls .env  # Should exist

# Check .env content
cat .env  # Should have: ASSEMBLYAI_API_KEY=...
```

### "python: command not found"
**Cause:** venv not activated

**Fix:**
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

## Best Practices Summary

✓ **Do:**
- Create venv in project root
- Keep .env in project root (same level as venv/)
- Activate venv before working
- Use `.env.example` as template
- Commit `.env.example` to git
- One venv per project

✗ **Don't:**
- Put .env inside venv/
- Commit .env to git (secrets!)
- Commit venv/ to git (huge, unnecessary)
- Share .env files (each person uses their own key)
- Hardcode API keys in code

## Resources

- **[VIRTUAL_ENV_GUIDE.md](VIRTUAL_ENV_GUIDE.md)** - Complete venv guide with troubleshooting
- **[ENV_SETUP.md](ENV_SETUP.md)** - .env setup and security best practices
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Step-by-step benchmarking setup
- **[README.md](README.md)** - Main installation and usage guide

## TL;DR

```bash
# Setup once
cd stt-benchmarking-sdk
python -m venv venv
source venv/bin/activate
pip install -e .
cp .env.example .env
nano .env  # Add your API key

# Use daily
cd stt-benchmarking-sdk
source venv/bin/activate
python your_script.py
deactivate
```

**Key points:**
- `.env` in project root ← API keys here
- `venv/` in project root ← Python packages here
- Both git-ignored automatically ✓
- Works on all platforms identically ✓
