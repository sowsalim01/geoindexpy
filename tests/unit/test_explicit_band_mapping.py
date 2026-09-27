"""
Tests for explicit band mapping functionality - the core requirement for flexible band management.
Tests that users can explicitly define band-to-spectral-role mappings without assumptions.
"""

import numpy as np
import pytest
import geoindexpy
from geoindexpy.exceptions import MissingBandError


class TestExplicitBandMapping:
    """Test explicit band mapping with various input types."""

    def test_explicit_mapping_with_string_names(self):
        """Test explicit mapping using string band names."""
        # Create raster with bands named "1", "2", "3", "4"
        bands = {
            "1": np.random.uniform(0.1, 0.3, (10, 10)).astype(np.float32),
            "2": np.random.uniform(0.2, 0.4, (10, 10)).astype(np.float32),
            "3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
            "4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),
        }

        # Explicit mapping: red=3, nir=4
        result = geoindexpy.calculate_index(
            image=bands,
            index="NDVI",
            bands={"red": "3", "nir": "4"}
        )

        assert result.shape == (10, 10)
        stats = result.summary()
        assert stats["valid_pixels"] == 100
        assert -1.0 <= stats["min"] <= 1.0
        assert -1.0 <= stats["max"] <= 1.0

    def test_explicit_mapping_with_integer_indices(self):
        """Test explicit mapping using integer band indices."""
        # Create raster with bands named as numbers (1, 2, 3, 4)
        bands = {
            "1": np.random.uniform(0.1, 0.3, (10, 10)).astype(np.float32),
            "2": np.random.uniform(0.2, 0.4, (10, 10)).astype(np.float32),
            "3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
            "4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),
        }

        # Explicit mapping using integers: red=3, nir=4
        result = geoindexpy.calculate_index(
            image=bands,
            index="NDVI",
            bands={"red": 3, "nir": 4}
        )

        assert result.shape == (10, 10)
        stats = result.summary()
        assert stats["valid_pixels"] == 100

    def test_explicit_mapping_priority_over_sensor(self):
        """Test that explicit mapping takes priority over sensor presets."""
        bands = {
            "B1": np.random.uniform(0.1, 0.3, (10, 10)).astype(np.float32),
            "B2": np.random.uniform(0.2, 0.4, (10, 10)).astype(np.float32),
            "B3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
            "B4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),
        }

        # Even with sensor='sentinel2', explicit mapping should override
        result = geoindexpy.calculate_index(
            image=bands,
            index="NDVI",
            bands={"red": "B3", "nir": "B4"},  # Explicit mapping
            sensor="sentinel2"  # This should be ignored for these bands
        )

        assert result.shape == (10, 10)

    def test_explicit_mapping_evi_multiple_bands(self):
        """Test explicit mapping for indices requiring multiple bands (EVI)."""
        bands = {
            "1": np.random.uniform(0.02, 0.15, (10, 10)).astype(np.float32),
            "2": np.random.uniform(0.1, 0.25, (10, 10)).astype(np.float32),
            "3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
            "4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),
        }

        # EVI requires blue, red, nir
        result = geoindexpy.calculate_index(
            image=bands,
            index="EVI",
            bands={"blue": "1", "red": "3", "nir": "4"}
        )

        assert result.shape == (10, 10)
        stats = result.summary()
        assert -1.0 <= stats["min"] <= 1.0
        assert -1.0 <= stats["max"] <= 1.0

    def test_explicit_mapping_gndvi(self):
        """Test explicit mapping for GNDVI (green, nir)."""
        bands = {
            "band_1": np.random.uniform(0.02, 0.15, (10, 10)).astype(np.float32),
            "band_2": np.random.uniform(0.1, 0.25, (10, 10)).astype(np.float32),
            "band_3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
            "band_4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),
        }

        result = geoindexpy.calculate_index(
            image=bands,
            index="GNDVI",
            bands={"green": "band_2", "nir": "band_4"}
        )

        assert result.shape == (10, 10)

    def test_explicit_mapping_missing_band_error(self):
        """Test that explicit mapping to non-existent band raises clear error."""
        bands = {
            "B1": np.random.uniform(0.1, 0.3, (10, 10)).astype(np.float32),
            "B2": np.random.uniform(0.2, 0.4, (10, 10)).astype(np.float32),
            "B3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
        }

        # Try to map to non-existent band "B99"
        with pytest.raises(MissingBandError) as exc_info:
            geoindexpy.calculate_index(
                image=bands,
                index="NDVI",
                bands={"red": "B3", "nir": "B99"}  # B99 doesn't exist
            )

        error_msg = str(exc_info.value)
        assert "B99" in error_msg or "nir" in error_msg

    def test_explicit_mapping_incomplete_mapping(self):
        """Test error when not all required bands are explicitly mapped."""
        bands = {
            "B1": np.random.uniform(0.1, 0.3, (10, 10)).astype(np.float32),
            "B2": np.random.uniform(0.2, 0.4, (10, 10)).astype(np.float32),
            "B3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
            "B4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),
        }

        # Only map red, not nir
        with pytest.raises(MissingBandError) as exc_info:
            geoindexpy.calculate_index(
                image=bands,
                index="NDVI",
                bands={"red": "B3"}  # Missing nir mapping
            )

        error_msg = str(exc_info.value)
        assert "nir" in error_msg.lower()

    def test_explicit_mapping_with_custom_band_names(self):
        """Test explicit mapping with custom/complex band names."""
        bands = {
            "image_mai2024_1": np.random.uniform(0.02, 0.15, (10, 10)).astype(np.float32),
            "image_mai2024_2": np.random.uniform(0.1, 0.25, (10, 10)).astype(np.float32),
            "image_mai2024_3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
            "image_mai2024_4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),
        }

        result = geoindexpy.calculate_index(
            image=bands,
            index="NDVI",
            bands={
                "red": "image_mai2024_3",
                "nir": "image_mai2024_4"
            }
        )

        assert result.shape == (10, 10)

    def test_explicit_mapping_case_insensitive(self):
        """Test that explicit mapping is case-insensitive for band names."""
        bands = {
            "B1": np.random.uniform(0.1, 0.3, (10, 10)).astype(np.float32),
            "B2": np.random.uniform(0.2, 0.4, (10, 10)).astype(np.float32),
            "B3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
            "B4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),
        }

        # Use different case in mapping
        result = geoindexpy.calculate_index(
            image=bands,
            index="NDVI",
            bands={"red": "b3", "nir": "b4"}  # lowercase
        )

        assert result.shape == (10, 10)

    def test_explicit_mapping_multiple_indices(self):
        """Test explicit mapping works with calculate_indices."""
        bands = {
            "1": np.random.uniform(0.02, 0.15, (10, 10)).astype(np.float32),
            "2": np.random.uniform(0.1, 0.25, (10, 10)).astype(np.float32),
            "3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
            "4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),
        }

        results = geoindexpy.calculate_indices(
            image=bands,
            indices=["NDVI", "SAVI", "GNDVI"],
            bands={"red": "3", "nir": "4", "green": "2"}
        )

        assert len(results) == 3
        assert "NDVI" in results
        assert "SAVI" in results
        assert "GNDVI" in results

        for result in results.values():
            assert result.shape == (10, 10)

    def test_no_mapping_uses_available_bands(self):
        """Test that without explicit mapping, system uses available band names."""
        bands = {
            "nir": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),
            "red": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
        }

        # No explicit mapping, should work if band names match
        result = geoindexpy.calculate_index(
            image=bands,
            index="NDVI"
        )

        assert result.shape == (10, 10)

    def test_explicit_mapping_overrides_automatic_detection(self):
        """Test that explicit mapping overrides automatic band detection."""
        bands = {
            "nir": np.random.uniform(0.1, 0.3, (10, 10)).astype(np.float32),  # This is actually low values
            "red": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),  # This is actually high values
            "real_nir": np.random.uniform(0.7, 0.9, (10, 10)).astype(np.float32),
            "real_red": np.random.uniform(0.1, 0.3, (10, 10)).astype(np.float32),
        }

        # Without mapping, would use "nir" and "red" (wrong values)
        # With explicit mapping, use "real_nir" and "real_red" (correct values)
        result = geoindexpy.calculate_index(
            image=bands,
            index="NDVI",
            bands={"nir": "real_nir", "red": "real_red"}
        )

        assert result.shape == (10, 10)
        # With correct mapping, NDVI should be positive (nir > red)
        stats = result.summary()
        assert stats["mean"] > 0  # Should be positive with correct band assignment


