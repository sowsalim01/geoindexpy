"""Result container for computed spectral indices with statistics and spatial export."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Union
import numpy as np
from geoindexpy.raster.metadata import RasterMetadata


@dataclass
class IndexResult:
    """Encapsulates the calculation output of a spectral index.

    Attributes
    ----------
    index_name : str
        Short acronym of the computed index (e.g. 'NDVI').
    data : np.ndarray
        Computed index values (typically 2D [H, W] or 3D [bands, H, W]).
    metadata : RasterMetadata or None
        Associated georeferencing metadata (CRS, transform, resolution, etc.).
    params : dict[str, Any]
        Parameters and hyperparameters applied during calculation.
    """

    index_name: str
    data: np.ndarray
    metadata: Optional[RasterMetadata] = None
    params: Dict[str, Any] = field(default_factory=dict)

    @property
    def shape(self) -> tuple[int, ...]:
        return self.data.shape

    @property
    def dtype(self) -> np.dtype:
        return self.data.dtype

    def to_numpy(self) -> np.ndarray:
        """Return the underlying raw NumPy array."""
        return self.data

    def summary(self) -> Dict[str, Any]:
        """Compute statistical summary of the valid pixels in the index result.

        Returns
        -------
        dict[str, Any]
            Statistical metrics: min, max, mean, median, std, total_pixels,
            valid_pixels, nodata_pixels, nodata_percentage, percentiles (p10, p25, p75, p90).
        """
        arr = self.data
        total_pixels = int(arr.size)

        # Identify valid pixels (finite and not equal to nodata if nodata defined)
        valid_mask = np.isfinite(arr)
        if self.metadata is not None and self.metadata.nodata is not None:
            valid_mask = valid_mask & (arr != self.metadata.nodata)

        valid_count = int(np.count_nonzero(valid_mask))
        nodata_count = total_pixels - valid_count
        nodata_pct = (nodata_count / total_pixels * 100.0) if total_pixels > 0 else 0.0

        if valid_count == 0:
            return {
                "index": self.index_name,
                "total_pixels": total_pixels,
                "valid_pixels": 0,
                "nodata_pixels": total_pixels,
                "nodata_percentage": nodata_pct,
                "min": None,
                "max": None,
                "mean": None,
                "median": None,
                "std": None,
                "p10": None,
                "p25": None,
                "p75": None,
                "p90": None,
            }

        valid_values = arr[valid_mask]
        p10, p25, p75, p90 = np.percentile(valid_values, [10, 25, 75, 90])

        return {
            "index": self.index_name,
            "total_pixels": total_pixels,
            "valid_pixels": valid_count,
            "nodata_pixels": nodata_count,
            "nodata_percentage": round(nodata_pct, 2),
            "min": float(np.min(valid_values)),
            "max": float(np.max(valid_values)),
            "mean": float(np.mean(valid_values)),
            "median": float(np.median(valid_values)),
            "std": float(np.std(valid_values)),
            "p10": float(p10),
            "p25": float(p25),
            "p75": float(p75),
            "p90": float(p90),
        }

    def save(
        self,
        output_path: Union[str, Path],
        nodata: float = -9999.0,
        compress: str = "deflate",
    ) -> None:
        """Save the index result as a georeferenced GeoTIFF raster file.

        Parameters
        ----------
        output_path : str or Path
            Destination filepath.
        nodata : float, optional
            NoData fill value for non-finite pixels. Default is -9999.0.
        compress : str, optional
            Compression algorithm ('deflate', 'lzw', 'none'). Default is 'deflate'.

        Raises
        ------
        ValueError
            If the result does not contain georeferencing metadata.
        """
        import rasterio

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Prepare 2D output array
        arr = self.data.copy()
        if arr.ndim == 3 and arr.shape[0] == 1:
            arr = arr[0]

        h, w = arr.shape
        fill_mask = ~np.isfinite(arr)
        arr[fill_mask] = nodata

        profile = {
            "driver": "GTiff",
            "height": h,
            "width": w,
            "count": 1,
            "dtype": "float32",
            "nodata": nodata,
            "compress": compress,
        }

        if self.metadata is not None:
            if self.metadata.crs is not None:
                profile["crs"] = self.metadata.crs
            if self.metadata.transform is not None:
                profile["transform"] = self.metadata.transform

        with rasterio.open(str(path), "w", **profile) as dst:
            dst.write(arr.astype(np.float32), 1)
            dst.set_band_description(1, self.index_name)

    def __repr__(self) -> str:
        s = self.summary()
        stats_str = (
            f"min={s['min']:.3f}, max={s['max']:.3f}, mean={s['mean']:.3f}"
            if s["min"] is not None
            else "empty"
        )
        return f"<IndexResult [{self.index_name}]: shape={self.shape}, dtype={self.dtype}, {stats_str}>"
