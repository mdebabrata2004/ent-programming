"""
Token types and Token definitions for the ENT programming language.
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass
from typing import Any
from ent.errors import SourceLocation


class TokenType(Enum):
    # Program & Block Delimiters
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    COMMA = auto()          # ,
    DOT = auto()            # .
    COLON = auto()          # :
    SEMICOLON = auto()      # ;
    QUESTION = auto()       # ?
    NEWLINE = auto()        # newline as statement separator

    # Assignment & Operators
    ASSIGN = auto()         # =
    PLUS = auto()           # +
    MINUS = auto()          # -
    STAR = auto()           # *
    SLASH = auto()          # /
    PERCENT = auto()        # %

    # Comparison Operators
    EQUAL = auto()          # ==
    NOT_EQUAL = auto()      # !=
    LESS_THAN = auto()      # <
    LESS_EQUAL = auto()     # <=
    GREATER_THAN = auto()   # >
    GREATER_EQUAL = auto()  # >=

    # Keywords
    REMEMBER = auto()       # remember
    IF = auto()             # if
    OTHERWISE = auto()      # otherwise
    WHILE = auto()          # while
    REPEAT = auto()         # repeat
    FOR = auto()            # for
    IN = auto()             # in
    AS = auto()             # as
    FUNCTION = auto()       # function
    ACTION = auto()         # action
    RETURN = auto()         # return
    GIVE = auto()           # give
    AND = auto()            # and
    OR = auto()             # or
    NOT = auto()            # not
    TRUE = auto()           # true, yes
    FALSE = auto()          # false, no
    NOTHING = auto()        # nothing, none

    # Literals & Identifiers
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

    # Special
    EOF = auto()


KEYWORDS: dict[str, TokenType] = {
    "remember": TokenType.REMEMBER,
    "if": TokenType.IF,
    "otherwise": TokenType.OTHERWISE,
    "while": TokenType.WHILE,
    "repeat": TokenType.REPEAT,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "as": TokenType.AS,
    "function": TokenType.FUNCTION,
    "action": TokenType.ACTION,
    "return": TokenType.RETURN,
    "give": TokenType.GIVE,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "true": TokenType.TRUE,
    "yes": TokenType.TRUE,
    "false": TokenType.FALSE,
    "no": TokenType.FALSE,
    "nothing": TokenType.NOTHING,
    "none": TokenType.NOTHING,
}


@dataclass
class Token:
    type: TokenType
    value: Any
    location: SourceLocation
    source_line: str = ""

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, line={self.location.line}, col={self.location.column})"