class TestRasterDatasetBandAccess:
    """Test enhanced RasterDataset with integer band access."""

    def test_raster_dataset_integer_access(self):
        """Test accessing bands by integer index."""
        from geoindexpy.raster.io import RasterDataset
        from geoindexpy.raster.metadata import RasterMetadata

        bands = {
            "B1": np.ones((5, 5)) * 1.0,
            "B2": np.ones((5, 5)) * 2.0,
            "B3": np.ones((5, 5)) * 3.0,
            "B4": np.ones((5, 5)) * 4.0,
        }

        metadata = RasterMetadata(
            width=5, height=5, count=4, crs=None, transform=None,
            dtype="float32", nodata=None, band_names=tuple(bands.keys())
        )

        dataset = RasterDataset(bands=bands, metadata=metadata)

        # Test integer access (1-based)
        assert np.allclose(dataset[1], bands["B1"])
        assert np.allclose(dataset[2], bands["B2"])
        assert np.allclose(dataset[3], bands["B3"])
        assert np.allclose(dataset[4], bands["B4"])

    def test_raster_dataset_contains_integer(self):
        """Test __contains__ with integer indices."""
        from geoindexpy.raster.io import RasterDataset
        from geoindexpy.raster.metadata import RasterMetadata

        bands = {
            "B1": np.ones((5, 5)),
            "B2": np.ones((5, 5)),
        }

        metadata = RasterMetadata(
            width=5, height=5, count=2, crs=None, transform=None,
            dtype="float32", nodata=None, band_names=tuple(bands.keys())
        )

        dataset = RasterDataset(bands=bands, metadata=metadata)

        assert 1 in dataset
        assert 2 in dataset
        assert 3 not in dataset
        assert "B1" in dataset
        assert "B99" not in dataset

    def test_raster_dataset_band_count(self):
        """Test band_count method."""
        from geoindexpy.raster.io import RasterDataset
        from geoindexpy.raster.metadata import RasterMetadata

        bands = {
            "B1": np.ones((5, 5)),
            "B2": np.ones((5, 5)),
            "B3": np.ones((5, 5)),
        }

        metadata = RasterMetadata(
            width=5, height=5, count=3, crs=None, transform=None,
            dtype="float32", nodata=None, band_names=tuple(bands.keys())
        )

        dataset = RasterDataset(bands=bands, metadata=metadata)
        assert dataset.band_count() == 3


