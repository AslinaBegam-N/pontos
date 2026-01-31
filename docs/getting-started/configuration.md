# Configuration

Pontos can be configured through environment variables or programmatically via Python.

## Environment Variables

Create a `.env` file in the project root directory:

```bash title=".env"
# Sentinel Hub Credentials (Required)
SH_CLIENT_ID=your-client-id
SH_CLIENT_SECRET=your-client-secret

# Model Configuration
MODEL_PATH=models/yolo11s_tci.pt
DEVICE=0
CONFIDENCE_THRESHOLD=0.05

# Processing Parameters
PATCH_SIZE=320
PATCH_OVERLAP=0.5
MAX_WORKERS=4
BATCH_SIZE=8
```

---

## Configuration Reference

### Required Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SH_CLIENT_ID` | `str` | `None` | Sentinel Hub OAuth Client ID |
| `SH_CLIENT_SECRET` | `str` | `None` | Sentinel Hub OAuth Client Secret |

!!! warning "Required"
    These credentials are required to download satellite imagery. See [Installation](installation.md#sentinel-hub-configuration) for setup instructions.

### Model Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MODEL_PATH` | `str` | `models/yolo11s_tci.pt` | Path to YOLO model weights |
| `DEVICE` | `str` | `0` | Computation device (`cpu`, `0`, `1`, etc.) |
| `CONFIDENCE_THRESHOLD` | `float` | `0.05` | Minimum detection confidence (0.0-1.0) |

### Processing Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PATCH_SIZE` | `int` | `320` | Image patch size for tiled detection |
| `PATCH_OVERLAP` | `float` | `0.5` | Overlap ratio between patches (0.0-1.0) |
| `MAX_WORKERS` | `int` | `4` | Maximum parallel worker threads |
| `BATCH_SIZE` | `int` | `8` | Batch size for model inference |

---

## Programmatic Configuration

You can also configure Pontos directly in Python:

```python
from pontos import config

# Set Sentinel Hub credentials
config.sentinel_client_id = "your-client-id"
config.sentinel_client_secret = "your-client-secret"

# Set model configuration
config.model_path = "models/yolo11s_tci.pt"
config.device = "0"  # Use first GPU
config.confidence_threshold = 0.1

# Set processing parameters
config.patch_size = 320
config.patch_overlap = 0.5
config.max_workers = 4
config.batch_size = 8
```

### Configuration Validation

Validate configuration before running:

```python
from pontos import config

# Check if configuration is valid
config.validate()
# Raises ValueError if model file doesn't exist or credentials missing
```

---

## Device Configuration

### Automatic GPU Detection

Pontos automatically detects available GPUs:

```python
from pontos import VesselDetector

detector = VesselDetector()

# Check if GPU is available
print(f"GPU available: {detector.is_gpu_available}")

# Get device name
print(f"Device: {detector.get_device_name()}")
```

### Force CPU Mode

To force CPU inference (useful for debugging or systems without GPU):

=== "Environment Variable"

    ```bash
    export DEVICE=cpu
    pontos scan --bbox 5.85,43.08,6.05,43.18 --date-start 2026-01-01 --date-end 2026-01-31
    ```

=== "Python"

    ```python
    from pontos import VesselDetector

    detector = VesselDetector(device="cpu")
    ```

### Multi-GPU Selection

For systems with multiple GPUs:

=== "Environment Variable"

    ```bash
    # Use second GPU
    export DEVICE=1
    ```

=== "Python"

    ```python
    from pontos import VesselDetector

    # Use second GPU
    detector = VesselDetector(device="1")
    ```

---

## Confidence Threshold

The confidence threshold controls detection sensitivity:

| Value | Sensitivity | False Positives | Use Case |
|-------|-------------|-----------------|----------|
| `0.01` | Very High | Many | Exploratory analysis |
| `0.05` | High | Some | Default, general use |
| `0.10` | Medium | Few | Production scans |
| `0.50` | Low | Rare | High-precision requirements |

### Choosing a Threshold

```python
from pontos import VesselDetector

# High sensitivity (more detections, more false positives)
detector = VesselDetector(confidence_threshold=0.01)

# Balanced (default)
detector = VesselDetector(confidence_threshold=0.05)

# High precision (fewer detections, fewer false positives)
detector = VesselDetector(confidence_threshold=0.5)
```

---

## Cloud Coverage Filtering

Control the maximum cloud coverage for satellite imagery:

```python
from pontos import SentinelDataSource

sentinel = SentinelDataSource()

# Only accept very clear images
scene = sentinel.get_scene(
    bbox=(5.85, 43.08, 6.05, 43.18),
    time_range=("2026-01-01", "2026-01-31"),
    max_cloud_coverage=0.1  # 10% max clouds
)

# Accept more cloudy images (wider date range may help)
scene = sentinel.get_scene(
    bbox=(5.85, 43.08, 6.05, 43.18),
    time_range=("2025-06-01", "2026-01-31"),
    max_cloud_coverage=0.5  # 50% max clouds
)
```

---

## Configuration Priority

Configuration values are resolved in the following order (highest priority first):

1. **Programmatic** - Values set directly in Python code
2. **Environment Variables** - Values from `.env` file or shell environment
3. **Defaults** - Built-in default values

Example:

```python
from pontos import config

# This overrides environment variable
config.confidence_threshold = 0.1

# Even if .env contains CONFIDENCE_THRESHOLD=0.05
# the value 0.1 will be used
```

---

## Example Configurations

### Development

```bash title=".env.development"
SH_CLIENT_ID=dev-client-id
SH_CLIENT_SECRET=dev-client-secret
DEVICE=cpu
CONFIDENCE_THRESHOLD=0.01
MAX_WORKERS=2
BATCH_SIZE=4
```

### Production

```bash title=".env.production"
SH_CLIENT_ID=prod-client-id
SH_CLIENT_SECRET=prod-client-secret
DEVICE=0
CONFIDENCE_THRESHOLD=0.1
MAX_WORKERS=8
BATCH_SIZE=16
```

### CI/CD Testing

```bash title=".env.test"
SH_CLIENT_ID=test-ci-client-id
SH_CLIENT_SECRET=test-ci-client-secret
DEVICE=cpu
CONFIDENCE_THRESHOLD=0.05
```

---

## Next Steps

- [CLI Reference](../user-guide/cli.md) - Complete CLI documentation
- [Python API](../user-guide/python-api.md) - Detailed API usage
