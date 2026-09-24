"""Input/Output operations for spatial rasters via Rasterio."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union
import numpy as np
import rasterio

from geoindexpy.exceptions import InvalidRasterError
from geoindexpy.raster.metadata import RasterMetadata


@dataclass
class RasterDataset:
    """In-memory spatial raster containing bands and georeferencing metadata.

    Attributes
    ----------
    bands : dict[str, np.ndarray]
        Dictionary mapping band names (e.g. 'B02', 'B04', 'nir') to 2D numpy arrays.
    metadata : RasterMetadata
        Geospatial metadata (CRS, transform, resolution, etc.).
    """

    bands: Dict[str, np.ndarray]
    metadata: RasterMetadata

    def __getitem__(self, key: str) -> np.ndarray:
        return self.bands[key]

    def __contains__(self, key: str) -> bool:
        return key in self.bands

    def band_names(self) -> List[str]:
        return list(self.bands.keys())

    @property
    def shape(self) -> tuple[int, int]:
        return (self.metadata.height, self.metadata.width)


def open_raster(
    filepath: Union[str, Path],
    band_names: Optional[Sequence[str]] = None,
) -> RasterDataset:
    """Open and load a geospatial raster file into memory.

    Parameters
    ----------
    filepath : str or Path
        Path to the raster dataset (e.g. GeoTIFF).
    band_names : Sequence[str], optional
        Custom band names to assign to the raster bands (1-to-1 mapping with file bands).
        If omitted, attempts to read band descriptions from the raster metadata,
        falling back to ['B1', 'B2', ...] or ['B01', 'B02', ...].

    Returns
    -------
    RasterDataset
        Loaded raster dataset with bands dict and spatial metadata.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    InvalidRasterError
        If the raster is corrupted or has invalid dimensions.
    """
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"Raster file not found: {path}")

    try:
        with rasterio.open(str(path)) as src:
            count = src.count
            if count == 0:
                raise InvalidRasterError(f"Raster '{path}' has 0 bands.")

            # Determine band names
            names: List[str] = []
            if band_names is not None:
                if len(band_names) != count:
                    raise InvalidRasterError(
                        f"Custom band_names length ({len(band_names)}) does not match raster band count ({count})."
                    )
                names = list(band_names)
            else:
                for b_idx in range(1, count + 1):
                    desc = src.descriptions[b_idx - 1]
                    if desc and desc.strip():
                        names.append(desc.strip())
                    else:
                        names.append(f"B{b_idx}")

            # Read all bands as float32 to avoid precision issues
            raw_data = src.read(out_dtype=np.float32)  # shape (count, height, width)

            bands_dict: Dict[str, np.ndarray] = {}
            for i, name in enumerate(names):
                bands_dict[name] = raw_data[i]

            meta = RasterMetadata(
                width=src.width,
                height=src.height,
                count=count,
                crs=src.crs,
                transform=src.transform,
                dtype=str(src.dtypes[0]),
                nodata=float(src.nodata) if src.nodata is not None else None,
                band_names=tuple(names),
            )

            return RasterDataset(bands=bands_dict, metadata=meta)

    except rasterio.errors.RasterioError as e:
        raise InvalidRasterError(f"Failed to read raster file '{path}': {e}") from e


def write_raster(
    output_path: Union[str, Path],
    data: np.ndarray,
    metadata: Optional[RasterMetadata] = None,
    nodata: float = -9999.0,
    band_name: str = "",
) -> None:
    """Write an array to a georeferenced GeoTIFF raster file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    arr = np.asanyarray(data, dtype=np.float32)
    if arr.ndim == 2:
        count = 1
        h, w = arr.shape
        write_arr = arr[np.newaxis, :, :]
    elif arr.ndim == 3:
        count, h, w = arr.shape
        write_arr = arr
    else:
        raise InvalidRasterError(f"Data must be 2D or 3D, got {arr.ndim}D array.")

    profile: Dict[str, Any] = {
        "driver": "GTiff",
        "height": h,
        "width": w,
        "count": count,
        "dtype": "float32",
        "nodata": nodata,
        "compress": "deflate",
    }

    if metadata is not None:
        if metadata.crs is not None:
            profile["crs"] = metadata.crs
        if metadata.transform is not None:
            profile["transform"] = metadata.transform

    with rasterio.open(str(path), "w", **profile) as dst:
        dst.write(write_arr)
        if band_name:
            dst.set_band_description(1, band_name)
