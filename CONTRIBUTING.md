![pontos_banner.png](assets/pontos_banner.png)

Thank you for your interest in contributing to Pontos! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## Getting Started

### Prerequisites

- Python 3.12+
- Git with LFS support
- A Sentinel Hub account (for integration testing)

### Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/pontos.git
   cd pontos
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/teyk0o/pontos.git
   ```

4. **Pull model weights**
   ```bash
   git lfs pull
   ```

5. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or: venv\Scripts\activate  # Windows
   ```

6. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

7. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

8. **Verify setup**
   ```bash
   pytest
   pontos --help
   ```

## Development Workflow

### 1. Sync with upstream

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

### 2. Create a feature branch

Follow conventional branch naming:

```bash
git checkout -b <type>/<scope>/<description>
```

**Branch types:**
- `feat/` - New feature
- `fix/` - Bug fix
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Test improvements
- `ci/` - CI/CD changes

**Examples:**
```bash
git checkout -b feat/detector/add-tiled-detection
git checkout -b fix/sentinel/handle-timeout
git checkout -b docs/readme/update-examples
```

### 3. Make your changes

- Write clean, documented code
- Follow existing code style
- Add tests for new functionality
- Update documentation as needed

### 4. Test your changes

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=pontos

# Check formatting
black --check pontos tests

# Check linting
ruff check pontos tests
```

### 5. Commit your changes

See [Commit Guidelines](#commit-guidelines) below.

### 6. Push and create PR

```bash
git push origin <your-branch-name>
```

Then create a Pull Request on GitHub.

## Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code restructuring |
| `test` | Adding/updating tests |
| `ci` | CI/CD changes |
| `chore` | Maintenance tasks |

### Examples

```bash
# Feature
git commit -m "feat(detector): add batch processing support"

# Bug fix
git commit -m "fix(sentinel): handle API rate limiting"

# Documentation
git commit -m "docs(readme): add GPU setup instructions"

# With body
git commit -m "feat(geo): add support for multiple CRS

- Add pyproj transformation
- Support EPSG codes
- Add validation for bbox

Closes #42"
```

## Pull Request Process

### Before submitting

- [ ] Code follows style guidelines (Black, Ruff)
- [ ] All tests pass (`pytest`)
- [ ] New code has test coverage
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main

### PR title format

Use the same format as commits:
```
feat(detector): add tiled detection support
```

### PR description

Include:
- Summary of changes
- Motivation/context
- Testing performed
- Related issues

### Review process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, maintainers will merge

## Code Standards

### Python Style

- **Formatter**: Black (default settings)
- **Linter**: Ruff
- **Python**: 3.12+

```bash
# Format code
black pontos tests

# Lint code
ruff check pontos tests
ruff check --fix pontos tests
```

### Guidelines

1. **Type hints** for all public functions
2. **Docstrings** for all public classes and functions (Google style)
3. **No magic numbers** - use named constants
4. **Error handling** - use specific exceptions
5. **Logging** - use `logging` module, not `print()`

### Docstring format

```python
def detect(self, image_path: Path, confidence: float = 0.05) -> list[dict]:
    """
    Detect vessels in an image.

    Args:
        image_path: Path to the input image file.
        confidence: Minimum detection confidence threshold.

    Returns:
        List of detection dictionaries containing bbox, confidence,
        class, and center coordinates.

    Raises:
        FileNotFoundError: If image_path doesn't exist.
        ValueError: If confidence is not between 0 and 1.

    Example:
        >>> detector = VesselDetector()
        >>> detections = detector.detect("scene.png")
    """
```

## Testing

### Requirements

- Minimum 90% coverage for new code
- Maintain overall 97% coverage

### Running tests

```bash
# All tests
pytest

# With coverage
pytest --cov=pontos --cov-report=html

# Specific file
pytest tests/test_detector.py

# Specific test
pytest tests/test_detector.py::test_detect_basic

# Exclude slow tests
pytest -m "not slow"
```

### Writing tests

- Use pytest fixtures for common setup
- Mock external services (Sentinel Hub API)
- Test edge cases and error conditions
- Use meaningful test names

## Documentation

### Updating docs

Documentation is in `docs/` using MkDocs Material.

```bash
# Install docs dependencies
pip install -r docs/requirements.txt

# Serve locally
mkdocs serve

# Build
mkdocs build
```

### What to document

- New features (user guide + API reference)
- Configuration options
- CLI commands
- Breaking changes

## Questions?

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
- Use discussions for questions

Thank you for contributing!
