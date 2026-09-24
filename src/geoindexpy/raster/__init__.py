"""Geospatial raster input/output and metadata handling."""

from geoindexpy.raster.io import RasterDataset, open_raster, write_raster
from geoindexpy.raster.metadata import RasterMetadata

__all__ = ["RasterDataset", "RasterMetadata", "open_raster", "write_raster"]
