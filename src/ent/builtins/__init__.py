"""
Standard library and built-ins registry for ENT.
"""

from __future__ import annotations
from typing import Callable, Optional
from ent.runtime import Scope, EntBuiltinFunction
from ent.builtins.core import (
    make_say_builtin,
    builtin_length,
    builtin_type_of,
    builtin_to_number,
    builtin_to_string,
    builtin_to_bool,
)
from ent.builtins.math_ops import (
    builtin_round,
    builtin_abs,
    builtin_min,
    builtin_max,
    builtin_power,
    builtin_square_root,
)
from ent.builtins.strings import (
    builtin_uppercase,
    builtin_lowercase,
    builtin_trim,
    builtin_contains,
    builtin_starts_with,
    builtin_ends_with,
    builtin_replace,
    builtin_split,
    builtin_join,
    builtin_push,
    builtin_pop,
    builtin_first,
    builtin_last,
    builtin_reverse,
    builtin_range,
)
from ent.builtins.web_builtins import make_web_builtins


def register_standard_builtins(scope: Scope, output_sink: Optional[Callable[[str], None]] = None) -> None:
    """Registers all ENT standard built-in functions into the given root Scope."""
    sink = output_sink if output_sink is not None else print

    # Core
    scope.define("say", make_say_builtin(sink))
    scope.define("length", EntBuiltinFunction("length", builtin_length))
    scope.define("type_of", EntBuiltinFunction("type_of", builtin_type_of))
    scope.define("to_number", EntBuiltinFunction("to_number", builtin_to_number))
    scope.define("to_string", EntBuiltinFunction("to_string", builtin_to_string))
    scope.define("to_bool", EntBuiltinFunction("to_bool", builtin_to_bool))

    # Math
    scope.define("round", EntBuiltinFunction("round", builtin_round))
    scope.define("abs", EntBuiltinFunction("abs", builtin_abs))
    scope.define("min", EntBuiltinFunction("min", builtin_min))
    scope.define("max", EntBuiltinFunction("max", builtin_max))
    scope.define("power", EntBuiltinFunction("power", builtin_power))
    scope.define("square_root", EntBuiltinFunction("square_root", builtin_square_root))

    # Strings & Collections
    scope.define("uppercase", EntBuiltinFunction("uppercase", builtin_uppercase))
    scope.define("lowercase", EntBuiltinFunction("lowercase", builtin_lowercase))
    scope.define("trim", EntBuiltinFunction("trim", builtin_trim))
    scope.define("contains", EntBuiltinFunction("contains", builtin_contains))
    scope.define("starts_with", EntBuiltinFunction("starts_with", builtin_starts_with))
    scope.define("ends_with", EntBuiltinFunction("ends_with", builtin_ends_with))
    scope.define("replace", EntBuiltinFunction("replace", builtin_replace))
    scope.define("split", EntBuiltinFunction("split", builtin_split))
    scope.define("join", EntBuiltinFunction("join", builtin_join))
    scope.define("push", EntBuiltinFunction("push", builtin_push))
    scope.define("pop", EntBuiltinFunction("pop", builtin_pop))
    scope.define("first", EntBuiltinFunction("first", builtin_first))
    scope.define("last", EntBuiltinFunction("last", builtin_last))
    scope.define("reverse", EntBuiltinFunction("reverse", builtin_reverse))
    scope.define("range", EntBuiltinFunction("range", builtin_range))

    # Web built-ins
    for name, fn_obj in make_web_builtins(output_sink=sink).items():
        scope.define(name, fn_obj)
