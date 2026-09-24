"""Integration tests for raster IO, georeferenced pipeline, and engine execution."""

import os
for proj_var in ("PROJ_LIB", "PROJ_DATA"):
    val = os.environ.get(proj_var, "")
    if val and ("postgres" in val.lower() or not os.path.exists(os.path.join(val, "proj.db"))):
        os.environ.pop(proj_var, None)

from pathlib import Path
import affine
import numpy as np
import pytest
import rasterio
from rasterio.crs import CRS
import geoindexpy


@pytest.fixture
def synthetic_geotiff(tmp_path: Path) -> Path:
    """Create a temporary multi-band GeoTIFF with Sentinel-2 band names and EPSG:32631 CRS."""
    file_path = tmp_path / "synthetic_sentinel2.tif"
    height, width = 20, 20
    count = 4  # B02 (Blue), B03 (Green), B04 (Red), B08 (NIR)
    crs = CRS.from_epsg(32631)
    transform = affine.Affine(10.0, 0.0, 500000.0, 0.0, -10.0, 6000000.0)

    # Generate synthetic reflectance data
    np.random.seed(42)
    b02 = np.random.uniform(0.01, 0.20, (height, width)).astype(np.float32)
    b03 = np.random.uniform(0.02, 0.25, (height, width)).astype(np.float32)
    b04 = np.random.uniform(0.02, 0.30, (height, width)).astype(np.float32)
    b08 = np.random.uniform(0.40, 0.85, (height, width)).astype(np.float32)

    profile = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": count,
        "dtype": "float32",
        "crs": crs,
        "transform": transform,
        "nodata": -9999.0,
    }

    with rasterio.open(str(file_path), "w", **profile) as dst:
        dst.write(b02, 1)
        dst.set_band_description(1, "B02")
        dst.write(b03, 2)
        dst.set_band_description(2, "B03")
        dst.write(b04, 3)
        dst.set_band_description(3, "B04")
        dst.write(b08, 4)
        dst.set_band_description(4, "B08")

    return file_path


def test_open_raster_and_metadata(synthetic_geotiff: Path) -> None:
    ds = geoindexpy.open_raster(synthetic_geotiff)
    assert ds.shape == (20, 20)
    assert set(ds.band_names()) == {"B02", "B03", "B04", "B08"}
    assert ds.metadata.crs is not None
    assert ds.metadata.resolution == (10.0, 10.0)


def test_calculate_index_from_file_and_preservation(synthetic_geotiff: Path, tmp_path: Path) -> None:
    # Calculate NDVI using automatic Sentinel-2 resolution (B08 -> NIR, B04 -> RED)
    result = geoindexpy.calculate_index(synthetic_geotiff, "NDVI", sensor="sentinel2")
    assert result.index_name == "NDVI"
    assert result.shape == (20, 20)
    assert result.metadata is not None
    assert result.metadata.crs.to_epsg() == 32631

    # Verify statistics
    stats = result.summary()
    assert stats["min"] is not None
    assert stats["max"] is not None
    assert stats["min"] >= -1.0
    assert stats["max"] <= 1.0
    assert stats["valid_pixels"] == 400

    # Save output to georeferenced GeoTIFF
    out_file = tmp_path / "ndvi_result.tif"
    result.save(out_file)
    assert out_file.is_file()

    # Re-read saved GeoTIFF to verify georeferencing
    with rasterio.open(str(out_file)) as src:
        assert src.crs.to_epsg() == 32631
        assert src.width == 20
        assert src.height == 20
        assert src.descriptions[0] == "NDVI"


def test_calculate_indices_multi(synthetic_geotiff: Path) -> None:
    results = geoindexpy.calculate_indices(
        synthetic_geotiff,
        indices=["NDVI", "NDWI"],
        sensor="sentinel2",
    )
    assert "NDVI" in results
    assert "NDWI" in results
    assert results["NDVI"].shape == (20, 20)
    assert results["NDWI"].shape == (20, 20)


def test_calculate_all(synthetic_geotiff: Path) -> None:
    outcome = geoindexpy.calculate_all(synthetic_geotiff, sensor="sentinel2")
    # NDVI and NDWI should succeed because Blue, Green, Red, NIR are present
    assert "NDVI" in outcome["results"]
    assert "NDWI" in outcome["results"]
    assert "NDVI" in outcome["available_indices"]
    # NDBI requires SWIR, which is absent in synthetic_geotiff: should be skipped with clear explanation
    assert "NDBI" in outcome["skipped"]
    assert "missing" in outcome["skipped"]["NDBI"].lower()
