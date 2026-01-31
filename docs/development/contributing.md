# Contributing

Thank you for your interest in contributing to Pontos. This guide covers the contribution process.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment ([Setup Guide](setup.md))
4. Create a feature branch
5. Make your changes
6. Submit a pull request

---

## Development Workflow

### 1. Fork and Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/pontos.git
cd pontos

# Add upstream remote
git remote add upstream https://github.com/teyk0o/pontos.git
```

### 2. Create Branch

Follow conventional branch naming:

```bash
git checkout -b feat/detector/add-tiled-detection
```

**Branch Types:**

| Type | Description |
|------|-------------|
| `feat/` | New feature |
| `fix/` | Bug fix |
| `docs/` | Documentation |
| `refactor/` | Code refactoring |
| `test/` | Test improvements |
| `ci/` | CI/CD changes |

### 3. Make Changes

- Write clean, documented code
- Follow existing code style
- Add tests for new functionality
- Update documentation as needed

### 4. Commit Changes

Use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat(detector): add tiled detection support"
```

**Commit Format:**

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Formatting |
| `refactor` | Refactoring |
| `test` | Tests |
| `ci` | CI/CD |
| `chore` | Maintenance |

### 5. Push and PR

```bash
# Push to your fork
git push origin feat/detector/add-tiled-detection

# Create PR on GitHub
```

---

## Code Standards

### Python Style

- **Formatter**: Black (default settings)
- **Linter**: Ruff
- **Python Version**: 3.12+

```bash
# Format code
black pontos tests

# Lint code
ruff check pontos tests
ruff check --fix pontos tests
```

### Code Guidelines

1. **Type hints** for all public functions
2. **Docstrings** for all public classes and functions
3. **No magic numbers** - use named constants
4. **Error handling** - use specific exceptions
5. **Logging** - use `logging` module, not `print()`

### Docstring Format

Use Google-style docstrings:

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

---

## Testing Requirements

### Coverage

- **Minimum**: 90% coverage for new code
- **Target**: Maintain 97% overall coverage

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=pontos --cov-report=html

# Specific tests
pytest tests/test_detector.py -v
```

### Test Guidelines

1. **Unit tests** for all new functions
2. **Integration tests** for component interactions
3. **Edge cases** - empty inputs, invalid data
4. **Mock external services** - don't call real APIs

---

## Pull Request Process

### PR Checklist

Before submitting:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New code has tests
- [ ] Documentation updated
- [ ] Conventional commit messages
- [ ] No merge conflicts

### PR Template

```markdown
## Description

Brief description of changes.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing

- [ ] Tests pass locally
- [ ] New tests added
- [ ] Coverage maintained

## Related Issues

Closes #123
```

### Review Process

1. Maintainer reviews code
2. CI checks must pass
3. Changes requested (if any)
4. Approval and merge

---

## Issue Reporting

### Bug Reports

Include:

1. **Description** - What happened?
2. **Expected** - What should happen?
3. **Steps to Reproduce** - How to trigger the bug
4. **Environment** - OS, Python version, GPU
5. **Logs/Screenshots** - Error messages, outputs

### Feature Requests

Include:

1. **Use Case** - Why is this needed?
2. **Proposed Solution** - How would it work?
3. **Alternatives** - Other approaches considered
4. **Implementation** - Willing to implement?

---

## Code Review Guidelines

### For Authors

1. Keep PRs focused and small
2. Respond to feedback promptly
3. Explain design decisions
4. Update based on feedback

### For Reviewers

1. Be constructive and respectful
2. Focus on code, not the person
3. Suggest improvements, not just criticisms
4. Approve when requirements met

---

## Release Process

Releases follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Release steps (maintainers only):

1. Update version in `setup.py`
2. Update CHANGELOG
3. Create release tag
4. Build and publish

---

## Community

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Report inappropriate behavior

### Getting Help

- GitHub Issues for bugs/features
- Discussions for questions
- Documentation for usage

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Recognition

Contributors are recognized in:

- GitHub contributors list
- Release notes
- CONTRIBUTORS file (if applicable)

Thank you for contributing to Pontos.
