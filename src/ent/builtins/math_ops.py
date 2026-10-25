"""
Math built-in functions for ENT.
"""

from __future__ import annotations
import math
from typing import Any
from ent.runtime import EntValue, EntNumber, EntBuiltinFunction
from ent.errors import EntRuntimeError


def builtin_round(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) == 0 or len(args) > 2:
        raise EntRuntimeError(f"'round' expects 1 or 2 arguments, got {len(args)}.")
    val = args[0]
    if not isinstance(val, EntNumber):
        raise EntRuntimeError(f"'round' requires a numeric first argument, got {type(val).__name__}.")
    decimals = 0
    if len(args) == 2:
        d_val = args[1]
        if not isinstance(d_val, EntNumber):
            raise EntRuntimeError("'round' second argument (decimals) must be a number.")
        decimals = int(d_val.value)
    res = round(val.value, decimals) if decimals > 0 else round(val.value)
    return EntNumber(int(res) if isinstance(res, float) and res.is_integer() else res)


def builtin_abs(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 1 or not isinstance(args[0], EntNumber):
        raise EntRuntimeError("'abs' expects exactly 1 numeric argument.")
    return EntNumber(abs(args[0].value))


def builtin_min(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) == 0:
        raise EntRuntimeError("'min' expects at least 1 argument.")
    for a in args:
        if not isinstance(a, EntNumber):
            raise EntRuntimeError(f"'min' expects numeric arguments, got {type(a).__name__}.")
    return EntNumber(min(a.value for a in args))


def builtin_max(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) == 0:
        raise EntRuntimeError("'max' expects at least 1 argument.")
    for a in args:
        if not isinstance(a, EntNumber):
            raise EntRuntimeError(f"'max' expects numeric arguments, got {type(a).__name__}.")
    return EntNumber(max(a.value for a in args))


def builtin_power(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 2 or not isinstance(args[0], EntNumber) or not isinstance(args[1], EntNumber):
        raise EntRuntimeError("'power' expects base and exponent as numbers.")
    res = args[0].value ** args[1].value
    if isinstance(res, complex):
        raise EntRuntimeError("Complex numbers are not supported in standard ENT operations.")
    return EntNumber(int(res) if isinstance(res, float) and res.is_integer() else res)


def builtin_square_root(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 1 or not isinstance(args[0], EntNumber):
        raise EntRuntimeError("'square_root' expects 1 numeric argument.")
    if args[0].value < 0:
        raise EntRuntimeError("Cannot take the square root of a negative number.")
    res = math.isqrt(int(args[0].value)) if isinstance(args[0].value, int) and math.isqrt(int(args[0].value))**2 == args[0].value else math.sqrt(args[0].value)
    return EntNumber(int(res) if isinstance(res, float) and res.is_integer() else res)
