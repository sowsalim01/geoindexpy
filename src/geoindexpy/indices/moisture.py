"""Moisture and vegetation water content indices (NDMI)."""

import numpy as np
from geoindexpy.core.model import SpectralIndex
from geoindexpy.core.registry import get_registry
from geoindexpy.utils.math import ArrayLike, safe_divide


def compute_ndmi(nir: ArrayLike, swir: ArrayLike) -> np.ndarray:
    """Calculate the Normalized Difference Moisture Index (NDMI, Gao 1996).

    Formula:
        NDMI = (NIR - SWIR) / (NIR + SWIR)

    Parameters
    ----------
    nir : ArrayLike
        Near-Infrared band reflectance.
    swir : ArrayLike
        Shortwave Infrared band (SWIR1, ~1.6 µm) reflectance.
    """
    nir_arr = np.asanyarray(nir)
    swir_arr = np.asanyarray(swir)
    return safe_divide(nir_arr - swir_arr, nir_arr + swir_arr, fill_value=np.nan)


NDMI_INDEX = SpectralIndex(
    short_name="NDMI",
    long_name="Normalized Difference Moisture Index",
    category="moisture",
    required_bands=("nir", "swir"),
    formula_str="(nir - swir) / (nir + swir)",
    compute_fn=compute_ndmi,
    reference="Gao, B. C. (1996). NDWI—A normalized difference water index for remote sensing of vegetation liquid water from space. Remote Sensing of Environment, 58(3), 257-266.",
    valid_range=(-1.0, 1.0),
)

# Register globally
get_registry().register(NDMI_INDEX, overwrite=True)
