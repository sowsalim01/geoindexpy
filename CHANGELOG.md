# Changelog

All notable changes to GeoIndexPy will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.1.0] — 2026-09-24

### Added

#### Core Architecture
- `SpectralIndex` dataclass with full scientific metadata (name, formula, required bands, reference, valid range, version)
- `IndexRegistry` — centralized, extensible, thread-safe registry for all spectral indices
- `get_registry()` — global singleton accessor
- `IndexResult` — result container with statistical summary (`min`, `max`, `mean`, `median`, `std`, `valid_pixels`, `nodata_pixels`, percentiles) and georeferenced GeoTIFF export (`save()`)
- `IndexNotFoundError`, `MissingBandError`, `AmbiguousBandError`, `InvalidRasterError`, `IncompatibleRasterError`, `InvalidParameterError`, `UnsupportedSensorError` — full custom exception hierarchy

#### Spectral Indices (9 total)
- **Vegetation**: NDVI (Rouse et al. 1974), SAVI (Huete 1988), EVI (Huete et al. 2002), GNDVI (Gitelson et al. 1996)
- **Water**: NDWI (McFeeters 1996), MNDWI (Xu 2006)
- **Urban**: NDBI (Zha et al. 2003)
- **Moisture**: NDMI (Gao 1996)
- **Soil**: BSI (Rikimaru et al. 2002)

#### Public API
- `calculate_index(image, index, bands, sensor, params)` — single index engine
- `calculate_indices(image, indices, bands, sensor, params)` — multi-index engine
- `calculate_all(image, bands, sensor)` — auto-discover all compatible indices
- `list_indices(category)` — list available indices with optional category filter
- `get_index_info(name)` — retrieve scientific metadata
- `summary(result)` — statistical summary of any result or array
- Direct functions: `ndvi()`, `savi()`, `evi()`, `gndvi()`, `ndwi()`, `mndwi()`, `ndbi()`, `ndmi()`, `bsi()`
- `plot_index()` — lightweight visualization (optional `[viz]` extra)

#### Raster Layer
- `open_raster(filepath, band_names)` — load georeferenced rasters via Rasterio; preserves CRS, transform, resolution
- `write_raster(path, data, metadata)` — export arrays to GeoTIFF
- `RasterDataset` — in-memory container for bands + metadata
- `RasterMetadata` — immutable spatial metadata (CRS, affine transform, resolution, nodata, band names)

#### Band Resolution
- `BandResolver` — intelligent, strict, non-ambiguous band resolver
- Synonym dictionary for standard band roles (nir, red, green, swir, etc.)
- Sensor profiles: **Sentinel-2**, **Landsat 8**, **Landsat 9**, **Landsat 5**, **Landsat 7**
- `extract_band_arrays()` — dictionary-based band extraction

#### Math Utilities
- `safe_divide(num, den, fill_value, eps)` — vectorized safe division (zero + NaN + Inf safe)
- `apply_scale(values, scale_factor, offset)` — explicit DN-to-reflectance conversion

#### Testing (43 tests, 100% passing)
- Unit tests: exceptions, math utilities, SpectralIndex model, IndexRegistry, BandResolver, sensor profiles
- Scientific tests: formula validation on exact known values for all 9 indices; 2D multi-pixel fixture coverage
- Integration tests: georeferenced GeoTIFF pipeline (open → compute → export → re-read CRS verification)
- Automatic handling of PostgreSQL/PostGIS PROJ_LIB environment conflict on Windows

#### Project Infrastructure
- `pyproject.toml` using `hatchling` build system (PEP 517/518/621 compliant)
- MIT License
- `CITATION.cff` for scientific citation
- `README.md` with quickstart and installation instructions
- `examples/basic_ndvi.py` and `examples/multispectral_sentinel2.py`
- `.gitignore` for Python/IDE/raster artifacts

---

[Unreleased]: https://github.com/sowsalim01/geoindexpy/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sowsalim01/geoindexpy/releases/tag/v0.1.0
