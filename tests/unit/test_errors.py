import pytest
from ent.errors import EntLexicalError, EntSyntaxError, EntRuntimeError, SourceLocation


def test_error_diagnostic_formatting():
    loc = SourceLocation(file="script.ent", line=3, column=5)
    err = EntSyntaxError(
        message="Unexpected identifier 'foo'.",
        location=loc,
        source_line="    foo = 10",
        suggestion="Did you mean to use 'remember(foo = 10)'?",
    )
    formatted = err.format_diagnostic()
    assert "[Syntax Error] in script.ent:3:5:" in formatted
    assert "Error: Unexpected identifier 'foo'." in formatted
    assert "foo = 10" in formatted
    assert "^" in formatted
    assert "Tip: Did you mean to use 'remember(foo = 10)'?" in formatted


def test_error_to_dict():
    loc = SourceLocation(file="test.ent", line=1, column=1)
    err = EntRuntimeError("Something went wrong", location=loc)
    d = err.to_dict()
    assert d["category"] == "Runtime Error"
    assert d["message"] == "Something went wrong"
    assert d["file"] == "test.ent"
    assert d["line"] == 1
    assert d["column"] == 1
