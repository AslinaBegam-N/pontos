# pontos.sentinel

Sentinel Hub API client for downloading Sentinel-2 satellite imagery.

## SentinelDataSource

Client for downloading Sentinel-2 L1C RGB imagery from Sentinel Hub.

### Class Definition

```python
class SentinelDataSource:
    """
    Sentinel Hub API client for Sentinel-2 imagery.

    Downloads Level-1C (Top of Atmosphere) RGB imagery using the
    Sentinel Hub Process API.

    Attributes:
        client_id: Sentinel Hub OAuth Client ID
        client_secret: Sentinel Hub OAuth Client Secret

    Example:
        >>> sentinel = SentinelDataSource()
        >>> scene = sentinel.get_scene(
        ...     bbox=(5.85, 43.08, 6.05, 43.18),
        ...     time_range=("2026-01-01", "2026-01-31")
        ... )
    """
```

### Constructor

```python
def __init__(
    self,
    client_id: str | None = None,
    client_secret: str | None = None
) -> None
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client_id` | `str` | From environment | Sentinel Hub OAuth Client ID |
| `client_secret` | `str` | From environment | Sentinel Hub OAuth Client Secret |

**Environment Variables:**

If not provided, credentials are loaded from:

- `SH_CLIENT_ID`
- `SH_CLIENT_SECRET`

**Example:**

```python
from pontos import SentinelDataSource

# Using environment variables
sentinel = SentinelDataSource()

# Explicit credentials
sentinel = SentinelDataSource(
    client_id="your-client-id",
    client_secret="your-client-secret"
)
```

---

### Methods

#### get_scene()

Download a Sentinel-2 scene for the specified area and time range.

```python
def get_scene(
    self,
    bbox: tuple[float, float, float, float],
    time_range: tuple[str, str],
    size: int = 1024,
    max_cloud_coverage: float = 0.2,
    output_path: Path | None = None
) -> Path
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `bbox` | `tuple` | — | Bounding box as `(min_lon, min_lat, max_lon, max_lat)` in WGS84 |
| `time_range` | `tuple` | — | Date range as `(start_date, end_date)` in ISO format |
| `size` | `int` | `1024` | Output image size in pixels (square) |
| `max_cloud_coverage` | `float` | `0.2` | Maximum allowed cloud coverage (0.0-1.0) |
| `output_path` | `Path` | `None` | Custom save location (auto-generated if None) |

**Returns:**

`Path` - Path to the saved PNG image file.

**Raises:**

- `ValueError` - If credentials are not configured
- `RuntimeError` - If no suitable scene is found

---

### Bounding Box Format

The bounding box uses WGS84 coordinates (EPSG:4326):

```
bbox = (min_lon, min_lat, max_lon, max_lat)
       (west,    south,   east,    north)
```

**Example:**

```python
# Toulon, France
bbox = (5.85, 43.08, 6.05, 43.18)
#       west  south  east  north
```

### Finding Coordinates

Use tools like:

- [bboxfinder.com](http://bboxfinder.com)
- [geojson.io](https://geojson.io)
- QGIS or Google Earth

---

### Date Range Format

Dates must be in ISO format: `YYYY-MM-DD`

```python
time_range = ("2026-01-01", "2026-01-31")
```

**Tips:**

- Sentinel-2 revisit time is ~5 days
- Use at least 2-week windows for reliable results
- Wider ranges increase chances of cloud-free imagery

---

## Usage Examples

### Basic Download

```python
from pontos import SentinelDataSource

sentinel = SentinelDataSource()

scene = sentinel.get_scene(
    bbox=(5.85, 43.08, 6.05, 43.18),
    time_range=("2026-01-01", "2026-01-31")
)

print(f"Scene saved to: {scene}")
```

### Custom Output Path

```python
from pathlib import Path

scene = sentinel.get_scene(
    bbox=(5.85, 43.08, 6.05, 43.18),
    time_range=("2026-01-01", "2026-01-31"),
    output_path=Path("data/toulon_scene.png")
)
```

### High Resolution

```python
scene = sentinel.get_scene(
    bbox=(5.90, 43.10, 5.95, 43.15),  # Smaller area
    time_range=("2026-01-01", "2026-01-31"),
    size=2048  # Higher resolution
)
```

### Strict Cloud Filter

```python
scene = sentinel.get_scene(
    bbox=(5.85, 43.08, 6.05, 43.18),
    time_range=("2025-06-01", "2026-01-31"),  # Wider date range
    max_cloud_coverage=0.1  # Maximum 10% clouds
)
```

---

## Sentinel-2 Data

### Bands Used

Pontos uses the True Color Image (TCI) bands:

| Band | Wavelength | Description |
|------|------------|-------------|
| B04 | 665 nm | Red |
| B03 | 560 nm | Green |
| B02 | 490 nm | Blue |

### Processing Level

- **L1C** (Level-1C): Top of Atmosphere reflectance
- Already radiometrically and geometrically corrected
- Native resolution: 10m (for RGB bands)

### Evalscript

The API uses this evalscript internally:

```javascript
//VERSION=3
function setup() {
  return {
    input: ["B04", "B03", "B02"],
    output: { bands: 3, sampleType: "UINT8" }
  };
}

function evaluatePixel(sample) {
  return [sample.B04, sample.B03, sample.B02];
}
```

---

## Image Mosaicking

When multiple scenes are available in the time range, the API selects imagery using:

- **Mosaicking Order**: `LEAST_CC` (least cloud coverage)
- Cloud coverage is calculated per-scene
- The clearest available scene is returned

---

## Error Handling

```python
from pontos import SentinelDataSource

sentinel = SentinelDataSource()

try:
    scene = sentinel.get_scene(
        bbox=(5.85, 43.08, 6.05, 43.18),
        time_range=("2026-01-01", "2026-01-31")
    )
except ValueError as e:
    print(f"Configuration error: {e}")
except RuntimeError as e:
    print(f"No suitable scene found: {e}")
except Exception as e:
    print(f"API error: {e}")
```

---

## Rate Limits & Quotas

Sentinel Hub has usage limits:

| Tier | Processing Units/Month | Requests/Minute |
|------|------------------------|-----------------|
| Trial | 30,000 | 300 |
| Basic | 100,000 | 300 |
| Enterprise | Custom | Custom |

**Tips:**

- Cache downloaded scenes locally
- Reuse scenes when possible
- Use appropriate image sizes (smaller = fewer PU)

---

## Output Format

Downloaded images are saved as:

- **Format**: PNG (8-bit RGB)
- **Size**: Square, as specified (default 1024x1024)
- **Location**: `data/` directory or custom path

**Auto-generated filename format:**

```
data/sentinel2_YYYYMMDD_HHMMSS.png
```

---

## Integration Example

```python
from pontos import SentinelDataSource, VesselDetector, GeoExporter
from pathlib import Path

# Define area
bbox = (5.85, 43.08, 6.05, 43.18)

# Download imagery
sentinel = SentinelDataSource()
scene = sentinel.get_scene(
    bbox=bbox,
    time_range=("2026-01-01", "2026-01-31"),
    output_path=Path("runs/scene.png")
)

# Detect vessels
detector = VesselDetector()
detections = detector.detect(scene)

# Export to GeoJSON
GeoExporter.detections_to_geojson(
    detections,
    bbox=bbox,
    image_size=(1024, 1024),
    output_path=Path("runs/vessels.geojson")
)
```
