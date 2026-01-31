# pontos.config

Configuration management for Pontos.

## Overview

Pontos configuration can be set through:

1. Environment variables (`.env` file or shell)
2. Programmatic configuration via `config` object
3. Constructor parameters for individual classes

---

## PontosConfig

Dataclass for centralized configuration.

### Class Definition

```python
@dataclass
class PontosConfig:
    """
    Configuration dataclass for Pontos.

    Loads settings from environment variables with sensible defaults.
    Validates configuration before use.

    Attributes:
        model_path: Path to YOLO model weights
        sentinel_client_id: Sentinel Hub OAuth Client ID
        sentinel_client_secret: Sentinel Hub OAuth Client Secret
        confidence_threshold: Minimum detection confidence
        device: Computation device (CPU/GPU)
        patch_size: Image patch size for tiling
        patch_overlap: Overlap ratio for tiling
        max_workers: Maximum parallel workers
        batch_size: Inference batch size
    """
```

### Attributes

| Attribute | Type | Default | Environment Variable |
|-----------|------|---------|---------------------|
| `model_path` | `Path` | `models/yolo11s_tci.pt` | `MODEL_PATH` |
| `sentinel_client_id` | `str` | `None` | `SH_CLIENT_ID` |
| `sentinel_client_secret` | `str` | `None` | `SH_CLIENT_SECRET` |
| `confidence_threshold` | `float` | `0.05` | `CONFIDENCE_THRESHOLD` |
| `device` | `str` | `"0"` | `DEVICE` |
| `patch_size` | `int` | `320` | `PATCH_SIZE` |
| `patch_overlap` | `float` | `0.5` | `PATCH_OVERLAP` |
| `max_workers` | `int` | `4` | `MAX_WORKERS` |
| `batch_size` | `int` | `8` | `BATCH_SIZE` |

---

### Methods

#### validate()

Validate configuration settings.

```python
def validate(self) -> None
```

**Raises:**

- `ValueError` - If model file doesn't exist
- `ValueError` - If Sentinel Hub credentials are missing

**Example:**

```python
from pontos import config

try:
    config.validate()
    print("Configuration is valid")
except ValueError as e:
    print(f"Configuration error: {e}")
```

---

## Global Config Object

The `config` object is a pre-instantiated `PontosConfig` available for import:

```python
from pontos import config

# View settings
print(config.model_path)
print(config.device)
print(config.confidence_threshold)

# Modify settings
config.device = "cpu"
config.confidence_threshold = 0.1
```

---

## Configuration Methods

### Environment Variables

Create a `.env` file in the project root:

```bash title=".env"
# Required: Sentinel Hub credentials
SH_CLIENT_ID=your-client-id
SH_CLIENT_SECRET=your-client-secret

# Optional: Model configuration
MODEL_PATH=models/yolo11s_tci.pt
DEVICE=0
CONFIDENCE_THRESHOLD=0.05

# Optional: Processing parameters
PATCH_SIZE=320
PATCH_OVERLAP=0.5
MAX_WORKERS=4
BATCH_SIZE=8
```

### Shell Environment

```bash
export SH_CLIENT_ID="your-client-id"
export SH_CLIENT_SECRET="your-client-secret"
export DEVICE=cpu
```

### Programmatic Configuration

```python
from pontos import config

# Set credentials
config.sentinel_client_id = "your-client-id"
config.sentinel_client_secret = "your-client-secret"

# Set model options
config.model_path = "models/custom_model.pt"
config.device = "0"
config.confidence_threshold = 0.1

# Set processing options
config.patch_size = 512
config.batch_size = 16
```

---

## Configuration Reference

### Model Settings

#### model_path

Path to the YOLO model weights file.

```python
config.model_path = "models/yolo11s_tci.pt"
```

- **Type**: `Path` or `str`
- **Default**: `models/yolo11s_tci.pt`
- **Environment**: `MODEL_PATH`

#### device

Computation device for inference.

```python
config.device = "0"  # First GPU
config.device = "1"  # Second GPU
config.device = "cpu"  # CPU only
```

- **Type**: `str`
- **Default**: `"0"`
- **Environment**: `DEVICE`

#### confidence_threshold

Minimum confidence threshold for detections.

