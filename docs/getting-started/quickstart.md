# Quick Start

This guide walks you through running your first vessel detection scan with Pontos.

## Prerequisites

Before starting, ensure you have:

- [x] Pontos installed ([Installation Guide](installation.md))
- [x] Sentinel Hub credentials configured
- [x] Model weights downloaded (`git lfs pull`)

---

## Your First Scan

### Using the CLI

The fastest way to detect vessels is through the command line:

```bash
# Scan Toulon naval base (January 2026)
pontos scan \
  --bbox 5.85,43.08,6.05,43.18 \
  --date-start 2026-01-01 \
  --date-end 2026-01-31 \
  --output vessels.geojson
```

This command:

1. Downloads Sentinel-2 imagery for the specified bounding box and date range
2. Runs YOLO11s detection on the satellite image
3. Converts detections to geographic coordinates
4. Exports results to `vessels.geojson`

### Expected Output

```
Downloading Sentinel-2 scene...
Scene saved to: data/sentinel2_20260115_123456.png
Running vessel detection...
Detected 12 vessels
Exporting to GeoJSON...
Results saved to: vessels.geojson
```

---

## Using Python API

For more control, use the Python API directly:

```python
from pontos import SentinelDataSource, VesselDetector, GeoExporter
from pathlib import Path

# Define area of interest (Toulon, France)
bbox = (5.85, 43.08, 6.05, 43.18)
time_range = ("2026-01-01", "2026-01-31")

# Step 1: Download satellite imagery
sentinel = SentinelDataSource()
scene_path = sentinel.get_scene(
    bbox=bbox,
    time_range=time_range,
    size=1024,
    max_cloud_coverage=0.2
)
print(f"Scene saved to: {scene_path}")

# Step 2: Detect vessels
detector = VesselDetector()
detections = detector.detect(
    image_path=scene_path,
    save_visualization=True,
    output_dir=Path("runs/toulon")
)
print(f"Detected {len(detections)} vessels")

# Step 3: Export to GeoJSON
geojson_path = GeoExporter.detections_to_geojson(
    detections=detections,
    bbox=bbox,
    image_size=(1024, 1024),
    output_path=Path("runs/toulon/vessels.geojson")
)
print(f"Results saved to: {geojson_path}")
```

---

## Understanding the Output

### Detection Results

Each detection contains:

```python
{
    "bbox": [x1, y1, x2, y2],      # Pixel coordinates
    "confidence": 0.87,             # Detection confidence (0.0-1.0)
    "class": "vessel",              # Object class
    "center": [512, 384]            # Center pixel coordinates
}
```

### GeoJSON Output

The exported GeoJSON contains Point features for each detected vessel:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [5.92, 43.12]
      },
      "properties": {
        "id": 0,
        "confidence": 0.87,
        "class": "vessel"
      }
    }
  ]
}
```

---

## Visualizing Results

### Using geojson.io

1. Open [geojson.io](https://geojson.io)
2. Drag and drop your `vessels.geojson` file
3. View detected vessels on an interactive map

### Using QGIS

1. Open QGIS
2. Layer > Add Layer > Add Vector Layer
3. Select your `vessels.geojson` file
4. Add a basemap (e.g., OpenStreetMap)

### Using Python (Folium)

```python
import folium
import json

# Load GeoJSON
with open("vessels.geojson") as f:
    data = json.load(f)

# Create map centered on Toulon
m = folium.Map(location=[43.12, 5.95], zoom_start=12)

# Add vessel markers
for feature in data["features"]:
    coords = feature["geometry"]["coordinates"]
    conf = feature["properties"]["confidence"]
    folium.CircleMarker(
        location=[coords[1], coords[0]],
        radius=8,
        color="red",
        fill=True,
        popup=f"Confidence: {conf:.2f}"
    ).add_to(m)

# Save map
m.save("vessels_map.html")
```

---

## Common Scan Locations

Here are some interesting locations to scan:

| Location | Bounding Box | Description |
|----------|--------------|-------------|
| Toulon, France | `5.85,43.08,6.05,43.18` | French naval base |
| San Diego, USA | `-117.25,32.65,-117.15,32.75` | US Navy port |
| Portsmouth, UK | `-1.12,50.78,-1.05,50.82` | Royal Navy base |
| Norfolk, USA | `-76.35,36.90,-76.25,36.98` | Largest US naval station |
| Yokosuka, Japan | `139.65,35.27,139.70,35.30` | US Navy base in Japan |

---

## Adjusting Detection

### Confidence Threshold

Lower values detect more vessels (but may include false positives):

```bash
# High sensitivity (more detections)
pontos scan --bbox 5.85,43.08,6.05,43.18 \
  --date-start 2026-01-01 --date-end 2026-01-31 \
  --conf 0.01

# High precision (fewer false positives)
pontos scan --bbox 5.85,43.08,6.05,43.18 \
  --date-start 2026-01-01 --date-end 2026-01-31 \
  --conf 0.5
```

### Date Range

Expand the date range to increase chances of cloud-free imagery:

```bash
# Wider date range for better imagery
pontos scan --bbox 5.85,43.08,6.05,43.18 \
  --date-start 2025-12-01 --date-end 2026-01-31 \
  --output vessels.geojson
```

---

## Running the Demo

Pontos includes a complete demo script for Toulon:

```bash
# Run the Toulon demo
python examples/toulon_demo.py
```

This script demonstrates the full pipeline with detailed output.

---

## Next Steps

- [Configuration](configuration.md) - Learn about all configuration options
- [CLI Reference](../user-guide/cli.md) - Complete CLI documentation
- [Python API](../user-guide/python-api.md) - Detailed API usage
- [Examples](../user-guide/examples.md) - More usage examples
