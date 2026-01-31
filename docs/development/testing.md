# Testing

Pontos maintains 97% test coverage with comprehensive unit and integration tests.

## Running Tests

### All Tests

```bash
# Run all tests
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=pontos --cov-report=html
```

### Specific Tests

```bash
# Single file
pytest tests/test_detector.py

# Single test function
pytest tests/test_detector.py::test_detect_basic

# Pattern matching
pytest -k "detector"

# Exclude slow tests
pytest -m "not slow"
```

---

## Test Structure

```
tests/
├── conftest.py           # Fixtures and configuration
├── test_cli.py           # CLI command tests
├── test_config.py        # Configuration tests
├── test_detector.py      # YOLO detection tests
├── test_geo.py           # Geospatial tests
└── test_sentinel.py      # Sentinel Hub API tests
```

---

## Fixtures

Common fixtures defined in `conftest.py`:

### Environment Fixtures

```python
@pytest.fixture(scope="session", autouse=True)
def isolate_env():
    """Isolate test environment from real credentials."""
    ...

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set mock environment variables."""
    monkeypatch.setenv("SH_CLIENT_ID", "test-id")
    monkeypatch.setenv("SH_CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("DEVICE", "cpu")
```

### Data Fixtures

```python
@pytest.fixture
def sample_image(tmp_path):
    """Generate random test image."""
    img = Image.fromarray(np.random.randint(0, 255, (1024, 1024, 3), dtype=np.uint8))
    path = tmp_path / "test_image.png"
    img.save(path)
    return path

@pytest.fixture
def sample_detections():
    """Sample detection results."""
    return [
        {"bbox": [100, 100, 200, 200], "confidence": 0.87, "class": "vessel", "center": [150, 150]},
        {"bbox": [500, 300, 600, 400], "confidence": 0.65, "class": "vessel", "center": [550, 350]},
    ]

@pytest.fixture
def toulon_bbox():
    """Toulon naval base bounding box."""
    return (5.85, 43.08, 6.05, 43.18)
```

### Real Data Fixtures

```python
@pytest.fixture
def toulon_image():
    """Real Sentinel-2 test image."""
    return Path("data/samples/toulon_l1c.png")
```

---

## Test Categories

### Markers

```python
# Mark slow tests
@pytest.mark.slow
def test_full_pipeline():
    ...

# Mark integration tests
@pytest.mark.integration
def test_sentinel_api():
    ...
```

### Run by Category

```bash
# Only integration tests
pytest -m integration

# Only slow tests
pytest -m slow

# Exclude slow tests
pytest -m "not slow"

# Exclude integration tests
pytest -m "not integration"
```

---

## Coverage

### Generate Report

```bash
# Terminal report
pytest --cov=pontos

# HTML report
pytest --cov=pontos --cov-report=html

# XML report (for CI)
pytest --cov=pontos --cov-report=xml
```

### View HTML Report

```bash
# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Configuration

```ini title="pytest.ini"
[pytest]
testpaths = tests
addopts = --cov=pontos --cov-report=term-missing
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

---

## Writing Tests

### Basic Test

```python
def test_detector_initialization():
    """Test VesselDetector initializes correctly."""
    detector = VesselDetector(device="cpu")

    assert detector is not None
    assert detector.get_device_name() == "CPU"
```

### Test with Fixtures

```python
def test_detect_vessels(sample_image):
    """Test vessel detection on sample image."""
    detector = VesselDetector(device="cpu")
    detections = detector.detect(sample_image)

    assert isinstance(detections, list)
    for det in detections:
        assert "bbox" in det
        assert "confidence" in det
        assert "class" in det
        assert "center" in det
```

### Test with Mocks

```python
from unittest.mock import Mock, patch

def test_sentinel_download(mock_env_vars):
    """Test Sentinel Hub download with mocked API."""
    with patch("pontos.sentinel.SentinelHubRequest") as mock_request:
        mock_request.return_value.get_data.return_value = [np.zeros((1024, 1024, 3))]

        sentinel = SentinelDataSource()
        # ... test logic
```

### Parametrized Tests

