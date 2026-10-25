"""
Lexer (tokenizer) for the ENT programming language.
"""

from __future__ import annotations
from typing import List, Optional
from ent.tokens import Token, TokenType, KEYWORDS
from ent.errors import EntLexicalError, SourceLocation


class Lexer:
    """Scans ENT source code and produces a stream of Tokens."""

    def __init__(self, source: str, file_path: str = "<stdin>"):
        self.source = source
        self.file_path = file_path
        self.length = len(source)
        self.index = 0
        self.line = 1
        self.column = 1
        self.lines = source.splitlines(keepends=False)
        self.paren_depth = 0

    def _get_current_line(self, line_num: int) -> str:
        if 1 <= line_num <= len(self.lines):
            return self.lines[line_num - 1]
        return ""

    def _location(self, line: Optional[int] = None, col: Optional[int] = None) -> SourceLocation:
        return SourceLocation(
            file=self.file_path,
            line=line if line is not None else self.line,
            column=col if col is not None else self.column,
        )

    def _peek(self, offset: int = 0) -> str:
        pos = self.index + offset
        if pos < self.length:
            return self.source[pos]
        return "\0"

    def _advance(self) -> str:
        if self.index >= self.length:
            return "\0"
        ch = self.source[self.index]
        self.index += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []

        while self.index < self.length:
            start_line = self.line
            start_col = self.column
            ch = self._peek()

            # Forbidden curly braces check (Mandatory Design Rule 2)
            if ch in ("{", "}"):
                loc = self._location(start_line, start_col)
                src_line = self._get_current_line(start_line)
                self._advance()
                raise EntLexicalError(
                    message=f"Curly brace '{ch}' is forbidden in ENT.",
                    location=loc,
                    source_line=src_line,
                    suggestion="In ENT, code blocks must be delimited with square brackets '[ ]', never curly braces '{ }'.",
                )

            # Whitespace handling
            if ch in (" ", "\t", "\r"):
                self._advance()
                continue

            # Newlines
            if ch == "\n":
                self._advance()
                # Ignore newlines inside parentheses
                if self.paren_depth > 0:
                    continue
                # Collapse consecutive newlines and ignore leading/trailing newlines
                if tokens and tokens[-1].type not in (
                    TokenType.NEWLINE,
                    TokenType.SEMICOLON,
                    TokenType.LBRACKET,
                    TokenType.COMMA,
                ):
                    tokens.append(
                        Token(
                            TokenType.NEWLINE,
                            "\n",
                            self._location(start_line, start_col),
                            self._get_current_line(start_line),
                        )
                    )
                continue

            # Comments: # or //
            if ch == "#" or (ch == "/" and self._peek(1) == "/"):
                while self._peek() not in ("\n", "\0"):
                    self._advance()
                continue

            # Semicolon as explicit statement separator
            if ch == ";":
                self._advance()
                if tokens and tokens[-1].type not in (TokenType.NEWLINE, TokenType.SEMICOLON):
                    tokens.append(
                        Token(
                            TokenType.SEMICOLON,
                            ";",
                            self._location(start_line, start_col),
                            self._get_current_line(start_line),
                        )
                    )
                continue

            # Two-character operators
            if ch == "=" and self._peek(1) == "=":
                self._advance()
                self._advance()
                tokens.append(Token(TokenType.EQUAL, "==", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == "!" and self._peek(1) == "=":
                self._advance()
                self._advance()
                tokens.append(Token(TokenType.NOT_EQUAL, "!=", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == "<" and self._peek(1) == "=":
                self._advance()
                self._advance()
                tokens.append(Token(TokenType.LESS_EQUAL, "<=", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == ">" and self._peek(1) == "=":
                self._advance()
                self._advance()
                tokens.append(Token(TokenType.GREATER_EQUAL, ">=", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            # Single-character tokens
            if ch == "=":
                self._advance()
                tokens.append(Token(TokenType.ASSIGN, "=", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == "+":
                self._advance()
                tokens.append(Token(TokenType.PLUS, "+", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == "-":
                self._advance()
                tokens.append(Token(TokenType.MINUS, "-", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == "*":
                self._advance()
                tokens.append(Token(TokenType.STAR, "*", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == "/":
                self._advance()
                tokens.append(Token(TokenType.SLASH, "/", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == "%":
                self._advance()
                tokens.append(Token(TokenType.PERCENT, "%", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == "<":
                self._advance()
                tokens.append(Token(TokenType.LESS_THAN, "<", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == ">":
                self._advance()
                tokens.append(Token(TokenType.GREATER_THAN, ">", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == "(":
                self._advance()
                self.paren_depth += 1
                tokens.append(Token(TokenType.LPAREN, "(", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == ")":
                self._advance()
                self.paren_depth = max(0, self.paren_depth - 1)
                tokens.append(Token(TokenType.RPAREN, ")", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == "[":
                self._advance()
                tokens.append(Token(TokenType.LBRACKET, "[", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == "]":
                self._advance()
                tokens.append(Token(TokenType.RBRACKET, "]", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == ",":
                self._advance()
                tokens.append(Token(TokenType.COMMA, ",", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == ".":
                self._advance()
                tokens.append(Token(TokenType.DOT, ".", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == ":":
                self._advance()
                tokens.append(Token(TokenType.COLON, ":", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            if ch == "?":
                self._advance()
                tokens.append(Token(TokenType.QUESTION, "?", self._location(start_line, start_col), self._get_current_line(start_line)))
                continue

            # Strings
            if ch in ('"', "'"):
                quote_char = ch
                self._advance()  # consume opening quote
                chars: List[str] = []
                closed = False

                while self._peek() != "\0":
                    c = self._advance()
                    if c == quote_char:
                        closed = True
                        break
                    elif c == "\\":
                        nxt = self._advance()
                        if nxt == "n":
                            chars.append("\n")
                        elif nxt == "t":
                            chars.append("\t")
                        elif nxt == "r":
                            chars.append("\r")
                        elif nxt == "\\":
                            chars.append("\\")
                        elif nxt == quote_char:
                            chars.append(quote_char)
                        else:
                            chars.append("\\" + nxt)
                    elif c == "\n":
                        # Unterminated string across newline
                        break
                    else:
                        chars.append(c)

                if not closed:
                    raise EntLexicalError(
                        message=f"Unterminated string literal.",
                        location=self._location(start_line, start_col),
                        source_line=self._get_current_line(start_line),
                        suggestion=f"Did you forget a closing {quote_char} quote?",
                    )

                str_val = "".join(chars)
                tokens.append(
                    Token(
                        TokenType.STRING,
                        str_val,
                        self._location(start_line, start_col),
                        self._get_current_line(start_line),
                    )
                )
                continue

            # Numbers
            if ch.isdigit():
                num_chars: List[str] = []
                is_float = False
                while self._peek().isdigit():
                    num_chars.append(self._advance())

                if self._peek() == "." and self._peek(1).isdigit():
                    is_float = True
                    num_chars.append(self._advance())  # consume '.'
                    while self._peek().isdigit():
                        num_chars.append(self._advance())

                num_str = "".join(num_chars)
                num_val = float(num_str) if is_float else int(num_str)
                tokens.append(
                    Token(
                        TokenType.NUMBER,
                        num_val,
                        self._location(start_line, start_col),
                        self._get_current_line(start_line),
                    )
                )
                continue

            # Identifiers and keywords
            if ch.isalpha() or ch == "_":
                ident_chars: List[str] = []
                while self._peek().isalnum() or self._peek() == "_":
                    ident_chars.append(self._advance())
                ident_str = "".join(ident_chars)

                # Keyword check (case-sensitive)
                tok_type = KEYWORDS.get(ident_str, TokenType.IDENTIFIER)
                tok_val = ident_str
                if tok_type == TokenType.TRUE:
                    tok_val = True
                elif tok_type == TokenType.FALSE:
                    tok_val = False
                elif tok_type == TokenType.NOTHING:
                    tok_val = None

                tokens.append(
                    Token(
                        tok_type,
                        tok_val,
                        self._location(start_line, start_col),
                        self._get_current_line(start_line),
                    )
                )
                continue

            # If we reached here, unrecognized character
            loc = self._location(start_line, start_col)
            src_line = self._get_current_line(start_line)
            bad_char = self._advance()
            raise EntLexicalError(
                message=f"Unexpected character '{bad_char}'.",
                location=loc,
                source_line=src_line,
                suggestion="Check for typos or unsupported symbols.",
            )

        # End of file token
        # Strip trailing newlines/semicolons before EOF
        while tokens and tokens[-1].type in (TokenType.NEWLINE, TokenType.SEMICOLON):
            tokens.pop()

        tokens.append(
            Token(
                TokenType.EOF,
                None,
                self._location(self.line, self.column),
                self._get_current_line(self.line),
            )
        )
        return tokens
