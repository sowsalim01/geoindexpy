"""
Script pour calculer tous les indices compatibles avec conversion
automatique des données brutes en réflectance
"""

import os
import numpy as np
import geoindexpy
from pathlib import Path

# Nettoyage PROJ
for var in ("PROJ_LIB", "PROJ_DATA"):
    val = os.environ.get(var, "")
    if val and ("postgres" in val.lower() or not os.path.exists(os.path.join(val, "proj.db"))):
        os.environ.pop(var, None)

# Remplacez par votre chemin
votre_image = "chemin/vers/votre_image_sentinel.tif"

print("=== Calcul de tous les indices avec conversion ===")

# Ouverture du dataset
dataset = geoindexpy.open_raster(votre_image)
print(f"Image: {votre_image}")
print(f"Bandes: {dataset.band_names()}")

# Mapping pour vos bandes B1, B2, B3, B4
mapping = {
    "blue": "B1",
    "green": "B2", 
    "red": "B3",
    "nir": "B4"
}

# Conversion des données brutes en réflectance
SCALE_FACTOR = 12000.0

print(f"\nConversion des données brutes (facteur: {SCALE_FACTOR})")
reflectance_bands = {}
for role, band_name in mapping.items():
    if band_name in dataset.bands:
        raw = dataset.bands[band_name]
        reflectance = np.clip(raw / SCALE_FACTOR, 0.0, 1.0)
        reflectance_bands[role] = reflectance
        print(f"{role}: converti")

# Indices compatibles avec vos 4 bandes (Blue, Green, Red, NIR)
# NDVI (nir, red), SAVI (nir, red), EVI (nir, red, blue), GNDVI (nir, green)
indices_compatibles = ["NDVI", "SAVI", "EVI", "GNDVI"]

print(f"\n=== Calcul des indices: {indices_compatibles} ===")

results = geoindexpy.calculate_indices(
    image=reflectance_bands,
    indices=indices_compatibles
)

# Affichage et export
output_dir = Path("resultats_indices_corriges")
output_dir.mkdir(exist_ok=True)

for name, result in results.items():
    stats = result.summary()
    print(f"\n{name}:")
    print(f"  Min: {stats['min']:.4f}")
    print(f"  Max: {stats['max']:.4f}")
    print(f"  Mean: {stats['mean']:.4f}")
    
    # Vérification de la plage normale
    if -1.0 <= stats['min'] <= 1.0 and -1.0 <= stats['max'] <= 1.0:
        print(f"  ✅ Plage normale [-1, 1]")
    else:
        print(f"  ⚠️ Plage anormale")
    
    # Export avec métadonnées
    result.metadata = dataset.metadata
    output_path = output_dir / f"{name.lower()}_corrige.tif"
    result.save(output_path)
    print(f"  Exporté: {output_path}")

print(f"\n✅ Tous les indices calculés et exportés dans: {output_dir}")
