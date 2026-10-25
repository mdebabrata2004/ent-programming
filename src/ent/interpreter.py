"""
AST Tree-Walking Interpreter and Execution Engine for ENT.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from ent.ast_nodes import (
    Program,
    Block,
    Statement,
    RememberStatement,
    AssignmentStatement,
    IfStatement,
    WhileStatement,
    RepeatStatement,
    ForStatement,
    FunctionDefStatement,
    ReturnStatement,
    BlockCallStatement,
    ExpressionStatement,
    Expression,
    Literal,
    Identifier,
    BinaryOp,
    UnaryOp,
    CallExpr,
    ListLiteral,
    IndexExpr,
    MemberExpr,
)
from ent.runtime import (
    Scope,
    RuntimeLimits,
    EntValue,
    EntNumber,
    EntString,
    EntBool,
    EntNull,
    EntList,
    EntFunction,
    EntBuiltinFunction,
    EntUIElement,
    ReturnSignal,
    to_ent_value,
)
from ent.builtins import register_standard_builtins
from ent.errors import EntError, EntRuntimeError, SourceLocation
from ent.lexer import Lexer
from ent.parser import Parser


@dataclass
class InterpreterResult:
    output: str
    output_lines: List[str] = field(default_factory=list)
    success: bool = True
    error: Optional[EntError] = None
    steps: int = 0


class Interpreter:
    """Interprets ENT AST nodes using lexical environments and safety limits."""

    def __init__(
        self,
        limits: Optional[RuntimeLimits] = None,
        output_sink: Optional[Callable[[str], None]] = None,
        custom_block_handler: Optional[Callable[[BlockCallStatement, Scope, Interpreter], Any]] = None,
    ):
        self.limits = limits or RuntimeLimits()
        self.output_lines: List[str] = []
        self.custom_block_handler = custom_block_handler

        def default_sink(line: str) -> None:
            self.output_lines.append(line)
            if output_sink:
                output_sink(line)

        self.output_sink = default_sink
        self.global_scope = Scope(name="global")
        register_standard_builtins(self.global_scope, output_sink=self.output_sink)

    def execute_program(self, program: Program) -> InterpreterResult:
        try:
            self.execute_block(program.body, self.global_scope)
            return InterpreterResult(
                output="\n".join(self.output_lines) + ("\n" if self.output_lines else ""),
                output_lines=self.output_lines,
                success=True,
                steps=self.limits.steps_executed,
            )
        except EntError as err:
            return InterpreterResult(
                output="\n".join(self.output_lines) + ("\n" if self.output_lines else ""),
                output_lines=self.output_lines,
                success=False,
                error=err,
                steps=self.limits.steps_executed,
            )

    def execute_block(self, block: Block, scope: Scope) -> None:
        for stmt in block.statements:
            self.limits.tick(stmt.location)
            self.execute_statement(stmt, scope)

    def execute_statement(self, stmt: Statement, scope: Scope) -> None:
        if isinstance(stmt, RememberStatement):
            for name, expr in stmt.declarations:
                val = self.evaluate_expression(expr, scope)
                scope.define(name, val)

        elif isinstance(stmt, AssignmentStatement):
            val = self.evaluate_expression(stmt.value, scope)
            scope.assign(stmt.name, val)

        elif isinstance(stmt, IfStatement):
            cond_val = self.evaluate_expression(stmt.condition, scope)
            if cond_val.is_truthy():
                then_scope = Scope(parent=scope, name="if_then")
                self.execute_block(stmt.then_branch, then_scope)
            else:
                executed_elif = False
                for elif_cond, elif_body in stmt.elif_branches:
                    self.limits.tick(elif_cond.location)
                    if self.evaluate_expression(elif_cond, scope).is_truthy():
                        elif_scope = Scope(parent=scope, name="if_elif")
                        self.execute_block(elif_body, elif_scope)
                        executed_elif = True
                        break
                if not executed_elif and stmt.else_branch is not None:
                    else_scope = Scope(parent=scope, name="if_else")
                    self.execute_block(stmt.else_branch, else_scope)

        elif isinstance(stmt, WhileStatement):
            while True:
                self.limits.tick(stmt.location)
                cond_val = self.evaluate_expression(stmt.condition, scope)
                if not cond_val.is_truthy():
                    break
                loop_scope = Scope(parent=scope, name="while_body")
                self.execute_block(stmt.body, loop_scope)

        elif isinstance(stmt, RepeatStatement):
            count_val = self.evaluate_expression(stmt.count, scope)
            if not isinstance(count_val, EntNumber):
                raise EntRuntimeError(
                    f"Repeat count must be a number, got {type(count_val).__name__}.",
                    location=stmt.location,
                    suggestion="Example: repeat (5) [ say(\"Hi\") ]",
                )
            count = int(count_val.value)
            if count < 0:
                count = 0
            for i in range(count):
                self.limits.tick(stmt.location)
                loop_scope = Scope(parent=scope, name="repeat_body")
                if stmt.counter_var:
                    loop_scope.define(stmt.counter_var, EntNumber(i))
                self.execute_block(stmt.body, loop_scope)

        elif isinstance(stmt, ForStatement):
            iter_val = self.evaluate_expression(stmt.iterable, scope)
            items: List[EntValue] = []
            if isinstance(iter_val, EntList):
                items = iter_val.elements
            elif isinstance(iter_val, EntString):
                items = [EntString(ch) for ch in iter_val.value]
            else:
                raise EntRuntimeError(
                    f"Cannot iterate over {type(iter_val).__name__}.",
                    location=stmt.location,
                    suggestion="In ENT, for-loops iterate over lists or strings: for (x in items) [ ... ]",
                )
            for item in items:
                self.limits.tick(stmt.location)
                loop_scope = Scope(parent=scope, name="for_body")
                loop_scope.define(stmt.item_name, item)
                self.execute_block(stmt.body, loop_scope)

        elif isinstance(stmt, FunctionDefStatement):
            fn = EntFunction(
                name=stmt.name,
                parameters=stmt.parameters,
                body=stmt.body,
                closure_scope=scope,
            )
            scope.define(stmt.name, fn)

        elif isinstance(stmt, ReturnStatement):
            val = EntNull()
            if stmt.value is not None:
                val = self.evaluate_expression(stmt.value, scope)
            raise ReturnSignal(val)

        elif isinstance(stmt, BlockCallStatement):
            if self.custom_block_handler:
                self.custom_block_handler(stmt, scope, self)
            else:
                # Default console mode execution for web and custom blocks
                block_scope = Scope(parent=scope, name=stmt.name)
                if stmt.name == "page":
                    title = "ENT Website"
                    if "title" in stmt.kwargs:
                        title = self.evaluate_expression(stmt.kwargs["title"], scope).to_display_string()
                    elif stmt.args:
                        title = self.evaluate_expression(stmt.args[0], scope).to_display_string()
                    self.output_sink(f"[Page: {title}]")
                elif stmt.name in ("section", "container", "box"):
                    self.output_sink(f"[{stmt.name.capitalize()}]")
                self.execute_block(stmt.body, block_scope)

        elif isinstance(stmt, ExpressionStatement):
            self.evaluate_expression(stmt.expression, scope)

    def evaluate_expression(self, expr: Expression, scope: Scope) -> EntValue:
        self.limits.tick(expr.location)

        if isinstance(expr, Literal):
            return to_ent_value(expr.value)

        elif isinstance(expr, Identifier):
            val = scope.lookup(expr.name)
            if val is None:
                raise EntRuntimeError(
                    f"Undefined variable or function '{expr.name}'.",
                    location=expr.location,
                    suggestion=f"Did you forget to define '{expr.name}' with remember({expr.name} = ...) first?",
                )
            return val

        elif isinstance(expr, UnaryOp):
            operand = self.evaluate_expression(expr.operand, scope)
            if expr.operator == "-":
                if not isinstance(operand, EntNumber):
                    raise EntRuntimeError(
                        f"Cannot negate non-number type {type(operand).__name__}.",
                        location=expr.location,
                    )
                return EntNumber(-operand.value)
            elif expr.operator == "+":
                if not isinstance(operand, EntNumber):
                    raise EntRuntimeError(
                        f"Unary '+' requires a number, got {type(operand).__name__}.",
                        location=expr.location,
                    )
                return operand
            elif expr.operator == "not":
                return EntBool(not operand.is_truthy())
            else:
                raise EntRuntimeError(f"Unknown unary operator '{expr.operator}'.", location=expr.location)

        elif isinstance(expr, BinaryOp):
            # Short-circuit logical operators
            if expr.operator == "and":
                left = self.evaluate_expression(expr.left, scope)
                if not left.is_truthy():
                    return left
                return self.evaluate_expression(expr.right, scope)

            if expr.operator == "or":
                left = self.evaluate_expression(expr.left, scope)
                if left.is_truthy():
                    return left
                return self.evaluate_expression(expr.right, scope)

            left = self.evaluate_expression(expr.left, scope)
            right = self.evaluate_expression(expr.right, scope)

            # Addition & string concatenation
            if expr.operator == "+":
                if isinstance(left, EntNumber) and isinstance(right, EntNumber):
                    res = left.value + right.value
                    return EntNumber(int(res) if isinstance(res, float) and res.is_integer() else res)
                # Beginner-friendly string concatenation
                if isinstance(left, EntString) or isinstance(right, EntString):
                    return EntString(left.to_display_string() + right.to_display_string())
                if isinstance(left, EntList) and isinstance(right, EntList):
                    return EntList(left.elements + right.elements)
                raise EntRuntimeError(
                    f"Cannot add {type(left).__name__} and {type(right).__name__}.",
                    location=expr.location,
                )

            # Subtraction
            if expr.operator == "-":
                if isinstance(left, EntNumber) and isinstance(right, EntNumber):
                    res = left.value - right.value
                    return EntNumber(int(res) if isinstance(res, float) and res.is_integer() else res)
                raise EntRuntimeError(
                    f"Subtraction requires numbers, got {type(left).__name__} and {type(right).__name__}.",
                    location=expr.location,
                )

            # Multiplication
            if expr.operator == "*":
                if isinstance(left, EntNumber) and isinstance(right, EntNumber):
                    res = left.value * right.value
                    return EntNumber(int(res) if isinstance(res, float) and res.is_integer() else res)
                if isinstance(left, EntString) and isinstance(right, EntNumber):
                    return EntString(left.value * max(0, int(right.value)))
                if isinstance(left, EntList) and isinstance(right, EntNumber):
                    return EntList(left.elements * max(0, int(right.value)))
                raise EntRuntimeError(
                    f"Multiplication requires numbers or string/list * number.",
                    location=expr.location,
                )

            # Division
            if expr.operator == "/":
                if not isinstance(left, EntNumber) or not isinstance(right, EntNumber):
                    raise EntRuntimeError(
                        f"Division requires numbers, got {type(left).__name__} and {type(right).__name__}.",
                        location=expr.location,
                    )
                if right.value == 0:
                    raise EntRuntimeError("Division by zero.", location=expr.location)
                res = left.value / right.value
                return EntNumber(int(res) if res.is_integer() else res)

            # Modulo
            if expr.operator == "%":
                if not isinstance(left, EntNumber) or not isinstance(right, EntNumber):
                    raise EntRuntimeError(
                        f"Modulo requires numbers, got {type(left).__name__} and {type(right).__name__}.",
                        location=expr.location,
                    )
                if right.value == 0:
                    raise EntRuntimeError("Modulo by zero.", location=expr.location)
                return EntNumber(left.value % right.value)

            # Equality
            if expr.operator == "==":
                return EntBool(left.unwrap() == right.unwrap())
            if expr.operator == "!=":
                return EntBool(left.unwrap() != right.unwrap())

            # Relational comparisons
            if expr.operator in ("<", "<=", ">", ">="):
                if isinstance(left, EntNumber) and isinstance(right, EntNumber):
                    lv, rv = left.value, right.value
                elif isinstance(left, EntString) and isinstance(right, EntString):
                    lv, rv = left.value, right.value
                else:
                    raise EntRuntimeError(
                        f"Cannot compare {type(left).__name__} and {type(right).__name__}.",
                        location=expr.location,
                    )
                if expr.operator == "<":
                    return EntBool(lv < rv)
                elif expr.operator == "<=":
                    return EntBool(lv <= rv)
                elif expr.operator == ">":
                    return EntBool(lv > rv)
                elif expr.operator == ">=":
                    return EntBool(lv >= rv)

            raise EntRuntimeError(f"Unsupported binary operator '{expr.operator}'.", location=expr.location)

        elif isinstance(expr, CallExpr):
            callee_val = self.evaluate_expression(expr.callee, scope)
            eval_args = [self.evaluate_expression(a, scope) for a in expr.args]
            eval_kwargs = {k: self.evaluate_expression(v, scope) for k, v in expr.kwargs.items()}

            if isinstance(callee_val, EntBuiltinFunction):
                try:
                    return callee_val.fn(*eval_args, **eval_kwargs)
                except EntError:
                    raise
                except Exception as ex:
                    raise EntRuntimeError(str(ex), location=expr.location)

            elif isinstance(callee_val, EntFunction):
                if len(eval_args) != len(callee_val.parameters):
                    raise EntRuntimeError(
                        f"Function '{callee_val.name}' expects {len(callee_val.parameters)} arguments, got {len(eval_args)}.",
                        location=expr.location,
                    )
                call_scope = Scope(parent=callee_val.closure_scope, name=f"call_{callee_val.name}")
                for param_name, arg_val in zip(callee_val.parameters, eval_args):
                    call_scope.define(param_name, arg_val)

                self.limits.enter_call(expr.location)
                try:
                    self.execute_block(callee_val.body, call_scope)
                except ReturnSignal as ret:
                    return ret.value
                finally:
                    self.limits.exit_call()
                return EntNull()

            else:
                raise EntRuntimeError(
                    f"Target '{callee_val.to_display_string()}' is not callable.",
                    location=expr.location,
                )

        elif isinstance(expr, ListLiteral):
            elements = [self.evaluate_expression(elem, scope) for elem in expr.elements]
            return EntList(elements)

        elif isinstance(expr, IndexExpr):
            target_val = self.evaluate_expression(expr.target, scope)
            idx_val = self.evaluate_expression(expr.index, scope)

            if not isinstance(idx_val, EntNumber):
                raise EntRuntimeError("List/string index must be a number.", location=expr.location)
            idx = int(idx_val.value)

            if isinstance(target_val, EntList):
                if idx < 0 or idx >= len(target_val.elements):
                    raise EntRuntimeError(
                        f"Index {idx} out of range for list of length {len(target_val.elements)}.",
                        location=expr.location,
                    )
                return target_val.elements[idx]
            elif isinstance(target_val, EntString):
                if idx < 0 or idx >= len(target_val.value):
                    raise EntRuntimeError(
                        f"Index {idx} out of range for string of length {len(target_val.value)}.",
                        location=expr.location,
                    )
                return EntString(target_val.value[idx])
            else:
                raise EntRuntimeError(f"Cannot index into {type(target_val).__name__}.", location=expr.location)

        elif isinstance(expr, MemberExpr):
            target_val = self.evaluate_expression(expr.target, scope)
            if isinstance(target_val, EntUIElement):
                if expr.member in target_val.props:
                    return to_ent_value(target_val.props[expr.member])
            raise EntRuntimeError(
                f"Property '{expr.member}' not found on {type(target_val).__name__}.",
                location=expr.location,
            )

        raise EntRuntimeError(f"Cannot evaluate AST node {type(expr).__name__}.", location=expr.location)


def run_ent(
    source: str,
    file_path: str = "<stdin>",
    limits: Optional[RuntimeLimits] = None,
    output_sink: Optional[Callable[[str], None]] = None,
) -> InterpreterResult:
    """Convenience function: Lex -> Parse -> Execute."""
    try:
        lexer = Lexer(source, file_path=file_path)
        tokens = lexer.tokenize()
        parser = Parser(tokens, source=source, file_path=file_path)
        program = parser.parse()
        interpreter = Interpreter(limits=limits, output_sink=output_sink)
        return interpreter.execute_program(program)
    except EntError as err:
        return InterpreterResult(
            output="",
            output_lines=[],
            success=False,
            error=err,
            steps=0,
        )
