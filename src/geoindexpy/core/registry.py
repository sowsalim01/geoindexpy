"""Centralized registry for all available spectral indices in GeoIndexPy."""

from typing import Dict, Iterable, List, Optional
from geoindexpy.core.model import SpectralIndex
from geoindexpy.exceptions import IndexNotFoundError


class IndexRegistry:
    """Thread-safe registry managing available spectral indices."""

    def __init__(self) -> None:
        self._indices: Dict[str, SpectralIndex] = {}

    def register(self, index: SpectralIndex, overwrite: bool = False) -> None:
        """Register a new spectral index in the registry.

        Parameters
        ----------
        index : SpectralIndex
            The index instance to register.
        overwrite : bool, optional
            Whether to overwrite an existing index with the same identifier. Default is False.
        """
        key = index.short_name.upper()
        if key in self._indices and not overwrite:
            raise ValueError(
                f"Spectral index '{key}' is already registered. Set overwrite=True to replace it."
            )
        self._indices[key] = index

    def get(self, name: str) -> SpectralIndex:
        """Retrieve a spectral index by its short name (case-insensitive).

        Parameters
        ----------
        name : str
            The short name/acronym of the index (e.g. 'NDVI').

        Returns
        -------
        SpectralIndex
            The requested spectral index definition.

        Raises
        ------
        IndexNotFoundError
            If the index is not found in the registry.
        """
        key = name.strip().upper()
        if key not in self._indices:
            raise IndexNotFoundError(name, available_indices=self.list())
        return self._indices[key]

    def has(self, name: str) -> bool:
        """Check whether an index is registered."""
        return name.strip().upper() in self._indices

    def list(self, category: Optional[str] = None) -> List[str]:
        """List registered index names, optionally filtered by category.

        Parameters
        ----------
        category : str, optional
            Category filter ('vegetation', 'water', 'urban', etc.).

        Returns
        -------
        list[str]
            Alphabetically sorted list of registered index short names.
        """
        if category is None:
            return sorted(self._indices.keys())
        cat_lower = category.strip().lower()
        return sorted(k for k, idx in self._indices.items() if idx.category == cat_lower)

    def info(self, name: str) -> Dict[str, object]:
        """Return the dictionary metadata of an index."""
        return self.get(name).to_dict()

    def filter_by_bands(self, available_bands: Iterable[str]) -> List[str]:
        """Find all indices that can be computed with the given set of available bands.

        Parameters
        ----------
        available_bands : Iterable[str]
            Collection of standard band names provided by an image.

        Returns
        -------
        list[str]
            List of index names that are fully compatible.
        """
        avail_set = {b.strip().lower() for b in available_bands}
        matching: List[str] = []
        for name, idx in self._indices.items():
            if set(idx.required_bands).issubset(avail_set):
                matching.append(name)
        return sorted(matching)

    def clear(self) -> None:
        """Clear all registered indices (mostly for testing)."""
        self._indices.clear()

    def __len__(self) -> int:
        return len(self._indices)

    def __contains__(self, item: str) -> bool:
        return self.has(item)


# Global default registry singleton
_DEFAULT_REGISTRY = IndexRegistry()


def get_registry() -> IndexRegistry:
    """Return the global default index registry instance."""
    return _DEFAULT_REGISTRY
