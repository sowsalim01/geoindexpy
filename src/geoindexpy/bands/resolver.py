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
    """Resolves standard spectral role requirements to concrete band inputs."""

    def __init__(
        self,
        available_band_names: Iterable[str],
        sensor: Optional[str] = None,
        band_mapping: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.available_band_names = list(available_band_names)
        self.sensor = sensor
        self.explicit_mapping = {
            k.strip().lower(): v.strip() for k, v in (band_mapping or {}).items()
        }

        # If sensor specified, build mapping from preset
        self.sensor_mapping: Dict[str, str] = {}
        if sensor:
            self.sensor_mapping = get_sensor_band_map(sensor)

    def resolve(self, required_band: str) -> str:
        """Resolve a single standard band role to an available band name.

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
            If no matching band is found.
        """
        role = required_band.strip().lower()

        # 1. Explicit user mapping takes top priority
        if role in self.explicit_mapping:
            target = self.explicit_mapping[role]
            # Check existence (case-insensitive)
            for avail in self.available_band_names:
                if avail.strip().lower() == target.lower():
                    return avail
            raise MissingBandError(
                index_name=f"resolution({role})",
                missing_bands=[target],
                available_bands=self.available_band_names,
            )

        # 2. Sensor preset mapping
        if self.sensor and role in self.sensor_mapping:
            sensor_band = self.sensor_mapping[role]
            for avail in self.available_band_names:
                if avail.strip().lower() == sensor_band.lower():
                    return avail
            raise MissingBandError(
                index_name=f"{self.sensor} resolution({role})",
                missing_bands=[sensor_band],
                available_bands=self.available_band_names,
            )

        # 3. Exact name match (case-insensitive)
        exact_matches = [
            b for b in self.available_band_names if b.strip().lower() == role
        ]
        if len(exact_matches) == 1:
            return exact_matches[0]
        elif len(exact_matches) > 1:
            raise AmbiguousBandError(role, exact_matches)

        # 4. Synonym match
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

        # Not found
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
    band_mapping: Optional[Mapping[str, str]] = None,
) -> Dict[str, np.ndarray]:
    """Resolve and extract numpy band arrays from a dictionary or source.

    Parameters
    ----------
    bands_source : Mapping[str, Any] or Sequence
        Source dictionary containing band arrays keyed by band names.
    required_roles : Iterable[str]
        Roles needed by an index (e.g., ['nir', 'red']).
    sensor : str, optional
        Satellite sensor preset.
    band_mapping : Mapping[str, str], optional
        Explicit mapping dictionary.

    Returns
    -------
    dict[str, np.ndarray]
        Resolved dictionary keyed by standard role (e.g. {'nir': arr, 'red': arr}).
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
