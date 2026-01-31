# Python API

This guide covers the programmatic usage of Pontos in Python applications.

## Quick Start

```python
from pontos import SentinelDataSource, VesselDetector, GeoExporter

# Download imagery, detect vessels, export to GeoJSON
sentinel = SentinelDataSource()
scene = sentinel.get_scene(
    bbox=(5.85, 43.08, 6.05, 43.18),
    time_range=("2026-01-01", "2026-01-31")
)

detector = VesselDetector()
detections = detector.detect(scene)

GeoExporter.detections_to_geojson(
    detections,
    bbox=(5.85, 43.08, 6.05, 43.18),
    image_size=(1024, 1024),
    output_path="vessels.geojson"
)
```

---

## Module Overview

| Module | Class | Description |
|--------|-------|-------------|
| `pontos` | `SentinelDataSource` | Download Sentinel-2 satellite imagery |
| `pontos` | `VesselDetector` | Detect vessels using YOLO11s |
| `pontos` | `GeoExporter` | Convert detections to GeoJSON |
| `pontos` | `config` | Global configuration object |
| `pontos` | `PontosConfig` | Configuration dataclass |

---

## SentinelDataSource

Downloads Sentinel-2 L1C RGB imagery from Sentinel Hub.

### Initialization

```python
from pontos import SentinelDataSource

# Using environment variables
sentinel = SentinelDataSource()

# With explicit credentials
sentinel = SentinelDataSource(
    client_id="your-client-id",
    client_secret="your-client-secret"
)
```

### get_scene()

Download a satellite scene for a given area and time range.

```python
scene_path = sentinel.get_scene(
    bbox=(5.85, 43.08, 6.05, 43.18),
    time_range=("2026-01-01", "2026-01-31"),
    size=1024,
    max_cloud_coverage=0.2,
    output_path=None
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `bbox` | `tuple` | — | Bounding box as (min_lon, min_lat, max_lon, max_lat) |
| `time_range` | `tuple` | — | Date range as (start_date, end_date) in ISO format |
| `size` | `int` | `1024` | Output image size in pixels (square) |
| `max_cloud_coverage` | `float` | `0.2` | Maximum cloud coverage (0.0-1.0) |
| `output_path` | `Path` | `None` | Custom save location (auto-generated if None) |

**Returns:** `Path` to the saved image file.

**Example:**

```python
from pontos import SentinelDataSource
from pathlib import Path

sentinel = SentinelDataSource()

# Basic usage
scene = sentinel.get_scene(
    bbox=(5.85, 43.08, 6.05, 43.18),
    time_range=("2026-01-01", "2026-01-31")
)
print(f"Scene saved to: {scene}")

# Custom output path
scene = sentinel.get_scene(
    bbox=(5.85, 43.08, 6.05, 43.18),
    time_range=("2026-01-01", "2026-01-31"),
    output_path=Path("data/toulon_scene.png")
)

# High-resolution with strict cloud filter
scene = sentinel.get_scene(
    bbox=(5.85, 43.08, 6.05, 43.18),
    time_range=("2025-06-01", "2026-01-31"),
    size=2048,
    max_cloud_coverage=0.1
)
```

---

## VesselDetector

YOLO11s-based vessel detection.

### Initialization

```python
from pontos import VesselDetector

# Using defaults from config
detector = VesselDetector()

