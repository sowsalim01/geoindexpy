"""Scientific validation tests for all 9 v0.1.0 spectral indices."""

import numpy as np
import pytest
import geoindexpy


def test_savi_exact_values() -> None:
    """Verify SAVI with standard L=0.5."""
    nir = 0.8
    red = 0.2
    # ((0.8 - 0.2) / (0.8 + 0.2 + 0.5)) * 1.5 = (0.6 / 1.5) * 1.5 = 0.6
    res = geoindexpy.savi(nir, red, L=0.5)
    assert np.isclose(res, 0.6)

    # Test with custom L=1.0: ((0.6) / (1.0 + 1.0)) * 2.0 = 0.6
    res_l1 = geoindexpy.savi(nir, red, L=1.0)
    assert np.isclose(res_l1, 0.6)


def test_evi_exact_values() -> None:
    """Verify EVI calculation on controlled inputs."""
    nir = np.array([0.8])
    red = np.array([0.2])
    blue = np.array([0.05])
    # num = 2.5 * (0.8 - 0.2) = 1.5
    # den = 0.8 + 6.0*0.2 - 7.5*0.05 + 1.0 = 2.625
    # res = 1.5 / 2.625 = 0.5714285714285714
    res = geoindexpy.evi(nir, red, blue)
    expected = 1.5 / 2.625
    assert np.allclose(res, expected)


def test_gndvi_exact_values() -> None:
    """Verify GNDVI calculation: (NIR - GREEN) / (NIR + GREEN)."""
    nir = np.array([0.8, 0.1])
    green = np.array([0.2, 0.4])
    res = geoindexpy.gndvi(nir, green)
    # Case 1: (0.8 - 0.2) / 1.0 = 0.6
    # Case 2: (0.1 - 0.4) / 0.5 = -0.6
    assert np.allclose(res, [0.6, -0.6])


def test_mndwi_exact_values() -> None:
    """Verify MNDWI calculation: (GREEN - SWIR) / (GREEN + SWIR)."""
    green = np.array([0.4, 0.1])
    swir = np.array([0.1, 0.4])
    res = geoindexpy.mndwi(green, swir)
    assert np.allclose(res, [0.6, -0.6])


def test_ndmi_exact_values() -> None:
    """Verify NDMI calculation: (NIR - SWIR) / (NIR + SWIR)."""
    nir = np.array([0.7, 0.2])
    swir = np.array([0.3, 0.6])
    res = geoindexpy.ndmi(nir, swir)
    # (0.7 - 0.3) / 1.0 = 0.4
    # (0.2 - 0.6) / 0.8 = -0.5
    assert np.allclose(res, [0.4, -0.5])


def test_bsi_exact_values() -> None:
    """Verify BSI calculation: ((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))."""
    swir = np.array([0.45])
    red = np.array([0.25])
    nir = np.array([0.30])
    blue = np.array([0.12])
    res = geoindexpy.bsi(swir, red, nir, blue)
    # (0.70 - 0.42) / (0.70 + 0.42) = 0.28 / 1.12 = 0.25
    assert np.allclose(res, [0.25])


def test_calculate_all_nine_indices(synthetic_bands_2d: dict[str, np.ndarray]) -> None:
    """Test calculate_indices with all 9 v0.1.0 indices on synthetic 2D data."""
    all_nine = ["NDVI", "SAVI", "EVI", "GNDVI", "NDWI", "MNDWI", "NDBI", "NDMI", "BSI"]
    results = geoindexpy.calculate_indices(
        image=synthetic_bands_2d,
        indices=all_nine,
    )
    assert len(results) == 9
    for name in all_nine:
        assert name in results
        assert results[name].shape == (4, 4)
        summary = results[name].summary()
        assert summary["valid_pixels"] == 16
        assert summary["min"] is not None
        assert summary["max"] is not None


def test_registry_has_all_nine_indices() -> None:
    indices = geoindexpy.list_indices()
    expected = {"NDVI", "SAVI", "EVI", "GNDVI", "NDWI", "MNDWI", "NDBI", "NDMI", "BSI"}
    assert expected.issubset(set(indices))

    # Verify categories
    assert set(geoindexpy.list_indices(category="vegetation")) == {"NDVI", "SAVI", "EVI", "GNDVI"}
    assert set(geoindexpy.list_indices(category="water")) == {"NDWI", "MNDWI"}
    assert set(geoindexpy.list_indices(category="urban")) == {"NDBI"}
    assert set(geoindexpy.list_indices(category="moisture")) == {"NDMI"}
    assert set(geoindexpy.list_indices(category="soil")) == {"BSI"}
