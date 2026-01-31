# Examples

This page contains practical examples for using Pontos in various scenarios.

## Basic Examples

### Scan a Naval Base

```python
from pontos import SentinelDataSource, VesselDetector, GeoExporter
from pathlib import Path

# Define area (Toulon, France)
bbox = (5.85, 43.08, 6.05, 43.18)

# Download imagery
sentinel = SentinelDataSource()
scene = sentinel.get_scene(
    bbox=bbox,
    time_range=("2026-01-01", "2026-01-31")
)

# Detect vessels
detector = VesselDetector()
detections = detector.detect(scene)

# Export results
GeoExporter.detections_to_geojson(
    detections=detections,
    bbox=bbox,
    image_size=(1024, 1024),
    output_path="toulon_vessels.geojson"
)

print(f"Found {len(detections)} vessels")
```

### High-Resolution Scan

```python
from pontos import SentinelDataSource, VesselDetector, GeoExporter

bbox = (5.90, 43.10, 5.95, 43.15)  # Smaller area, higher detail

sentinel = SentinelDataSource()
scene = sentinel.get_scene(
    bbox=bbox,
    time_range=("2026-01-01", "2026-01-31"),
    size=2048,  # Higher resolution
    max_cloud_coverage=0.1  # Stricter cloud filter
)

detector = VesselDetector(confidence_threshold=0.1)
detections = detector.detect(scene, save_visualization=True)

GeoExporter.detections_to_geojson(
    detections=detections,
    bbox=bbox,
    image_size=(2048, 2048),
    output_path="high_res_vessels.geojson"
)
```

---

## Multi-Location Scanning

### Batch Processing Multiple Ports

```python
from pontos import SentinelDataSource, VesselDetector, GeoExporter
from pathlib import Path

# Define locations
locations = {
    "toulon": (5.85, 43.08, 6.05, 43.18),
    "san_diego": (-117.25, 32.65, -117.15, 32.75),
    "portsmouth": (-1.12, 50.78, -1.05, 50.82),
    "norfolk": (-76.35, 36.90, -76.25, 36.98),
}

# Initialize components
sentinel = SentinelDataSource()
detector = VesselDetector()

# Process each location
results = {}
for name, bbox in locations.items():
    print(f"Scanning {name}...")

    output_dir = Path(f"runs/{name}")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        scene = sentinel.get_scene(
            bbox=bbox,
            time_range=("2026-01-01", "2026-01-31"),
            output_path=output_dir / "scene.png"
        )

        detections = detector.detect(scene)

        GeoExporter.detections_to_geojson(
            detections=detections,
            bbox=bbox,
            image_size=(1024, 1024),
            output_path=output_dir / "vessels.geojson"
        )

        results[name] = len(detections)
        print(f"  Found {len(detections)} vessels")

    except Exception as e:
        print(f"  Error: {e}")
        results[name] = -1

# Summary
print("\n--- Summary ---")
for name, count in results.items():
    status = f"{count} vessels" if count >= 0 else "failed"
    print(f"{name}: {status}")
```

---

## Time Series Analysis

### Track Vessel Counts Over Time

```python
from pontos import SentinelDataSource, VesselDetector, GeoExporter
from pathlib import Path
from datetime import datetime, timedelta
import json

bbox = (5.85, 43.08, 6.05, 43.18)  # Toulon

sentinel = SentinelDataSource()
detector = VesselDetector()

# Scan monthly for 6 months
results = []
start_date = datetime(2025, 7, 1)

for month in range(6):
    date_start = start_date + timedelta(days=30 * month)
    date_end = date_start + timedelta(days=30)

    month_str = date_start.strftime("%Y-%m")
    print(f"Scanning {month_str}...")

    try:
        scene = sentinel.get_scene(
            bbox=bbox,
            time_range=(
                date_start.strftime("%Y-%m-%d"),
                date_end.strftime("%Y-%m-%d")
            )
        )

        detections = detector.detect(scene)

        results.append({
            "month": month_str,
            "vessel_count": len(detections),
            "avg_confidence": sum(d["confidence"] for d in detections) / max(len(detections), 1)
        })

    except Exception as e:
        print(f"  Error: {e}")
        results.append({
            "month": month_str,
            "vessel_count": None,
            "error": str(e)
        })

# Save time series
with open("vessel_timeseries.json", "w") as f:
    json.dump(results, f, indent=2)

# Print results
print("\n--- Monthly Vessel Counts ---")
for r in results:
    if r.get("vessel_count") is not None:
        print(f"{r['month']}: {r['vessel_count']} vessels (avg conf: {r['avg_confidence']:.2%})")
```

