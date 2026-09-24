"""Unit tests for GeoIndexPy exception hierarchy."""

import pytest
from geoindexpy.exceptions import (
    AmbiguousBandError,
    GeoIndexError,
    IncompatibleRasterError,
    IndexNotFoundError,
    InvalidParameterError,
    InvalidRasterError,
    MissingBandError,
    UnsupportedSensorError,
)


def test_exception_inheritance() -> None:
    """Ensure all custom exceptions inherit from GeoIndexError."""
    assert issubclass(IndexNotFoundError, GeoIndexError)
    assert issubclass(MissingBandError, GeoIndexError)
    assert issubclass(AmbiguousBandError, GeoIndexError)
    assert issubclass(InvalidRasterError, GeoIndexError)
    assert issubclass(IncompatibleRasterError, GeoIndexError)
    assert issubclass(InvalidParameterError, GeoIndexError)
    assert issubclass(UnsupportedSensorError, GeoIndexError)


def test_index_not_found_error_message() -> None:
    err = IndexNotFoundError("UNKNOWN", available_indices=["NDVI", "NDWI"])
    msg = str(err)
    assert "UNKNOWN" in msg
    assert "NDVI, NDWI" in msg


def test_missing_band_error_message() -> None:
    err = MissingBandError("NDVI", missing_bands=["nir"], available_bands=["red", "green"])
    msg = str(err)
    assert "NDVI" in msg
    assert "nir" in msg
    assert "red, green" in msg


def test_ambiguous_band_error_message() -> None:
    err = AmbiguousBandError("nir", candidates=["B08", "B8A"])
    msg = str(err)
    assert "nir" in msg
    assert "B08, B8A" in msg


def test_unsupported_sensor_error_message() -> None:
    err = UnsupportedSensorError("MODIS", supported_sensors=["sentinel2", "landsat8"])
    msg = str(err)
    assert "MODIS" in msg
    assert "landsat8, sentinel2" in msg
