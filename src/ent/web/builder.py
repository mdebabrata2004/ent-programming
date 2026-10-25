"""
Static website generation engine for ENT.
Safely translates ENT page definitions into semantic HTML5 and CSS.
"""

from __future__ import annotations
import html
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from ent.lexer import Lexer
from ent.parser import Parser
from ent.ast_nodes import Program, Block, Statement, BlockCallStatement, ExpressionStatement, CallExpr, Literal, Identifier
from ent.runtime import Scope, RuntimeLimits, EntValue, EntString, EntNumber, EntBuiltinFunction, to_ent_value
from ent.interpreter import Interpreter
from ent.errors import EntBuildError, EntError


@dataclass
class UIElement:
    tag: str
    props: Dict[str, Any] = field(default_factory=dict)
    text: Optional[str] = None
    children: List[UIElement] = field(default_factory=list)


@dataclass
class PageModel:
    title: str = "ENT Website"
    theme: str = "light"
    styles: List[str] = field(default_factory=list)
    elements: List[UIElement] = field(default_factory=list)


@dataclass
class GeneratedWebsite:
    html: str
    css: str
    title: str


DEFAULT_CSS = """/* ENT Programming Default Web Stylesheet */
:root {
  --ent-bg: #f8fafc;
  --ent-surface: #ffffff;
  --ent-text: #0f172a;
  --ent-text-muted: #64748b;
  --ent-primary: #3b82f6;
  --ent-primary-hover: #2563eb;
  --ent-border: #e2e8f0;
  --ent-radius: 8px;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: var(--ent-bg);
  color: var(--ent-text);
  line-height: 1.6;
  padding: 2rem 1rem;
}

.ent-container {
  max-width: 800px;
  margin: 0 auto;
  background: var(--ent-surface);
  padding: 2.5rem;
  border-radius: var(--ent-radius);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--ent-border);
}

h1, h2, h3, h4, h5, h6 {
  color: #1e293b;
  margin-bottom: 1rem;
  font-weight: 700;
}

h1 { font-size: 2.25rem; line-height: 1.25; }
h2 { font-size: 1.75rem; margin-top: 1.5rem; }
h3 { font-size: 1.35rem; margin-top: 1.25rem; }

p {
  margin-bottom: 1.25rem;
  color: #334155;
  font-size: 1.05rem;
}

.ent-button {
  display: inline-block;
  background-color: var(--ent-primary);
  color: #ffffff;
  font-weight: 600;
  padding: 0.65rem 1.4rem;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  text-decoration: none;
  transition: background-color 0.15s ease, transform 0.1s ease;
  font-size: 1rem;
  margin: 0.5rem 0.5rem 0.5rem 0;
}

.ent-button:hover {
  background-color: var(--ent-primary-hover);
  transform: translateY(-1px);
}

.ent-link {
  color: var(--ent-primary);
  text-decoration: underline;
  font-weight: 500;
  transition: color 0.15s ease;
}

.ent-link:hover {
  color: var(--ent-primary-hover);
}

.ent-section {
  margin: 1.5rem 0;
  padding: 1.25rem;
  background-color: #f1f5f9;
  border-radius: 6px;
  border-left: 4px solid var(--ent-primary);
}

img.ent-image {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  margin: 1rem 0;
}

footer.ent-footer {
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--ent-border);
  text-align: center;
  font-size: 0.875rem;
  color: var(--ent-text-muted);
}
"""


DANGEROUS_JS_PATTERNS = [
    r"eval\(",
    r"Function\(",
    r"document\.",
    r"window\.",
    r"location\.",
    r"localStorage",
    r"sessionStorage",
    r"cookie",
    r"fetch\(",
    r"XMLHttpRequest",
    r"<script",
    r"__proto__",
]


def _sanitize_url(url: str) -> str:
    """Disallows dangerous URI schemes like javascript: or data:, even if obfuscated."""
    cleaned = url.strip()
    # Strip whitespace and control characters to detect obfuscated schemes
    stripped = re.sub(r"[\s\x00-\x1f\x7f]+", "", cleaned)
    if re.match(r"^(javascript|data|vbscript):", stripped, re.IGNORECASE):
        return "#"
    return html.escape(cleaned, quote=True)


