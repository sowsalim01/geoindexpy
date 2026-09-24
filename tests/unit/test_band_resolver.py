"""Unit tests for BandResolver and sensor profiles."""

import numpy as np
import pytest
from geoindexpy.bands.resolver import BandResolver, extract_band_arrays
from geoindexpy.bands.sensors import get_sensor_band_map, list_supported_sensors
from geoindexpy.exceptions import (
    AmbiguousBandError,
    MissingBandError,
    UnsupportedSensorError,
)


def test_supported_sensors_list() -> None:
    sensors = list_supported_sensors()
    assert "sentinel2" in sensors
    assert "landsat8" in sensors
    assert "landsat9" in sensors


def test_get_sensor_band_map() -> None:
    s2 = get_sensor_band_map("sentinel2")
    assert s2["nir"] == "B08"
    assert s2["red"] == "B04"

    # Test alias
    s2_alias = get_sensor_band_map("s2")
    assert s2_alias["nir"] == "B08"

    with pytest.raises(UnsupportedSensorError):
        get_sensor_band_map("UNKNOWN_SENSOR_XYZ")


def test_resolver_exact_match() -> None:
    resolver = BandResolver(available_band_names=["NIR", "Red", "Green"])
    assert resolver.resolve("nir") == "NIR"
    assert resolver.resolve("red") == "Red"


def test_resolver_synonyms() -> None:
    resolver = BandResolver(available_band_names=["B08", "B04", "B03"])
    assert resolver.resolve("nir") == "B08"
    assert resolver.resolve("red") == "B04"
    assert resolver.resolve("green") == "B03"


def test_resolver_explicit_mapping() -> None:
    available = ["Channel_8", "Channel_4"]
    mapping = {"nir": "Channel_8", "red": "Channel_4"}
    resolver = BandResolver(available_band_names=available, band_mapping=mapping)
    assert resolver.resolve("nir") == "Channel_8"
    assert resolver.resolve("red") == "Channel_4"


def test_resolver_missing_band() -> None:
    resolver = BandResolver(available_band_names=["B04", "B03"])
    with pytest.raises(MissingBandError) as exc_info:
        resolver.resolve("nir")
    assert "nir" in str(exc_info.value)


def test_resolver_ambiguity_raises_error() -> None:
    # If both B08 and B8 are present, or multiple synonyms match
    resolver = BandResolver(available_band_names=["B08", "B8"])
    with pytest.raises(AmbiguousBandError) as exc_info:
        resolver.resolve("nir")
    assert "nir" in str(exc_info.value)
    assert "B08" in str(exc_info.value)


def test_extract_band_arrays() -> None:
    bands = {
        "B08": np.array([0.7, 0.8]),
        "B04": np.array([0.1, 0.2]),
    }
    extracted = extract_band_arrays(
        bands_source=bands,
        required_roles=["nir", "red"],
        sensor="sentinel2",
    )
    assert "nir" in extracted
    assert "red" in extracted
    assert np.allclose(extracted["nir"], [0.7, 0.8])
    assert np.allclose(extracted["red"], [0.1, 0.2])
