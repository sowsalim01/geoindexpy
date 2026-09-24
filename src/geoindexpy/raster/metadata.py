"""Geospatial raster metadata container and utilities."""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import affine
import rasterio.crs


@dataclass(frozen=True)
class RasterMetadata:
    """Georeferencing and grid properties of a spatial raster.

    Attributes
    ----------
    crs : rasterio.crs.CRS or None
        Coordinate Reference System.
    transform : affine.Affine or None
        Affine geotransform matrix mapping pixel coordinates to spatial coordinates.
    width : int
        Number of pixel columns.
    height : int
        Number of pixel rows.
    count : int
        Number of bands in the source raster.
    dtype : str
        Data type representation (e.g. 'float32', 'uint16').
    nodata : float or None
        NoData value indicator.
    band_names : tuple[str, ...]
        Descriptions or role names assigned to bands (e.g. ('B02', 'B03', 'B04', 'B08')).
    """

    width: int
    height: int
    count: int = 1
    crs: Optional[Any] = None
    transform: Optional[affine.Affine] = None
    dtype: str = "float32"
    nodata: Optional[float] = None
    band_names: Tuple[str, ...] = ()

    @property
    def resolution(self) -> Optional[Tuple[float, float]]:
        """Return the spatial pixel resolution (abs(res_x), abs(res_y))."""
        if self.transform is not None:
            return (abs(self.transform.a), abs(self.transform.e))
        return None

    def to_profile(self, **overrides: Any) -> Dict[str, Any]:
        """Generate a rasterio profile dictionary suitable for dataset creation."""
        profile: Dict[str, Any] = {
            "driver": "GTiff",
            "width": self.width,
            "height": self.height,
            "count": self.count,
            "dtype": self.dtype,
            "crs": self.crs,
            "transform": self.transform,
            "nodata": self.nodata,
        }
        profile.update(overrides)
        return profile
