"""Vegetation spectral indices implementations (NDVI, SAVI, EVI, GNDVI)."""

import numpy as np
from geoindexpy.core.model import SpectralIndex
from geoindexpy.core.registry import get_registry
from geoindexpy.utils.math import ArrayLike, safe_divide


def compute_ndvi(nir: ArrayLike, red: ArrayLike) -> np.ndarray:
    """Calculate the Normalized Difference Vegetation Index (NDVI).

    Formula:
        NDVI = (NIR - RED) / (NIR + RED)
    """
    nir_arr = np.asanyarray(nir)
    red_arr = np.asanyarray(red)
    return safe_divide(nir_arr - red_arr, nir_arr + red_arr, fill_value=np.nan)


def compute_savi(nir: ArrayLike, red: ArrayLike, L: float = 0.5) -> np.ndarray:
    """Calculate the Soil-Adjusted Vegetation Index (SAVI, Huete 1988).

    Formula:
        SAVI = ((NIR - RED) / (NIR + RED + L)) * (1 + L)

    Parameters
    ----------
    nir : ArrayLike
        Near-Infrared band reflectance.
    red : ArrayLike
        Red band reflectance.
    L : float, optional
        Soil brightness correction factor. Default is 0.5.
    """
    nir_arr = np.asanyarray(nir)
    red_arr = np.asanyarray(red)
    num = nir_arr - red_arr
    den = nir_arr + red_arr + float(L)
    ratio = safe_divide(num, den, fill_value=np.nan)
    return ratio * (1.0 + float(L))


def compute_evi(
    nir: ArrayLike,
    red: ArrayLike,
    blue: ArrayLike,
    G: float = 2.5,
    C1: float = 6.0,
    C2: float = 7.5,
    L: float = 1.0,
) -> np.ndarray:
    """Calculate the Enhanced Vegetation Index (EVI, Huete et al. 2002).

    Formula:
        EVI = G * (NIR - RED) / (NIR + C1 * RED - C2 * BLUE + L)

    Parameters
    ----------
    nir : ArrayLike
        Near-Infrared band reflectance.
    red : ArrayLike
        Red band reflectance.
    blue : ArrayLike
        Blue band reflectance.
    G : float, optional
        Gain factor. Default is 2.5.
    C1 : float, optional
        Atmosphere resistance aerosol correction coefficient 1. Default is 6.0.
    C2 : float, optional
        Atmosphere resistance aerosol correction coefficient 2. Default is 7.5.
    L : float, optional
        Canopy background adjustment factor. Default is 1.0.
    """
    nir_arr = np.asanyarray(nir)
    red_arr = np.asanyarray(red)
    blue_arr = np.asanyarray(blue)

    num = float(G) * (nir_arr - red_arr)
    den = nir_arr + (float(C1) * red_arr) - (float(C2) * blue_arr) + float(L)
    return safe_divide(num, den, fill_value=np.nan)


def compute_gndvi(nir: ArrayLike, green: ArrayLike) -> np.ndarray:
    """Calculate the Green Normalized Difference Vegetation Index (GNDVI, Gitelson 1996).

    Formula:
        GNDVI = (NIR - GREEN) / (NIR + GREEN)
    """
    nir_arr = np.asanyarray(nir)
    green_arr = np.asanyarray(green)
    return safe_divide(nir_arr - green_arr, nir_arr + green_arr, fill_value=np.nan)


# Definitions
NDVI_INDEX = SpectralIndex(
    short_name="NDVI",
    long_name="Normalized Difference Vegetation Index",
    category="vegetation",
    required_bands=("nir", "red"),
    formula_str="(nir - red) / (nir + red)",
    compute_fn=compute_ndvi,
    reference="Rouse, J. W., Haas, R. H., Schell, J. A., & Deering, D. W. (1974). Monitoring the vernal advancement and retrogradation (Green wave effect) of natural vegetation. NASA/GSFC Final Report, 371.",
    valid_range=(-1.0, 1.0),
)

SAVI_INDEX = SpectralIndex(
    short_name="SAVI",
    long_name="Soil-Adjusted Vegetation Index",
    category="vegetation",
    required_bands=("nir", "red"),
    formula_str="((nir - red) / (nir + red + L)) * (1 + L)",
    compute_fn=compute_savi,
    default_params={"L": 0.5},
    reference="Huete, A. R. (1988). A soil-adjusted vegetation index (SAVI). Remote Sensing of Environment, 25(3), 295-309.",
    valid_range=(-1.0, 1.5),
)

EVI_INDEX = SpectralIndex(
    short_name="EVI",
    long_name="Enhanced Vegetation Index",
    category="vegetation",
    required_bands=("nir", "red", "blue"),
    formula_str="G * (nir - red) / (nir + C1 * red - C2 * blue + L)",
    compute_fn=compute_evi,
    default_params={"G": 2.5, "C1": 6.0, "C2": 7.5, "L": 1.0},
    reference="Huete, A., Didan, K., Miura, T., Rodriguez, E. P., Gao, X., & Ferreira, L. G. (2002). Overview of the radiometric and biophysical performance of the MODIS vegetation indices. Remote Sensing of Environment, 83(1-2), 195-213.",
    valid_range=(-1.0, 1.0),
)

GNDVI_INDEX = SpectralIndex(
    short_name="GNDVI",
    long_name="Green Normalized Difference Vegetation Index",
    category="vegetation",
    required_bands=("nir", "green"),
    formula_str="(nir - green) / (nir + green)",
    compute_fn=compute_gndvi,
    reference="Gitelson, A. A., Kaufman, Y. J., & Merzlyak, M. N. (1996). Use of a green channel in remote sensing of global vegetation from EOS-MODIS. Remote Sensing of Environment, 58(3), 289-298.",
    valid_range=(-1.0, 1.0),
)

# Register globally
registry = get_registry()
registry.register(NDVI_INDEX, overwrite=True)
registry.register(SAVI_INDEX, overwrite=True)
registry.register(EVI_INDEX, overwrite=True)
registry.register(GNDVI_INDEX, overwrite=True)
