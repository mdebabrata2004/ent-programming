import pytest
from ent.interpreter import run_ent
from ent.runtime import RuntimeLimits
from ent.errors import EntRuntimeError, EntLimitExceededError


def test_interpret_hello_canonical():
    src = '[\n    say("Hello, World!")\n]'
    res = run_ent(src)
    assert res.success is True
    assert res.output.strip() == "Hello, World!"


def test_interpret_variables_canonical():
    src = """[
        remember(name = "ENT")
        remember(version = "0.1.0")

        say("Welcome to " + name)
        say("Version: " + version)
    ]"""
    res = run_ent(src)
    assert res.success is True
    lines = [l.strip() for l in res.output_lines]
    assert lines == ["Welcome to ENT", "Version: 0.1.0"]


def test_interpret_math_canonical():
    src = "[\n    say(2 + 2 - 9 + 3)\n]"
    res = run_ent(src)
    assert res.success is True
    assert res.output.strip() == "-2"


def test_interpret_conditions():
    src = """[
        remember(age = 20)
        if (age >= 18) [
            say("Adult")
        ] otherwise [
            say("Minor")
        ]

        age = 15
        if (age >= 18) [
            say("Adult")
        ] otherwise [
            say("Minor")
        ]
    ]"""
    res = run_ent(src)
    assert res.success is True
    assert res.output_lines == ["Adult", "Minor"]


def test_interpret_loops():
    src = """[
        remember(total = 0)
        repeat (4 as i) [
            total = total + i
        ]
        say(total)

        remember(c = 0)
        while (c < 3) [
            c = c + 1
        ]
        say(c)
    ]"""
    res = run_ent(src)
    assert res.success is True
    assert res.output_lines == ["6", "3"]


def test_interpret_functions():
    src = """[
        function multiply(x, y) [
            give x * y
        ]

        say(multiply(6, 7))
    ]"""
    res = run_ent(src)
    assert res.success is True
    assert res.output_lines == ["42"]


def test_interpret_division_by_zero():
    src = "[\n    say(10 / 0)\n]"
    res = run_ent(src)
    assert res.success is False
    assert isinstance(res.error, EntRuntimeError)
    assert "Division by zero" in str(res.error)


def test_interpret_undefined_variable():
    src = "[\n    say(unknown_variable)\n]"
    res = run_ent(src)
    assert res.success is False
    assert isinstance(res.error, EntRuntimeError)
    assert "Undefined variable" in str(res.error)


def test_interpret_infinite_loop_safety_limit():
    src = """[
        while (true) [
            remember(x = 1)
        ]
    ]"""
    # Set a tiny limit to trigger quickly
    limits = RuntimeLimits(max_steps=50)
    res = run_ent(src, limits=limits)
    assert res.success is False
    assert isinstance(res.error, EntLimitExceededError)
    assert "limit exceeded" in str(res.error)


def test_builtins_math_and_strings():
    src = """[
        say(abs(-42))
        say(min(10, 5, 20))
        say(max(10, 5, 20))
        say(power(2, 3))
        say(square_root(49))

        say(uppercase("hello"))
        say(lowercase("WORLD"))
        say(length("abcde"))
        say(contains("hello world", "world"))
        say(replace("banana", "a", "o"))
    ]"""
    res = run_ent(src)
    assert res.success is True
    assert res.output_lines == [
        "42",
        "5",
        "20",
        "8",
        "7",
        "HELLO",
        "world",
        "5",
        "true",
        "bonono",
    ]


def test_builtins_list_operations():
    src = """[
        remember(nums = [1, 2, 3])
        push(nums, 4)
        say(length(nums))
        say(pop(nums))
        say(first(nums))
        say(last(nums))
        say(join(reverse(nums), "-"))
    ]"""
    res = run_ent(src)
    assert res.success is True
    assert res.output_lines == [
        "4",
        "4",
        "1",
        "3",
        "3-2-1",
    ]
