"""
Script simple et direct pour calculer l'EVI correctement
avec conversion automatique des données brutes (DN) en réflectance
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

print("=== Calcul EVI avec conversion automatique ===")

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
SCALE_FACTOR = 12000.0  # Ajusté pour max=11920

print(f"\nConversion des données brutes (facteur: {SCALE_FACTOR})")
reflectance_bands = {}
for role, band_name in mapping.items():
    if band_name in dataset.bands:
        raw = dataset.bands[band_name]
        reflectance = np.clip(raw / SCALE_FACTOR, 0.0, 1.0)
        reflectance_bands[role] = reflectance
        print(f"{role}: {np.min(raw):.0f}→{np.min(reflectance):.4f}, {np.max(raw):.0f}→{np.max(reflectance):.4f}")

# Calcul EVI avec données converties
print("\n=== Calcul EVI ===")
evi_result = geoindexpy.calculate_index(
    image=reflectance_bands,
    index="EVI"
)

stats = evi_result.summary()
print(f"EVI corrigé:")
print(f"  Min: {stats['min']:.4f}")
print(f"  Max: {stats['max']:.4f}")
print(f"  Mean: {stats['mean']:.4f}")
print(f"  Std: {stats['std']:.4f}")

# Vérification
if -1.0 <= stats['min'] <= 1.0 and -1.0 <= stats['max'] <= 1.0:
    print("✅ Valeurs EVI normales (plage [-1, 1])")
else:
    print("⚠️ Valeurs encore anormales - ajuster SCALE_FACTOR")

# Export
evi_result.metadata = dataset.metadata
output_path = Path("evi_corrige.tif")
evi_result.save(output_path)
print(f"\nExporté: {output_path}")
