from pathlib import Path
import pytest
from typer.testing import CliRunner
from ent.cli import app
from ent import __version__

runner = CliRunner()


def test_cli_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert f"ENT Programming Language v{__version__}" in result.output


def test_cli_help_command():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ENT Programming Language" in result.output
    assert "check" in result.output
    assert "run" in result.output
    assert "repl" in result.output


def test_cli_run_valid_file(tmp_path: Path):
    f = tmp_path / "test.ent"
    f.write_text('[\n    say("CLI Test Output")\n]', encoding="utf-8")

    result = runner.invoke(app, ["run", str(f)])
    assert result.exit_code == 0
    assert "CLI Test Output" in result.output


def test_cli_run_missing_file(tmp_path: Path):
    missing_file = tmp_path / "nonexistent.ent"
    result = runner.invoke(app, ["run", str(missing_file)])
    assert result.exit_code == 1
    assert "File not found" in result.output or "Error" in result.output


def test_cli_run_syntax_error(tmp_path: Path):
    f = tmp_path / "bad_syntax.ent"
    f.write_text('[\n    say("missing closing paren"\n]', encoding="utf-8")

    result = runner.invoke(app, ["run", str(f)])
    assert result.exit_code == 1
    assert "Syntax Error" in result.output


def test_cli_run_runtime_error(tmp_path: Path):
    f = tmp_path / "runtime_err.ent"
    f.write_text('[\n    say(10 / 0)\n]', encoding="utf-8")

    result = runner.invoke(app, ["run", str(f)])
    assert result.exit_code == 1
    assert "Division by zero" in result.output


def test_cli_check_valid_file(tmp_path: Path):
    f = tmp_path / "valid.ent"
    f.write_text('[\n    remember(x = 10)\n    say(x)\n]', encoding="utf-8")

    result = runner.invoke(app, ["check", str(f)])
    assert result.exit_code == 0
    assert "Syntax check passed" in result.output


def test_cli_check_invalid_file(tmp_path: Path):
    f = tmp_path / "invalid.ent"
    f.write_text('say("No outer brackets")', encoding="utf-8")

    result = runner.invoke(app, ["check", str(f)])
    assert result.exit_code == 1
    assert "Syntax Error" in result.output


def test_cli_new_command_valid(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["new", "my-portfolio"])
    assert result.exit_code == 0
    assert "Created new ENT project" in result.output
    proj_dir = tmp_path / "my-portfolio"
    assert proj_dir.is_dir()
    assert (proj_dir / "website.ent").is_file()
    assert (proj_dir / "README.md").is_file()


def test_cli_new_command_invalid_name(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["new", "../bad_path"])
    assert result.exit_code == 1
    assert "Invalid project name" in result.output


def test_cli_new_command_existing_dir(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    existing = tmp_path / "existing-proj"
    existing.mkdir()
    (existing / "file.txt").write_text("content")

    result = runner.invoke(app, ["new", "existing-proj"])
    assert result.exit_code == 1
    assert "already exists and is not empty" in result.output


def test_cli_dev_missing_file(tmp_path: Path):
    result = runner.invoke(app, ["dev", str(tmp_path / "missing.ent")])
    assert result.exit_code == 1
    assert "File not found" in result.output
