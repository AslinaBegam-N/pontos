# pontos.detector

YOLO11s-based vessel detection module.

## VesselDetector

Main class for detecting vessels in satellite imagery using YOLO11s.

### Class Definition

```python
class VesselDetector:
    """
    YOLO11s-based vessel detector for satellite imagery.

    Attributes:
        model: Loaded YOLO model
        device: Computation device (CPU or GPU)
        confidence_threshold: Minimum detection confidence

    Example:
        >>> detector = VesselDetector()
        >>> detections = detector.detect("scene.png")
        >>> print(f"Found {len(detections)} vessels")
    """
```

### Constructor

```python
def __init__(
    self,
    model_path: str | Path | None = None,
    device: str | None = None,
    confidence_threshold: float = 0.05
) -> None
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_path` | `str` or `Path` | From config | Path to YOLO model weights file |
| `device` | `str` | From config | Device for inference (`"cpu"`, `"0"`, `"1"`, etc.) |
| `confidence_threshold` | `float` | `0.05` | Minimum confidence for detections |

**Example:**

```python
from pontos import VesselDetector

# Default configuration
detector = VesselDetector()

# Custom configuration
detector = VesselDetector(
    model_path="models/custom_model.pt",
    device="0",
    confidence_threshold=0.1
)

# Force CPU mode
detector = VesselDetector(device="cpu")
```

---

### Methods

#### detect()

Detect vessels in an image.

```python
def detect(
    self,
    image_path: str | Path,
    save_visualization: bool = False,
    output_dir: Path | None = None
) -> list[dict]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image_path` | `str` or `Path` | — | Path to the image file |
| `save_visualization` | `bool` | `False` | Save annotated image with bounding boxes |
| `output_dir` | `Path` | `None` | Directory for visualization output |

**Returns:**

`list[dict]` - List of detection dictionaries, each containing:

| Key | Type | Description |
|-----|------|-------------|
| `bbox` | `list[float]` | Bounding box as `[x1, y1, x2, y2]` in pixels |
| `confidence` | `float` | Detection confidence (0.0 to 1.0) |
| `class` | `str` | Object class name (e.g., `"vessel"`) |
| `center` | `list[float]` | Center point as `[x, y]` in pixels |

**Example:**

```python
from pontos import VesselDetector
from pathlib import Path

detector = VesselDetector()

# Basic detection
detections = detector.detect("data/scene.png")

for det in detections:
    print(f"Vessel at {det['center']} with confidence {det['confidence']:.2%}")

# With visualization
detections = detector.detect(
    "data/scene.png",
    save_visualization=True,
    output_dir=Path("runs/detect")
)
# Saves annotated image to runs/detect/
```

---

#### detect_tiled()

!!! warning "Not Implemented"
    This method is planned for v2.1 and currently raises `NotImplementedError`.

Detect vessels using a sliding window approach for large images.

```python
def detect_tiled(
    self,
    image_path: str | Path,
    tile_size: int = 320,
    overlap: float = 0.5
) -> list[dict]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image_path` | `str` or `Path` | — | Path to the image file |
| `tile_size` | `int` | `320` | Size of each tile in pixels |
| `overlap` | `float` | `0.5` | Overlap ratio between tiles |

**Raises:** `NotImplementedError` - This feature is not yet implemented.

---

### Properties

#### is_gpu_available

```python
@property
def is_gpu_available(self) -> bool
```

Check if GPU is available for inference.

**Returns:** `bool` - `True` if GPU is available, `False` otherwise.

**Example:**

```python
detector = VesselDetector()

if detector.is_gpu_available:
    print("Using GPU acceleration")
else:
    print("Running on CPU")
```

---

#### get_device_name()

```python
def get_device_name(self) -> str
```

Get the name of the current computation device.

**Returns:** `str` - Device name (e.g., `"NVIDIA GeForce RTX 3080"` or `"CPU"`).

**Example:**

```python
detector = VesselDetector()
print(f"Using device: {detector.get_device_name()}")
# Output: "Using device: NVIDIA GeForce RTX 3080"
```

---

## Detection Output Format

Each detection is a dictionary with the following structure:

```python
{
    "bbox": [x1, y1, x2, y2],      # Top-left and bottom-right corners
    "confidence": 0.87,             # Detection confidence score
    "class": "vessel",              # Detected object class
    "center": [center_x, center_y]  # Center point of bounding box
}
```

### Coordinate System

- Origin: Top-left corner of image
- X-axis: Horizontal, increasing right
- Y-axis: Vertical, increasing down
- Units: Pixels

```
(0,0) ────────────────────► X
  │
  │    ┌─────────────┐
  │    │   (x1,y1)   │
  │    │      ●──────┼── center
  │    │   (x2,y2)   │
  │    └─────────────┘
  │
  ▼
  Y
```

---

## Usage Patterns

### Basic Detection

```python
from pontos import VesselDetector

detector = VesselDetector()
detections = detector.detect("scene.png")

print(f"Detected {len(detections)} vessels")
for i, det in enumerate(detections):
    print(f"  {i+1}. confidence={det['confidence']:.2%}, center={det['center']}")
```

### High-Precision Detection

```python
detector = VesselDetector(confidence_threshold=0.5)
detections = detector.detect("scene.png")

# Only high-confidence detections
for det in detections:
    print(f"High-confidence vessel: {det['confidence']:.2%}")
```

### GPU Selection

```python
# Use first GPU
detector = VesselDetector(device="0")

# Use second GPU
detector = VesselDetector(device="1")

# Force CPU
detector = VesselDetector(device="cpu")
```

### Filter Results

```python
detector = VesselDetector()
detections = detector.detect("scene.png")

# Filter by confidence
high_conf = [d for d in detections if d["confidence"] > 0.8]
print(f"{len(high_conf)} high-confidence detections")

# Get bounding boxes only
boxes = [d["bbox"] for d in detections]

# Get center points only
centers = [d["center"] for d in detections]
```

---

## Error Handling

```python
from pontos import VesselDetector

detector = VesselDetector()

# File not found
try:
    detections = detector.detect("nonexistent.png")
except FileNotFoundError as e:
    print(f"Image not found: {e}")

# Invalid model path
try:
    detector = VesselDetector(model_path="invalid.pt")
except Exception as e:
    print(f"Failed to load model: {e}")
```

---

## Performance Tips

1. **Use GPU when available** - GPU inference is significantly faster
2. **Batch processing** - Process multiple images in sequence with the same detector instance
3. **Appropriate confidence threshold** - Higher thresholds reduce post-processing time
4. **Image size** - Larger images require more memory and processing time

```python
# Reuse detector for multiple images
detector = VesselDetector()

images = ["scene1.png", "scene2.png", "scene3.png"]
all_detections = []

for img in images:
    dets = detector.detect(img)
    all_detections.extend(dets)
```
