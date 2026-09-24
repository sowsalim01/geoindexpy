"""Unit tests for mathematical operations and safe numeric utilities."""

import numpy as np
import pytest
from geoindexpy.utils.math import apply_scale, safe_divide


def test_safe_divide_normal() -> None:
    num = np.array([10.0, 20.0, 30.0], dtype=np.float32)
    den = np.array([2.0, 4.0, 5.0], dtype=np.float32)
    res = safe_divide(num, den)
    assert np.allclose(res, [5.0, 5.0, 6.0])
    assert res.dtype == np.float32


def test_safe_divide_zero_division() -> None:
    num = np.array([1.0, 0.0, -1.0])
    den = np.array([0.0, 0.0, 0.0])
    res = safe_divide(num, den, fill_value=np.nan)
    assert np.all(np.isnan(res))


def test_safe_divide_custom_fill() -> None:
    num = np.array([10.0, 20.0])
    den = np.array([2.0, 0.0])
    res = safe_divide(num, den, fill_value=-9999.0)
    assert res[0] == 5.0
    assert res[1] == -9999.0


def test_safe_divide_nan_and_inf_handling() -> None:
    num = np.array([np.nan, 10.0, np.inf])
    den = np.array([5.0, np.nan, 2.0])
    res = safe_divide(num, den)
    assert np.isnan(res[0])
    assert np.isnan(res[1])
    assert np.isnan(res[2])


def test_safe_divide_2d_array() -> None:
    num = np.ones((3, 3), dtype=np.float32)
    den = np.array([[1.0, 0.0, 2.0], [4.0, 0.0, 5.0], [0.0, 2.0, 1.0]], dtype=np.float32)
    res = safe_divide(num, den)
    assert res.shape == (3, 3)
    assert res[0, 0] == 1.0
    assert np.isnan(res[0, 1])
    assert res[0, 2] == 0.5


def test_apply_scale_default() -> None:
    dn = np.array([10000, 5000, 0], dtype=np.int16)
    scaled = apply_scale(dn)
    assert np.allclose(scaled, [1.0, 0.5, 0.0])
    assert scaled.dtype == np.float32


def test_apply_scale_custom() -> None:
    dn = np.array([100, 200])
    scaled = apply_scale(dn, scale_factor=0.01, offset=5.0)
    assert np.allclose(scaled, [6.0, 7.0])
