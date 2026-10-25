"""
Web-related standard built-in functions for ENT.
Provides graceful console-mode execution and UIElement creation when running outside the HTML builder.
"""

from __future__ import annotations
from typing import Any, Callable, Dict, Optional
from ent.runtime import (
    EntValue,
    EntString,
    EntNumber,
    EntNull,
    EntUIElement,
    EntBuiltinFunction,
    to_ent_value,
)
from ent.errors import EntRuntimeError


def make_web_builtins(output_sink: Optional[Callable[[str], None]] = None) -> Dict[str, EntBuiltinFunction]:
    """Generates standard web built-in functions for console and general runtime execution."""

    def log(msg: str) -> None:
        if output_sink:
            output_sink(msg)

    def builtin_heading(*args: EntValue, **kwargs: Any) -> EntValue:
        if not args:
            raise EntRuntimeError("heading() requires at least a text argument.")
        text = args[0].to_display_string()
        level = 1
        if len(args) >= 2 and isinstance(args[1], EntNumber):
            level = max(1, min(6, int(args[1].value)))
        if "level" in kwargs:
            lvl_val = kwargs["level"]
            if isinstance(lvl_val, EntNumber):
                level = max(1, min(6, int(lvl_val.value)))
        log(f"[Heading {level}]: {text}")
        return EntUIElement(tag=f"h{level}", props={"level": level}, children=[EntString(text)])

    def builtin_paragraph(*args: EntValue, **kwargs: Any) -> EntValue:
        if not args:
            raise EntRuntimeError("paragraph() requires a text argument.")
        text = " ".join(a.to_display_string() for a in args)
        log(f"[Paragraph]: {text}")
        return EntUIElement(tag="p", props={}, children=[EntString(text)])

    def builtin_button(*args: EntValue, **kwargs: Any) -> EntValue:
        text = args[0].to_display_string() if args else "Button"
        props: Dict[str, Any] = {}
        if "onclick" in kwargs:
            props["onclick"] = kwargs["onclick"].to_display_string()
        log(f"[Button]: {text}")
        return EntUIElement(tag="button", props=props, children=[EntString(text)])

    def builtin_link(*args: EntValue, **kwargs: Any) -> EntValue:
        text = args[0].to_display_string() if args else "Link"
        url = "#"
        if "url" in kwargs:
            url = kwargs["url"].to_display_string()
        elif len(args) >= 2:
            url = args[1].to_display_string()
        log(f"[Link]: {text} ({url})")
        return EntUIElement(tag="a", props={"href": url}, children=[EntString(text)])

    def builtin_image(*args: EntValue, **kwargs: Any) -> EntValue:
        src = args[0].to_display_string() if args else ""
        alt = "Image"
        if "alt" in kwargs:
            alt = kwargs["alt"].to_display_string()
        elif len(args) >= 2:
            alt = args[1].to_display_string()
        log(f"[Image]: {src} (alt={alt})")
        return EntUIElement(tag="img", props={"src": src, "alt": alt})

    def builtin_style(*args: EntValue, **kwargs: Any) -> EntValue:
        return EntNull()

    return {
        "heading": EntBuiltinFunction("heading", builtin_heading, doc="Renders a heading."),
        "paragraph": EntBuiltinFunction("paragraph", builtin_paragraph, doc="Renders a paragraph."),
        "button": EntBuiltinFunction("button", builtin_button, doc="Renders a button."),
        "link": EntBuiltinFunction("link", builtin_link, doc="Renders a hyperlink."),
        "image": EntBuiltinFunction("image", builtin_image, doc="Renders an image."),
        "style": EntBuiltinFunction("style", builtin_style, doc="Applies custom styling."),
    }
