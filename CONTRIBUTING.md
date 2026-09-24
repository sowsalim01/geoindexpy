# Contributing to GeoIndexPy

Thank you for your interest in contributing to GeoIndexPy! This document explains the workflow for contributions.

---

## Development Setup

```bash
git clone https://github.com/sowsalim01/geoindexpy.git
cd geoindexpy
pip install -e ".[dev]"
```

---

## Running Tests

```bash
pytest
pytest -v --tb=short    # verbose
pytest tests/unit/       # unit tests only
pytest tests/scientific/ # scientific validation
pytest tests/integration/# integration tests
```

---

## Adding a New Spectral Index

1. Implement the vectorized compute function in the appropriate `src/geoindexpy/indices/<category>.py` file.
2. Create a `SpectralIndex` instance with complete scientific metadata (formula, required bands, reference, valid range).
3. Register it with `get_registry().register(MY_INDEX, overwrite=True)` at module import.
4. Export the function and index from `src/geoindexpy/indices/__init__.py`.
5. Add a direct function wrapper in `src/geoindexpy/__init__.py`.
6. Write a scientific validation test in `tests/scientific/` verifying the result on known exact values.
7. Document all edge cases (zero division, NaN, nodata).

### Checklist for a New Index

- [ ] Vectorized NumPy implementation (no pixel loops)
- [ ] `safe_divide` used for ratio computation
- [ ] `SpectralIndex` dataclass with all metadata fields populated
- [ ] Scientific reference verified (no invented citations)
- [ ] `required_bands` uses lowercase standard role names
- [ ] Registered in the global registry
- [ ] Exported in `indices/__init__.py`
- [ ] Direct function wrapper in top-level `__init__.py`
- [ ] Scientific test with at least one exact known-value assertion
- [ ] Edge case tests (zero denominator, NaN propagation)

---

## Code Quality

This project uses:
- **ruff** for linting and formatting
- **mypy** for type checking
- **pytest** with **hypothesis** for property-based testing

```bash
ruff check src/ tests/
mypy src/geoindexpy/
```

---

## Scientific Standards

- All formulas must be traceable to a peer-reviewed publication or recognized standard.
- Never use `eval()` or `exec()` for formula computation.
- The library **calculates** indices; it does not interpret results agronomically or environmentally.
- Prefer `np.nan` as the fill for invalid pixels rather than silent Inf values.

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
