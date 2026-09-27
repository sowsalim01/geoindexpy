"""
Script de diagnostic pour vérifier les valeurs des bandes d'entrée
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

print("=== Diagnostic des valeurs d'entrée ===")

# Ouverture du dataset
dataset = geoindexpy.open_raster(votre_image)
print(f"Bandes disponibles: {dataset.band_names()}")

# Mapping personnalisé
mapping = {
    "blue": "B1",
    "green": "B2", 
    "red": "B3",
    "nir": "B4"
}

# Analyse des valeurs de chaque bande
for role, band_name in mapping.items():
    if band_name in dataset.bands:
        band_data = dataset.bands[band_name]
        print(f"\n{role.upper()} ({band_name}):")
        print(f"  Forme: {band_data.shape}")
        print(f"  Min: {np.min(band_data):.2f}")
        print(f"  Max: {np.max(band_data):.2f}")
        print(f"  Mean: {np.mean(band_data):.2f}")
        print(f"  Std: {np.std(band_data):.2f}")
        
        # Diagnostic du type de données
        if np.max(band_data) > 1.0:
            print(f"  ⚠️  DONNÉES BRUTES détectées (valeurs > 1.0)")
            print(f"      Conversion en réflectance nécessaire")
        else:
            print(f"  ✅ Données de réflectance (valeurs 0-1)")
    else:
        print(f"\n{role.upper()} ({band_name}): ❌ Bande non trouvée")

print("\n=== Recommandations ===")
print("Si les valeurs > 1.0: Vos données sont brutes (DN)")
print("Solution: Convertir en réflectance ou utiliser le facteur d'échelle")