class TestPracticalExamples:
    """Test practical examples similar to GeoIndexR usage."""

    def test_example_geoiindexr_style(self):
        """Test example similar to GeoIndexR documentation."""
        # Simulate a raster with 4 bands
        bands = {
            "image_mai2024_1": np.random.uniform(0.02, 0.15, (10, 10)).astype(np.float32),
            "image_mai2024_2": np.random.uniform(0.1, 0.25, (10, 10)).astype(np.float32),
            "image_mai2024_3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
            "image_mai2024_4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),
        }

        # GeoIndexR style: bands = c(red = "image_mai2024_3", nir = "image_mai2024_4")
        ndvi = geoindexpy.calculate_index(
            bands,
            "NDVI",
            bands={
                "red": "image_mai2024_3",
                "nir": "image_mai2024_4"
            }
        )

        assert ndvi.shape == (10, 10)

    def test_example_simple_integer_mapping(self):
        """Test simple integer mapping example."""
        bands = {
            "1": np.random.uniform(0.02, 0.15, (10, 10)).astype(np.float32),
            "2": np.random.uniform(0.1, 0.25, (10, 10)).astype(np.float32),
            "3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
            "4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),
        }

        # Simple: bands = c(red = 3, nir = 4)
        ndvi = geoindexpy.calculate_index(
            bands,
            "NDVI",
            bands={"red": 3, "nir": 4}
        )

        assert ndvi.shape == (10, 10)

    def test_example_multiple_indices_different_mappings(self):
        """Test different indices with different band requirements."""
        bands = {
            "1": np.random.uniform(0.02, 0.15, (10, 10)).astype(np.float32),
            "2": np.random.uniform(0.1, 0.25, (10, 10)).astype(np.float32),
            "3": np.random.uniform(0.3, 0.5, (10, 10)).astype(np.float32),
            "4": np.random.uniform(0.4, 0.8, (10, 10)).astype(np.float32),
        }

        # Different indices can use the same mapping
        ndvi = geoindexpy.calculate_index(bands, "NDVI", bands={"red": 3, "nir": 4})
        savi = geoindexpy.calculate_index(bands, "SAVI", bands={"red": 3, "nir": 4})
        evi = geoindexpy.calculate_index(bands, "EVI", bands={"blue": 1, "red": 3, "nir": 4})
        gndvi = geoindexpy.calculate_index(bands, "GNDVI", bands={"green": 2, "nir": 4})

        assert all(result.shape == (10, 10) for result in [ndvi, savi, evi, gndvi])
