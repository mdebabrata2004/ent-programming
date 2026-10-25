import pytest
from ent.interpreter import run_ent
from ent.runtime import RuntimeLimits
from ent.errors import EntRuntimeError, EntLimitExceededError


def test_no_host_python_globals():
    # Verify ENT code cannot access Python built-ins or modules
    for dangerous in ["__import__", "eval", "exec", "open", "os", "sys", "__builtins__"]:
        res = run_ent(f"[\n    say({dangerous})\n]")
        assert res.success is False
        assert isinstance(res.error, EntRuntimeError)
        assert "Undefined variable" in str(res.error)


def test_no_prototype_pollution_or_dunder_access():
    res = run_ent('[\n    remember(x = "test")\n    say(x.__class__)\n]')
    assert res.success is False
    assert isinstance(res.error, EntRuntimeError)


def test_recursion_limit():
    src = """[
        function recurse(n) [
            give recurse(n + 1)
        ]
        recurse(1)
    ]"""
    limits = RuntimeLimits(max_call_depth=20)
    res = run_ent(src, limits=limits)
    assert res.success is False
    assert isinstance(res.error, EntLimitExceededError)
    assert "recursion depth" in str(res.error).lower()


def test_step_limit():
    src = """[
        remember(i = 0)
        while (true) [
            i = i + 1
        ]
    ]"""
    limits = RuntimeLimits(max_steps=100)
    res = run_ent(src, limits=limits)
    assert res.success is False
    assert isinstance(res.error, EntLimitExceededError)
    assert "limit exceeded" in str(res.error).lower()


def test_no_unrestricted_filesystem_access():
    # Calling open() or file functions is not supported
    res = run_ent('[\n    open("secret.txt")\n]')
    assert res.success is False
    assert "Undefined variable" in str(res.error)
