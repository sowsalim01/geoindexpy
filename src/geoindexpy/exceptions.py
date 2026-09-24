"""Custom exceptions hierarchy for GeoIndexPy."""

from typing import Iterable, Optional


class GeoIndexError(Exception):
    """Base exception for all errors raised by GeoIndexPy."""


class IndexNotFoundError(GeoIndexError):
    """Raised when a requested spectral index does not exist in the registry."""

    def __init__(self, index_name: str, available_indices: Optional[Iterable[str]] = None) -> None:
        self.index_name = index_name
        self.available_indices = list(available_indices) if available_indices else []
        msg = f"Spectral index '{index_name}' was not found in the registry."
        if self.available_indices:
            msg += f" Available indices are: {', '.join(sorted(self.available_indices))}."
        super().__init__(msg)


class MissingBandError(GeoIndexError):
    """Raised when one or more bands required by an index are missing from the input."""

    def __init__(
        self,
        index_name: str,
        missing_bands: Iterable[str],
        available_bands: Optional[Iterable[str]] = None,
    ) -> None:
        self.index_name = index_name
        self.missing_bands = list(missing_bands)
        self.available_bands = list(available_bands) if available_bands else []
        msg = (
            f"Index '{index_name}' cannot be computed because the following required band(s) "
            f"are missing: {', '.join(self.missing_bands)}."
        )
        if self.available_bands:
            msg += f" Available band(s): {', '.join(self.available_bands)}."
        super().__init__(msg)


class AmbiguousBandError(GeoIndexError):
    """Raised when automatic band resolution finds multiple candidates for a standard band name."""

    def __init__(self, band_name: str, candidates: Iterable[str]) -> None:
        self.band_name = band_name
        self.candidates = list(candidates)
        msg = (
            f"Multiple candidate bands match standard role '{band_name}': {', '.join(self.candidates)}. "
            "Please provide an explicit band mapping to resolve ambiguity."
        )
        super().__init__(msg)


class InvalidRasterError(GeoIndexError):
    """Raised when an input raster is malformed, has incompatible dimensions or unsupported format."""


class IncompatibleRasterError(GeoIndexError):
    """Raised when bands or rasters in a multi-band calculation have mismatching shapes, CRS or transform."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Incompatible rasters: {detail}")


class InvalidParameterError(GeoIndexError):
    """Raised when an invalid parameter or out-of-range value is supplied to an index calculation."""

    def __init__(self, param_name: str, value: object, reason: str = "") -> None:
        self.param_name = param_name
        self.value = value
        msg = f"Invalid value '{value}' for parameter '{param_name}'."
        if reason:
            msg += f" {reason}"
        super().__init__(msg)


class UnsupportedSensorError(GeoIndexError):
    """Raised when a specified sensor name is not recognized or not supported."""

    def __init__(self, sensor: str, supported_sensors: Optional[Iterable[str]] = None) -> None:
        self.sensor = sensor
        self.supported_sensors = list(supported_sensors) if supported_sensors else []
        msg = f"Unsupported sensor '{sensor}'."
        if self.supported_sensors:
            msg += f" Supported sensors are: {', '.join(sorted(self.supported_sensors))}."
        super().__init__(msg)
