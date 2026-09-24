"""Scientific definition and metadata model for spectral indices."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple
import numpy as np


@dataclass(frozen=True)
class SpectralIndex:
    """Scientific representation of a spectral or geospatial index.

    Attributes
    ----------
    short_name : str
        Standardized identifier/acronym of the index (e.g., 'NDVI', 'NDWI'). Case-insensitive in lookup.
    long_name : str
        Complete scientific name of the index (e.g., 'Normalized Difference Vegetation Index').
    category : str
        Thematic category: 'vegetation', 'water', 'urban', 'soil', 'moisture', 'burn', 'salinity'.
    required_bands : tuple[str, ...]
        List of standard band roles needed (e.g., ('nir', 'red')).
    formula_str : str
        Human-readable mathematical expression (e.g., '(nir - red) / (nir + red)').
    compute_fn : Callable[..., np.ndarray]
        Vectorized Python callable that performs the calculation.
    default_params : dict[str, float]
        Dictionary of default hyper-parameters (e.g. {'L': 0.5} for SAVI).
    reference : str
        Scientific bibliographic citation.
    valid_range : tuple[Optional[float], Optional[float]]
        Theoretical or typical numerical range (e.g., (-1.0, 1.0)).
    version : str
        Index metadata specification version.
    """

    short_name: str
    long_name: str
    category: str
    required_bands: Tuple[str, ...]
    formula_str: str
    compute_fn: Callable[..., np.ndarray] = field(repr=False)
    default_params: Dict[str, float] = field(default_factory=dict)
    reference: str = ""
    valid_range: Tuple[Optional[float], Optional[float]] = (-1.0, 1.0)
    version: str = "1.0.0"

    def __post_init__(self) -> None:
        # Standardize short_name to uppercase and band names to lowercase
        object.__setattr__(self, "short_name", self.short_name.strip().upper())
        object.__setattr__(
            self,
            "required_bands",
            tuple(b.strip().lower() for b in self.required_bands),
        )
        object.__setattr__(self, "category", self.category.strip().lower())

    def to_dict(self) -> Dict[str, Any]:
        """Export index metadata as a dictionary."""
        return {
            "short_name": self.short_name,
            "long_name": self.long_name,
            "category": self.category,
            "required_bands": list(self.required_bands),
            "formula": self.formula_str,
            "default_params": dict(self.default_params),
            "reference": self.reference,
            "valid_range": list(self.valid_range),
            "version": self.version,
        }
