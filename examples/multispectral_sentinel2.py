"""Multispectral example: Sentinel-2 image simulation, multi-index computation and GeoTIFF export."""

# --- PROJ protection: must come before any rasterio import ---
import os
for _var in ("PROJ_LIB", "PROJ_DATA"):
    _val = os.environ.get(_var, "")
    if _val and ("postgres" in _val.lower() or not os.path.exists(os.path.join(_val, "proj.db"))):
        os.environ.pop(_var, None)
# -------------------------------------------------------------

from pathlib import Path
import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.transform import from_origin
import geoindexpy


def create_sample_sentinel2_geotiff(output_path: Path) -> None:
    """Generate a sample 4-band Sentinel-2 GeoTIFF (B02, B03, B04, B08)."""
    height, width = 64, 64
    transform = from_origin(500000.0, 6000000.0, 10.0, 10.0)
    crs = CRS.from_epsg(32631)  # WGS 84 / UTM zone 31N

    # Simulated reflectance
    np.random.seed(42)
    b02 = np.random.uniform(0.02, 0.15, (height, width)).astype(np.float32)  # Blue
    b03 = np.random.uniform(0.04, 0.20, (height, width)).astype(np.float32)  # Green
    b04 = np.random.uniform(0.03, 0.25, (height, width)).astype(np.float32)  # Red
    b08 = np.random.uniform(0.35, 0.85, (height, width)).astype(np.float32)  # NIR

    profile = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 4,
        "dtype": "float32",
        "crs": crs,
        "transform": transform,
        "nodata": -9999.0,
    }

    with rasterio.open(str(output_path), "w", **profile) as dst:
        dst.write(b02, 1)
        dst.set_band_description(1, "B02")
        dst.write(b03, 2)
        dst.set_band_description(2, "B03")
        dst.write(b04, 3)
        dst.set_band_description(3, "B04")
        dst.write(b08, 4)
        dst.set_band_description(4, "B08")


def main() -> None:
    out_dir = Path("scratch/example_run")
    out_dir.mkdir(parents=True, exist_ok=True)
    sample_tif = out_dir / "sample_sentinel2.tif"

    print("1. Creating sample Sentinel-2 GeoTIFF dataset...")
    create_sample_sentinel2_geotiff(sample_tif)

    print("2. Opening raster dataset with geoindexpy...")
    dataset = geoindexpy.open_raster(sample_tif)
    print(f"Loaded raster shape: {dataset.shape}")
    print(f"Available bands: {dataset.band_names()}")
    print(f"CRS: {dataset.metadata.crs}")
    print(f"Pixel resolution: {dataset.metadata.resolution}")

    print("\n3. Calculating multiple indices simultaneously (NDVI, NDWI, SAVI, GNDVI)...")
    results = geoindexpy.calculate_indices(
        image=sample_tif,
        indices=["NDVI", "NDWI", "SAVI", "GNDVI"],
        sensor="sentinel2",
    )

    for name, res in results.items():
        stats = res.summary()
        print(f"\n[{name}] Statistics:")
        print(f"  Min: {stats['min']:.3f} | Max: {stats['max']:.3f} | Mean: {stats['mean']:.3f} | Std: {stats['std']:.3f}")
        print(f"  Valid pixels: {stats['valid_pixels']}/{stats['total_pixels']}")

        # Save result to georeferenced GeoTIFF
        out_result_tif = out_dir / f"result_{name}.tif"
        res.save(out_result_tif)
        print(f"  Exported GeoTIFF -> {out_result_tif}")

    print("\nWorkflow completed successfully.")


if __name__ == "__main__":
    main()
