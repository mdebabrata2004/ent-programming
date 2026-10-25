"""
String and Collection helper built-in functions for ENT.
"""

from __future__ import annotations
from typing import Any, List
from ent.runtime import EntValue, EntString, EntNumber, EntBool, EntList, to_ent_value
from ent.errors import EntRuntimeError


def builtin_uppercase(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 1 or not isinstance(args[0], EntString):
        raise EntRuntimeError("'uppercase' expects exactly 1 string argument.")
    return EntString(args[0].value.upper())


def builtin_lowercase(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 1 or not isinstance(args[0], EntString):
        raise EntRuntimeError("'lowercase' expects exactly 1 string argument.")
    return EntString(args[0].value.lower())


def builtin_trim(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 1 or not isinstance(args[0], EntString):
        raise EntRuntimeError("'trim' expects exactly 1 string argument.")
    return EntString(args[0].value.strip())


def builtin_contains(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 2:
        raise EntRuntimeError("'contains' expects 2 arguments: (collection, item).")
    coll, target = args[0], args[1]
    if isinstance(coll, EntString):
        return EntBool(target.to_display_string() in coll.value)
    elif isinstance(coll, EntList):
        return EntBool(any(elem.unwrap() == target.unwrap() for elem in coll.elements))
    raise EntRuntimeError(f"'contains' cannot be used on {type(coll).__name__}.")


def builtin_starts_with(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 2 or not isinstance(args[0], EntString) or not isinstance(args[1], EntString):
        raise EntRuntimeError("'starts_with' expects 2 string arguments.")
    return EntBool(args[0].value.startswith(args[1].value))


def builtin_ends_with(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 2 or not isinstance(args[0], EntString) or not isinstance(args[1], EntString):
        raise EntRuntimeError("'ends_with' expects 2 string arguments.")
    return EntBool(args[0].value.endswith(args[1].value))


def builtin_replace(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 3 or not isinstance(args[0], EntString) or not isinstance(args[1], EntString) or not isinstance(args[2], EntString):
        raise EntRuntimeError("'replace' expects 3 string arguments: (source, old, new).")
    return EntString(args[0].value.replace(args[1].value, args[2].value))


def builtin_split(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) < 1 or not isinstance(args[0], EntString):
        raise EntRuntimeError("'split' expects a string as first argument.")
    delimiter = " "
    if len(args) >= 2 and isinstance(args[1], EntString):
        delimiter = args[1].value
    parts = args[0].value.split(delimiter)
    return EntList([EntString(p) for p in parts])


def builtin_join(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) < 1 or not isinstance(args[0], EntList):
        raise EntRuntimeError("'join' expects a list as first argument.")
    sep = ", "
    if len(args) >= 2 and isinstance(args[1], EntString):
        sep = args[1].value
    return EntString(sep.join(elem.to_display_string() for elem in args[0].elements))


# List helpers
def builtin_push(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 2 or not isinstance(args[0], EntList):
        raise EntRuntimeError("'push' expects (list, item).")
    args[0].elements.append(args[1])
    return args[0]


def builtin_pop(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 1 or not isinstance(args[0], EntList):
        raise EntRuntimeError("'pop' expects 1 list argument.")
    if not args[0].elements:
        raise EntRuntimeError("Cannot pop from an empty list.")
    return args[0].elements.pop()


def builtin_first(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 1:
        raise EntRuntimeError("'first' expects 1 argument.")
    target = args[0]
    if isinstance(target, EntList):
        if not target.elements:
            raise EntRuntimeError("Cannot get first item of an empty list.")
        return target.elements[0]
    elif isinstance(target, EntString):
        if not target.value:
            raise EntRuntimeError("Cannot get first character of an empty string.")
        return EntString(target.value[0])
    raise EntRuntimeError(f"'first' not supported on {type(target).__name__}.")


def builtin_last(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 1:
        raise EntRuntimeError("'last' expects 1 argument.")
    target = args[0]
    if isinstance(target, EntList):
        if not target.elements:
            raise EntRuntimeError("Cannot get last item of an empty list.")
        return target.elements[-1]
    elif isinstance(target, EntString):
        if not target.value:
            raise EntRuntimeError("Cannot get last character of an empty string.")
        return EntString(target.value[-1])
    raise EntRuntimeError(f"'last' not supported on {type(target).__name__}.")


def builtin_reverse(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) != 1:
        raise EntRuntimeError("'reverse' expects 1 argument.")
    target = args[0]
    if isinstance(target, EntList):
        return EntList(list(reversed(target.elements)))
    elif isinstance(target, EntString):
        return EntString(target.value[::-1])
    raise EntRuntimeError(f"'reverse' not supported on {type(target).__name__}.")


def builtin_range(*args: EntValue, **kwargs: Any) -> EntValue:
    if len(args) == 1 and isinstance(args[0], EntNumber):
        start = 0
        end = int(args[0].value)
        step = 1
    elif len(args) == 2 and isinstance(args[0], EntNumber) and isinstance(args[1], EntNumber):
        start = int(args[0].value)
        end = int(args[1].value)
        step = 1
    elif len(args) == 3 and isinstance(args[0], EntNumber) and isinstance(args[1], EntNumber) and isinstance(args[2], EntNumber):
        start = int(args[0].value)
        end = int(args[1].value)
        step = int(args[2].value)
        if step == 0:
            raise EntRuntimeError("'range' step cannot be zero.")
    else:
        raise EntRuntimeError("'range' expects 1 to 3 numeric arguments.")
    return EntList([EntNumber(i) for i in range(start, end, step)])
