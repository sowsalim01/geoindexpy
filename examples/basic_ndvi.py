"""Basic example: Direct spectral index computation with NumPy arrays."""

import numpy as np
import geoindexpy


def main() -> None:
    print("--- GeoIndexPy: Basic NDVI Calculation ---")

    # Simulate Near-Infrared and Red surface reflectance
    # (Values scaled between 0.0 and 1.0)
    nir = np.array([0.72, 0.68, 0.15, 0.05], dtype=np.float32)
    red = np.array([0.08, 0.12, 0.20, 0.04], dtype=np.float32)

    # 1. Direct function call
    ndvi_result = geoindexpy.ndvi(nir=nir, red=red)
    print("NIR bands: ", nir)
    print("RED bands: ", red)
    print("Calculated NDVI:", np.round(ndvi_result, 3))

    # 2. Inspecting index metadata from the scientific registry
    info = geoindexpy.get_index_info("NDVI")
    print("\n--- Scientific Index Metadata ---")
    print(f"Index: {info['long_name']} ({info['short_name']})")
    print(f"Category: {info['category']}")
    print(f"Formula: {info['formula']}")
    print(f"Reference: {info['reference']}")


if __name__ == "__main__":
    main()
