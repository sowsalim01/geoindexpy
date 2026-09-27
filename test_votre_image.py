"""
Script adapté pour votre image Sentinel avec bandes B1, B2, B3, B4
Mapping personnalisé : B1=Blue, B2=Green, B3=Red, B4=NIR
"""

import os
import geoindexpy
from pathlib import Path

# Nettoyage environnement PROJ (important pour Windows)
for var in ("PROJ_LIB", "PROJ_DATA"):
    val = os.environ.get(var, "")
    if val and ("postgres" in val.lower() or not os.path.exists(os.path.join(val, "proj.db"))):
        os.environ.pop(var, None)

# Remplacez par le chemin de votre image
votre_image = "chemin/vers/votre_image_sentinel.tif"

# Mapping personnalisé pour vos bandes B1, B2, B3, B4
# B1 = Blue, B2 = Green, B3 = Red, B4 = NIR
mapping_personnalise = {
    "blue": "B1",
    "green": "B2", 
    "red": "B3",
    "nir": "B4"
}

print("=== Analyse de votre image Sentinel ===")

# 1. Ouverture et inspection
dataset = geoindexpy.open_raster(votre_image)
print(f"Forme de l'image: {dataset.shape}")
print(f"Bandes disponibles: {dataset.band_names()}")
print(f"CRS: {dataset.metadata.crs}")
print(f"Résolution: {dataset.metadata.resolution}")

# 2. Calcul d'indices avec mapping personnalisé
print("\n=== Calcul des indices ===")

# Indices possibles avec vos 4 bandes:
# NDVI (nir, red), NDWI (green, nir), GNDVI (nir, green)
# SAVI (nir, red), EVI (nir, red, blue) - manque SWIR pour NDWI, MNDWI, NDBI, NDMI, BSI

indices_compatibles = ["NDVI", "SAVI", "EVI", "GNDVI"]

results = geoindexpy.calculate_indices(
    image=votre_image,
    indices=indices_compatibles,
    bands=mapping_personnalise  # Utilisation du mapping personnalisé
)

# 3. Affichage des résultats et export
print("\n=== Résultats ===")
output_dir = Path("resultats_votre_image")
output_dir.mkdir(exist_ok=True)

for name, result in results.items():
    stats = result.summary()
    print(f"\n{name}:")
    print(f"  Min: {stats['min']:.3f}")
    print(f"  Max: {stats['max']:.3f}")
    print(f"  Mean: {stats['mean']:.3f}")
    print(f"  Std: {stats['std']:.3f}")
    print(f"  Pixels valides: {stats['valid_pixels']}/{stats['total_pixels']}")
    
    # Export
    output_path = output_dir / f"{name.lower()}_resultat.tif"
    result.save(output_path)
    print(f"  Exporté: {output_path}")

print("\n✅ Traitement terminé avec succès !")
print(f"Les résultats sont dans le dossier: {output_dir}")
