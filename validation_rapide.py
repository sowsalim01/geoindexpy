"""
Script de validation rapide pour vérifier que les données
sont bien en réflectance avant calcul d'indices
"""

import os
import numpy as np
import geoindexpy

# Nettoyage PROJ
for var in ("PROJ_LIB", "PROJ_DATA"):
    val = os.environ.get(var, "")
    if val and ("postgres" in val.lower() or not os.path.exists(os.path.join(val, "proj.db"))):
        os.environ.pop(var, None)

def valider_donnees(image_path, expected_scale_factor=12000.0):
    """Valide que les données sont dans le bon format pour le calcul d'indices"""
    
    dataset = geoindexpy.open_raster(image_path)
    print(f"=== Validation de {image_path} ===")
    print(f"Bandes: {dataset.band_names()}")
    
    # Vérifier les valeurs de chaque bande
    bandes_a_verifier = ["B1", "B2", "B3", "B4"]
    conversion_necessaire = False
    
    for bande in bandes_a_verifier:
        if bande in dataset.bands:
            data = dataset.bands[bande]
            min_val, max_val = np.min(data), np.max(data)
            print(f"{bande}: min={min_val:.1f}, max={max_val:.1f}")
            
            if max_val > 1.0:
                conversion_necessaire = True
                estimated_scale = max_val / 1.0
                print(f"  ⚠️  Données brutes détectées (échelle estimée: {estimated_scale:.0f})")
            else:
                print(f"  ✅ Données de réflectance")
    
    if conversion_necessaire:
        print(f"\n🔧 Conversion nécessaire avec facteur ≈ {expected_scale_factor:.0f}")
        print("Utilisez le script calcul_evi_corrige.py ou calcul_tous_indices_corrige.py")
    else:
        print("\n✅ Données prêtes pour le calcul direct d'indices")
    
    return not conversion_necessaire

# Utilisation
# valider_donnees("chemin/vers/votre_image.tif")
print("Pour utiliser: valider_donnees('chemin/vers/votre_image.tif')")
