"""Pytest fixtures for GeoIndexPy test suite."""

import os

for proj_var in ("PROJ_LIB", "PROJ_DATA"):
    val = os.environ.get(proj_var, "")
    if val and ("postgres" in val.lower() or not os.path.exists(os.path.join(val, "proj.db"))):
        os.environ.pop(proj_var, None)

import numpy as np
import pytest


@pytest.fixture
def synthetic_bands_2d() -> dict[str, np.ndarray]:
    """Provide a dictionary of synthetic 2D spectral bands (4x4 pixels, float32).

    Simulates reflectance values scaled between 0.0 and 1.0:
    - Pixel (0, 0): Typical dense healthy vegetation (high NIR, low Red, low Blue)
    - Pixel (0, 1): Water surface (high Green/Blue, very low NIR/SWIR)
    - Pixel (0, 2): Bare soil / Urban (high SWIR/Red, moderate NIR)
    - Pixel (0, 3): Cloud / Bright surface
    """
    blue = np.array([
        [0.02, 0.20, 0.12, 0.80],
        [0.03, 0.18, 0.14, 0.85],
        [0.02, 0.15, 0.11, 0.78],
        [0.04, 0.19, 0.13, 0.82],
    ], dtype=np.float32)

    green = np.array([
        [0.05, 0.35, 0.15, 0.82],
        [0.06, 0.32, 0.16, 0.87],
        [0.05, 0.30, 0.14, 0.80],
        [0.07, 0.34, 0.17, 0.84],
    ], dtype=np.float32)

    red = np.array([
        [0.03, 0.10, 0.25, 0.85],
        [0.04, 0.09, 0.26, 0.89],
        [0.03, 0.08, 0.24, 0.83],
        [0.05, 0.11, 0.27, 0.86],
    ], dtype=np.float32)

    nir = np.array([
        [0.70, 0.05, 0.30, 0.90],
        [0.68, 0.04, 0.32, 0.92],
        [0.65, 0.03, 0.28, 0.88],
        [0.72, 0.06, 0.31, 0.91],
    ], dtype=np.float32)

    swir1 = np.array([
        [0.10, 0.02, 0.45, 0.90],
        [0.12, 0.01, 0.48, 0.91],
        [0.09, 0.01, 0.42, 0.87],
        [0.11, 0.02, 0.46, 0.92],
    ], dtype=np.float32)

    swir2 = np.array([
        [0.05, 0.01, 0.35, 0.88],
        [0.06, 0.01, 0.38, 0.90],
        [0.04, 0.00, 0.32, 0.85],
        [0.05, 0.01, 0.36, 0.89],
    ], dtype=np.float32)

    return {
        "blue": blue,
        "green": green,
        "red": red,
        "nir": nir,
        "swir1": swir1,
        "swir2": swir2,
    }
