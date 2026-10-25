"""
ENT Runtime Environment, Scopes, Value representations, and Execution limits.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from ent.errors import EntRuntimeError, EntLimitExceededError, SourceLocation


class EntValue:
    """Base class for all runtime ENT values."""

    def to_display_string(self) -> str:
        return str(self)

    def is_truthy(self) -> bool:
        return True

    def unwrap(self) -> Any:
        return self


@dataclass
class EntNumber(EntValue):
    value: int | float

    def to_display_string(self) -> str:
        if isinstance(self.value, float) and self.value.is_integer():
            return str(int(self.value))
        return str(self.value)

    def is_truthy(self) -> bool:
        return self.value != 0

    def unwrap(self) -> int | float:
        return self.value

    def __repr__(self) -> str:
        return f"EntNumber({self.value})"


@dataclass
class EntString(EntValue):
    value: str

    def to_display_string(self) -> str:
        return self.value

    def is_truthy(self) -> bool:
        return len(self.value) > 0

    def unwrap(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"EntString({self.value!r})"


@dataclass
class EntBool(EntValue):
    value: bool

    def to_display_string(self) -> str:
        return "true" if self.value else "false"

    def is_truthy(self) -> bool:
        return self.value

    def unwrap(self) -> bool:
        return self.value

    def __repr__(self) -> str:
        return f"EntBool({self.value})"


@dataclass
class EntNull(EntValue):
    def to_display_string(self) -> str:
        return "nothing"

    def is_truthy(self) -> bool:
        return False

    def unwrap(self) -> None:
        return None

    def __repr__(self) -> str:
        return "EntNull()"


@dataclass
class EntList(EntValue):
    elements: List[EntValue] = field(default_factory=list)

    def to_display_string(self) -> str:
        inner = ", ".join(elem.to_display_string() for elem in self.elements)
        return f"[{inner}]"

    def is_truthy(self) -> bool:
        return len(self.elements) > 0

    def unwrap(self) -> List[Any]:
        return [elem.unwrap() for elem in self.elements]

    def __repr__(self) -> str:
        return f"EntList({self.elements!r})"


@dataclass
class EntFunction(EntValue):
    name: str
    parameters: List[str]
    body: Any  # AST Block
    closure_scope: Scope

    def to_display_string(self) -> str:
        params_str = ", ".join(self.parameters)
        return f"<function {self.name}({params_str})>"

    def __repr__(self) -> str:
        return f"EntFunction(name={self.name!r}, params={self.parameters!r})"


@dataclass
class EntBuiltinFunction(EntValue):
    name: str
    fn: Callable[..., EntValue]
    doc: str = ""

    def to_display_string(self) -> str:
        return f"<built-in function {self.name}>"

    def __repr__(self) -> str:
        return f"EntBuiltinFunction({self.name})"


@dataclass
class EntUIElement(EntValue):
    tag: str
    props: Dict[str, Any] = field(default_factory=dict)
    children: List[EntValue] = field(default_factory=list)

    def to_display_string(self) -> str:
        return f"<UIElement {self.tag}>"

    def __repr__(self) -> str:
        return f"EntUIElement(tag={self.tag!r}, props={self.props!r}, children_count={len(self.children)})"


def to_ent_value(val: Any) -> EntValue:
    """Helper to convert standard Python primitives into ENT values."""
    if isinstance(val, EntValue):
        return val
    if val is None:
        return EntNull()
    if isinstance(val, bool):
        return EntBool(val)
    if isinstance(val, (int, float)):
        return EntNumber(val)
    if isinstance(val, str):
        return EntString(val)
    if isinstance(val, (list, tuple)):
        return EntList([to_ent_value(x) for x in val])
    return EntString(str(val))


class ReturnSignal(Exception):
    """Used for flow control when returning a value from a function."""
    def __init__(self, value: EntValue):
        super().__init__()
        self.value = value


class Scope:
    """Lexical scope holding variable bindings."""

    def __init__(self, parent: Optional[Scope] = None, name: str = "local"):
        self.parent = parent
        self.name = name
        self.bindings: Dict[str, EntValue] = {}

    def define(self, name: str, value: EntValue) -> None:
        """Bind a variable in the current local scope."""
        self.bindings[name] = value

    def assign(self, name: str, value: EntValue) -> bool:
        """Assign to an existing variable in the nearest enclosing scope."""
        if name in self.bindings:
            self.bindings[name] = value
            return True
        if self.parent is not None:
            return self.parent.assign(name, value)
        # If not found anywhere, define in current scope
        self.bindings[name] = value
        return False

    def lookup(self, name: str) -> Optional[EntValue]:
        """Look up variable by identifier name."""
        if name in self.bindings:
            return self.bindings[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def exists(self, name: str) -> bool:
        return self.lookup(name) is not None


@dataclass
class RuntimeLimits:
    """Safety boundaries and execution counters."""
    max_steps: int = 100_000
    max_call_depth: int = 256
    max_output_length: int = 1_000_000
    steps_executed: int = 0
    current_call_depth: int = 0

    def tick(self, location: Optional[SourceLocation] = None, source_line: Optional[str] = None) -> None:
        self.steps_executed += 1
        if self.steps_executed > self.max_steps:
            raise EntLimitExceededError(
                message=f"Execution step limit exceeded ({self.max_steps} steps).",
                location=location,
                source_line=source_line,
                suggestion="Check for infinite loops or increase the execution step limit.",
            )

    def enter_call(self, location: Optional[SourceLocation] = None, source_line: Optional[str] = None) -> None:
        self.current_call_depth += 1
        if self.current_call_depth > self.max_call_depth:
            raise EntLimitExceededError(
                message=f"Maximum recursion depth exceeded ({self.max_call_depth} frames).",
                location=location,
                source_line=source_line,
                suggestion="Check for unbounded recursion in your functions.",
            )

    def exit_call(self) -> None:
        self.current_call_depth = max(0, self.current_call_depth - 1)
