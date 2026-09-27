# Explicit Band Mapping Feature - Implementation Summary

## 🎯 Objective

Implement explicit and flexible band management for GeoIndexPy, allowing users to define band-to-spectral-role mappings without any assumptions about band numbering or naming conventions, similar to GeoIndexR.

## ✅ Requirements Met

### 1. **Explicit User Mapping Priority**
- Users can explicitly define which raster bands correspond to which spectral roles
- No automatic assumptions about band numbering
- Takes priority over sensor presets

### 2. **Flexible Input Types**
- **Integer indices**: `bands={"red": 3, "nir": 4}`
- **String names**: `bands={"red": "B3", "nir": "B4"}`
- **Custom names**: `bands={"red": "image_mai2024_3", "nir": "image_mai2024_4"}`

### 3. **Comprehensive Validation**
- Checks all required bands are provided
- Validates band existence in raster
- Provides clear error messages for missing bands
- Validates band compatibility with index requirements

### 4. **Generic System**
- Works with any raster format
- Independent of sensor conventions
- Fallback to automatic matching only when no explicit mapping provided

## 🔧 Implementation Details

### Modified Files

#### 1. `src/geoindexpy/bands/resolver.py`
- **Enhanced `BandResolver.__init__`**: Now accepts both string and integer values in `band_mapping`
- **Updated `resolve()` method**: Explicit mapping takes absolute priority over sensor presets
- **Improved error messages**: Clear indication when explicit mapping points to non-existent bands
- **Type hints**: Updated to support `Union[str, int]` for band identifiers

#### 2. `src/geoindexpy/raster/io.py`
- **Enhanced `RasterDataset`**: Added integer band access support
- **New `__getitem__`**: Accepts both string names and integer indices (1-based)
- **New `__contains__`**: Checks band existence by name or index
- **New `band_count()` method**: Returns number of bands in dataset

#### 3. `src/geoindexpy/core/engine.py`
- **Updated `calculate_index()`**: Enhanced documentation for explicit mapping
- **Updated `calculate_indices()`**: Same enhancements for batch processing
- **Type hints**: Updated parameter types to `Union[str, int]`

### New Files

#### 1. `tests/unit/test_explicit_band_mapping.py`
- **18 comprehensive tests** covering all aspects of explicit mapping
- Tests for integer indices, string names, custom names
- Error handling tests (missing bands, incomplete mapping)
- Priority tests (explicit mapping vs sensor presets)
- Practical examples similar to GeoIndexR usage

#### 2. `examples/explicit_band_mapping.py`
- **9 practical examples** demonstrating the feature
- Shows different input types and use cases
- Error handling demonstrations
- Multiple indices with different band requirements

## 📊 API Examples

### Basic Usage
```python
# Integer indices
ndvi = geoindexpy.calculate_index(
    image_path,
    "NDVI",
    bands={"red": 3, "nir": 4}
)

# String names
ndvi = geoindexpy.calculate_index(
    image_path,
    "NDVI",
    bands={"red": "B3", "nir": "B4"}
)

# Custom names (GeoIndexR style)
ndvi = geoindexpy.calculate_index(
    image_path,
    "NDVI",
    bands={
        "red": "image_mai2024_3",
        "nir": "image_mai2024_4"
    }
)
```

### Multiple Indices
```python
# Different band requirements
evi = geoindexpy.calculate_index(
    image_path,
    "EVI",
    bands={"blue": 1, "red": 3, "nir": 4}
)

gndvi = geoindexpy.calculate_index(
    image_path,
    "GNDVI",
    bands={"green": 2, "nir": 4}
)
```

### Batch Processing
```python
results = geoindexpy.calculate_indices(
    image_path,
    indices=["NDVI", "SAVI", "GNDVI"],
    bands={"red": 3, "nir": 4, "green": 2}
)
```

## 🛡️ Error Handling

### Missing Band in Mapping
```python
# Error: missing 'nir' in mapping
try:
    geoindexpy.calculate_index(
        image_path,
        "NDVI",
        bands={"red": 3}  # Missing nir
    )
except geoindexpy.MissingBandError as e:
    # Clear error: "Index 'resolution(nir)' cannot be computed..."
    pass
```

### Non-existent Band
```python
# Error: band 99 doesn't exist
try:
    geoindexpy.calculate_index(
        image_path,
        "NDVI",
        bands={"red": 3, "nir": 99}  # Band 99 doesn't exist
    )
except geoindexpy.MissingBandError as e:
    # Clear error: "explicit mapping for 'nir' cannot be computed..."
    pass
```

## ✅ Test Results

All 18 tests in `test_explicit_band_mapping.py` pass successfully:
- ✅ Explicit mapping with string names
- ✅ Explicit mapping with integer indices
- ✅ Explicit mapping priority over sensor
- ✅ EVI with multiple bands
- ✅ GNDVI mapping
- ✅ Missing band error handling
- ✅ Incomplete mapping error
- ✅ Custom band names
- ✅ Case-insensitive mapping
- ✅ Multiple indices processing
- ✅ No mapping fallback
- ✅ Override automatic detection
- ✅ RasterDataset integer access
- ✅ RasterDataset contains check
- ✅ RasterDataset band count
- ✅ GeoIndexR style examples
- ✅ Simple integer mapping
- ✅ Multiple indices different mappings

## 🔄 Backward Compatibility

The implementation maintains full backward compatibility:
- Existing code without explicit mapping continues to work
- Sensor presets still function when no explicit mapping is provided
- Automatic band detection remains as fallback
- All existing tests continue to pass

## 📈 Performance Impact

Minimal performance impact:
- Explicit mapping resolution is O(1) for direct lookups
- No additional overhead when explicit mapping is not used
- Validation adds negligible overhead for error checking

## 🎯 Key Benefits

1. **User Control**: Complete control over band-to-role mapping
2. **Flexibility**: Works with any raster format and naming convention
3. **Clarity**: Explicit mappings make code self-documenting
4. **Safety**: Comprehensive validation prevents silent errors
5. **Compatibility**: Matches GeoIndexR functionality for easy migration

## 🚀 Future Enhancements

Potential future improvements:
- Support for band ranges (e.g., `{"nir": [8, 9]}`)
- Band aliases and synonyms in explicit mapping
- Validation warnings for suspicious mappings
- Interactive band selection for GUI applications

## 📝 Documentation Updates

- Updated README.md with explicit mapping examples
- Added feature to feature comparison table
- Created comprehensive examples file
- Updated API documentation in docstrings

---

**Implementation completed and tested successfully**
**All requirements met and fully functional**
