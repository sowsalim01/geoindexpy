"""Execution engine for spectral and geospatial index calculations."""

from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Union
import numpy as np

from geoindexpy.bands.resolver import BandResolver, extract_band_arrays
from geoindexpy.core.registry import get_registry
from geoindexpy.core.result import IndexResult
from geoindexpy.exceptions import (
    IncompatibleRasterError,
    IndexNotFoundError,
    MissingBandError,
)
from geoindexpy.raster.io import RasterDataset, open_raster
from geoindexpy.raster.metadata import RasterMetadata

RasterInput = Union[RasterDataset, Mapping[str, Any], str, Path]


def _prepare_bands_and_metadata(
    source: RasterInput,
) -> tuple[Dict[str, np.ndarray], Optional[RasterMetadata]]:
    """Extract raw bands dictionary and metadata from diverse input types."""
    if isinstance(source, (str, Path)):
        ds = open_raster(source)
        return ds.bands, ds.metadata
    elif isinstance(source, RasterDataset):
        return source.bands, source.metadata
    elif isinstance(source, Mapping):
        bands: Dict[str, np.ndarray] = {
            str(k): np.asanyarray(v) for k, v in source.items()
        }
        return bands, None
    else:
        raise TypeError(
            f"Unsupported raster input type '{type(source).__name__}'. "
            "Expected RasterDataset, dict of arrays, or file path."
        )


def calculate_index(
    image: RasterInput,
    index: str,
    bands: Optional[Mapping[str, Union[str, int]]] = None,
    sensor: Optional[str] = None,
    params: Optional[Mapping[str, float]] = None,
) -> IndexResult:
    """Calculate a single spectral index on an input raster or band dictionary with explicit band mapping.

    Parameters
    ----------
    image : RasterDataset, Mapping[str, ArrayLike], str, or Path
        Input image, dictionary of band arrays, or raster filepath.
    index : str
        Short name of the index to calculate (e.g. 'NDVI', 'NDWI').
    bands : Mapping[str, Union[str, int]], optional
        Explicit mapping from standard role to band identifier.
        Supports both string names (e.g., {'nir': 'B08', 'red': 'B04'}) 
        and integer indices (e.g., {'nir': 4, 'red': 3}).
        This takes priority over sensor presets.
    sensor : str, optional
        Satellite sensor preset name (e.g. 'sentinel2', 'landsat8').
        Only used if no explicit band mapping is provided.
    params : Mapping[str, float], optional
        Custom index hyperparameters to override defaults (e.g. {'L': 0.5}).

    Returns
    -------
    IndexResult
        Result object with computed array, spatial metadata, and summary statistics.

    Raises
    ------
    MissingBandError
        If required bands are missing or explicit mapping points to non-existent bands.
    IncompatibleRasterError
        If bands have incompatible spatial dimensions.
    """
    registry = get_registry()
    index_def = registry.get(index)

    bands_dict, metadata = _prepare_bands_and_metadata(image)

    # Resolve required bands with explicit user mapping priority
    resolver = BandResolver(
        available_band_names=bands_dict.keys(),
        sensor=sensor,
        band_mapping=bands,
    )
    resolved_names = resolver.resolve_all(index_def.required_bands)

    # Extract arrays
    input_arrays: Dict[str, np.ndarray] = {}
    first_shape = None
    first_role = None

    for role, actual_name in resolved_names.items():
        arr = bands_dict[actual_name]
        if first_shape is None:
            first_shape = arr.shape
            first_role = role
        elif arr.shape != first_shape:
            raise IncompatibleRasterError(
                f"Shape mismatch between band '{first_role}' ({first_shape}) "
                f"and band '{role}' ({arr.shape}). All bands must have identical spatial dimensions."
            )
        input_arrays[role] = arr

    # Merge default params with user overrides
    applied_params = dict(index_def.default_params)
    if params:
        applied_params.update(params)

    # Execute pure vectorized scientific calculation
    calc_kwargs = {**input_arrays, **applied_params}
    result_data = index_def.compute_fn(**calc_kwargs)

    return IndexResult(
        index_name=index_def.short_name,
        data=result_data,
        metadata=metadata,
        params=applied_params,
    )


def calculate_indices(
    image: RasterInput,
    indices: Sequence[str],
    bands: Optional[Mapping[str, Union[str, int]]] = None,
    sensor: Optional[str] = None,
    params: Optional[Mapping[str, Mapping[str, float]]] = None,
) -> Dict[str, IndexResult]:
    """Calculate multiple spectral indices simultaneously on an input raster with explicit band mapping.

    Parameters
    ----------
    image : RasterDataset, Mapping, str, or Path
        Input raster source.
    indices : Sequence[str]
        List of index names to compute (e.g. ['NDVI', 'NDWI', 'NDBI']).
    bands : Mapping[str, Union[str, int]], optional
        Explicit mapping from standard role to band identifier.
        Supports both string names and integer indices.
        This takes priority over sensor presets.
    sensor : str, optional
        Satellite sensor preset. Only used if no explicit band mapping is provided.
    params : Mapping[str, Mapping[str, float]], optional
        Nested parameter dictionary per index name.

    Returns
    -------
    dict[str, IndexResult]
        Dictionary mapping each index name to its corresponding IndexResult.
    """
    results: Dict[str, IndexResult] = {}
    for idx_name in indices:
        idx_params = params.get(idx_name) if params else None
        res = calculate_index(
            image=image,
            index=idx_name,
            bands=bands,
            sensor=sensor,
            params=idx_params,
        )
        results[res.index_name] = res
    return results


def calculate_all(
    image: RasterInput,
    bands: Optional[Mapping[str, str]] = None,
    sensor: Optional[str] = None,
) -> Dict[str, Any]:
    """Automatically discover and calculate all compatible indices for the input raster.

    Parameters
    ----------
    image : RasterDataset, Mapping, str, or Path
        Input raster source.
    bands : Mapping[str, str], optional
        Explicit band mapping.
    sensor : str, optional
        Satellite sensor preset.

    Returns
    -------
    dict[str, Any]
        Dictionary containing:
        - 'results': dict[str, IndexResult] for all successfully calculated indices.
        - 'available_indices': list[str] of compatible index names.
        - 'skipped': dict[str, str] mapping incompatible index names to missing band reasons.
    """
    bands_dict, _ = _prepare_bands_and_metadata(image)
    registry = get_registry()

    resolver = BandResolver(
        available_band_names=bands_dict.keys(),
        sensor=sensor,
        band_mapping=bands,
    )

    results: Dict[str, IndexResult] = {}
    skipped: Dict[str, str] = {}
    available_indices: List[str] = []

    for name in registry.list():
        idx_def = registry.get(name)
        try:
            resolver.resolve_all(idx_def.required_bands)
            res = calculate_index(image=bands_dict, index=name, bands=bands, sensor=sensor)
            results[name] = res
            available_indices.append(name)
        except MissingBandError as e:
            skipped[name] = str(e)

    return {
        "results": results,
        "available_indices": available_indices,
        "skipped": skipped,
    }
