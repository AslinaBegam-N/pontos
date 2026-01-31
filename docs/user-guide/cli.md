# CLI Reference

Pontos provides a command-line interface for quick vessel detection scans.

## Basic Usage

```bash
pontos [OPTIONS] COMMAND [ARGS]...
```

## Commands

### `pontos scan`

Scan satellite imagery for vessels.

```bash
pontos scan [OPTIONS]
```

#### Options

| Option | Type | Default | Required | Description |
|--------|------|---------|----------|-------------|
| `--bbox` | `TEXT` | — | Yes | Bounding box as `min_lon,min_lat,max_lon,max_lat` (WGS84) |
| `--date-start` | `TEXT` | — | Yes | Start date in `YYYY-MM-DD` format |
| `--date-end` | `TEXT` | — | Yes | End date in `YYYY-MM-DD` format |
| `--output`, `-o` | `PATH` | `vessels.geojson` | No | Output GeoJSON file path |
| `--conf` | `FLOAT` | `0.05` | No | Detection confidence threshold (0.0-1.0) |

#### Examples

**Basic Scan**

```bash
pontos scan \
  --bbox 5.85,43.08,6.05,43.18 \
  --date-start 2026-01-01 \
  --date-end 2026-01-31
```

**Custom Output Path**

```bash
pontos scan \
  --bbox 5.85,43.08,6.05,43.18 \
  --date-start 2026-01-01 \
  --date-end 2026-01-31 \
  --output results/toulon_vessels.geojson
```

**High Precision Mode**

```bash
pontos scan \
  --bbox 5.85,43.08,6.05,43.18 \
  --date-start 2026-01-01 \
  --date-end 2026-01-31 \
  --conf 0.5
```

**Short Flags**

```bash
pontos scan \
  --bbox 5.85,43.08,6.05,43.18 \
  --date-start 2026-01-01 \
  --date-end 2026-01-31 \
  -o vessels.geojson
```

---

## Bounding Box Format

The bounding box defines the geographic area to scan:

```
--bbox min_lon,min_lat,max_lon,max_lat
```

- **min_lon**: Western longitude (left edge)
- **min_lat**: Southern latitude (bottom edge)
- **max_lon**: Eastern longitude (right edge)
- **max_lat**: Northern latitude (top edge)

All coordinates are in WGS84 (EPSG:4326).

### Finding Coordinates

1. Go to [bboxfinder.com](http://bboxfinder.com)
2. Draw a rectangle over your area of interest
3. Copy the bounding box coordinates

### Example Locations

| Location | Bounding Box |
|----------|--------------|
| Toulon, France | `5.85,43.08,6.05,43.18` |
| San Diego, USA | `-117.25,32.65,-117.15,32.75` |
| Portsmouth, UK | `-1.12,50.78,-1.05,50.82` |
| Norfolk, USA | `-76.35,36.90,-76.25,36.98` |
| Singapore Strait | `103.75,1.15,104.05,1.35` |

---

## Date Range Format

Dates must be in ISO format: `YYYY-MM-DD`

```bash
--date-start 2026-01-01 --date-end 2026-01-31
```

### Tips

- **Wider date ranges** increase chances of finding cloud-free imagery
- Sentinel-2 revisit time is approximately 5 days
- Use at least a 2-week window for reliable results

---

## Confidence Threshold

The `--conf` option controls detection sensitivity:

```bash
--conf 0.05  # Default: balanced sensitivity
--conf 0.01  # High sensitivity: more detections, more false positives
--conf 0.50  # High precision: fewer detections, fewer false positives
```

| Threshold | Sensitivity | False Positives | Use Case |
|-----------|-------------|-----------------|----------|
| 0.01 | Very High | Many | Exploratory analysis |
| 0.05 | High | Some | General use (default) |
| 0.10 | Medium | Few | Production scans |
| 0.50 | Low | Rare | High-precision requirements |

---

## Output Format

The output is a GeoJSON FeatureCollection:

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

### Viewing Results

- **geojson.io**: Drag and drop the file at [geojson.io](https://geojson.io)
- **QGIS**: Layer > Add Layer > Add Vector Layer
- **Folium**: Load with Python and create interactive maps
- **kepler.gl**: Upload to [kepler.gl](https://kepler.gl) for advanced visualization

---

## Environment Variables

The CLI respects environment variables for configuration:

```bash
# Set credentials
export SH_CLIENT_ID="your-client-id"
export SH_CLIENT_SECRET="your-client-secret"

# Set device
export DEVICE=0  # Use GPU 0
export DEVICE=cpu  # Force CPU

# Run scan
pontos scan --bbox 5.85,43.08,6.05,43.18 --date-start 2026-01-01 --date-end 2026-01-31
```

---

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Error (check stderr for details) |
| 2 | Invalid arguments |

---

## Help

Get help on any command:

```bash
# General help
pontos --help

# Scan command help
pontos scan --help
```

---

## Scripting Examples

### Batch Processing

```bash
#!/bin/bash
# Scan multiple locations

locations=(
  "5.85,43.08,6.05,43.18:toulon"
  "-117.25,32.65,-117.15,32.75:san_diego"
  "-1.12,50.78,-1.05,50.82:portsmouth"
)

for loc in "${locations[@]}"; do
  bbox="${loc%%:*}"
  name="${loc##*:}"

  echo "Scanning $name..."
  pontos scan \
    --bbox "$bbox" \
    --date-start 2026-01-01 \
    --date-end 2026-01-31 \
    --output "results/${name}_vessels.geojson"
done
```

### Pipeline with jq

```bash
# Count detected vessels
pontos scan \
  --bbox 5.85,43.08,6.05,43.18 \
  --date-start 2026-01-01 \
  --date-end 2026-01-31 \
  --output vessels.geojson

# Count vessels using jq
cat vessels.geojson | jq '.features | length'

# Get high-confidence detections
cat vessels.geojson | jq '.features[] | select(.properties.confidence > 0.8)'
```

### Cron Job

```bash
# Run daily scan at 6 AM
0 6 * * * cd /path/to/pontos && pontos scan --bbox 5.85,43.08,6.05,43.18 --date-start $(date -d "yesterday" +\%Y-\%m-\%d) --date-end $(date +\%Y-\%m-\%d) --output /data/vessels_$(date +\%Y\%m\%d).geojson
```

---

## Troubleshooting

??? question "Error: Missing Sentinel Hub credentials"

    Set environment variables or create `.env` file:
    ```bash
    export SH_CLIENT_ID="your-id"
    export SH_CLIENT_SECRET="your-secret"
    ```

??? question "Error: Model file not found"

    Ensure you pulled the model with Git LFS:
    ```bash
    git lfs pull
    ```

??? question "No vessels detected"

    Try:
    - Lower the confidence threshold: `--conf 0.01`
    - Expand the date range for better imagery
    - Check if the area contains vessels

??? question "Slow performance"

    Ensure GPU is being used:
    ```bash
    export DEVICE=0
    python -c "import torch; print(torch.cuda.is_available())"
    ```
