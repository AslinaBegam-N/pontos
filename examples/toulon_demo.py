"""Reproduce Toulon 10 vessels demo from MVP."""
from pathlib import Path

from pontos.detector import VesselDetector
from pontos.sentinel import SentinelDataSource
from pontos.geo import GeoExporter


def main():
    """Run Toulon naval base ship detection demo."""
    # Toulon bounding box (French naval base)
    bbox_toulon = (5.85, 43.08, 6.05, 43.18)
    time_range = ("2026-01-01", "2026-01-31")

    print("Downloading Sentinel-2 scene for Toulon...")
    sentinel = SentinelDataSource()
    scene_path = sentinel.get_scene(
        bbox=bbox_toulon,
        time_range=time_range,
        output_path=Path("data/toulon_sentinel2.png")
    )
    print(f"Scene saved: {scene_path}")

    print("\nDetecting vessels...")
    detector = VesselDetector()
    print(f"   Device: {detector.get_device_name()}")

    detections = detector.detect(
        image_path=scene_path,
        save_visualization=True,
        output_dir=Path("runs/toulon")
    )
    print(f"Found {len(detections)} vessels")

    print("\nExporting to GeoJSON...")
    geojson_path = GeoExporter.detections_to_geojson(
        detections=detections,
        bbox=bbox_toulon,
        image_size=(1024, 1024),
        output_path=Path("runs/toulon/vessels.geojson")
    )
    print(f"Saved: {geojson_path}")

    print("\nSummary:")
    for idx, det in enumerate(detections[:5]):  # Show first 5
        print(f"   Vessel {idx}: conf={det['confidence']:.2f}")


if __name__ == "__main__":
    main()