```python
config.confidence_threshold = 0.05  # Default
config.confidence_threshold = 0.01  # High sensitivity
config.confidence_threshold = 0.50  # High precision
```

- **Type**: `float`
- **Range**: `0.0` to `1.0`
- **Default**: `0.05`
- **Environment**: `CONFIDENCE_THRESHOLD`

---

### Sentinel Hub Settings

#### sentinel_client_id

Sentinel Hub OAuth Client ID.

```python
config.sentinel_client_id = "your-client-id"
```

- **Type**: `str`
- **Default**: `None`
- **Environment**: `SH_CLIENT_ID`
- **Required**: Yes (for satellite imagery download)

#### sentinel_client_secret

Sentinel Hub OAuth Client Secret.

```python
config.sentinel_client_secret = "your-client-secret"
```

- **Type**: `str`
- **Default**: `None`
- **Environment**: `SH_CLIENT_SECRET`
- **Required**: Yes (for satellite imagery download)

---

### Processing Settings

#### patch_size

Size of image patches for tiled detection.

```python
config.patch_size = 320  # Default
config.patch_size = 640  # Larger patches
```

- **Type**: `int`
- **Default**: `320`
- **Environment**: `PATCH_SIZE`

#### patch_overlap

Overlap ratio between patches.

```python
config.patch_overlap = 0.5  # 50% overlap
config.patch_overlap = 0.25  # 25% overlap
```

- **Type**: `float`
- **Range**: `0.0` to `1.0`
- **Default**: `0.5`
- **Environment**: `PATCH_OVERLAP`

#### max_workers

Maximum number of parallel worker threads.

```python
config.max_workers = 4  # Default
config.max_workers = 8  # More parallelism
```

- **Type**: `int`
- **Default**: `4`
- **Environment**: `MAX_WORKERS`

#### batch_size

Batch size for model inference.

```python
config.batch_size = 8  # Default
config.batch_size = 16  # Larger batches (requires more GPU memory)
```

- **Type**: `int`
- **Default**: `8`
- **Environment**: `BATCH_SIZE`

---

## Configuration Priority

Values are resolved in this order (highest priority first):

1. **Programmatic** - `config.attribute = value`
2. **Environment Variables** - `.env` file or shell
3. **Defaults** - Built-in default values

**Example:**

```python
from pontos import config

# Environment: CONFIDENCE_THRESHOLD=0.05

print(config.confidence_threshold)  # 0.05 (from env)

config.confidence_threshold = 0.1  # Override

print(config.confidence_threshold)  # 0.1 (programmatic)
```

---

## Usage Examples

### Validate Before Use

```python
from pontos import config

# Set configuration
config.sentinel_client_id = "your-id"
config.sentinel_client_secret = "your-secret"

# Validate
try:
    config.validate()
except ValueError as e:
    print(f"Invalid configuration: {e}")
    exit(1)

# Now safe to use
from pontos import SentinelDataSource
sentinel = SentinelDataSource()
```

### Environment-Specific Config

```python
import os
from pontos import config

env = os.getenv("ENV", "development")

if env == "production":
    config.device = "0"
    config.confidence_threshold = 0.1
    config.batch_size = 16
else:
    config.device = "cpu"
    config.confidence_threshold = 0.05
    config.batch_size = 4
```

### Custom Configuration

```python
from pontos import PontosConfig, VesselDetector

# Create custom config
custom_config = PontosConfig(
    model_path="models/custom_model.pt",
    sentinel_client_id="your-id",
    sentinel_client_secret="your-secret",
    confidence_threshold=0.1,
    device="0"
)

custom_config.validate()

# Use with detector
detector = VesselDetector(
    model_path=custom_config.model_path,
    device=custom_config.device,
    confidence_threshold=custom_config.confidence_threshold
)
```

---

## Device Auto-Detection

The configuration includes smart device selection:

```python
from pontos import config

# Default behavior:
# 1. Check if GPU 0 is available
# 2. If yes, use GPU 0
# 3. If no, fallback to CPU

print(f"Using device: {config.device}")
```

To check GPU availability programmatically:

```python
import torch

if torch.cuda.is_available():
    print(f"GPU available: {torch.cuda.get_device_name(0)}")
else:
    print("No GPU available, using CPU")
```