```python
@pytest.mark.parametrize("confidence,expected_count", [
    (0.01, 10),
    (0.5, 5),
    (0.9, 1),
])
def test_confidence_filtering(sample_image, confidence, expected_count):
    """Test different confidence thresholds."""
    detector = VesselDetector(confidence_threshold=confidence)
    detections = detector.detect(sample_image)

    # Adjust assertion based on actual test logic
    assert len(detections) <= expected_count
```

---

## Test Examples

### CLI Tests

```python
from click.testing import CliRunner
from pontos.cli import cli

def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Pontos" in result.output

def test_cli_scan_missing_args():
    """Test scan command with missing arguments."""
    runner = CliRunner()
    result = runner.invoke(cli, ["scan"])

    assert result.exit_code != 0
    assert "Missing option" in result.output
```

### Config Tests

```python
def test_config_defaults():
    """Test default configuration values."""
    config = PontosConfig()

    assert config.confidence_threshold == 0.05
    assert config.device == "0"
    assert config.batch_size == 8

def test_config_validation_missing_model():
    """Test validation fails with missing model."""
    config = PontosConfig(model_path="nonexistent.pt")

    with pytest.raises(ValueError, match="Model file not found"):
        config.validate()
```

### GeoExporter Tests

```python
def test_pixel_to_geo_conversion(toulon_bbox):
    """Test pixel to geographic coordinate conversion."""
    # Center of image should map to center of bbox
    lon, lat = GeoExporter._pixel_to_geo(
        x_px=512, y_px=512,
        bbox=toulon_bbox,
        image_size=(1024, 1024)
    )

    expected_lon = (toulon_bbox[0] + toulon_bbox[2]) / 2
    expected_lat = (toulon_bbox[1] + toulon_bbox[3]) / 2

    assert abs(lon - expected_lon) < 0.001
    assert abs(lat - expected_lat) < 0.001

def test_geojson_export(sample_detections, toulon_bbox, tmp_path):
    """Test GeoJSON export."""
    output_path = tmp_path / "test.geojson"

    result = GeoExporter.detections_to_geojson(
        detections=sample_detections,
        bbox=toulon_bbox,
        image_size=(1024, 1024),
        output_path=output_path
    )

    assert result.exists()

    with open(result) as f:
        geojson = json.load(f)

    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == len(sample_detections)
```

---

## Mocking External Services

### Mock Sentinel Hub

```python
@pytest.fixture
def mock_sentinel(monkeypatch):
    """Mock Sentinel Hub API."""
    def mock_get_data(*args, **kwargs):
        return [np.random.randint(0, 255, (1024, 1024, 3), dtype=np.uint8)]

    monkeypatch.setattr(
        "pontos.sentinel.SentinelHubRequest.get_data",
        mock_get_data
    )
```

### Mock YOLO Model

```python
@pytest.fixture
def mock_yolo(monkeypatch):
    """Mock YOLO model."""
    class MockResults:
        def __init__(self):
            self.boxes = MockBoxes()

    class MockBoxes:
        @property
        def xyxy(self):
            return [[100, 100, 200, 200]]

        @property
        def conf(self):
            return [0.87]

        @property
        def cls(self):
            return [0]

    def mock_predict(*args, **kwargs):
        return [MockResults()]

    monkeypatch.setattr("ultralytics.YOLO.predict", mock_predict)
```

---

## CI Integration

Tests run automatically on GitHub Actions:

```yaml title=".github/workflows/tests.yml"
- name: Run Tests
  run: |
    pytest --cov=pontos --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

---

## Best Practices

1. **Isolate tests** - Each test should be independent
2. **Use fixtures** - Share common setup via fixtures
3. **Mock external services** - Don't call real APIs in tests
4. **Test edge cases** - Empty inputs, invalid data, etc.
5. **Maintain coverage** - Aim for 90%+ coverage
6. **Fast tests** - Keep unit tests fast, mark slow tests

---

## Troubleshooting

??? question "Tests fail with import errors"

    Install package in editable mode:
    ```bash
    pip install -e .
    ```

??? question "Coverage report missing lines"

    Ensure you're running with coverage:
    ```bash
    pytest --cov=pontos --cov-report=term-missing
    ```

??? question "Fixtures not found"

    Check `conftest.py` is in the `tests/` directory.

---

## Next Steps

- [Contributing](contributing.md) - Contribution guidelines
- [CI/CD](../deployment/ci-cd.md) - Automated testing pipeline
