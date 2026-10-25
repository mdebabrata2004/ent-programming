import pytest
from ent.lexer import Lexer
from ent.tokens import TokenType
from ent.errors import EntLexicalError


def test_lex_hello_world():
    source = '[\n    say("Hello, World!")\n]'
    lexer = Lexer(source, file_path="test_hello.ent")
    tokens = lexer.tokenize()

    # Filter out whitespace statement separators for structural comparison
    types = [t.type for t in tokens if t.type != TokenType.NEWLINE]
    assert types == [
        TokenType.LBRACKET,
        TokenType.IDENTIFIER,
        TokenType.LPAREN,
        TokenType.STRING,
        TokenType.RPAREN,
        TokenType.RBRACKET,
        TokenType.EOF,
    ]
    assert tokens[3].value == "Hello, World!"


def test_lex_forbidden_curly_braces():
    # Mandatory Design Rule 2: Curly braces must not be part of ENT source syntax
    with pytest.raises(EntLexicalError) as exc_info:
        Lexer("[\n    say('test') {\n    }\n]").tokenize()
    assert "Curly brace '{' is forbidden in ENT" in str(exc_info.value)

    with pytest.raises(EntLexicalError) as exc_info2:
        Lexer("}").tokenize()
    assert "Curly brace '}' is forbidden in ENT" in str(exc_info2.value)


def test_lex_comments():
    source = """
    # Full line comment
    [
        // C++ style comment
        say(10) # inline comment
    ]
    """
    tokens = Lexer(source).tokenize()
    values = [t.value for t in tokens if t.type not in (TokenType.EOF, TokenType.NEWLINE)]
    assert values == ["[", "say", "(", 10, ")", "]"]


def test_lex_numbers():
    source = "[ 42 3.14 0 ]"
    tokens = Lexer(source).tokenize()
    nums = [t.value for t in tokens if t.type == TokenType.NUMBER]
    assert nums == [42, 3.14, 0]


def test_lex_strings_with_escapes():
    source = r'[ "hello\nworld" "tab\there" "quote\"inner\"" ]'
    tokens = Lexer(source).tokenize()
    strs = [t.value for t in tokens if t.type == TokenType.STRING]
    assert strs == ["hello\nworld", "tab\there", 'quote"inner"']


def test_lex_unterminated_string():
    with pytest.raises(EntLexicalError) as exc_info:
        Lexer('[ "unclosed string ]').tokenize()
    assert "Unterminated string literal" in str(exc_info.value)


def test_lex_line_column_tracking():
    source = "[\n  say(\"hi\")\n]"
    tokens = Lexer(source).tokenize()
    say_token = tokens[1]
    assert say_token.value == "say"
    assert say_token.location.line == 2
    assert say_token.location.column == 3


def test_lex_invalid_character():
    with pytest.raises(EntLexicalError) as exc_info:
        Lexer("[ say(@) ]").tokenize()
    assert "Unexpected character '@'" in str(exc_info.value)
