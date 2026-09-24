"""Soil and bare ground spectral indices (BSI)."""

import numpy as np
from geoindexpy.core.model import SpectralIndex
from geoindexpy.core.registry import get_registry
from geoindexpy.utils.math import ArrayLike, safe_divide


def compute_bsi(swir: ArrayLike, red: ArrayLike, nir: ArrayLike, blue: ArrayLike) -> np.ndarray:
    """Calculate the Bare Soil Index (BSI, Rikimaru et al. 2002).

    Formula:
        BSI = ((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))

    Parameters
    ----------
    swir : ArrayLike
        Shortwave Infrared band (SWIR1, ~1.6 µm) reflectance.
    red : ArrayLike
        Red band reflectance.
    nir : ArrayLike
        Near-Infrared band reflectance.
    blue : ArrayLike
        Blue band reflectance.
    """
    swir_arr = np.asanyarray(swir)
    red_arr = np.asanyarray(red)
    nir_arr = np.asanyarray(nir)
    blue_arr = np.asanyarray(blue)

    term1 = swir_arr + red_arr
    term2 = nir_arr + blue_arr

    num = term1 - term2
    den = term1 + term2
    return safe_divide(num, den, fill_value=np.nan)


BSI_INDEX = SpectralIndex(
    short_name="BSI",
    long_name="Bare Soil Index",
    category="soil",
    required_bands=("swir", "red", "nir", "blue"),
    formula_str="((swir + red) - (nir + blue)) / ((swir + red) + (nir + blue))",
    compute_fn=compute_bsi,
    reference="Rikimaru, A., Roy, P. S., & Miyatake, S. (2002). Tropical forest cover density mapping. Tropical Ecology, 43(1), 39-47.",
    valid_range=(-1.0, 1.0),
)

# Register globally
get_registry().register(BSI_INDEX, overwrite=True)
