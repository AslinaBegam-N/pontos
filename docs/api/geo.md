# pontos.geo

Geospatial utilities for coordinate transformation and GeoJSON export.

## GeoExporter

Static class for converting pixel-space detections to geographic coordinates and exporting to GeoJSON.

### Class Definition

```python
class GeoExporter:
    """
    Geospatial export utilities for vessel detections.

    Converts pixel coordinates to geographic coordinates (WGS84)
    and exports results as GeoJSON FeatureCollections.

    All methods are static - no instantiation required.

    Example:
        >>> GeoExporter.detections_to_geojson(
        ...     detections, bbox, image_size, "vessels.geojson"
        ... )
    """
```

---

### Methods

#### detections_to_geojson() (static)

Convert pixel-space detections to a GeoJSON FeatureCollection.

```python
@staticmethod
def detections_to_geojson(
    detections: list[dict],
    bbox: tuple[float, float, float, float],
    image_size: tuple[int, int],
    output_path: str | Path
) -> Path
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `detections` | `list[dict]` | List of detection dictionaries with `center` key |
| `bbox` | `tuple` | Geographic bounding box `(min_lon, min_lat, max_lon, max_lat)` |
| `image_size` | `tuple` | Image dimensions as `(width, height)` in pixels |
| `output_path` | `str` or `Path` | Output file path for GeoJSON |

**Returns:**

`Path` - Path to the saved GeoJSON file.

**Example:**

```python
from pontos import GeoExporter

detections = [
    {"center": [512, 384], "confidence": 0.87, "class": "vessel"},
    {"center": [256, 128], "confidence": 0.65, "class": "vessel"}
]

geojson_path = GeoExporter.detections_to_geojson(
    detections=detections,
    bbox=(5.85, 43.08, 6.05, 43.18),
    image_size=(1024, 1024),
    output_path="vessels.geojson"
)
```

---

#### _pixel_to_geo() (private static)

Convert pixel coordinates to geographic coordinates.

```python
@staticmethod
def _pixel_to_geo(
    x_px: float,
    y_px: float,
    bbox: tuple[float, float, float, float],
    image_size: tuple[int, int]
) -> tuple[float, float]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `x_px` | `float` | X coordinate in pixels |
| `y_px` | `float` | Y coordinate in pixels |
| `bbox` | `tuple` | Geographic bounding box |
| `image_size` | `tuple` | Image dimensions `(width, height)` |

**Returns:**

`tuple[float, float]` - Geographic coordinates as `(longitude, latitude)`.

**Transformation Formula:**

```python
lon = min_lon + (x_px / width) * (max_lon - min_lon)
lat = max_lat - (y_px / height) * (max_lat - min_lat)
```

!!! note "Coordinate System"
    The Y-axis is inverted because image coordinates have origin at top-left,
    while geographic coordinates have latitude increasing northward.

---

## GeoJSON Output Format

### FeatureCollection Structure

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [longitude, latitude]
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

### Feature Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | `int` | Sequential detection ID |
| `confidence` | `float` | Detection confidence (0.0-1.0) |
| `class` | `str` | Object class name |

---

## Coordinate Transformation

### Pixel to Geographic

The transformation maps pixel coordinates to WGS84 coordinates:

```
Image Space (pixels)          Geographic Space (WGS84)
                                    max_lat (north)
    (0,0) ──────────► X                 │
      │                            min_lon ─────── max_lon
      │                             (west)          (east)
      ▼                                 │
      Y                             min_lat (south)
    (w,h)
```

### Transformation Details

1. **X-axis mapping**: Linear interpolation from `min_lon` to `max_lon`
2. **Y-axis mapping**: Inverted linear interpolation from `max_lat` to `min_lat`

```python
# Example transformation
image_size = (1024, 1024)
bbox = (5.85, 43.08, 6.05, 43.18)  # min_lon, min_lat, max_lon, max_lat

# Pixel (512, 512) -> center of image
x_px, y_px = 512, 512

# Calculate geographic coordinates
lon = 5.85 + (512 / 1024) * (6.05 - 5.85)  # = 5.95
lat = 43.18 - (512 / 1024) * (43.18 - 43.08)  # = 43.13

# Result: (5.95, 43.13)
```

---

## Usage Examples

### Basic Export

```python
from pontos import GeoExporter

# Sample detections from VesselDetector
detections = [
    {
        "bbox": [100, 100, 200, 200],
        "confidence": 0.87,
        "class": "vessel",
        "center": [150, 150]
    },
    {
        "bbox": [500, 300, 600, 400],
        "confidence": 0.65,
        "class": "vessel",
        "center": [550, 350]
    }
]

# Export to GeoJSON
GeoExporter.detections_to_geojson(
    detections=detections,
    bbox=(5.85, 43.08, 6.05, 43.18),
    image_size=(1024, 1024),
    output_path="vessels.geojson"
)
```

### Full Pipeline

```python
from pontos import SentinelDataSource, VesselDetector, GeoExporter
from pathlib import Path

# Define area
bbox = (5.85, 43.08, 6.05, 43.18)
image_size = (1024, 1024)

# Download scene
sentinel = SentinelDataSource()
scene = sentinel.get_scene(
    bbox=bbox,
    time_range=("2026-01-01", "2026-01-31"),
    size=image_size[0]
)

# Detect vessels
detector = VesselDetector()
detections = detector.detect(scene)

# Export to GeoJSON
output_path = GeoExporter.detections_to_geojson(
    detections=detections,
    bbox=bbox,
    image_size=image_size,
    output_path=Path("output/vessels.geojson")
)

print(f"Exported {len(detections)} vessels to {output_path}")
```

### Load and Visualize

```python
import json
import folium

# Load GeoJSON
with open("vessels.geojson") as f:
    geojson = json.load(f)

# Create map
center = [43.13, 5.95]
m = folium.Map(location=center, zoom_start=12)

# Add features
for feature in geojson["features"]:
    coords = feature["geometry"]["coordinates"]
    props = feature["properties"]

    folium.Marker(
        location=[coords[1], coords[0]],  # [lat, lon]
        popup=f"Confidence: {props['confidence']:.2%}"
    ).add_to(m)

m.save("vessels_map.html")
```

---

## Integration with GIS Tools

### QGIS

1. Layer > Add Layer > Add Vector Layer
2. Select `vessels.geojson`
3. Add a basemap for context

### geojson.io

Drag and drop the file at [geojson.io](https://geojson.io)

### Python Libraries

```python
import geopandas as gpd

# Load as GeoDataFrame
gdf = gpd.read_file("vessels.geojson")

print(gdf.head())
print(f"Total vessels: {len(gdf)}")
print(f"CRS: {gdf.crs}")

# Filter high-confidence
high_conf = gdf[gdf["confidence"] > 0.8]
```

---

## Error Handling

```python
from pontos import GeoExporter
from pathlib import Path

try:
    GeoExporter.detections_to_geojson(
        detections=[],  # Empty list
        bbox=(5.85, 43.08, 6.05, 43.18),
        image_size=(1024, 1024),
        output_path="empty.geojson"
    )
    # Still creates valid GeoJSON with empty features array
except Exception as e:
    print(f"Export failed: {e}")
```

---

## Notes

- All coordinates are in WGS84 (EPSG:4326)
- GeoJSON follows the [RFC 7946](https://tools.ietf.org/html/rfc7946) specification
- Point geometries are used (vessel center points)
- Output directory is created automatically if it doesn't exist
