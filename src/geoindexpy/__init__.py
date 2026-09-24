import os
import sys

# Proactive protection: On systems where external software (e.g. PostgreSQL/PostGIS)
# defines a global PROJ_LIB or PROJ_DATA incompatible with rasterio's PROJ wheel,
# clean up the environment so rasterio safely uses its bundled PROJ database.
for proj_var in ("PROJ_LIB", "PROJ_DATA"):
    val = os.environ.get(proj_var, "")
    if val and ("postgres" in val.lower() or not os.path.exists(os.path.join(val, "proj.db"))):
        os.environ.pop(proj_var, None)

from geoindexpy.core.engine import calculate_all, calculate_index, calculate_indices
from geoindexpy.core.model import SpectralIndex
from geoindexpy.core.registry import IndexRegistry, get_registry
from geoindexpy.core.result import IndexResult
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
# Load all default index definitions into registry
import geoindexpy.indices
from geoindexpy.indices.moisture import compute_ndmi
from geoindexpy.indices.soil import compute_bsi
from geoindexpy.indices.urban import compute_ndbi
from geoindexpy.indices.vegetation import (
    compute_evi,
    compute_gndvi,
    compute_ndvi,
    compute_savi,
)
from geoindexpy.indices.water import compute_mndwi, compute_ndwi
from geoindexpy.raster.io import RasterDataset, open_raster, write_raster
from geoindexpy.raster.metadata import RasterMetadata
from geoindexpy.utils.math import ArrayLike, apply_scale, safe_divide
from geoindexpy.version import __version__, __version_info__
from geoindexpy.visualization.plotting import plot_index


# Direct functional API
def ndvi(nir: ArrayLike, red: ArrayLike) -> ArrayLike:
    """Calculate the Normalized Difference Vegetation Index (NDVI)."""
    return compute_ndvi(nir=nir, red=red)


def savi(nir: ArrayLike, red: ArrayLike, L: float = 0.5) -> ArrayLike:
    """Calculate the Soil-Adjusted Vegetation Index (SAVI, Huete 1988)."""
    return compute_savi(nir=nir, red=red, L=L)


def evi(
    nir: ArrayLike,
    red: ArrayLike,
    blue: ArrayLike,
    G: float = 2.5,
    C1: float = 6.0,
    C2: float = 7.5,
    L: float = 1.0,
) -> ArrayLike:
    """Calculate the Enhanced Vegetation Index (EVI, Huete et al. 2002)."""
    return compute_evi(nir=nir, red=red, blue=blue, G=G, C1=C1, C2=C2, L=L)


def gndvi(nir: ArrayLike, green: ArrayLike) -> ArrayLike:
    """Calculate the Green Normalized Difference Vegetation Index (GNDVI, Gitelson 1996)."""
    return compute_gndvi(nir=nir, green=green)


def ndwi(green: ArrayLike, nir: ArrayLike) -> ArrayLike:
    """Calculate the Normalized Difference Water Index (NDWI, McFeeters 1996)."""
    return compute_ndwi(green=green, nir=nir)


def mndwi(green: ArrayLike, swir: ArrayLike) -> ArrayLike:
    """Calculate the Modified Normalized Difference Water Index (MNDWI, Xu 2006)."""
    return compute_mndwi(green=green, swir=swir)


def ndbi(swir: ArrayLike, nir: ArrayLike) -> ArrayLike:
    """Calculate the Normalized Difference Built-Up Index (NDBI, Zha 2003)."""
    return compute_ndbi(swir=swir, nir=nir)


def ndmi(nir: ArrayLike, swir: ArrayLike) -> ArrayLike:
    """Calculate the Normalized Difference Moisture Index (NDMI, Gao 1996)."""
    return compute_ndmi(nir=nir, swir=swir)


def bsi(swir: ArrayLike, red: ArrayLike, nir: ArrayLike, blue: ArrayLike) -> ArrayLike:
    """Calculate the Bare Soil Index (BSI, Rikimaru et al. 2002)."""
    return compute_bsi(swir=swir, red=red, nir=nir, blue=blue)


def list_indices(category: str | None = None) -> list[str]:
    """List all registered spectral indices, optionally filtered by category."""
    return get_registry().list(category=category)


def get_index_info(name: str) -> dict[str, object]:
    """Get scientific metadata for a given spectral index."""
    return get_registry().info(name)


def summary(result: IndexResult | ArrayLike) -> dict[str, object]:
    """Compute summary statistics for an IndexResult or raw array."""
    if isinstance(result, IndexResult):
        return result.summary()
    arr = IndexResult(index_name="Custom", data=result)
    return arr.summary()


__all__ = [
    "__version__",
    "__version_info__",
    # Core API
    "calculate_index",
    "calculate_indices",
    "calculate_all",
    "list_indices",
    "get_index_info",
    "summary",
    # Direct indices API
    "ndvi",
    "savi",
    "evi",
    "gndvi",
    "ndwi",
    "mndwi",
    "ndbi",
    "ndmi",
    "bsi",
    # Visualization
    "plot_index",
    # Core types
    "SpectralIndex",
    "IndexRegistry",
    "IndexResult",
    "get_registry",
    # Raster layer
    "open_raster",
    "write_raster",
    "RasterDataset",
    "RasterMetadata",
    # Exceptions
    "GeoIndexError",
    "IndexNotFoundError",
    "MissingBandError",
    "AmbiguousBandError",
    "InvalidRasterError",
    "IncompatibleRasterError",
    "InvalidParameterError",
    "UnsupportedSensorError",
    # Math utilities
    "safe_divide",
    "apply_scale",
]
