# Development Setup

This guide covers setting up a development environment for contributing to Pontos.

## Prerequisites

- Python 3.12+
- Git with LFS support
- Virtual environment tool (venv, conda, etc.)

---

## Clone Repository

```bash
# Clone with Git LFS
git clone https://github.com/teyk0o/pontos.git
cd pontos

# Pull model weights
git lfs pull
```

---

## Virtual Environment

=== "venv"

    ```bash
    # Create virtual environment
    python -m venv venv

    # Activate (Linux/macOS)
    source venv/bin/activate

    # Activate (Windows)
    venv\Scripts\activate
    ```

=== "conda"

    ```bash
    # Create conda environment
    conda create -n pontos python=3.12
    conda activate pontos
    ```

---

## Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Install package in editable mode
pip install -e .
```

### Development Dependencies

The `requirements.txt` includes development tools:

- `pytest`, `pytest-cov`, `pytest-mock` - Testing
- `black` - Code formatting
- `ruff` - Linting

---

## Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

Minimum required variables:

```bash title=".env"
SH_CLIENT_ID=your-client-id
SH_CLIENT_SECRET=your-client-secret
DEVICE=cpu
```

---

## Verify Installation

```bash
# Run tests
pytest

# Check CLI
pontos --help

# Check imports
python -c "from pontos import VesselDetector; print('OK')"
```

---

## Project Structure

```
pontos/
├── pontos/                 # Main package
│   ├── __init__.py        # Exports
│   ├── cli.py             # CLI commands
│   ├── config.py          # Configuration
│   ├── detector.py        # YOLO detection
│   ├── sentinel.py        # Sentinel Hub API
│   └── geo.py             # Geospatial utilities
│
├── tests/                  # Test suite
│   ├── conftest.py        # Fixtures
│   ├── test_*.py          # Test modules
│
├── examples/              # Usage examples
├── docker/                # Container config
├── models/                # Model weights (LFS)
├── data/samples/          # Sample data
└── docs/                  # Documentation
```

---

## Code Quality Tools

### Black (Formatting)

```bash
# Format code
black pontos tests

# Check formatting (no changes)
black --check pontos tests

# Show diff without changes
black --diff pontos tests
```

Configuration in `pyproject.toml` (if present) or defaults.

### Ruff (Linting)

```bash
# Check for issues
ruff check pontos tests

# Auto-fix issues
ruff check --fix pontos tests

# Show all rules
ruff rule --all
```

---

## IDE Setup

### VS Code

Recommended extensions:

- Python (`ms-python.python`)
- Pylance (`ms-python.vscode-pylance`)
- Black Formatter (`ms-python.black-formatter`)
- Ruff (`charliermarsh.ruff`)

Settings (`.vscode/settings.json`):

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter"
    },
    "ruff.lint.run": "onSave"
}
```

### PyCharm

1. Set interpreter to `venv/bin/python`
2. Enable Black: Settings > Tools > Black
3. Enable Ruff: Install Ruff plugin

---

## Git Workflow

### Branch Naming

Follow conventional branch naming:

```
type/scope/short-description
```

Examples:

- `feat/detector/add-tiled-detection`
- `fix/sentinel/handle-api-errors`
- `docs/readme/update-examples`
- `refactor/config/simplify-validation`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Examples:

```
feat(detector): add tiled detection support

Implements sliding window detection for large images
with configurable tile size and overlap.

Closes #123
```

```
fix(sentinel): handle API rate limit errors

- Add retry logic with exponential backoff
- Log warning on rate limit hit
```

---

## Pre-commit Hooks

Install pre-commit for automatic checks:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Example `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.2.0
    hooks:
      - id: ruff
        args: [--fix]

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest --cov=pontos -q
        language: system
        pass_filenames: false
        always_run: true
```

---

## Debugging

### VS Code Launch Configuration

```json title=".vscode/launch.json"
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        },
        {
            "name": "Python: CLI Scan",
            "type": "python",
            "request": "launch",
            "module": "pontos.cli",
            "args": ["scan", "--bbox", "5.85,43.08,6.05,43.18",
                     "--date-start", "2026-01-01",
                     "--date-end", "2026-01-31"],
            "console": "integratedTerminal"
        },
        {
            "name": "Python: Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["-v", "tests/"],
            "console": "integratedTerminal"
        }
    ]
}
```

### Debugging Tips

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use built-in breakpoint (Python 3.7+)
breakpoint()

# Check GPU memory
import torch
print(torch.cuda.memory_summary())
```

---

## Common Tasks

### Add New Dependency

```bash
# Add to requirements.txt
echo "new-package>=1.0.0" >> requirements.txt

# Install
pip install -r requirements.txt
```

### Run Specific Test

```bash
# Single test file
pytest tests/test_detector.py

# Single test function
pytest tests/test_detector.py::test_detect_basic

# Tests matching pattern
pytest -k "detector"
```

### Build Documentation

```bash
# Install mkdocs dependencies
pip install mkdocs-material mkdocstrings[python]

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

---

## Troubleshooting

??? question "Import errors after install"

    Ensure package is installed in editable mode:
    ```bash
    pip install -e .
    ```

??? question "Tests fail with model not found"

    Pull model weights:
    ```bash
    git lfs pull
    ```

??? question "Black and Ruff conflict"

    Run Black first, then Ruff:
    ```bash
    black pontos tests && ruff check --fix pontos tests
    ```

---

## Next Steps

- [Testing](testing.md) - Write and run tests
- [Contributing](contributing.md) - Contribution guidelines
