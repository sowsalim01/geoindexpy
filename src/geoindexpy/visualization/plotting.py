"""Lightweight visualization utilities for spectral index results."""

from pathlib import Path
from typing import Any, Optional, Union
import numpy as np
from geoindexpy.core.result import IndexResult

# Default scientific colormaps per index category
DEFAULT_COLORMAPS = {
    "NDVI": "RdYlGn",
    "SAVI": "RdYlGn",
    "EVI": "RdYlGn",
    "GNDVI": "RdYlGn",
    "NDWI": "Blues",
    "MNDWI": "Blues",
    "NDBI": "YlOrRd",
    "NDMI": "YlGnBu",
    "BSI": "YlOrBr",
}


def plot_index(
    result: Union[IndexResult, np.ndarray],
    title: Optional[str] = None,
    cmap: Optional[str] = None,
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    colorbar: bool = True,
    save_path: Optional[Union[str, Path]] = None,
    show: bool = False,
) -> Any:
    """Plot a spectral index raster using matplotlib.

    Parameters
    ----------
    result : IndexResult or np.ndarray
        Computed index result or 2D NumPy array.
    title : str, optional
        Custom title for the plot.
    cmap : str, optional
        Matplotlib colormap name. If None, selects a thematic colormap based on the index name.
    vmin : float, optional
        Minimum value for color scaling (default: -1.0 or array min).
    vmax : float, optional
        Maximum value for color scaling (default: 1.0 or array max).
    colorbar : bool, optional
        Whether to display the colorbar. Default is True.
    save_path : str or Path, optional
        If provided, saves the figure to the specified path.
    show : bool, optional
        Whether to call plt.show(). Default is False.

    Returns
    -------
    matplotlib.figure.Figure
        The created matplotlib figure.

    Raises
    ------
    ImportError
        If matplotlib is not installed.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise ImportError(
            "Visualization requires 'matplotlib'. Install it using: pip install 'geoindexpy[viz]'"
        ) from e

    if isinstance(result, IndexResult):
        arr = result.data
        idx_name = result.index_name
    else:
        arr = np.asanyarray(result)
        idx_name = "Spectral Index"

    if arr.ndim == 3 and arr.shape[0] == 1:
        arr = arr[0]

    if cmap is None:
        cmap = DEFAULT_COLORMAPS.get(idx_name.upper(), "viridis")

    if vmin is None:
        vmin = -1.0 if "ND" in idx_name.upper() else float(np.nanmin(arr))
    if vmax is None:
        vmax = 1.0 if "ND" in idx_name.upper() else float(np.nanmax(arr))

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(arr, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_title(title or f"{idx_name} Map")
    ax.axis("off")

    if colorbar:
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label=idx_name)

    if save_path:
        out_p = Path(save_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_p, bbox_inches="tight", dpi=300)

    if show:
        plt.show()

    return fig
