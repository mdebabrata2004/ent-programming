"""
Core standard built-in functions for ENT.
"""

from __future__ import annotations
import math
from typing import List, Any, Callable
from ent.runtime import (
    EntValue,
    EntString,
    EntNumber,
    EntBool,
    EntNull,
    EntList,
    EntBuiltinFunction,
    to_ent_value,
)
from ent.errors import EntRuntimeError


def make_say_builtin(output_sink: Callable[[str], None]) -> EntBuiltinFunction:
    """Creates the 'say' function wired to the given output sink."""

    def say_fn(*args: EntValue, **kwargs: Any) -> EntValue:
        text = " ".join(arg.to_display_string() for arg in args)
        output_sink(text)
        return EntNull()

    return EntBuiltinFunction(name="say", fn=say_fn, doc="Outputs text or values to the console.")


def builtin_length(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 1:
        raise EntRuntimeError(f"'length' expects exactly 1 argument, got {len(args)}.")
    arg = args[0]
    if isinstance(arg, EntString):
        return EntNumber(len(arg.value))
    elif isinstance(arg, EntList):
        return EntNumber(len(arg.elements))
    else:
        raise EntRuntimeError(f"'length' cannot be used on type {type(arg).__name__}.")


def builtin_type_of(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 1:
        raise EntRuntimeError(f"'type_of' expects exactly 1 argument, got {len(args)}.")
    arg = args[0]
    if isinstance(arg, EntNumber):
        return EntString("number")
    elif isinstance(arg, EntString):
        return EntString("string")
    elif isinstance(arg, EntBool):
        return EntString("boolean")
    elif isinstance(arg, EntList):
        return EntString("list")
    elif isinstance(arg, EntNull):
        return EntString("nothing")
    else:
        return EntString("object")


def builtin_to_number(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 1:
        raise EntRuntimeError(f"'to_number' expects 1 argument, got {len(args)}.")
    arg = args[0]
    if isinstance(arg, EntNumber):
        return arg
    if isinstance(arg, EntBool):
        return EntNumber(1 if arg.value else 0)
    if isinstance(arg, EntString):
        try:
            val = float(arg.value)
            if val.is_integer():
                return EntNumber(int(val))
            return EntNumber(val)
        except ValueError:
            raise EntRuntimeError(f"Cannot convert string '{arg.value}' to number.")
    raise EntRuntimeError(f"Cannot convert value of type {type(arg).__name__} to number.")


def builtin_to_string(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 1:
        raise EntRuntimeError(f"'to_string' expects 1 argument, got {len(args)}.")
    return EntString(args[0].to_display_string())


def builtin_to_bool(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 1:
        raise EntRuntimeError(f"'to_bool' expects 1 argument, got {len(args)}.")
    return EntBool(args[0].is_truthy())