---

## Visualization Examples

### Interactive Map with Folium

```python
import folium
import json
from pontos import SentinelDataSource, VesselDetector, GeoExporter

# Run detection
bbox = (5.85, 43.08, 6.05, 43.18)

sentinel = SentinelDataSource()
scene = sentinel.get_scene(bbox=bbox, time_range=("2026-01-01", "2026-01-31"))

detector = VesselDetector()
detections = detector.detect(scene)

GeoExporter.detections_to_geojson(
    detections, bbox, (1024, 1024), "vessels.geojson"
)

# Create interactive map
with open("vessels.geojson") as f:
    geojson = json.load(f)

# Calculate center
center_lat = (bbox[1] + bbox[3]) / 2
center_lon = (bbox[0] + bbox[2]) / 2

# Create map
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=13,
    tiles="CartoDB positron"
)

# Add vessel markers
for feature in geojson["features"]:
    coords = feature["geometry"]["coordinates"]
    props = feature["properties"]

    # Color based on confidence
    if props["confidence"] > 0.8:
        color = "green"
    elif props["confidence"] > 0.5:
        color = "orange"
    else:
        color = "red"

    folium.CircleMarker(
        location=[coords[1], coords[0]],
        radius=10,
        color=color,
        fill=True,
        fillOpacity=0.7,
        popup=f"ID: {props['id']}<br>Confidence: {props['confidence']:.2%}"
    ).add_to(m)

# Add bounding box
folium.Rectangle(
    bounds=[[bbox[1], bbox[0]], [bbox[3], bbox[2]]],
    color="blue",
    fill=False,
    weight=2
).add_to(m)

# Save map
m.save("vessels_map.html")
print("Map saved to vessels_map.html")
```

### Matplotlib Detection Overlay

```python
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from pontos import VesselDetector

# Detect vessels
detector = VesselDetector()
detections = detector.detect("data/samples/toulon_l1c.png")

# Load image
img = Image.open("data/samples/toulon_l1c.png")

# Create figure
fig, ax = plt.subplots(1, figsize=(12, 12))
ax.imshow(img)

# Draw bounding boxes
for det in detections:
    x1, y1, x2, y2 = det["bbox"]
    width = x2 - x1
    height = y2 - y1

    # Color based on confidence
    color = "lime" if det["confidence"] > 0.5 else "yellow"

    rect = patches.Rectangle(
        (x1, y1), width, height,
        linewidth=2,
        edgecolor=color,
        facecolor="none"
    )
    ax.add_patch(rect)

    # Add label
    ax.text(
        x1, y1 - 5,
        f"{det['confidence']:.2f}",
        color=color,
        fontsize=10,
        fontweight="bold"
    )

ax.set_title(f"Detected {len(detections)} vessels")
ax.axis("off")

plt.tight_layout()
plt.savefig("detection_overlay.png", dpi=150, bbox_inches="tight")
plt.show()
```

---

## Integration Examples

### FastAPI Web Service

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pontos import SentinelDataSource, VesselDetector, GeoExporter
from pathlib import Path
import uuid

app = FastAPI(title="Pontos API")

sentinel = SentinelDataSource()
detector = VesselDetector()


class ScanRequest(BaseModel):
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float
    date_start: str
    date_end: str
    confidence: float = 0.05


class ScanResponse(BaseModel):
    scan_id: str
    vessel_count: int
    geojson_path: str


