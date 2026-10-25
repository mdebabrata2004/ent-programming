"""
Abstract Syntax Tree (AST) node definitions for the ENT programming language.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple, Dict
from ent.errors import SourceLocation


@dataclass
class ASTNode:
    location: SourceLocation = field(default_factory=SourceLocation)


# Statements
@dataclass
class Statement(ASTNode):
    pass


@dataclass
class Block(ASTNode):
    statements: List[Statement] = field(default_factory=list)


@dataclass
class Program(ASTNode):
    body: Block = field(default_factory=Block)


@dataclass
class RememberStatement(Statement):
    """remember(name = expr, ...)"""
    declarations: List[Tuple[str, Expression]] = field(default_factory=list)


@dataclass
class AssignmentStatement(Statement):
    """name = expr"""
    name: str = ""
    value: Optional[Expression] = None


@dataclass
class IfStatement(Statement):
    """if (cond) [ ... ] otherwise if (cond) [ ... ] otherwise [ ... ]"""
    condition: Optional[Expression] = None
    then_branch: Optional[Block] = None
    elif_branches: List[Tuple[Expression, Block]] = field(default_factory=list)
    else_branch: Optional[Block] = None


@dataclass
class WhileStatement(Statement):
    """while (cond) [ ... ]"""
    condition: Optional[Expression] = None
    body: Optional[Block] = None


@dataclass
class RepeatStatement(Statement):
    """repeat (count) [ ... ] or repeat (count as i) [ ... ]"""
    count: Optional[Expression] = None
    counter_var: Optional[str] = None
    body: Optional[Block] = None


@dataclass
class ForStatement(Statement):
    """for (item in iterable) [ ... ]"""
    item_name: str = ""
    iterable: Optional[Expression] = None
    body: Optional[Block] = None


@dataclass
class FunctionDefStatement(Statement):
    """function name(arg1, arg2) [ ... ] or action name(...) [ ... ]"""
    name: str = ""
    parameters: List[str] = field(default_factory=list)
    body: Optional[Block] = None


@dataclass
class ReturnStatement(Statement):
    """return expr or give expr"""
    value: Optional[Expression] = None


@dataclass
class BlockCallStatement(Statement):
    """page(title = "...") [ ... ] or section(...) [ ... ]"""
    name: str = ""
    args: List[Expression] = field(default_factory=list)
    kwargs: Dict[str, Expression] = field(default_factory=dict)
    body: Optional[Block] = None


@dataclass
class ExpressionStatement(Statement):
    """say(...) or any expression evaluated for side effects"""
    expression: Optional[Expression] = None


# Expressions
@dataclass
class Expression(ASTNode):
    pass


@dataclass
class Literal(Expression):
    value: Any = None


@dataclass
class Identifier(Expression):
    name: str = ""


@dataclass
class BinaryOp(Expression):
    left: Optional[Expression] = None
    operator: str = ""
    right: Optional[Expression] = None


@dataclass
class UnaryOp(Expression):
    operator: str = ""
    operand: Optional[Expression] = None


@dataclass
class CallExpr(Expression):
    callee: Optional[Expression] = None
    args: List[Expression] = field(default_factory=list)
    kwargs: Dict[str, Expression] = field(default_factory=dict)


@dataclass
class ListLiteral(Expression):
    elements: List[Expression] = field(default_factory=list)


@dataclass
class IndexExpr(Expression):
    target: Optional[Expression] = None
    index: Optional[Expression] = None


@dataclass
class MemberExpr(Expression):
    target: Optional[Expression] = None
    member: str = ""