def _sanitize_event_handler(code: str) -> str:
    """Validates and restricts inline event handlers to safe operations."""
    stripped = code.strip()
    for pat in DANGEROUS_JS_PATTERNS:
        if re.search(pat, stripped, re.IGNORECASE):
            return "/* event blocked by ENT security policy */"
    return html.escape(stripped, quote=True)


class WebASTBuilder:
    """Interprets page definitions in an ENT AST and accumulates UI elements."""

    def __init__(self):
        self.page = PageModel()
        self.element_stack: List[List[UIElement]] = [self.page.elements]

    @property
    def current_container(self) -> List[UIElement]:
        return self.element_stack[-1]

    def add_element(self, element: UIElement) -> None:
        self.current_container.append(element)


def build_website_from_source(source: str, file_path: str = "<stdin>") -> GeneratedWebsite:
    """Parses ENT source and converts it into a static HTML/CSS website."""
    try:
        lexer = Lexer(source, file_path=file_path)
        tokens = lexer.tokenize()
        parser = Parser(tokens, source=source, file_path=file_path)
        program = parser.parse()
    except EntError:
        raise

    builder = WebASTBuilder()

    # Interpreter custom block handler for page(...) [ ... ] and section(...) [ ... ]
    def block_handler(stmt: BlockCallStatement, scope: Scope, interp: Interpreter) -> None:
        name = stmt.name
        evaluated_args = [interp.evaluate_expression(a, scope).unwrap() for a in stmt.args]
        evaluated_kwargs = {k: interp.evaluate_expression(v, scope).unwrap() for k, v in stmt.kwargs.items()}

        if name == "page":
            title = evaluated_kwargs.get("title", "ENT Website")
            if evaluated_args:
                title = str(evaluated_args[0])
            builder.page.title = str(title)
            # Execute block statements inside page
            interp.execute_block(stmt.body, scope)

        elif name in ("section", "container", "box"):
            section_elem = UIElement(tag="div", props={"class": "ent-section"})
            builder.add_element(section_elem)
            builder.element_stack.append(section_elem.children)
            interp.execute_block(stmt.body, scope)
            builder.element_stack.pop()

        else:
            # Fallback
            interp.execute_block(stmt.body, scope)

    # Initialize interpreter
    interp = Interpreter(custom_block_handler=block_handler)

    # Register web-specific built-in functions
    def builtin_heading(*args: EntValue, **kwargs: Any) -> EntValue:
        if not args:
            raise EntBuildError("heading() requires at least a text argument.")
        text = args[0].to_display_string()
        level = 1
        if len(args) >= 2 and isinstance(args[1], EntNumber):
            level = max(1, min(6, int(args[1].value)))
        if "level" in kwargs:
            lvl_val = kwargs["level"]
            if isinstance(lvl_val, EntNumber):
                level = max(1, min(6, int(lvl_val.value)))
        builder.add_element(UIElement(tag=f"h{level}", text=text))
        return to_ent_value(None)

    def builtin_paragraph(*args: EntValue, **kwargs: Any) -> EntValue:
        if not args:
            raise EntBuildError("paragraph() requires a text argument.")
        text = " ".join(a.to_display_string() for a in args)
        builder.add_element(UIElement(tag="p", text=text))
        return to_ent_value(None)

    def builtin_button(*args: EntValue, **kwargs: Any) -> EntValue:
        text = args[0].to_display_string() if args else "Button"
        props: Dict[str, Any] = {"class": "ent-button"}
        if "onclick" in kwargs:
            props["onclick"] = _sanitize_event_handler(kwargs["onclick"].to_display_string())
        builder.add_element(UIElement(tag="button", props=props, text=text))
        return to_ent_value(None)

    def builtin_section(*args: EntValue, **kwargs: Any) -> EntValue:
        section_elem = UIElement(tag="div", props={"class": "ent-section"})
        if args:
            section_elem.text = args[0].to_display_string()
        builder.add_element(section_elem)
        return to_ent_value(None)

    def builtin_container(*args: EntValue, **kwargs: Any) -> EntValue:
        return builtin_section(*args, **kwargs)

    def builtin_link(*args: EntValue, **kwargs: Any) -> EntValue:
        text = args[0].to_display_string() if args else "Link"
        href = "#"
        if "url" in kwargs:
            href = kwargs["url"].to_display_string()
        elif len(args) >= 2:
            href = args[1].to_display_string()
        props = {"href": _sanitize_url(href), "class": "ent-link"}
        builder.add_element(UIElement(tag="a", props=props, text=text))
        return to_ent_value(None)

    def builtin_image(*args: EntValue, **kwargs: Any) -> EntValue:
        src = args[0].to_display_string() if args else ""
        alt = "Image"
        if "alt" in kwargs:
            alt = kwargs["alt"].to_display_string()
        elif len(args) >= 2:
            alt = args[1].to_display_string()
        props = {"src": _sanitize_url(src), "alt": html.escape(alt, quote=True), "class": "ent-image"}
        builder.add_element(UIElement(tag="img", props=props))
        return to_ent_value(None)

    def builtin_style(*args: EntValue, **kwargs: Any) -> EntValue:
        if args:
            builder.page.styles.append(args[0].to_display_string())
        return to_ent_value(None)

    interp.global_scope.define("heading", EntBuiltinFunction("heading", builtin_heading))
    interp.global_scope.define("paragraph", EntBuiltinFunction("paragraph", builtin_paragraph))
    interp.global_scope.define("button", EntBuiltinFunction("button", builtin_button))
    interp.global_scope.define("link", EntBuiltinFunction("link", builtin_link))
    interp.global_scope.define("image", EntBuiltinFunction("image", builtin_image))
    interp.global_scope.define("style", EntBuiltinFunction("style", builtin_style))
    interp.global_scope.define("section", EntBuiltinFunction("section", builtin_section))
    interp.global_scope.define("container", EntBuiltinFunction("container", builtin_container))

    # Execute
    res = interp.execute_program(program)
    if not res.success and res.error:
        raise res.error

    # Render HTML
    html_out = _render_page_html(builder.page)
    css_out = DEFAULT_CSS
    if builder.page.styles:
        css_out += "\n/* Custom user styles */\n" + "\n".join(builder.page.styles)

    return GeneratedWebsite(html=html_out, css=css_out, title=builder.page.title)