@app.post("/scan", response_model=ScanResponse)
async def scan_area(request: ScanRequest):
    """Scan an area for vessels."""
    scan_id = str(uuid.uuid4())[:8]
    output_dir = Path(f"scans/{scan_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    bbox = (request.min_lon, request.min_lat, request.max_lon, request.max_lat)

    try:
        # Download scene
        scene = sentinel.get_scene(
            bbox=bbox,
            time_range=(request.date_start, request.date_end),
            output_path=output_dir / "scene.png"
        )

        # Detect vessels
        detections = detector.detect(scene)

        # Export GeoJSON
        geojson_path = output_dir / "vessels.geojson"
        GeoExporter.detections_to_geojson(
            detections, bbox, (1024, 1024), geojson_path
        )

        return ScanResponse(
            scan_id=scan_id,
            vessel_count=len(detections),
            geojson_path=str(geojson_path)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok", "gpu": detector.is_gpu_available}
```

### Streamlit Dashboard

```python
import streamlit as st
from pontos import SentinelDataSource, VesselDetector, GeoExporter
import folium
from streamlit_folium import st_folium
import json

st.set_page_config(page_title="Pontos Dashboard", layout="wide")
st.title("Pontos Vessel Detection")

# Sidebar inputs
st.sidebar.header("Scan Parameters")

col1, col2 = st.sidebar.columns(2)
with col1:
    min_lon = st.number_input("Min Lon", value=5.85)
    min_lat = st.number_input("Min Lat", value=43.08)
with col2:
    max_lon = st.number_input("Max Lon", value=6.05)
    max_lat = st.number_input("Max Lat", value=43.18)

date_start = st.sidebar.date_input("Start Date")
date_end = st.sidebar.date_input("End Date")
confidence = st.sidebar.slider("Confidence Threshold", 0.01, 1.0, 0.05)

if st.sidebar.button("Run Scan"):
    with st.spinner("Downloading satellite imagery..."):
        sentinel = SentinelDataSource()
        scene = sentinel.get_scene(
            bbox=(min_lon, min_lat, max_lon, max_lat),
            time_range=(str(date_start), str(date_end))
        )

    with st.spinner("Running detection..."):
        detector = VesselDetector(confidence_threshold=confidence)
        detections = detector.detect(scene)

        GeoExporter.detections_to_geojson(
            detections,
            (min_lon, min_lat, max_lon, max_lat),
            (1024, 1024),
            "temp_vessels.geojson"
        )

    st.success(f"Detected {len(detections)} vessels!")

    # Display map
    with open("temp_vessels.geojson") as f:
        geojson = json.load(f)

    center = [(min_lat + max_lat) / 2, (min_lon + max_lon) / 2]
    m = folium.Map(location=center, zoom_start=12)

    for feature in geojson["features"]:
        coords = feature["geometry"]["coordinates"]
        folium.CircleMarker(
            location=[coords[1], coords[0]],
            radius=8,
            color="red",
            fill=True
        ).add_to(m)

    st_folium(m, width=700, height=500)

    # Display results table
    st.dataframe([
        {"ID": d["properties"]["id"],
         "Confidence": f"{d['properties']['confidence']:.2%}"}
        for d in geojson["features"]
    ])
```

---

## CLI Script Examples

### Automated Daily Scan

```bash
#!/bin/bash
# daily_scan.sh - Run automated vessel detection

DATE=$(date +%Y-%m-%d)
OUTPUT_DIR="scans/$DATE"
mkdir -p "$OUTPUT_DIR"

# Scan locations
locations=(
    "5.85,43.08,6.05,43.18:toulon"
    "-117.25,32.65,-117.15,32.75:san_diego"
)

for loc in "${locations[@]}"; do
    bbox="${loc%%:*}"
    name="${loc##*:}"

    echo "[$DATE] Scanning $name..."

    pontos scan \
        --bbox "$bbox" \
        --date-start "$(date -d '7 days ago' +%Y-%m-%d)" \
        --date-end "$DATE" \
        --output "$OUTPUT_DIR/${name}.geojson" \
        --conf 0.1

    # Count vessels
    count=$(cat "$OUTPUT_DIR/${name}.geojson" | jq '.features | length')
    echo "  Found $count vessels"
done

echo "Scan complete. Results in $OUTPUT_DIR/"
```

---

## Next Steps

- [API Reference](../api/detector.md) - Detailed class documentation
- [Docker Deployment](../deployment/docker.md) - Run Pontos in containers
- [CI/CD](../deployment/ci-cd.md) - Automated testing and deployment
