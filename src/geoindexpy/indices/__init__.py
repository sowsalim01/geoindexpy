"""Spectral indices categorized implementations."""

from geoindexpy.indices.moisture import NDMI_INDEX, compute_ndmi
from geoindexpy.indices.soil import BSI_INDEX, compute_bsi
from geoindexpy.indices.urban import NDBI_INDEX, compute_ndbi
from geoindexpy.indices.vegetation import (
    EVI_INDEX,
    GNDVI_INDEX,
    NDVI_INDEX,
    SAVI_INDEX,
    compute_evi,
    compute_gndvi,
    compute_ndvi,
    compute_savi,
)
from geoindexpy.indices.water import MNDWI_INDEX, NDWI_INDEX, compute_mndwi, compute_ndwi

__all__ = [
    # Vegetation
    "NDVI_INDEX",
    "compute_ndvi",
    "SAVI_INDEX",
    "compute_savi",
    "EVI_INDEX",
    "compute_evi",
    "GNDVI_INDEX",
    "compute_gndvi",
    # Water
    "NDWI_INDEX",
    "compute_ndwi",
    "MNDWI_INDEX",
    "compute_mndwi",
    # Urban
    "NDBI_INDEX",
    "compute_ndbi",
    # Moisture
    "NDMI_INDEX",
    "compute_ndmi",
    # Soil
    "BSI_INDEX",
    "compute_bsi",
]
