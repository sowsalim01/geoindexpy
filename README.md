# GeoIndexPy

**A Python library for spectral and geospatial index computation.**

[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://pypi.org/project/geoindexpy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-43%20passed-brightgreen)](https://github.com/geoindex/geoindexpy)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

GeoIndexPy is a modern, robust, vectorized and extensible scientific Python framework for computing **spectral and geospatial indices** from multispectral and hyperspectral satellite imagery.

It is designed for Earth Observation, remote sensing, multispectral image analysis and geospatial data science.

---

## Features

| Feature | Description |
|---|---|
| 🧮 **9 Spectral Indices** | NDVI, SAVI, EVI, GNDVI, NDWI, MNDWI, NDBI, NDMI, BSI |
| 🛰️ **Sensor Profiles** | Sentinel-2, Landsat 8/9/7/5 automatic band mapping |
| ⚡ **Vectorized Engine** | Pure NumPy — no pixel loops, zero silent divisions |
| 🗂️ **Scientific Registry** | Formulas, references, band roles, valid ranges |
| 🌍 **Geospatial Integrity** | CRS, affine transform and resolution fully preserved |
| 📊 **Statistics** | min, max, mean, std, percentiles, valid/nodata pixel counts |
| 💾 **GeoTIFF Export** | Georeferenced output via Rasterio |
| 🔌 **Extensible** | Register custom indices without modifying core engine |
| 🔒 **Safe by design** | Custom exceptions hierarchy, no silent failures |

---

## Installation

### Standard Installation
```bash
pip install geoindexpy
```

### With optional extras
```bash
pip install "geoindexpy[viz]"    # matplotlib visualization
pip install "geoindexpy[xarray]" # xarray/rioxarray support
pip install "geoindexpy[dask]"   # Dask for large rasters
pip install "geoindexpy[dev]"    # Development & testing tools
```

### Development Installation
```bash
git clone https://github.com/geoindex/geoindexpy.git
cd geoindexpy
pip install -e ".[dev]"
```

---

## Quickstart

### 1. Direct computation with NumPy arrays
```python
import numpy as np
import geoindexpy

nir = np.array([0.72, 0.68, 0.15])
red = np.array([0.08, 0.12, 0.20])

ndvi = geoindexpy.ndvi(nir=nir, red=red)
print("NDVI:", ndvi)
# → NDVI: [ 0.8    0.7   -0.143]
```

### 2. Generic engine with a GeoTIFF and sensor mapping
```python
import geoindexpy

result = geoindexpy.calculate_index(
    "sentinel2_scene.tif",
    index="NDVI",
    sensor="sentinel2",   # automatic B08→NIR, B04→RED
)

print(result.summary())
result.save("ndvi_output.tif")   # georeferenced GeoTIFF
```

### 3. Multiple indices at once
```python
results = geoindexpy.calculate_indices(
    "sentinel2_scene.tif",
    indices=["NDVI", "NDWI", "NDBI", "NDMI", "SAVI"],
    sensor="sentinel2",
)

for name, res in results.items():
    s = res.summary()
    print(f"{name}: min={s['min']:.3f}  max={s['max']:.3f}  mean={s['mean']:.3f}")
```

### 4. Discover available indices
```python
geoindexpy.list_indices()
# → ['BSI', 'EVI', 'GNDVI', 'MNDWI', 'NDBI', 'NDMI', 'NDVI', 'NDWI', 'SAVI']

geoindexpy.list_indices(category="vegetation")
# → ['EVI', 'GNDVI', 'NDVI', 'SAVI']

geoindexpy.get_index_info("NDVI")
# → {'short_name': 'NDVI', 'formula': '(nir - red) / (nir + red)', 'reference': 'Rouse et al. 1974', ...}
```

---

## Available Indices (v0.1.0)

| Index | Full Name | Category | Reference |
|---|---|---|---|
| NDVI | Normalized Difference Vegetation Index | Vegetation | Rouse et al. (1974) |
| SAVI | Soil-Adjusted Vegetation Index | Vegetation | Huete (1988) |
| EVI | Enhanced Vegetation Index | Vegetation | Huete et al. (2002) |
| GNDVI | Green Normalized Difference Vegetation Index | Vegetation | Gitelson et al. (1996) |
| NDWI | Normalized Difference Water Index | Water | McFeeters (1996) |
| MNDWI | Modified Normalized Difference Water Index | Water | Xu (2006) |
| NDBI | Normalized Difference Built-Up Index | Urban | Zha et al. (2003) |
| NDMI | Normalized Difference Moisture Index | Moisture | Gao (1996) |
| BSI | Bare Soil Index | Soil | Rikimaru et al. (2002) |

---

## Testing

```bash
pytest                   # all 43 tests
pytest tests/unit/       # unit tests
pytest tests/scientific/ # scientific formula validation
pytest tests/integration/# georeferenced pipeline tests
```

---

## Roadmap

- **v0.2.0** — MSAVI, OSAVI, NBR, NDSI, NDRE + xarray support
- **v0.3.0** — Dask large raster processing, COG support
- **v0.4.0** — Time series, STAC integration, hyperspectral
- **v1.0.0** — Stable API, fully documented, PyPI-ready

---

## Citation

If you use GeoIndexPy in your research, please cite it using the metadata in [CITATION.cff](CITATION.cff).

---

## License

MIT License — see [LICENSE](LICENSE).
