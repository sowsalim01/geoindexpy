"""Urban and built-up spectral indices implementations."""

import numpy as np
from geoindexpy.core.model import SpectralIndex
from geoindexpy.core.registry import get_registry
from geoindexpy.utils.math import ArrayLike, safe_divide


def compute_ndbi(swir: ArrayLike, nir: ArrayLike) -> np.ndarray:
    """Calculate the Normalized Difference Built-Up Index (NDBI).

    Formula:
        NDBI = (SWIR - NIR) / (SWIR + NIR)

    Parameters
    ----------
    swir : ArrayLike
        Shortwave Infrared band (typically SWIR1, ~1.6 µm) reflectance.
    nir : ArrayLike
        Near-Infrared band reflectance.

    Returns
    -------
    np.ndarray
        Computed NDBI values, with zero-denominator replaced by np.nan.
    """
    swir_arr = np.asanyarray(swir)
    nir_arr = np.asanyarray(nir)
    numerator = swir_arr - nir_arr
    denominator = swir_arr + nir_arr
    return safe_divide(numerator, denominator, fill_value=np.nan)


# Scientific index definition
NDBI_INDEX = SpectralIndex(
    short_name="NDBI",
    long_name="Normalized Difference Built-Up Index",
    category="urban",
    required_bands=("swir", "nir"),
    formula_str="(swir - nir) / (swir + nir)",
    compute_fn=compute_ndbi,
    reference="Zha, Y., Gao, J., & Ni, S. (2003). Use of normalized difference built-up index in automatically mapping urban areas from TM imagery. International Journal of Remote Sensing, 24(3), 583-594.",
    valid_range=(-1.0, 1.0),
    version="1.0.0",
)

# Register globally
get_registry().register(NDBI_INDEX, overwrite=True)
