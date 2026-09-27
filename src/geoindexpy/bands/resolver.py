"""Band resolution system for robust multispectral band mapping."""

import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Union
import numpy as np

from geoindexpy.bands.sensors import get_sensor_band_map
from geoindexpy.exceptions import AmbiguousBandError, MissingBandError

# Common aliases mapping for standard spectral roles
COMMON_BAND_SYNONYMS: Dict[str, Sequence[str]] = {
    "coastal": ("coastal", "b01", "b1", "band_1", "band1", "sr_b1"),
    "blue": ("blue", "b02", "b2", "band_2", "band2", "sr_b2"),
    "green": ("green", "b03", "b3", "band_3", "band3", "sr_b3"),
    "red": ("red", "b04", "b4", "band_4", "band4", "sr_b4"),
    "rededge1": ("rededge1", "re1", "b05", "b5"),
    "rededge2": ("rededge2", "re2", "b06", "b6"),
    "rededge3": ("rededge3", "re3", "b07", "b7"),
    "nir": ("nir", "b08", "b8", "band_8", "band8", "sr_b5", "b5"),
    "narrow_nir": ("narrow_nir", "b8a", "b08a"),
    "swir1": ("swir1", "b11", "b6", "band_6", "band6", "sr_b6", "swir"),
    "swir2": ("swir2", "b12", "b7", "band_7", "band7", "sr_b7"),
    "swir": ("swir", "swir1", "b11", "b6", "band_6", "band6", "sr_b6"),
}


def normalize_band_name(name: str) -> str:
    """Normalize a band name for comparison: lowercase, stripped, without leading zeros after B."""
    cleaned = name.strip().lower()
    cleaned = re.sub(r"[_\-\s]+", "_", cleaned)
    return cleaned


class BandResolver:
    """Resolves standard spectral role requirements to concrete band inputs with explicit user mapping support."""

    def __init__(
        self,
        available_band_names: Iterable[str],
        sensor: Optional[str] = None,
        band_mapping: Optional[Mapping[str, Union[str, int]]] = None,
    ) -> None:
        self.available_band_names = list(available_band_names)
        self.sensor = sensor
        
        # Process explicit user mapping - supports both strings and integers
        self.explicit_mapping: Dict[str, str] = {}
        if band_mapping:
            for k, v in band_mapping.items():
                role = k.strip().lower()
                # Convert integer band numbers to band names (e.g., 1 -> "1", 3 -> "3")
                if isinstance(v, int):
                    self.explicit_mapping[role] = str(v)
                else:
                    self.explicit_mapping[role] = v.strip()

        # If sensor specified, build mapping from preset (only used if no explicit mapping)
        self.sensor_mapping: Dict[str, str] = {}
        if sensor:
            self.sensor_mapping = get_sensor_band_map(sensor)

    def resolve(self, required_band: str) -> str:
        """Resolve a single standard band role to an available band name with explicit user mapping priority.

        Parameters
        ----------
        required_band : str
            Standard spectral role (e.g. 'nir', 'red').

        Returns
        -------
        str
            The concrete matched band name from available_band_names.

        Raises
        ------
        AmbiguousBandError
            If multiple candidates match and cannot be deterministically chosen.
        MissingBandError
            If no matching band is found or explicit mapping points to non-existent band.
        """
        role = required_band.strip().lower()

        # 1. Explicit user mapping takes TOP priority - this is the key requirement
        if role in self.explicit_mapping:
            target = self.explicit_mapping[role]
            
            # Check if the target exists in available bands (case-insensitive)
            for avail in self.available_band_names:
                if avail.strip().lower() == target.lower():
                    return avail
            
            # Explicit mapping provided but band doesn't exist - clear error
            raise MissingBandError(
                index_name=f"explicit mapping for '{role}'",
                missing_bands=[target],
                available_bands=self.available_band_names,
            )

        # 2. Sensor preset mapping (only used if no explicit mapping provided)
        if self.sensor and role in self.sensor_mapping:
            sensor_band = self.sensor_mapping[role]
            for avail in self.available_band_names:
                if avail.strip().lower() == sensor_band.lower():
                    return avail
            # Sensor mapping failed but that's okay - we'll try other methods
            pass

        # 3. Exact name match (case-insensitive)
        exact_matches = [
            b for b in self.available_band_names if b.strip().lower() == role
        ]
        if len(exact_matches) == 1:
            return exact_matches[0]
        elif len(exact_matches) > 1:
            raise AmbiguousBandError(role, exact_matches)

        # 4. Synonym match (only if no explicit mapping)
        synonyms = COMMON_BAND_SYNONYMS.get(role, ())
        candidates: List[str] = []
        for avail in self.available_band_names:
            norm_avail = normalize_band_name(avail)
            for syn in synonyms:
                norm_syn = normalize_band_name(syn)
                if norm_avail == norm_syn:
                    if avail not in candidates:
                        candidates.append(avail)

        if len(candidates) == 1:
            return candidates[0]
        elif len(candidates) > 1:
            raise AmbiguousBandError(role, candidates)

        # Not found - provide helpful error message
        raise MissingBandError(
            index_name=f"resolution({role})",
            missing_bands=[role],
            available_bands=self.available_band_names,
        )

    def resolve_all(self, required_bands: Iterable[str]) -> Dict[str, str]:
        """Resolve a collection of required standard band roles.

        Returns
        -------
        dict[str, str]
            Mapping from required band role to concrete band name.
        """
        resolved: Dict[str, str] = {}
        for role in required_bands:
            resolved[role.strip().lower()] = self.resolve(role)
        return resolved


def extract_band_arrays(
    bands_source: Union[Mapping[str, Any], Sequence[Any]],
    required_roles: Iterable[str],
    sensor: Optional[str] = None,
    band_mapping: Optional[Mapping[str, Union[str, int]]] = None,
) -> Dict[str, np.ndarray]:
    """Resolve and extract numpy band arrays from a dictionary or source with explicit band mapping support.

    Parameters
    ----------
    bands_source : Mapping[str, Any] or Sequence
        Source dictionary containing band arrays keyed by band names or indices.
    required_roles : Iterable[str]
        Roles needed by an index (e.g., ['nir', 'red']).
    sensor : str, optional
        Satellite sensor preset (only used if no explicit mapping provided).
    band_mapping : Mapping[str, Union[str, int]], optional
        Explicit mapping dictionary from spectral roles to band identifiers.
        Supports both string names (e.g., {"red": "B3"}) and integer indices (e.g., {"red": 3}).

    Returns
    -------
    dict[str, np.ndarray]
        Resolved dictionary keyed by standard role (e.g. {'nir': arr, 'red': arr}).

    Raises
    ------
    TypeError
        If bands_source is not a mapping.
    MissingBandError
        If required bands cannot be resolved.
    """
    if not isinstance(bands_source, Mapping):
        raise TypeError(f"bands_source must be a mapping (dict), got {type(bands_source).__name__}")

    resolver = BandResolver(
        available_band_names=bands_source.keys(),
        sensor=sensor,
        band_mapping=band_mapping,
    )
    resolved_names = resolver.resolve_all(required_roles)

    arrays: Dict[str, np.ndarray] = {}
    for role, actual_name in resolved_names.items():
        arr = np.asanyarray(bands_source[actual_name])
        arrays[role] = arr

    return arrays
