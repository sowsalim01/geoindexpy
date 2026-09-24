"""Water spectral indices implementations (NDWI, MNDWI)."""

import numpy as np
from geoindexpy.core.model import SpectralIndex
from geoindexpy.core.registry import get_registry
from geoindexpy.utils.math import ArrayLike, safe_divide


def compute_ndwi(green: ArrayLike, nir: ArrayLike) -> np.ndarray:
    """Calculate McFeeters' Normalized Difference Water Index (NDWI, 1996).

    Formula:
        NDWI = (GREEN - NIR) / (GREEN + NIR)
    """
    green_arr = np.asanyarray(green)
    nir_arr = np.asanyarray(nir)
    return safe_divide(green_arr - nir_arr, green_arr + nir_arr, fill_value=np.nan)


def compute_mndwi(green: ArrayLike, swir: ArrayLike) -> np.ndarray:
    """Calculate Modified Normalized Difference Water Index (MNDWI, Xu 2006).

    Formula:
        MNDWI = (GREEN - SWIR) / (GREEN + SWIR)

    Parameters
    ----------
    green : ArrayLike
        Green band reflectance.
    swir : ArrayLike
        Shortwave Infrared band (SWIR1, ~1.6 µm) reflectance.
    """
    green_arr = np.asanyarray(green)
    swir_arr = np.asanyarray(swir)
    return safe_divide(green_arr - swir_arr, green_arr + swir_arr, fill_value=np.nan)


# Definitions
NDWI_INDEX = SpectralIndex(
    short_name="NDWI",
    long_name="Normalized Difference Water Index",
    category="water",
    required_bands=("green", "nir"),
    formula_str="(green - nir) / (green + nir)",
    compute_fn=compute_ndwi,
    reference="McFeeters, S. K. (1996). The use of the Normalized Difference Water Index (NDWI) in the delineation of open water features. International Journal of Remote Sensing, 17(7), 1425-1432.",
    valid_range=(-1.0, 1.0),
)

MNDWI_INDEX = SpectralIndex(
    short_name="MNDWI",
    long_name="Modified Normalized Difference Water Index",
    category="water",
    required_bands=("green", "swir"),
    formula_str="(green - swir) / (green + swir)",
    compute_fn=compute_mndwi,
    reference="Xu, H. (2006). Modification of normalised difference water index (NDWI) to enhance open water features in remotely sensed imagery. International Journal of Remote Sensing, 27(14), 3025-3033.",
    valid_range=(-1.0, 1.0),
)

# Register globally
registry = get_registry()
registry.register(NDWI_INDEX, overwrite=True)
registry.register(MNDWI_INDEX, overwrite=True)
