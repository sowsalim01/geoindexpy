"""Sensor band mapping profiles for major Earth Observation satellites."""

from typing import Dict, List
from geoindexpy.exceptions import UnsupportedSensorError

# Standard spectral band aliases
SENSOR_PRESETS: Dict[str, Dict[str, str]] = {
    # Sentinel-2 MSI (MultiSpectral Instrument)
    "sentinel2": {
        "coastal": "B01",
        "blue": "B02",
        "green": "B03",
        "red": "B04",
        "rededge1": "B05",
        "rededge2": "B06",
        "rededge3": "B07",
        "nir": "B08",
        "narrow_nir": "B8A",
        "watervapour": "B09",
        "swir1": "B11",
        "swir2": "B12",
        "swir": "B11",  # default alias for single SWIR
    },
    # Landsat 8 and Landsat 9 OLI / TIRS
    "landsat8": {
        "coastal": "B1",
        "blue": "B2",
        "green": "B3",
        "red": "B4",
        "nir": "B5",
        "swir1": "B6",
        "swir2": "B7",
        "pan": "B8",
        "cirrus": "B9",
        "tirs1": "B10",
        "tirs2": "B11",
        "swir": "B6",
    },
    "landsat9": {
        "coastal": "B1",
        "blue": "B2",
        "green": "B3",
        "red": "B4",
        "nir": "B5",
        "swir1": "B6",
        "swir2": "B7",
        "pan": "B8",
        "cirrus": "B9",
        "tirs1": "B10",
        "tirs2": "B11",
        "swir": "B6",
    },
    # Landsat 4, 5 TM and Landsat 7 ETM+
    "landsat5": {
        "blue": "B1",
        "green": "B2",
        "red": "B3",
        "nir": "B4",
        "swir1": "B5",
        "thermal": "B6",
        "swir2": "B7",
        "swir": "B5",
    },
    "landsat7": {
        "blue": "B1",
        "green": "B2",
        "red": "B3",
        "nir": "B4",
        "swir1": "B5",
        "thermal": "B6",
        "swir2": "B7",
        "pan": "B8",
        "swir": "B5",
    },
}

# Sensor name aliases (e.g. 's2', 'l8')
SENSOR_ALIASES: Dict[str, str] = {
    "s2": "sentinel2",
    "sentinel-2": "sentinel2",
    "sentinel2a": "sentinel2",
    "sentinel2b": "sentinel2",
    "l8": "landsat8",
    "landsat-8": "landsat8",
    "l9": "landsat9",
    "landsat-9": "landsat9",
    "l5": "landsat5",
    "landsat-5": "landsat5",
    "l7": "landsat7",
    "landsat-7": "landsat7",
}


def list_supported_sensors() -> List[str]:
    """Return the list of supported satellite sensors."""
    return sorted(SENSOR_PRESETS.keys())


def get_sensor_band_map(sensor_name: str) -> Dict[str, str]:
    """Retrieve standard band mapping dictionary for a given sensor.

    Parameters
    ----------
    sensor_name : str
        Name or alias of the sensor (e.g., 'sentinel2', 's2', 'landsat8').

    Returns
    -------
    dict[str, str]
        Mapping from standard role (e.g. 'nir') to sensor band name (e.g. 'B08').

    Raises
    ------
    UnsupportedSensorError
        If the sensor is not recognized.
    """
    key = sensor_name.strip().lower()
    canonical = SENSOR_ALIASES.get(key, key)
    if canonical not in SENSOR_PRESETS:
        raise UnsupportedSensorError(sensor_name, supported_sensors=list_supported_sensors())
    return dict(SENSOR_PRESETS[canonical])
