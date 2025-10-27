# Virtual Environment Guide

## Why Use Virtual Environments?

Virtual environments (venv) create isolated Python environments for each project, preventing dependency conflicts:

**Without venv:**
```
System Python
├── Project A needs package X v1.0
├── Project B needs package X v2.0  ← CONFLICT!
└── STT SDK needs package X v1.5   ← CONFLICT!
```

**With venv:**
```
System Python
├── venv-project-a/  (has package X v1.0) ✓
├── venv-project-b/  (has package X v2.0) ✓
└── venv-stt-sdk/    (has package X v1.5) ✓
```

## Quick Start with Virtual Environment

### First Time Setup

```bash
# 1. Navigate to project
cd stt-benchmarking-sdk

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# 4. Install SDK
pip install -e .

# 5. Verify installation
python -c "from stt_benchmarking import STTBenchmark; print('✓ Installed')"
```

### Daily Usage

Each time you work on the project:

```bash
# 1. Navigate to project
cd stt-benchmarking-sdk

# 2. Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# 3. Work on your project
python examples/basic_usage.py
python run_benchmark.py

# 4. Deactivate when done
deactivate
```

## Platform-Specific Instructions

### Linux / macOS

```bash
# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate

# Deactivate
deactivate
```

**Your prompt will change:**
```bash
(venv) user@computer:~/stt-benchmarking-sdk$
```

### Windows (PowerShell)

```powershell
# Create venv
python -m venv venv

# Activate
venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Deactivate
deactivate
```

### Windows (Command Prompt)

```cmd
# Create venv
python -m venv venv

# Activate
venv\Scripts\activate.bat

# Deactivate
deactivate
```

## How .env Works with Virtual Environments

The `.env` file and virtual environment work together perfectly:

**Directory structure:**
```
stt-benchmarking-sdk/
├── .env              ← API keys (project level, git ignored)
├── .env.example      ← Template (safe to commit)
├── venv/             ← Virtual environment (git ignored)
│   ├── bin/
│   ├── lib/
│   └── ...
├── src/
│   └── stt_benchmarking/
│       └── llm_eval.py  ← Loads .env from project root
├── examples/
└── README.md
```

**How it works:**
1. `.env` is in project root (same level as `venv/`)
2. When you run scripts from project root, `load_dotenv()` finds `.env`
3. Virtual environment doesn't affect `.env` location
4. One `.env` file works with any virtual environment

**Example:**
```bash
# Activate venv
source venv/bin/activate

# Run from project root (where .env is)
python examples/llm_vibe_eval_example.py
# ✓ Loads .env from current directory
```

## Common Tasks

### Install New Packages

```bash
# Activate venv first
source venv/bin/activate

# Install package
pip install some-new-package

# Update requirements.txt if needed
pip freeze > requirements.txt
```

### Update Dependencies

```bash
source venv/bin/activate
pip install --upgrade -e .
```

### Delete and Recreate Virtual Environment

```bash
# Deactivate if active
deactivate

# Remove old venv
rm -rf venv  # Linux/macOS
# OR
rmdir /s venv  # Windows

# Create new venv
python -m venv venv

# Activate and reinstall
source venv/bin/activate  # Linux/macOS
pip install -e .
```

## Verification Checklist

### ✓ Is venv active?

**Check your prompt:**
```bash
(venv) user@computer:~/project$  # ✓ Active (note the (venv) prefix)
user@computer:~/project$         # ✗ Not active
```

**Check Python location:**
```bash
which python  # Linux/macOS
# Should show: /path/to/project/venv/bin/python

where python  # Windows
# Should show: C:\path\to\project\venv\Scripts\python.exe
```

### ✓ Is SDK installed?

```bash
python -c "import stt_benchmarking; print('✓ Installed')"
```

### ✓ Is .env loaded?

```bash
python -c "from stt_benchmarking import LLMEvaluator; print('✓ Can initialize')"
```

## Troubleshooting

### Issue: "Command not found: activate"

**Cause:** Venv not created or wrong path

**Solution:**
```bash
# Make sure venv exists
ls venv/  # Should see bin/, lib/, etc.

# If not, create it
python -m venv venv
```

### Issue: "No module named 'stt_benchmarking'"

**Cause:** Venv not active or SDK not installed

**Solution:**
```bash
# 1. Check if venv is active (look for (venv) in prompt)
# 2. If not, activate it
source venv/bin/activate

# 3. Install SDK
pip install -e .
```

### Issue: "AssemblyAI API key required" even with .env

**Cause:** Running from wrong directory

**Solution:**
```bash
# Make sure you're in project root (where .env is)
pwd  # Should show: /path/to/stt-benchmarking-sdk

# If not, navigate there
cd /path/to/stt-benchmarking-sdk

# Then run your script
python examples/llm_vibe_eval_example.py
```

### Issue: Permissions error on Windows

**Cause:** PowerShell execution policy

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

## Best Practices

### ✓ Do:
- Create one venv per project
- Name it `venv` (already in .gitignore)
- Activate venv before running scripts
- Keep `.env` in project root
- Commit `.env.example`, not `.env`
- Include venv in `.gitignore` (already done)

### ✗ Don't:
- Commit `venv/` to git (huge and unnecessary)
- Put `.env` inside `venv/` (won't work)
- Share the same venv across projects
- Forget to activate venv (pip installs to system)
- Commit `.env` with real API keys

## IDE Integration

### VS Code

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python"
}
```

VS Code will automatically:
- Use the venv for Python extension
- Activate venv in integrated terminal
- Show venv status in status bar

### PyCharm

1. **File → Settings → Project → Python Interpreter**
2. Click gear icon → **Add**
3. Select **Existing environment**
4. Browse to `venv/bin/python` (or `venv\Scripts\python.exe` on Windows)

PyCharm will automatically activate venv in its terminal.

## Alternative: virtualenvwrapper

For managing multiple projects (optional):

```bash
# Install
pip install virtualenvwrapper

# Create venv
mkvirtualenv stt-benchmark

# Switch to it
workon stt-benchmark

# List all venvs
workon

# Delete venv
rmvirtualenv stt-benchmark
```

## Summary

**Complete workflow:**
```bash
# First time setup
cd stt-benchmarking-sdk
python -m venv venv
source venv/bin/activate
pip install -e .
cp .env.example .env
nano .env  # Add your API key

# Daily usage
cd stt-benchmarking-sdk
source venv/bin/activate
python run_benchmark.py
deactivate  # when done
```

**Remember:**
- ✓ One venv per project
- ✓ `.env` in project root
- ✓ Activate before working
- ✓ Deactivate when done
- ✓ Never commit `venv/` or `.env`