def _render_element(elem: UIElement, indent: int = 4) -> str:
    spaces = " " * indent
    tag = elem.tag

    # Render attributes
    attr_parts: List[str] = []
    for k, v in elem.props.items():
        escaped_val = html.escape(str(v), quote=True)
        attr_parts.append(f'{k}="{escaped_val}"')
    attrs_str = (" " + " ".join(attr_parts)) if attr_parts else ""

    # Self-closing tags
    if tag in ("img", "br", "hr", "meta", "input"):
        return f"{spaces}<{tag}{attrs_str} />"

    # Inner text or children
    if elem.children:
        child_html = "\n".join(_render_element(c, indent + 2) for c in elem.children)
        return f"{spaces}<{tag}{attrs_str}>\n{child_html}\n{spaces}</{tag}>"
    else:
        text_content = html.escape(elem.text or "", quote=False)
        return f"{spaces}<{tag}{attrs_str}>{text_content}</{tag}>"


def _render_page_html(page: PageModel) -> str:
    escaped_title = html.escape(page.title, quote=False)
    elements_markup = "\n".join(_render_element(el, indent=6) for el in page.elements)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escaped_title}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="ent-container">
{elements_markup}
    <footer class="ent-footer">
      Built with <a href="https://github.com/debabrata/ent-programming" class="ent-link">ENT Programming</a>
    </footer>
  </div>
</body>
</html>
"""


def build_website_from_file(file_path: Path, out_dir: Path = Path("dist")) -> Path:
    """Builds an ENT website file to out_dir, outputting index.html and style.css."""
    source = file_path.read_text(encoding="utf-8")
    generated = build_website_from_source(source, file_path=str(file_path))

    out_dir.mkdir(parents=True, exist_ok=True)
    html_file = out_dir / "index.html"
    css_file = out_dir / "style.css"

    html_file.write_text(generated.html, encoding="utf-8")
    css_file.write_text(generated.css, encoding="utf-8")

    return html_file
