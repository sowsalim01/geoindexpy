# Manuel de Test Complet - GeoIndexPy

Ce manuel fournit un guide complet pour tester toutes les fonctionnalités de GeoIndexPy avec différents types de données.

---

## 📋 Table des Matières

1. [Installation et Configuration](#installation-et-configuration)
2. [Tests avec Données Synthétiques](#tests-avec-données-synthétiques)
3. [Tests avec GeoTIFF Réels](#tests-avec-geotiff-réels)
4. [Tests de Tous les Indices](#tests-de-tous-les-indices)
5. [Tests de Fonctionnalités Avancées](#tests-de-fonctionnalités-avancées)
6. [Tests d'Intégration Complets](#tests-dintégration-complets)
7. [Dépannage](#dépannage)

---

## 🚀 Installation et Configuration

### Installation Standard

```bash
# Installation de base
pip install geoindexpy

# Installation avec toutes les fonctionnalités
pip install "geoindexpy[all]"
```

### Installation de Développement

```bash
git clone https://github.com/sowsalim01/geoindexpy.git
cd geoindexpy
pip install -e ".[dev]"
```

### Vérification de l'Installation

```python
import geoindexpy
print(f"GeoIndexPy version: {geoindexpy.__version__}")
print(f"Indices disponibles: {geoindexpy.list_indices()}")
```

---

## 🧪 Tests avec Données Synthétiques

### Test 1 : Calcul NDVI avec Tableaux NumPy

```python
import numpy as np
import geoindexpy

# Création de données synthétiques
nir = np.array([0.72, 0.68, 0.15, 0.05], dtype=np.float32)
red = np.array([0.08, 0.12, 0.20, 0.04], dtype=np.float32)

# Calcul NDVI
ndvi_result = geoindexpy.ndvi(nir=nir, red=red)
print("NDVI calculé:", ndvi_result)

# Vérification attendue: [0.8, 0.7, -0.143, 0.107]
assert np.allclose(ndvi_result, [0.8, 0.7, -0.143, 0.107], atol=0.01)
print("✅ Test NDVI réussi")
```

### Test 2 : Calcul Multi-indices avec Données 2D

```python
import numpy as np
import geoindexpy

# Création de matrices 4x4
height, width = 4, 4
np.random.seed(42)

bands = {
    "nir": np.random.uniform(0.3, 0.8, (height, width)).astype(np.float32),
    "red": np.random.uniform(0.05, 0.3, (height, width)).astype(np.float32),
    "green": np.random.uniform(0.1, 0.25, (height, width)).astype(np.float32),
    "blue": np.random.uniform(0.02, 0.15, (height, width)).astype(np.float32),
    "swir": np.random.uniform(0.1, 0.5, (height, width)).astype(np.float32),
}

# Calcul de plusieurs indices
indices = ["NDVI", "SAVI", "EVI", "GNDVI", "NDWI", "MNDWI", "NDBI", "NDMI", "BSI"]
results = geoindexpy.calculate_indices(image=bands, indices=indices)

# Vérifications
assert len(results) == 9, "Tous les indices ne sont pas calculés"
for name, result in results.items():
    assert result.shape == (4, 4), f"Forme incorrecte pour {name}"
    stats = result.summary()
    assert stats["valid_pixels"] == 16, f"Pixels invalides pour {name}"
    print(f"{name}: min={stats['min']:.3f}, max={stats['max']:.3f}")

print("✅ Test multi-indices 2D réussi")
```

### Test 3 : Tests des Paramètres Personnalisés

```python
import numpy as np
import geoindexpy

nir = np.array([0.8])
red = np.array([0.2])

# Test SAVI avec différents paramètres L
savi_05 = geoindexpy.savi(nir, red, L=0.5)
savi_10 = geoindexpy.savi(nir, red, L=1.0)

print(f"SAVI (L=0.5): {savi_05}")
print(f"SAVI (L=1.0): {savi_10}")

# Test EVI avec paramètres personnalisés
blue = np.array([0.05])
evi_custom = geoindexpy.evi(nir, red, blue, G=3.0, C1=5.0, C2=8.0, L=1.5)
print(f"EVI personnalisé: {evi_custom}")

print("✅ Test paramètres personnalisés réussi")
```

---

## 🛰️ Tests avec GeoTIFF Réels

### Test 4 : Création et Traitement GeoTIFF Sentinel-2

```python
import os
import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.transform import from_origin
from pathlib import Path
import geoindexpy

# Nettoyage environnement PROJ
for var in ("PROJ_LIB", "PROJ_DATA"):
    val = os.environ.get(var, "")
    if val and ("postgres" in val.lower() or not os.path.exists(os.path.join(val, "proj.db"))):
        os.environ.pop(var, None)

def create_sentinel2_geotiff(output_path: Path):
    """Crée un GeoTIFF Sentinel-2 de test."""
    height, width = 64, 64
    transform = from_origin(500000.0, 6000000.0, 10.0, 10.0)
    crs = CRS.from_epsg(32631)  # UTM zone 31N

    np.random.seed(42)
    bands_data = {
        "B02": np.random.uniform(0.02, 0.15, (height, width)).astype(np.float32),  # Blue
        "B03": np.random.uniform(0.04, 0.20, (height, width)).astype(np.float32),  # Green
        "B04": np.random.uniform(0.03, 0.25, (height, width)).astype(np.float32),  # Red
        "B08": np.random.uniform(0.35, 0.85, (height, width)).astype(np.float32),  # NIR
        "B11": np.random.uniform(0.1, 0.5, (height, width)).astype(np.float32),   # SWIR
    }

    profile = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 5,
        "dtype": "float32",
        "crs": crs,
        "transform": transform,
        "nodata": -9999.0,
    }

    with rasterio.open(str(output_path), "w", **profile) as dst:
        for i, (band_name, data) in enumerate(bands_data.items(), 1):
            dst.write(data, i)
            dst.set_band_description(i, band_name)

# Création du fichier de test
test_dir = Path("test_data")
test_dir.mkdir(exist_ok=True)
test_tif = test_dir / "sentinel2_test.tif"

print("Création du GeoTIFF de test...")
create_sentinel2_geotiff(test_tif)

# Ouverture et traitement
print("Ouverture du raster...")
dataset = geoindexpy.open_raster(test_tif)
print(f"Bandes disponibles: {dataset.band_names()}")
print(f"Forme: {dataset.shape}")
print(f"CRS: {dataset.metadata.crs}")

# Calcul avec mapping automatique Sentinel-2
print("\nCalcul d'indices avec mapping Sentinel-2...")
results = geoindexpy.calculate_indices(
    image=test_tif,
    indices=["NDVI", "NDWI", "SAVI"],
    sensor="sentinel2",
)

for name, result in results.items():
    stats = result.summary()
    print(f"{name}: min={stats['min']:.3f}, max={stats['max']:.3f}, mean={stats['mean']:.3f}")

# Test d'export
print("\nTest d'export GeoTIFF...")
for name, result in results.items():
    output_path = test_dir / f"{name.lower()}_result.tif"
    result.save(output_path)
    print(f"Exporté: {output_path}")

print("✅ Test GeoTIFF Sentinel-2 réussi")
```

### Test 5 : Création GeoTIFF Landsat 8

```python
import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.transform import from_origin
from pathlib import Path
import geoindexpy

def create_landsat8_geotiff(output_path: Path):
    """Crée un GeoTIFF Landsat 8 de test."""
    height, width = 64, 64
    transform = from_origin(400000.0, 5000000.0, 30.0, 30.0)
    crs = CRS.from_epsg(32630)  # UTM zone 30N

    np.random.seed(123)
    bands_data = {
        "B2": np.random.uniform(0.02, 0.15, (height, width)).astype(np.float32),   # Blue
        "B3": np.random.uniform(0.04, 0.20, (height, width)).astype(np.float32),   # Green
        "B4": np.random.uniform(0.03, 0.25, (height, width)).astype(np.float32),   # Red
        "B5": np.random.uniform(0.35, 0.85, (height, width)).astype(np.float32),   # NIR
        "B6": np.random.uniform(0.1, 0.5, (height, width)).astype(np.float32),    # SWIR1
    }

    profile = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 5,
        "dtype": "float32",
        "crs": crs,
        "transform": transform,
        "nodata": -9999.0,
    }

    with rasterio.open(str(output_path), "w", **profile) as dst:
        for i, (band_name, data) in enumerate(bands_data.items(), 1):
            dst.write(data, i)
            dst.set_band_description(i, band_name)

# Création et test
landsat_tif = test_dir / "landsat8_test.tif"
print("Création du GeoTIFF Landsat 8...")
create_landsat8_geotiff(landsat_tif)

# Calcul avec mapping Landsat 8
results = geoindexpy.calculate_indices(
    image=landsat_tif,
    indices=["NDVI", "NDMI"],
    sensor="landsat8",
)

for name, result in results.items():
    stats = result.summary()
    print(f"{name} (Landsat 8): min={stats['min']:.3f}, max={stats['max']:.3f}")

print("✅ Test GeoTIFF Landsat 8 réussi")
```

---

## 📊 Tests de Tous les Indices

### Test 6 : Validation Scientifique des 9 Indices

```python
import numpy as np
import geoindexpy

def test_all_indices_exact_values():
    """Teste tous les indices avec des valeurs connues."""
    
    # NDVI
    nir, red = 0.8, 0.2
    ndvi = geoindexpy.ndvi(nir, red)
    expected_ndvi = (0.8 - 0.2) / (0.8 + 0.2)
    assert np.isclose(ndvi, expected_ndvi), "NDVI incorrect"
    print(f"✅ NDVI: {ndvi:.3f} (attendu: {expected_ndvi:.3f})")
    
    # SAVI
    savi = geoindexpy.savi(nir, red, L=0.5)
    expected_savi = ((0.8 - 0.2) / (0.8 + 0.2 + 0.5)) * 1.5
    assert np.isclose(savi, expected_savi), "SAVI incorrect"
    print(f"✅ SAVI: {savi:.3f} (attendu: {expected_savi:.3f})")
    
    # EVI
    blue = 0.05
    evi = geoindexpy.evi(nir, red, blue)
    expected_evi = 2.5 * (0.8 - 0.2) / (0.8 + 6.0*0.2 - 7.5*0.05 + 1.0)
    assert np.isclose(evi, expected_evi), "EVI incorrect"
    print(f"✅ EVI: {evi:.3f} (attendu: {expected_evi:.3f})")
    
    # GNDVI
    green = 0.2
    gndvi = geoindexpy.gndvi(nir, green)
    expected_gndvi = (0.8 - 0.2) / (0.8 + 0.2)
    assert np.isclose(gndvi, expected_gndvi), "GNDVI incorrect"
    print(f"✅ GNDVI: {gndvi:.3f} (attendu: {expected_gndvi:.3f})")
    
    # NDWI
    ndwi = geoindexpy.ndwi(green, nir)
    expected_ndwi = (0.2 - 0.8) / (0.2 + 0.8)
    assert np.isclose(ndwi, expected_ndwi), "NDWI incorrect"
    print(f"✅ NDWI: {ndwi:.3f} (attendu: {expected_ndwi:.3f})")
    
    # MNDWI
    swir = 0.3
    mndwi = geoindexpy.mndwi(green, swir)
    expected_mndwi = (0.2 - 0.3) / (0.2 + 0.3)
    assert np.isclose(mndwi, expected_mndwi), "MNDWI incorrect"
    print(f"✅ MNDWI: {mndwi:.3f} (attendu: {expected_mndwi:.3f})")
    
    # NDBI
    ndbi = geoindexpy.ndbi(swir, nir)
    expected_ndbi = (0.3 - 0.8) / (0.3 + 0.8)
    assert np.isclose(ndbi, expected_ndbi), "NDBI incorrect"
    print(f"✅ NDBI: {ndbi:.3f} (attendu: {expected_ndbi:.3f})")
    
    # NDMI
    ndmi = geoindexpy.ndmi(nir, swir)
    expected_ndmi = (0.8 - 0.3) / (0.8 + 0.3)
    assert np.isclose(ndmi, expected_ndmi), "NDMI incorrect"
    print(f"✅ NDMI: {ndmi:.3f} (attendu: {expected_ndmi:.3f})")
    
    # BSI
    bsi = geoindexpy.bsi(swir, red, nir, blue)
    expected_bsi = ((0.3 + 0.2) - (0.8 + 0.05)) / ((0.3 + 0.2) + (0.8 + 0.05))
    assert np.isclose(bsi, expected_bsi), "BSI incorrect"
    print(f"✅ BSI: {bsi:.3f} (attendu: {expected_bsi:.3f})")

test_all_indices_exact_values()
print("✅ Tous les indices validés scientifiquement")
```

### Test 7 : Tests des Catégories d'Indices

```python
import geoindexpy

# Test des catégories
vegetation_indices = geoindexpy.list_indices(category="vegetation")
print(f"Indices végétation: {vegetation_indices}")
assert set(vegetation_indices) == {"NDVI", "SAVI", "EVI", "GNDVI"}

water_indices = geoindexpy.list_indices(category="water")
print(f"Indices eau: {water_indices}")
assert set(water_indices) == {"NDWI", "MNDWI"}

urban_indices = geoindexpy.list_indices(category="urban")
print(f"Indices urbain: {urban_indices}")
assert set(urban_indices) == {"NDBI"}

moisture_indices = geoindexpy.list_indices(category="moisture")
print(f"Indices humidité: {moisture_indices}")
assert set(moisture_indices) == {"NDMI"}

soil_indices = geoindexpy.list_indices(category="soil")
print(f"Indices sol: {soil_indices}")
assert set(soil_indices) == {"BSI"}

print("✅ Tests des catégories réussis")
```

---

## 🔧 Tests de Fonctionnalités Avancées

### Test 8 : Tests de Mapping de Capteurs

```python
import geoindexpy

# Test des capteurs supportés
sensors = geoindexpy.bands.sensors.list_supported_sensors()
print(f"Capteurs supportés: {sensors}")

# Test de mapping Sentinel-2
s2_map = geoindexpy.bands.sensors.get_sensor_band_map("sentinel2")
print(f"Mapping Sentinel-2: {s2_map}")
assert s2_map["nir"] == "B08"
assert s2_map["red"] == "B04"

# Test de mapping Landsat 8
l8_map = geoindexpy.bands.sensors.get_sensor_band_map("landsat8")
print(f"Mapping Landsat 8: {l8_map}")
assert l8_map["nir"] == "B5"
assert l8_map["red"] == "B4"

# Test des alias
s2_alias = geoindexpy.bands.sensors.get_sensor_band_map("s2")
assert s2_alias == s2_map, "Alias s2 incorrect"

l8_alias = geoindexpy.bands.sensors.get_sensor_band_map("l8")
assert l8_alias == l8_map, "Alias l8 incorrect"

print("✅ Tests de mapping de capteurs réussis")
```

### Test 9 : Tests du Registre d'Indices

```python
import geoindexpy

# Test de récupération d'informations
ndvi_info = geoindexpy.get_index_info("NDVI")
print(f"Info NDVI: {ndvi_info}")
assert ndvi_info["short_name"] == "NDVI"
assert ndvi_info["category"] == "vegetation"
assert "formula" in ndvi_info
assert "reference" in ndvi_info

# Test de liste complète
all_indices = geoindexpy.list_indices()
print(f"Tous les indices: {all_indices}")
assert len(all_indices) == 9, "Nombre d'indices incorrect"

# Test de filtre par bandes disponibles
available_bands = ["nir", "red", "green"]
compatible = geoindexpy.get_registry().filter_by_bands(available_bands)
print(f"Indices compatibles avec {available_bands}: {compatible}")
assert "NDVI" in compatible
assert "GNDVI" in compatible

print("✅ Tests du registre réussis")
```

### Test 10 : Tests de Statistiques et Export

```python
import numpy as np
import geoindexpy
from pathlib import Path

# Création de données de test
data = np.random.uniform(-0.5, 0.9, (10, 10)).astype(np.float32)
data[0, 0] = np.nan  # Ajouter une valeur NaN
data[1, 1] = -9999.0  # Ajouter une valeur nodata

result = geoindexpy.IndexResult(
    index_name="Test",
    data=data,
    metadata=None
)

# Test des statistiques
stats = result.summary()
print(f"Statistiques: {stats}")
assert stats["total_pixels"] == 100
assert stats["valid_pixels"] < 100  # Certains pixels sont invalides
assert stats["nodata_pixels"] > 0

# Test avec métadonnées géospatiales
from geoindexpy.raster.metadata import RasterMetadata
from rasterio.transform import from_origin

metadata = RasterMetadata(
    crs="EPSG:4326",
    transform=from_origin(0.0, 10.0, 1.0, 1.0),
    nodata=-9999.0
)

result_geo = geoindexpy.IndexResult(
    index_name="TestGeo",
    data=data,
    metadata=metadata
)

# Test d'export
output_path = Path("test_data/test_export.tif")
result_geo.save(output_path)
assert output_path.exists(), "Export GeoTIFF échoué"
print(f"Export réussi: {output_path}")

print("✅ Tests de statistiques et export réussis")
```

---

## 🔄 Tests d'Intégration Complets

### Test 11 : Workflow Complet Sentinel-2

```python
import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.transform import from_origin
from pathlib import Path
import geoindexpy

def complete_sentinel2_workflow():
    """Workflow complet de traitement Sentinel-2."""
    
    # 1. Création de données
    test_dir = Path("test_data/integration")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    input_tif = test_dir / "input_sentinel2.tif"
    height, width = 128, 128
    
    transform = from_origin(500000.0, 6000000.0, 10.0, 10.0)
    crs = CRS.from_epsg(32631)
    
    np.random.seed(42)
    bands_data = {
        "B02": np.random.uniform(0.02, 0.15, (height, width)).astype(np.float32),
        "B03": np.random.uniform(0.04, 0.20, (height, width)).astype(np.float32),
        "B04": np.random.uniform(0.03, 0.25, (height, width)).astype(np.float32),
        "B08": np.random.uniform(0.35, 0.85, (height, width)).astype(np.float32),
        "B11": np.random.uniform(0.1, 0.5, (height, width)).astype(np.float32),
    }
    
    profile = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 5,
        "dtype": "float32",
        "crs": crs,
        "transform": transform,
        "nodata": -9999.0,
    }
    
    with rasterio.open(str(input_tif), "w", **profile) as dst:
        for i, (band_name, data) in enumerate(bands_data.items(), 1):
            dst.write(data, i)
            dst.set_band_description(i, band_name)
    
    print(f"✅ Fichier d'entrée créé: {input_tif}")
    
    # 2. Ouverture et inspection
    dataset = geoindexpy.open_raster(input_tif)
    print(f"Forme: {dataset.shape}")
    print(f"Bandes: {dataset.band_names()}")
    print(f"CRS: {dataset.metadata.crs}")
    
    # 3. Calcul de tous les indices compatibles
    all_results = geoindexpy.calculate_all(
        image=input_tif,
        sensor="sentinel2"
    )
    
    print(f"Indices calculés: {all_results['available_indices']}")
    print(f"Indices ignorés: {all_results['skipped']}")
    
    # 4. Export des résultats
    for name, result in all_results['results'].items():
        output_path = test_dir / f"{name.lower()}_complete.tif"
        result.save(output_path)
        print(f"Exporté: {output_path}")
        
        # Vérification
        assert output_path.exists(), f"Export échoué pour {name}"
        
        # Relecture pour vérifier l'intégrité
        with rasterio.open(str(output_path)) as src:
            assert src.shape == (height, width), "Forme incorrecte après export"
            assert src.crs == crs, "CRS perdu après export"
    
    print("✅ Workflow complet Sentinel-2 réussi")

complete_sentinel2_workflow()
```

### Test 12 : Test de calculate_all avec Bandes Personnalisées

```python
import numpy as np
import geoindexpy

# Création de bandes personnalisées
custom_bands = {
    "custom_nir": np.random.uniform(0.3, 0.8, (8, 8)).astype(np.float32),
    "custom_red": np.random.uniform(0.05, 0.3, (8, 8)).astype(np.float32),
    "custom_green": np.random.uniform(0.1, 0.25, (8, 8)).astype(np.float32),
}

# Mapping personnalisé
band_mapping = {
    "nir": "custom_nir",
    "red": "custom_red",
    "green": "custom_green"
}

# Calcul avec mapping personnalisé
results = geoindexpy.calculate_indices(
    image=custom_bands,
    indices=["NDVI", "GNDVI"],
    bands=band_mapping
)

for name, result in results.items():
    stats = result.summary()
    print(f"{name}: min={stats['min']:.3f}, max={stats['max']:.3f}")
    assert result.shape == (8, 8), "Forme incorrecte"

print("✅ Test bandes personnalisées réussi")
```

### Test 13 : Tests de Gestion d'Erreurs

```python
import geoindexpy
import numpy as np

# Test index inexistant
try:
    geoindexpy.calculate_index(
        image={"nir": np.array([0.5]), "red": np.array([0.2])},
        index="INDEX_INEXISTANT"
    )
    assert False, "Devrait lever une exception"
except geoindexpy.IndexNotFoundError as e:
    print(f"✅ Test index inexistant: {e}")

# Test bandes manquantes
try:
    geoindexpy.calculate_index(
        image={"nir": np.array([0.5])},  # manque 'red'
        index="NDVI"
    )
    assert False, "Devrait lever une exception"
except geoindexpy.MissingBandError as e:
    print(f"✅ Test bandes manquantes: {e}")

# Test capteur non supporté
try:
    geoindexpy.bands.sensors.get_sensor_band_map("capteur_inconnu")
    assert False, "Devrait lever une exception"
except geoindexpy.UnsupportedSensorError as e:
    print(f"✅ Test capteur non supporté: {e}")

# Test forme incompatible
try:
    geoindexpy.calculate_index(
        image={
            "nir": np.array([[0.5, 0.6], [0.7, 0.8]]),
            "red": np.array([0.2, 0.3])  # forme différente
        },
        index="NDVI"
    )
    assert False, "Devrait lever une exception"
except geoindexpy.IncompatibleRasterError as e:
    print(f"✅ Test forme incompatible: {e}")

print("✅ Tests de gestion d'erreurs réussis")
```

---

## 🧪 Suite de Tests Automatisée

### Script de Test Complet

```python
#!/usr/bin/env python3
"""
Suite de tests automatisée complète pour GeoIndexPy.
Exécute tous les tests avec vérification des résultats.
"""

import sys
import numpy as np
import geoindexpy
from pathlib import Path

def run_all_tests():
    """Exécute tous les tests et retourne le résultat."""
    
    tests_passed = 0
    tests_failed = 0
    
    print("=" * 60)
    print("SUITE DE TESTS COMPLÈTE - GeoIndexPy")
    print("=" * 60)
    
    # Test 1: Installation
    print("\n📦 Test 1: Installation et version")
    try:
        print(f"Version: {geoindexpy.__version__}")
        print(f"Indices: {len(geoindexpy.list_indices())}")
        tests_passed += 1
        print("✅ Test 1 réussi")
    except Exception as e:
        tests_failed += 1
        print(f"❌ Test 1 échoué: {e}")
    
    # Test 2: NDVI basique
    print("\n🧮 Test 2: NDVI basique")
    try:
        nir, red = np.array([0.8]), np.array([0.2])
        ndvi = geoindexpy.ndvi(nir, red)
        assert np.isclose(ndvi, 0.6), "NDVI incorrect"
        tests_passed += 1
        print("✅ Test 2 réussi")
    except Exception as e:
        tests_failed += 1
        print(f"❌ Test 2 échoué: {e}")
    
    # Test 3: Multi-indices
    print("\n📊 Test 3: Multi-indices")
    try:
        bands = {
            "nir": np.random.uniform(0.3, 0.8, (4, 4)).astype(np.float32),
            "red": np.random.uniform(0.05, 0.3, (4, 4)).astype(np.float32),
            "green": np.random.uniform(0.1, 0.25, (4, 4)).astype(np.float32),
            "blue": np.random.uniform(0.02, 0.15, (4, 4)).astype(np.float32),
            "swir": np.random.uniform(0.1, 0.5, (4, 4)).astype(np.float32),
        }
        results = geoindexpy.calculate_indices(
            image=bands,
            indices=["NDVI", "SAVI", "EVI"]
        )
        assert len(results) == 3, "Nombre d'indices incorrect"
        tests_passed += 1
        print("✅ Test 3 réussi")
    except Exception as e:
        tests_failed += 1
        print(f"❌ Test 3 échoué: {e}")
    
    # Test 4: Catégories
    print("\n🏷️ Test 4: Catégories d'indices")
    try:
        veg = geoindexpy.list_indices(category="vegetation")
        assert len(veg) == 4, "Catégorie végétation incorrecte"
        tests_passed += 1
        print("✅ Test 4 réussi")
    except Exception as e:
        tests_failed += 1
        print(f"❌ Test 4 échoué: {e}")
    
    # Test 5: Capteurs
    print("\n🛰️ Test 5: Mapping de capteurs")
    try:
        s2_map = geoindexpy.bands.sensors.get_sensor_band_map("sentinel2")
        assert s2_map["nir"] == "B08", "Mapping Sentinel-2 incorrect"
        tests_passed += 1
        print("✅ Test 5 réussi")
    except Exception as e:
        tests_failed += 1
        print(f"❌ Test 5 échoué: {e}")
    
    # Test 6: Métadonnées
    print("\n📋 Test 6: Métadonnées d'indices")
    try:
        info = geoindexpy.get_index_info("NDVI")
        assert "formula" in info, "Métadonnées incomplètes"
        assert "reference" in info, "Référence manquante"
        tests_passed += 1
        print("✅ Test 6 réussi")
    except Exception as e:
        tests_failed += 1
        print(f"❌ Test 6 échoué: {e}")
    
    # Test 7: Statistiques
    print("\n📈 Test 7: Statistiques")
    try:
        data = np.random.uniform(-0.5, 0.9, (10, 10)).astype(np.float32)
        result = geoindexpy.IndexResult("Test", data)
        stats = result.summary()
        assert stats["total_pixels"] == 100, "Statistiques incorrectes"
        tests_passed += 1
        print("✅ Test 7 réussi")
    except Exception as e:
        tests_failed += 1
        print(f"❌ Test 7 échoué: {e}")
    
    # Test 8: Gestion d'erreurs
    print("\n⚠️ Test 8: Gestion d'erreurs")
    try:
        try:
            geoindexpy.calculate_index(
                image={"nir": np.array([0.5])},
                index="NDVI"
            )
            assert False, "Devrait échouer"
        except geoindexpy.MissingBandError:
            pass  # Attendu
        tests_passed += 1
        print("✅ Test 8 réussi")
    except Exception as e:
        tests_failed += 1
        print(f"❌ Test 8 échoué: {e}")
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"Tests réussis: {tests_passed}")
    print(f"Tests échoués: {tests_failed}")
    print(f"Total: {tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        return 0
    else:
        print(f"\n❌ {tests_failed} TEST(S) ÉCHOUÉ(S)")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
```

### Exécution de la Suite de Tests

```bash
# Sauvegarder le script ci-dessus comme test_complet.py
python test_complet.py
```

---

## 🛠️ Dépannage

### Problèmes Courants

#### Problème Spécifique : Données Brutes Sentinel-2

**Symptôme**: Les indices calculés ont des valeurs anormales (ex: EVI min=-1597.5, max=2245 au lieu de [-1, 1])

**Cause**: Les bandes d'entrée contiennent des valeurs brutes (DN) au lieu de réflectance (0-1)

**Solution**: Convertir les données brutes en réflectance avant calcul

```python
import os
import numpy as np
import geoindexpy

# Nettoyage PROJ
for var in ("PROJ_LIB", "PROJ_DATA"):
    val = os.environ.get(var, "")
    if val and ("postgres" in val.lower() or not os.path.exists(os.path.join(val, "proj.db"))):
        os.environ.pop(var, None)

votre_image = "chemin/vers/image.tif"
dataset = geoindexpy.open_raster(votre_image)

# Vérifier les valeurs brutes
print(f"Valeurs brutes: min={np.min(dataset.bands['B1'])}, max={np.max(dataset.bands['B1'])}")

# Conversion en réflectance
SCALE_FACTOR = 12000.0  # Ajuster selon vos données (ex: 10000 pour max≈10000)
reflectance_bands = {}
for role, band_name in {"blue": "B1", "green": "B2", "red": "B3", "nir": "B4"}.items():
    if band_name in dataset.bands:
        reflectance_bands[role] = np.clip(dataset.bands[band_name] / SCALE_FACTOR, 0.0, 1.0)

# Calcul avec données converties
evi_result = geoindexpy.calculate_index(image=reflectance_bands, index="EVI")
print(f"EVI corrigé: min={evi_result.summary()['min']:.4f}, max={evi_result.summary()['max']:.4f}")
```

**Facteurs d'échelle courants**:
- Sentinel-2 L2A/L1C: 10000-12000
- Données 8-bit: 255
- Données 16-bit: 65535

#### 1. Erreur PROJ_LIB
```python
import os
for var in ("PROJ_LIB", "PROJ_DATA"):
    val = os.environ.get(var, "")
    if val and ("postgres" in val.lower() or not os.path.exists(os.path.join(val, "proj.db"))):
        os.environ.pop(var, None)
```

#### 2. Import Rasterio échoue
```bash
pip uninstall rasterio
pip install rasterio --no-binary rasterio
```

#### 3. Tests échouent avec GeoTIFF
```bash
# Vérifier que les fichiers de test existent
ls test_data/

# Recréer les fichiers de test
python examples/multispectral_sentinel2.py
```

#### 4. Problèmes de mémoire avec grands rasters
```python
# Utiliser des rasters plus petits pour les tests
height, width = 64, 64  # Au lieu de 1024, 1024
```

### Vérification de l'Environnement

```bash
# Vérifier les packages installés
pip list | grep -E "(numpy|rasterio|geoindexpy)"

# Vérifier les versions
python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
python -c "import rasterio; print(f'Rasterio: {rasterio.__version__}')"
python -c "import geoindexpy; print(f'GeoIndexPy: {geoindexpy.__version__}')"
```

---

## 📚 Ressources Supplémentaires

- Documentation officielle: https://github.com/sowsalim01/geoindexpy
- Tests unitaires: `tests/unit/`
- Tests scientifiques: `tests/scientific/`
- Tests d'intégration: `tests/integration/`
- Exemples: `examples/`

---

## 🎯 Checklist de Test Complet

- [ ] Installation et configuration
- [ ] Tests avec données synthétiques 1D
- [ ] Tests avec données synthétiques 2D
- [ ] Tests avec GeoTIFF Sentinel-2
- [ ] Tests avec GeoTIFF Landsat 8
- [ ] Validation des 9 indices scientifiques
- [ ] Tests des catégories d'indices
- [ ] Tests de mapping de capteurs
- [ ] Tests du registre d'indices
- [ ] Tests de statistiques et export
- [ ] Workflow complet d'intégration
- [ ] Tests de bandes personnalisées
- [ ] Tests de gestion d'erreurs
- [ ] Suite de tests automatisée

---

**Créé pour GeoIndexPy par Mamadou SOW**
**Version 0.1.0 - 2026**
