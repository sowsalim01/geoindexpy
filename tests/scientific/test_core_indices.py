"""Scientific validation tests for core indices (NDVI, NDWI, NDBI)."""

import numpy as np
import pytest
import geoindexpy


def test_ndvi_scientific_exact_values() -> None:
    """Verify NDVI formula on known exact values from literature.

    Formula: (NIR - RED) / (NIR + RED)
    Case 1: NIR=0.8, RED=0.2 => (0.8 - 0.2) / (0.8 + 0.2) = 0.6 / 1.0 = 0.6
    Case 2: NIR=0.5, RED=0.5 => 0.0 (bare soil / neutral)
    Case 3: NIR=0.1, RED=0.3 => (0.1 - 0.3) / (0.1 + 0.3) = -0.2 / 0.4 = -0.5 (water/negative)
    """
    nir = np.array([0.8, 0.5, 0.1])
    red = np.array([0.2, 0.5, 0.3])
    res = geoindexpy.ndvi(nir, red)
    expected = np.array([0.6, 0.0, -0.5])
    assert np.allclose(res, expected)


def test_ndvi_zero_division() -> None:
    """Ensure (NIR=0, RED=0) yields NaN safely and not Inf."""
    res = geoindexpy.ndvi(0.0, 0.0)
    assert np.isnan(res)


def test_ndwi_scientific_exact_values() -> None:
    """Verify NDWI formula on known exact values (McFeeters 1996).

    Formula: (GREEN - NIR) / (GREEN + NIR)
    Case 1: Deep water: GREEN=0.4, NIR=0.0 => (0.4 - 0.0) / 0.4 = +1.0
    Case 2: Dense vegetation: GREEN=0.1, NIR=0.9 => (0.1 - 0.9) / 1.0 = -0.8
    """
    green = np.array([0.4, 0.1])
    nir = np.array([0.0, 0.9])
    res = geoindexpy.ndwi(green, nir)
    expected = np.array([1.0, -0.8])
    assert np.allclose(res, expected)


def test_ndbi_scientific_exact_values() -> None:
    """Verify NDBI formula on known values (Zha et al. 2003).

    Formula: (SWIR - NIR) / (SWIR + NIR)
    Case 1: Built-up urban: SWIR=0.5, NIR=0.3 => (0.5 - 0.3) / 0.8 = 0.25 (> 0)
    Case 2: Healthy vegetation: SWIR=0.1, NIR=0.7 => (0.1 - 0.7) / 0.8 = -0.75 (< 0)
    """
    swir = np.array([0.5, 0.1])
    nir = np.array([0.3, 0.7])
    res = geoindexpy.ndbi(swir, nir)
    expected = np.array([0.25, -0.75])
    assert np.allclose(res, expected)


def test_indices_on_2d_synthetic_fixture(synthetic_bands_2d: dict[str, np.ndarray]) -> None:
    """Verify behavior on 2D multi-pixel rasters representing distinct land cover types."""
    nir = synthetic_bands_2d["nir"]
    red = synthetic_bands_2d["red"]
    green = synthetic_bands_2d["green"]
    swir1 = synthetic_bands_2d["swir1"]

    ndvi_map = geoindexpy.ndvi(nir, red)
    ndwi_map = geoindexpy.ndwi(green, nir)
    ndbi_map = geoindexpy.ndbi(swir1, nir)

    # Pixel (0, 0) is healthy vegetation: NDVI should be high, NDWI negative, NDBI negative
    assert ndvi_map[0, 0] > 0.8
    assert ndwi_map[0, 0] < -0.8
    assert ndbi_map[0, 0] < -0.6

    # Pixel (0, 1) is water: NDWI should be positive, NDVI very low
    assert ndwi_map[0, 1] > 0.6
    assert ndvi_map[0, 1] < 0.0


def test_registry_contains_core_indices() -> None:
    """Ensure NDVI, NDWI, NDBI are automatically registered and discoverable."""
    indices = geoindexpy.list_indices()
    assert "NDVI" in indices
    assert "NDWI" in indices
    assert "NDBI" in indices

    ndvi_info = geoindexpy.get_index_info("NDVI")
    assert ndvi_info["category"] == "vegetation"
    assert "nir" in ndvi_info["required_bands"]
    assert "red" in ndvi_info["required_bands"]
    assert "Rouse" in str(ndvi_info["reference"])