# With custom settings
detector = VesselDetector(
    model_path="models/yolo11s_tci.pt",
    device="0",  # GPU ID or "cpu"
    confidence_threshold=0.1
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_path` | `str` | From config | Path to YOLO model weights |
| `device` | `str` | From config | Computation device (`cpu`, `0`, `1`, etc.) |
| `confidence_threshold` | `float` | `0.05` | Minimum confidence threshold |

### detect()

Detect vessels in an image.

```python
detections = detector.detect(
    image_path="data/scene.png",
    save_visualization=False,
    output_dir=None
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image_path` | `str` or `Path` | — | Path to the image file |
| `save_visualization` | `bool` | `False` | Save image with bounding boxes |
| `output_dir` | `Path` | `None` | Directory for visualization output |

**Returns:** `List[dict]` with detection results.

**Detection Dictionary:**

```python
{
    "bbox": [x1, y1, x2, y2],  # Pixel coordinates
    "confidence": 0.87,        # Detection confidence
    "class": "vessel",         # Object class
    "center": [512, 384]       # Center coordinates
}
```

**Example:**

```python
from pontos import VesselDetector
from pathlib import Path

detector = VesselDetector()

# Basic detection
detections = detector.detect("data/scene.png")
print(f"Found {len(detections)} vessels")

# With visualization
detections = detector.detect(
    "data/scene.png",
    save_visualization=True,
    output_dir=Path("runs/detect")
)

# Process results
for i, det in enumerate(detections):
    print(f"Vessel {i}: confidence={det['confidence']:.2f}, center={det['center']}")
```

### Properties

```python
# Check GPU availability
print(detector.is_gpu_available)  # True or False

# Get device name
print(detector.get_device_name())  # e.g., "NVIDIA GeForce RTX 3080"
```

---

## GeoExporter

Convert pixel-space detections to geographic coordinates.

### detections_to_geojson() (static method)

```python
from pontos import GeoExporter

geojson_path = GeoExporter.detections_to_geojson(
    detections=detections,
    bbox=(5.85, 43.08, 6.05, 43.18),
    image_size=(1024, 1024),
    output_path="vessels.geojson"
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `detections` | `list` | List of detection dictionaries |
| `bbox` | `tuple` | Geographic bounding box (min_lon, min_lat, max_lon, max_lat) |
| `image_size` | `tuple` | Image dimensions as (width, height) |
| `output_path` | `str` or `Path` | Output file path |

**Returns:** `Path` to the saved GeoJSON file.

**Example:**

```python
from pontos import GeoExporter
from pathlib import Path

# Sample detections
detections = [
    {"center": [512, 384], "confidence": 0.87, "class": "vessel"},
    {"center": [256, 128], "confidence": 0.65, "class": "vessel"}
]

# Export to GeoJSON
geojson_path = GeoExporter.detections_to_geojson(
    detections=detections,
    bbox=(5.85, 43.08, 6.05, 43.18),
    image_size=(1024, 1024),
    output_path=Path("output/vessels.geojson")
)

print(f"GeoJSON saved to: {geojson_path}")
```

---

## Configuration

### Global Config Object

```python
from pontos import config

# View current configuration
print(config.model_path)
print(config.device)
print(config.confidence_threshold)

# Modify configuration
config.device = "cpu"
config.confidence_threshold = 0.1

# Validate configuration
config.validate()  # Raises ValueError if invalid
```

### PontosConfig Dataclass

```python
from pontos import PontosConfig

# Create custom configuration
custom_config = PontosConfig(
    model_path="models/custom_model.pt",
    sentinel_client_id="your-id",
    sentinel_client_secret="your-secret",
    confidence_threshold=0.1,
    device="0",
    patch_size=512,
    patch_overlap=0.3,
    max_workers=8,
    batch_size=16
)

# Use with detector
detector = VesselDetector(
    model_path=custom_config.model_path,
    device=custom_config.device,
    confidence_threshold=custom_config.confidence_threshold
)
```

---

## Complete Pipeline Example

```python
"""
Complete vessel detection pipeline example.
"""
from pontos import SentinelDataSource, VesselDetector, GeoExporter, config
from pathlib import Path
import json

def scan_area(bbox, date_start, date_end, output_dir):
    """
    Scan an area for vessels and export results.

    Args:
        bbox: Tuple of (min_lon, min_lat, max_lon, max_lat)
        date_start: Start date (YYYY-MM-DD)
        date_end: End date (YYYY-MM-DD)
        output_dir: Directory for output files

    Returns:
        Path to the GeoJSON results file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Download satellite imagery
    print("Downloading satellite imagery...")
    sentinel = SentinelDataSource()
    scene_path = sentinel.get_scene(
        bbox=bbox,
        time_range=(date_start, date_end),
        size=1024,
        max_cloud_coverage=0.2,
        output_path=output_dir / "scene.png"
    )
    print(f"Scene saved to: {scene_path}")

    # Step 2: Detect vessels
    print("Running vessel detection...")
    detector = VesselDetector()
    detections = detector.detect(
        image_path=scene_path,
        save_visualization=True,
        output_dir=output_dir
    )
    print(f"Detected {len(detections)} vessels")
    print(f"Using device: {detector.get_device_name()}")

    # Step 3: Export to GeoJSON
    print("Exporting to GeoJSON...")
    geojson_path = GeoExporter.detections_to_geojson(
        detections=detections,
        bbox=bbox,
        image_size=(1024, 1024),
        output_path=output_dir / "vessels.geojson"
    )
    print(f"Results saved to: {geojson_path}")

    # Print summary
    print("\n--- Detection Summary ---")
    for i, det in enumerate(detections):
        print(f"Vessel {i+1}: confidence={det['confidence']:.2%}")

    return geojson_path


if __name__ == "__main__":
    # Scan Toulon naval base
    results = scan_area(
        bbox=(5.85, 43.08, 6.05, 43.18),
        date_start="2026-01-01",
        date_end="2026-01-31",
        output_dir="runs/toulon"
    )

    # Load and display results
    with open(results) as f:
        geojson = json.load(f)

    print(f"\nTotal vessels in GeoJSON: {len(geojson['features'])}")
```

---

## Error Handling

```python
from pontos import SentinelDataSource, VesselDetector, GeoExporter
from pontos.config import PontosConfig

# Configuration validation
config = PontosConfig()
try:
    config.validate()
except ValueError as e:
    print(f"Configuration error: {e}")

# Handle API errors
sentinel = SentinelDataSource()
try:
    scene = sentinel.get_scene(
        bbox=(5.85, 43.08, 6.05, 43.18),
        time_range=("2026-01-01", "2026-01-31")
    )
except Exception as e:
    print(f"Failed to download scene: {e}")

# Handle detection errors
detector = VesselDetector()
try:
    detections = detector.detect("nonexistent.png")
except FileNotFoundError as e:
    print(f"Image not found: {e}")
```

---

## Next Steps

- [API Reference](../api/detector.md) - Detailed class documentation
- [Examples](examples.md) - More usage examples
- [Configuration](../getting-started/configuration.md) - Configuration options
