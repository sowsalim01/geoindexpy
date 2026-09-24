"""Unit tests for SpectralIndex and IndexRegistry."""

import numpy as np
import pytest
from geoindexpy.core.model import SpectralIndex
from geoindexpy.core.registry import IndexRegistry
from geoindexpy.exceptions import IndexNotFoundError


def dummy_compute(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    return (nir - red) / (nir + red)


@pytest.fixture
def mock_index() -> SpectralIndex:
    return SpectralIndex(
        short_name="TEST_NDVI",
        long_name="Test Normalized Difference Vegetation Index",
        category="vegetation",
        required_bands=("nir", "red"),
        formula_str="(nir - red) / (nir + red)",
        compute_fn=dummy_compute,
        default_params={},
        reference="Test Reference 2026",
    )


def test_spectral_index_normalization(mock_index: SpectralIndex) -> None:
    assert mock_index.short_name == "TEST_NDVI"
    assert mock_index.category == "vegetation"
    assert mock_index.required_bands == ("nir", "red")


def test_registry_register_and_get(mock_index: SpectralIndex) -> None:
    registry = IndexRegistry()
    registry.register(mock_index)

    # Retrieval should be case-insensitive
    retrieved = registry.get("test_ndvi")
    assert retrieved.short_name == "TEST_NDVI"
    assert retrieved.long_name == mock_index.long_name

    # Duplicate register without overwrite must raise ValueError
    with pytest.raises(ValueError, match="already registered"):
        registry.register(mock_index)

    # With overwrite=True it should succeed
    registry.register(mock_index, overwrite=True)
    assert len(registry) == 1


def test_registry_not_found() -> None:
    registry = IndexRegistry()
    with pytest.raises(IndexNotFoundError) as exc_info:
        registry.get("NON_EXISTENT")
    assert "NON_EXISTENT" in str(exc_info.value)


def test_registry_filtering(mock_index: SpectralIndex) -> None:
    registry = IndexRegistry()
    registry.register(mock_index)

    water_index = SpectralIndex(
        short_name="TEST_NDWI",
        long_name="Test Water Index",
        category="water",
        required_bands=("green", "nir"),
        formula_str="(green - nir) / (green + nir)",
        compute_fn=dummy_compute,
    )
    registry.register(water_index)

    assert registry.list() == ["TEST_NDVI", "TEST_NDWI"]
    assert registry.list(category="vegetation") == ["TEST_NDVI"]
    assert registry.list(category="water") == ["TEST_NDWI"]
    assert registry.list(category="soil") == []


def test_registry_filter_by_bands(mock_index: SpectralIndex) -> None:
    registry = IndexRegistry()
    registry.register(mock_index)  # requires nir, red

    water_index = SpectralIndex(
        short_name="TEST_NDWI",
        long_name="Test Water Index",
        category="water",
        required_bands=("green", "nir"),
        formula_str="(green - nir) / (green + nir)",
        compute_fn=dummy_compute,
    )
    registry.register(water_index)

    # Only red and green available: neither should match
    assert registry.filter_by_bands(["red", "green"]) == []

    # NIR and Red available: TEST_NDVI should match
    assert registry.filter_by_bands(["nir", "red"]) == ["TEST_NDVI"]

    # NIR, Red and Green available: both should match
    assert registry.filter_by_bands(["nir", "red", "green"]) == ["TEST_NDVI", "TEST_NDWI"]
