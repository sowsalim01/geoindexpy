"""Core module containing base models, registry, engine, and result abstractions."""

from geoindexpy.core.engine import calculate_all, calculate_index, calculate_indices
from geoindexpy.core.model import SpectralIndex
from geoindexpy.core.registry import IndexRegistry, get_registry
from geoindexpy.core.result import IndexResult

__all__ = [
    "IndexRegistry",
    "IndexResult",
    "SpectralIndex",
    "calculate_all",
    "calculate_index",
    "calculate_indices",
    "get_registry",
]
