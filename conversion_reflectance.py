"""
Script pour convertir les données brutes Sentinel-2 en réflectance
puis calculer les indices spectraux
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

print("=== Conversion des données brutes en réflectance ===")

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

# Facteurs de conversion pour Sentinel-2 (ajusté selon vos données max=11920)
# Valeurs typiques pour Sentinel-2 L1C/L2A
# Facteur de quantification = 10000 pour L2A en réflectance * 10000
# On utilise 12000 pour être sûr avec max=11920
SENTINEL2_SCALE_FACTOR = 12000.0  # Ajusté selon vos données (max=11920)

def convert_to_reflectance(band_data, scale_factor=10000.0):
    """Convertit les données brutes en réflectance"""
    # Éviter la division par zéro
    reflectance = np.where(band_data > 0, band_data / scale_factor, 0.0)
    # Clipper entre 0 et 1
    reflectance = np.clip(reflectance, 0.0, 1.0)
    return reflectance

# Conversion des bandes
reflectance_bands = {}
for role, band_name in mapping.items():
    if band_name in dataset.bands:
        raw_data = dataset.bands[band_name]
        print(f"\nConversion {role.upper()} ({band_name}):")
        print(f"  Avant: min={np.min(raw_data):.2f}, max={np.max(raw_data):.2f}")
        
        # Conversion
        reflectance = convert_to_reflectance(raw_data, SENTINEL2_SCALE_FACTOR)
        reflectance_bands[role] = reflectance
        
        print(f"  Après: min={np.min(reflectance):.4f}, max={np.max(reflectance):.4f}")
    else:
        print(f"\n{role.upper()} ({band_name}): ❌ Bande non trouvée")

print("\n=== Calcul des indices avec données converties ===")

# Calcul des indices avec les données converties
indices_compatibles = ["NDVI", "SAVI", "EVI", "GNDVI"]

results = geoindexpy.calculate_indices(
    image=reflectance_bands,  # Utiliser les bandes converties
    indices=indices_compatibles,
    # Pas besoin de mapping car on utilise déjà les noms de rôles
)

# Affichage et export
output_dir = Path("resultats_evi_corriges")
output_dir.mkdir(exist_ok=True)

for name, result in results.items():
    stats = result.summary()
    print(f"\n{name}:")
    print(f"  Min: {stats['min']:.4f}")
    print(f"  Max: {stats['max']:.4f}")
    print(f"  Mean: {stats['mean']:.4f}")
    print(f"  Std: {stats['std']:.4f}")
    
    # Vérification des valeurs plausibles
    if name == "EVI":
        if stats['min'] < -1.0 or stats['max'] > 1.0:
            print(f"  ⚠️  Valeurs EVI encore anormales - vérifier le facteur d'échelle")
        else:
            print(f"  ✅ Valeurs EVI dans la plage normale [-1, 1]")
    
    # Export avec métadonnées préservées
    result.metadata = dataset.metadata  # Préserver les métadonnées géospatiales
    output_path = output_dir / f"{name.lower()}_corrige.tif"
    result.save(output_path)
    print(f"  Exporté: {output_path}")

print(f"\n✅ Traitement terminé !")
print(f"Résultats dans: {output_dir}")
print(f"\nSi les valeurs EVI sont encore anormales, ajustez SENTINEL2_SCALE_FACTOR")
