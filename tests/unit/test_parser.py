import pytest
from ent.lexer import Lexer
from ent.parser import Parser
from ent.ast_nodes import (
    Program,
    RememberStatement,
    AssignmentStatement,
    IfStatement,
    WhileStatement,
    RepeatStatement,
    FunctionDefStatement,
    ExpressionStatement,
    BinaryOp,
    Literal,
    BlockCallStatement,
)
from ent.errors import EntSyntaxError


def parse_src(source: str) -> Program:
    tokens = Lexer(source).tokenize()
    return Parser(tokens, source=source).parse()


def test_parse_valid_program():
    prog = parse_src('[\n    say("Hello, World!")\n]')
    assert isinstance(prog, Program)
    assert len(prog.body.statements) == 1
    assert isinstance(prog.body.statements[0], ExpressionStatement)


def test_parse_missing_outer_brackets():
    with pytest.raises(EntSyntaxError) as exc_info:
        parse_src('say("Hello, World!")')
    assert "must be enclosed in square brackets" in str(exc_info.value)


def test_parse_unclosed_outer_bracket():
    with pytest.raises(EntSyntaxError) as exc_info:
        parse_src('[ say("Hello")')
    assert "Unclosed program block" in str(exc_info.value)


def test_parse_code_after_outer_bracket():
    with pytest.raises(EntSyntaxError) as exc_info:
        parse_src('[ say("Hello") ] say("Extra")')
    assert "Unexpected code found after closing program bracket" in str(exc_info.value)


def test_parse_remember_variable():
    prog = parse_src('[\n    remember(name = "ENT", version = "0.1.0")\n]')
    stmt = prog.body.statements[0]
    assert isinstance(stmt, RememberStatement)
    assert len(stmt.declarations) == 2
    assert stmt.declarations[0][0] == "name"
    assert stmt.declarations[1][0] == "version"


def test_parse_assignment():
    prog = parse_src('[\n    remember(x = 1)\n    x = 10\n]')
    assert isinstance(prog.body.statements[1], AssignmentStatement)
    assert prog.body.statements[1].name == "x"


def test_parse_operator_precedence():
    # 2 + 3 * 4 should be parsed as 2 + (3 * 4)
    prog = parse_src('[\n    say(2 + 3 * 4)\n]')
    expr_stmt = prog.body.statements[0]
    call = expr_stmt.expression
    arg = call.args[0]
    assert isinstance(arg, BinaryOp)
    assert arg.operator == "+"
    assert isinstance(arg.left, Literal) and arg.left.value == 2
    assert isinstance(arg.right, BinaryOp) and arg.right.operator == "*"


def test_parse_if_otherwise():
    src = """[
        if (age >= 18) [
            say("Adult")
        ] otherwise if (age >= 13) [
            say("Teen")
        ] otherwise [
            say("Child")
        ]
    ]"""
    prog = parse_src(src)
    stmt = prog.body.statements[0]
    assert isinstance(stmt, IfStatement)
    assert len(stmt.elif_branches) == 1
    assert stmt.else_branch is not None


def test_parse_repeat_and_while():
    src = """[
        repeat (5 as i) [
            say(i)
        ]
        while (count < 10) [
            count = count + 1
        ]
    ]"""
    prog = parse_src(src)
    assert isinstance(prog.body.statements[0], RepeatStatement)
    assert prog.body.statements[0].counter_var == "i"
    assert isinstance(prog.body.statements[1], WhileStatement)


def test_parse_function_and_return():
    src = """[
        function add(a, b) [
            give a + b
        ]
    ]"""
    prog = parse_src(src)
    stmt = prog.body.statements[0]
    assert isinstance(stmt, FunctionDefStatement)
    assert stmt.name == "add"
    assert stmt.parameters == ["a", "b"]


def test_parse_question_syntax_rejection():
    # Test Section 6: what is my age?
    with pytest.raises(EntSyntaxError) as exc_info:
        parse_src('[\n    what is my age?\n]')
    assert "Natural-language question syntax" in str(exc_info.value)


def test_parse_block_call():
    src = """[
        page(title = "My Website") [
            heading("Hello")
        ]
    ]"""
    prog = parse_src(src)
    stmt = prog.body.statements[0]
    assert isinstance(stmt, BlockCallStatement)
    assert stmt.name == "page"
    assert "title" in stmt.kwargs
    assert len(stmt.body.statements) == 1
