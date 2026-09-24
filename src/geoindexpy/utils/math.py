"""Mathematical operations and safe numerical utilities for spectral index calculations."""

from typing import Any, Union
import numpy as np
import numpy.typing as npt

ArrayLike = Union[npt.NDArray[np.floating[Any]], npt.NDArray[np.integer[Any]], float, int]


def safe_divide(
    numerator: ArrayLike,
    denominator: ArrayLike,
    fill_value: float = np.nan,
    eps: float = 0.0,
) -> np.ndarray:
    """Safely divide two arrays or values, avoiding ZeroDivisionError or Inf.

    Where the absolute value of the denominator is less than or equal to `eps`
    (or exactly zero when eps=0.0), `fill_value` (default: np.nan) is placed in the result.

    Parameters
    ----------
    numerator : ArrayLike
        Numerator array or scalar.
    denominator : ArrayLike
        Denominator array or scalar.
    fill_value : float, optional
        Value used to replace invalid or zero-division elements. Default is np.nan.
    eps : float, optional
        Small threshold near zero to guard against numerical instability. Default is 0.0.

    Returns
    -------
    np.ndarray
        Result of the element-wise division with non-finite/zero-division handled safely.
    """
    # Ensure inputs are NumPy arrays with floating-point representation for scientific accuracy
    num = np.asanyarray(numerator)
    den = np.asanyarray(denominator)

    # Determine optimal float type (prefer float32 for 32-bit inputs to conserve memory, float64 otherwise)
    if num.dtype == np.float32 and den.dtype == np.float32:
        target_dtype = np.float32
    else:
        target_dtype = np.float64

    num = num.astype(target_dtype, copy=False)
    den = den.astype(target_dtype, copy=False)

    # Define valid denominator condition
    if eps > 0.0:
        valid_mask = np.abs(den) > eps
    else:
        valid_mask = den != 0.0

    # Also check that both numerator and denominator are finite
    valid_mask = valid_mask & np.isfinite(den) & np.isfinite(num)

    # Initialize result array with fill_value
    result = np.full(np.broadcast_shapes(num.shape, den.shape), fill_value, dtype=target_dtype)

    # Perform vectorized division only on safe valid elements
    np.divide(num, den, out=result, where=valid_mask)

    return result


def apply_scale(
    values: ArrayLike,
    scale_factor: float = 0.0001,
    offset: float = 0.0,
    target_dtype: np.dtype = np.float32,
) -> np.ndarray:
    """Explicitly scale raw digital numbers (DN) to surface reflectance (typically 0.0 - 1.0).

    In remote sensing (e.g. Sentinel-2 L2A, Landsat Collection 2), pixel values are often
    stored as integers with a scale factor (such as 0.0001).

    Parameters
    ----------
    values : ArrayLike
        Input array containing raw digital numbers or reflectance.
    scale_factor : float, optional
        Multiplicative scale factor. Default is 0.0001 (1 / 10000).
    offset : float, optional
        Additive offset. Default is 0.0.
    target_dtype : np.dtype, optional
        Target numpy dtype. Default is np.float32.

    Returns
    -------
    np.ndarray
        Scaled reflectance array.
    """
    dtype = np.dtype(target_dtype)
    arr = np.asanyarray(values, dtype=dtype)
    result = arr * dtype.type(scale_factor) + dtype.type(offset)
    return result.astype(dtype, copy=False)
