# CI/CD Pipeline

Pontos uses GitHub Actions for continuous integration and deployment.

## Overview

The CI/CD pipeline automatically:

1. Runs tests on every push and PR
2. Checks code formatting (Black)
3. Lints code (Ruff)
4. Uploads coverage to Codecov
5. Verifies model weights (Git LFS)

---

## Pipeline Configuration

### Workflow File

```yaml title=".github/workflows/tests.yml"
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -e .

      - name: Verify model file
        run: |
          ls -la models/
          file models/yolo11s_tci.pt

      - name: Run tests
        env:
          SH_CLIENT_ID: test-ci-client-id
          SH_CLIENT_SECRET: test-ci-client-secret
          DEVICE: cpu
        run: |
          pytest --cov=pontos --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install linters
        run: |
          pip install black ruff

      - name: Check Black formatting
        run: black --check pontos tests

      - name: Run Ruff
        run: ruff check pontos tests
```

---

## Jobs

### Test Job

Runs the test suite with coverage:

| Step | Description |
|------|-------------|
| Checkout | Clone repo with LFS |
| Setup Python | Install Python 3.12 |
| Install deps | Install requirements |
| Verify model | Check LFS download |
| Run tests | Execute pytest with coverage |
| Upload coverage | Send report to Codecov |

### Lint Job

Checks code quality:

| Step | Description |
|------|-------------|
| Checkout | Clone repo |
| Setup Python | Install Python 3.12 |
| Install linters | Install Black and Ruff |
| Check Black | Verify formatting |
| Run Ruff | Check for lint errors |

---

## Git LFS Integration

Model weights are stored with Git LFS. The workflow ensures proper download:

```yaml
- uses: actions/checkout@v4
  with:
    lfs: true  # Enable LFS
```

Verification step:

```yaml
- name: Verify model file
  run: |
    ls -la models/
    file models/yolo11s_tci.pt
    # Should show "data" not "text" (pointer file)
```

---

## Environment Variables

Test environment configuration:

```yaml
env:
  SH_CLIENT_ID: test-ci-client-id
  SH_CLIENT_SECRET: test-ci-client-secret
  DEVICE: cpu
```

!!! note
    These are mock credentials. Tests mock external API calls.

---

## Coverage Reporting

### Codecov Integration

Coverage reports are uploaded to Codecov:

```yaml
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

### Coverage Badge

Add to README:

```markdown
[![codecov](https://codecov.io/gh/teyk0o/pontos/branch/main/graph/badge.svg)](https://codecov.io/gh/teyk0o/pontos)
```

---

## Branch Protection

Recommended branch protection rules for `main`:

1. **Require status checks**
   - `test` job must pass
   - `lint` job must pass

2. **Require PR reviews**
   - At least 1 approval

3. **Require up-to-date branches**
   - Branch must be current with main

---

## Local CI Simulation

Run CI checks locally before pushing:

```bash
# Install dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
pytest --cov=pontos --cov-report=xml

# Check formatting
black --check pontos tests

# Run linter
ruff check pontos tests
```

### Using act (GitHub Actions locally)

```bash
# Install act
brew install act  # macOS
# or download from https://github.com/nektos/act

# Run workflow
act push

# Run specific job
act -j test
```

---

## Adding New Workflows

### Docker Build Workflow

```yaml title=".github/workflows/docker.yml"
name: Docker

on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: docker/Dockerfile
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.ref_name }}
```

### Release Workflow

```yaml title=".github/workflows/release.yml"
name: Release

on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
```

---

## Secrets Management

### Required Secrets

For production workflows:

| Secret | Description |
|--------|-------------|
| `CODECOV_TOKEN` | Codecov upload token |
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub password |

### Adding Secrets

1. Go to repository Settings
2. Select Secrets and variables > Actions
3. Click "New repository secret"
4. Enter name and value

---

## Workflow Status Badges

Add to README:

```markdown
![Tests](https://github.com/teyk0o/pontos/actions/workflows/tests.yml/badge.svg)
![codecov](https://codecov.io/gh/teyk0o/pontos/branch/main/graph/badge.svg)
```

---

## Debugging Workflows

### View Logs

1. Go to Actions tab
2. Click on workflow run
3. Select job to view logs

### Enable Debug Logging

Set secret `ACTIONS_RUNNER_DEBUG` to `true`.

### Re-run Failed Jobs

Click "Re-run jobs" in the Actions tab.

---

## Best Practices

1. **Fast feedback** - Keep workflows under 10 minutes
2. **Fail fast** - Run quick checks first
3. **Cache dependencies** - Speed up builds
4. **Use matrix builds** - Test multiple versions
5. **Protect main branch** - Require passing CI
6. **Monitor coverage** - Track coverage trends

---

## Caching

Speed up workflows with caching:

```yaml
- name: Cache pip
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

---

## Matrix Builds

Test multiple Python versions:

```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12", "3.13"]

steps:
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python-version }}
```

---

## Next Steps

- [Docker](docker.md) - Container deployment
- [Testing](../development/testing.md) - Local testing
- [Contributing](../development/contributing.md) - Contribution workflow
