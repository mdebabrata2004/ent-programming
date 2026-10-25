from pathlib import Path
import pytest
from ent.web.builder import build_website_from_source, build_website_from_file
from ent.errors import EntBuildError, EntSyntaxError


def test_build_website_valid():
    src = """[
        page(title = "Test Page") [
            heading("Welcome")
            paragraph("Hello from test")
            button("Click Me")
            link("Link Text", url = "https://example.com")
        ]
    ]"""
    result = build_website_from_source(src)
    assert result.title == "Test Page"
    assert "<title>Test Page</title>" in result.html
    assert "<h1>Welcome</h1>" in result.html
    assert "<p>Hello from test</p>" in result.html
    assert 'class="ent-button">Click Me</button>' in result.html
    assert 'href="https://example.com"' in result.html
    assert "ent-container" in result.css


def test_build_website_xss_protection():
    src = """[
        page(title = "<script>alert(1)</script>") [
            heading("<img src=x onerror=alert(1)>")
            paragraph("Safe & sound <tag>")
            link("Malicious Link", url = "javascript:alert('pwned')")
        ]
    ]"""
    result = build_website_from_source(src)
    # Title must be escaped
    assert "<script>" not in result.html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in result.html

    # Heading must be escaped
    assert "<img src=x" not in result.html
    assert "&lt;img src=x onerror=alert(1)&gt;" in result.html

    # javascript: URL must be sanitized to '#'
    assert "javascript:" not in result.html
    assert 'href="#"' in result.html


def test_build_website_from_file(tmp_path: Path):
    ent_file = tmp_path / "site.ent"
    ent_file.write_text('[\n    page(title = "Site") [\n        heading("Heading")\n    ]\n]', encoding="utf-8")
    out_dir = tmp_path / "build_output"

    html_file = build_website_from_file(ent_file, out_dir=out_dir)
    assert html_file.exists()
    assert (out_dir / "style.css").exists()
    content = html_file.read_text(encoding="utf-8")
    assert "<h1>Heading</h1>" in content
