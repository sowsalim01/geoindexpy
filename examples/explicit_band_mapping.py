"""
Examples of explicit band mapping - the core feature for flexible band management.
This demonstrates how users can explicitly define band-to-spectral-role mappings
without any assumptions about band numbering or naming conventions.
"""

import numpy as np
import geoindexpy

print("=" * 70)
print("EXPLICIT BAND MAPPING EXAMPLES")
print("=" * 70)

# Example 1: Using integer band indices (most common case)
print("\n1. Using integer band indices:")
print("-" * 70)

# Simulate a raster with 4 bands numbered 1, 2, 3, 4
bands_with_indices = {
    "1": np.random.uniform(0.02, 0.15, (10, 10)).astype(np.float32),  # Band 1
    "2": np.random.uniform(0.1, 0.25, (10, 10)).astype(np.float32),   # Band 2
    "3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),    # Band 3
    "4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),    # Band 4
}

# Explicit mapping: red = 3, nir = 4
ndvi = geoindexpy.calculate_index(
    bands_with_indices,
    "NDVI",
    bands={"red": 3, "nir": 4}
)

print(f"NDVI with bands={{'red': 3, 'nir': 4}}:")
print(f"  Shape: {ndvi.shape}")
print(f"  Min: {ndvi.summary()['min']:.4f}, Max: {ndvi.summary()['max']:.4f}")

# Example 2: Using string band names
print("\n2. Using string band names:")
print("-" * 70)

bands_with_names = {
    "B1": np.random.uniform(0.02, 0.15, (10, 10)).astype(np.float32),
    "B2": np.random.uniform(0.1, 0.25, (10, 10)).astype(np.float32),
    "B3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
    "B4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),
}

# Explicit mapping using band names
ndvi = geoindexpy.calculate_index(
    bands_with_names,
    "NDVI",
    bands={"red": "B3", "nir": "B4"}
)

print(f"NDVI with bands={{'red': 'B3', 'nir': 'B4'}}:")
print(f"  Shape: {ndvi.shape}")
print(f"  Min: {ndvi.summary()['min']:.4f}, Max: {ndvi.summary()['max']:.4f}")

# Example 3: Complex/custom band names (like GeoIndexR example)
print("\n3. Using custom band names (GeoIndexR style):")
print("-" * 70)

bands_custom = {
    "image_mai2024_1": np.random.uniform(0.02, 0.15, (10, 10)).astype(np.float32),
    "image_mai2024_2": np.random.uniform(0.1, 0.25, (10, 10)).astype(np.float32),
    "image_mai2024_3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
    "image_mai2024_4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),
}

# GeoIndexR style: bands = c(red = "image_mai2024_3", nir = "image_mai2024_4")
ndvi = geoindexpy.calculate_index(
    bands_custom,
    "NDVI",
    bands={
        "red": "image_mai2024_3",
        "nir": "image_mai2024_4"
    }
)

print(f"NDVI with custom band names:")
print(f"  Shape: {ndvi.shape}")
print(f"  Min: {ndvi.summary()['min']:.4f}, Max: {ndvi.summary()['max']:.4f}")

# Example 4: Multiple indices with different band requirements
print("\n4. Multiple indices with different band requirements:")
print("-" * 70)

bands_4band = {
    "1": np.random.uniform(0.02, 0.15, (10, 10)).astype(np.float32),  # Blue
    "2": np.random.uniform(0.1, 0.25, (10, 10)).astype(np.float32),   # Green
    "3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),    # Red
    "4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),    # NIR
}

# Different indices with different band requirements
ndvi = geoindexpy.calculate_index(
    bands_4band, "NDVI",
    bands={"red": 3, "nir": 4}
)

savi = geoindexpy.calculate_index(
    bands_4band, "SAVI",
    bands={"red": 3, "nir": 4}
)

evi = geoindexpy.calculate_index(
    bands_4band, "EVI",
    bands={"blue": 1, "red": 3, "nir": 4}
)

gndvi = geoindexpy.calculate_index(
    bands_4band, "GNDVI",
    bands={"green": 2, "nir": 4}
)

print(f"NDVI (red=3, nir=4): min={ndvi.summary()['min']:.4f}")
print(f"SAVI (red=3, nir=4): min={savi.summary()['min']:.4f}")
print(f"EVI  (blue=1, red=3, nir=4): min={evi.summary()['min']:.4f}")
print(f"GNDVI (green=2, nir=4): min={gndvi.summary()['min']:.4f}")

# Example 5: Using calculate_indices with explicit mapping
print("\n5. Multiple indices with calculate_indices:")
print("-" * 70)

results = geoindexpy.calculate_indices(
    bands_4band,
    indices=["NDVI", "SAVI", "GNDVI"],
    bands={"red": 3, "nir": 4, "green": 2}
)

for name, result in results.items():
    stats = result.summary()
    print(f"{name}: min={stats['min']:.4f}, max={stats['max']:.4f}")

# Example 6: Error handling - missing band in mapping
print("\n6. Error handling - incomplete mapping:")
print("-" * 70)

try:
    # This will fail because we only map 'red' but NDVI also needs 'nir'
    geoindexpy.calculate_index(
        bands_4band,
        "NDVI",
        bands={"red": 3}  # Missing 'nir'
    )
except geoindexpy.MissingBandError as e:
    print(f"[OK] Expected error caught: {e}")

# Example 7: Error handling - mapping to non-existent band
print("\n7. Error handling - mapping to non-existent band:")
print("-" * 70)

try:
    # This will fail because band 99 doesn't exist
    geoindexpy.calculate_index(
        bands_4band,
        "NDVI",
        bands={"red": 3, "nir": 99}  # Band 99 doesn't exist
    )
except geoindexpy.MissingBandError as e:
    print(f"[OK] Expected error caught: {e}")

# Example 8: Explicit mapping overrides sensor presets
print("\n8. Explicit mapping overrides sensor presets:")
print("-" * 70)

# Even with sensor='sentinel2', explicit mapping takes priority
result = geoindexpy.calculate_index(
    bands_4band,
    "NDVI",
    bands={"red": 3, "nir": 4},  # Explicit mapping
    sensor="sentinel2"  # This is ignored for bands with explicit mapping
)

print(f"NDVI with explicit mapping + sensor='sentinel2':")
print(f"  Shape: {result.shape}")
print(f"  Min: {result.summary()['min']:.4f}")

# Example 9: Case-insensitive mapping
print("\n9. Case-insensitive band mapping:")
print("-" * 70)

bands_case = {
    "B1": np.random.uniform(0.02, 0.15, (10, 10)).astype(np.float32),
    "B2": np.random.uniform(0.1, 0.25, (10, 10)).astype(np.float32),
    "B3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
    "B4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),
}

# Use lowercase in mapping, bands are uppercase
result = geoindexpy.calculate_index(
    bands_case,
    "NDVI",
    bands={"red": "b3", "nir": "b4"}  # lowercase
)

print(f"NDVI with case-insensitive mapping:")
print(f"  Shape: {result.shape}")
print(f"  Min: {result.summary()['min']:.4f}")

print("\n" + "=" * 70)
print("All examples completed successfully!")
print("=" * 70)
