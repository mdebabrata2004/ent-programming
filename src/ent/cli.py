"""
ENT Command-Line Interface (CLI).
Provides 'ent <file>', 'ent check <file>', 'ent repl', 'ent build <file>', and version info.
"""

from __future__ import annotations
import sys
import os
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from ent import __version__
from ent.lexer import Lexer
from ent.parser import Parser
from ent.interpreter import Interpreter, run_ent
from ent.errors import EntError
from ent.runtime import RuntimeLimits

app = typer.Typer(
    name="ent",
    help="ENT Programming Language — Beginner-friendly, English-readable language for website development.",
    add_completion=False,
    no_args_is_help=True,
)


def _print_out(message: str) -> None:
    Console().print(message)


def _print_err(message: str) -> None:
    Console(stderr=True).print(message)


def _execute_file(file_path: Path, max_steps: int = 100_000) -> None:
    if not file_path.exists():
        _print_err(f"[bold red]Error:[/bold red] File not found: '{file_path}'")
        raise typer.Exit(code=1)

    if file_path.is_dir():
        _print_err(f"[bold red]Error:[/bold red] Expected a file, but found directory: '{file_path}'")
        raise typer.Exit(code=1)

    if file_path.suffix != ".ent":
        _print_err(f"[yellow]Warning:[/yellow] File '{file_path}' does not have the recommended '.ent' extension.")

    try:
        source = file_path.read_text(encoding="utf-8")
    except Exception as ex:
        _print_err(f"[bold red]Error:[/bold red] Failed to read '{file_path}': {ex}")
        raise typer.Exit(code=1)

    limits = RuntimeLimits(max_steps=max_steps)
    res = run_ent(source, file_path=str(file_path), limits=limits, output_sink=lambda line: _print_out(line))

    if not res.success and res.error:
        _print_err(res.error.format_diagnostic())
        raise typer.Exit(code=1)

    raise typer.Exit(code=0)


def _check_file(file_path: Path) -> None:
    if not file_path.exists():
        _print_err(f"[bold red]Error:[/bold red] File not found: '{file_path}'")
        raise typer.Exit(code=1)

    try:
        source = file_path.read_text(encoding="utf-8")
    except Exception as ex:
        _print_err(f"[bold red]Error:[/bold red] Failed to read '{file_path}': {ex}")
        raise typer.Exit(code=1)

    try:
        lexer = Lexer(source, file_path=str(file_path))
        tokens = lexer.tokenize()
        parser = Parser(tokens, source=source, file_path=str(file_path))
        parser.parse()
        _print_out(f"[bold green]Success:[/bold green] Syntax check passed for '{file_path}'.")
        raise typer.Exit(code=0)
    except EntError as err:
        _print_err(err.format_diagnostic())
        raise typer.Exit(code=1)


@app.command("run")
def run_command(
    file: Path = typer.Argument(..., help="Path to .ent file to execute."),
    max_steps: int = typer.Option(100_000, "--max-steps", help="Maximum execution steps before aborting."),
) -> None:
    """Execute an ENT source file."""
    _execute_file(file, max_steps=max_steps)


@app.command("check")
def check_command(
    file: Path = typer.Argument(..., help="Path to .ent file to validate."),
) -> None:
    """Validate ENT syntax without executing."""
    _check_file(file)


@app.command("version")
def version_command() -> None:
    """Display the ENT language and CLI version."""
    _print_out(f"ENT Programming Language v{__version__}")


@app.command("repl")
def repl_command() -> None:
    """Start an interactive ENT REPL session."""
    _print_out(f"[bold cyan]ENT Interactive REPL (v{__version__})[/bold cyan]")
    _print_out("Type your ENT code, or 'exit' / 'quit' to leave. End blocks with ']'.\n")

    interpreter = Interpreter(output_sink=lambda line: _print_out(line))
    buffer: list[str] = []

    while True:
        try:
            prompt = "... " if buffer else "ent> "
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            _print_out("\nGoodbye!")
            break

        stripped = line.strip()
        if not buffer and stripped in ("exit", "quit"):
            _print_out("Goodbye!")
            break

        if not buffer and not stripped:
            continue

        buffer.append(line)
        full_code = "\n".join(buffer)

        # Auto-wrap bare expressions or statements in [ ... ] for REPL convenience
        code_to_try = full_code.strip()
        if not code_to_try.startswith("["):
            wrapped_code = f"[\n    {code_to_try}\n]"
        else:
            wrapped_code = code_to_try

        # Check if brackets are balanced
        open_sq = wrapped_code.count("[")
        close_sq = wrapped_code.count("]")
        if open_sq > close_sq:
            continue

        try:
            lexer = Lexer(wrapped_code, file_path="<repl>")
            tokens = lexer.tokenize()
            parser = Parser(tokens, source=wrapped_code, file_path="<repl>")
            prog = parser.parse()
            res = interpreter.execute_program(prog)
            if not res.success and res.error:
                _print_err(res.error.format_diagnostic())
        except EntError as err:
            _print_err(err.format_diagnostic())
        except Exception as ex:
            _print_err(f"[bold red]Unexpected Error:[/bold red] {ex}")

        buffer.clear()


@app.command("build")
def build_command(
    file: Path = typer.Argument(..., help="Path to .ent file containing web page definition."),
    out_dir: Path = typer.Option(Path("dist"), "--out", "-o", help="Output directory for generated website."),
) -> None:
    """Build a static website from an ENT source file."""
    from ent.web.builder import build_website_from_file

    if not file.exists():
        _print_err(f"[bold red]Error:[/bold red] File not found: '{file}'")
        raise typer.Exit(code=1)

    try:
        out_html = build_website_from_file(file, out_dir=out_dir)
        _print_out(f"[bold green]Success:[/bold green] Built website at '{out_html}'")
        raise typer.Exit(code=0)
    except (typer.Exit, typer.Abort):
        raise
    except EntError as err:
        _print_err(err.format_diagnostic())
        raise typer.Exit(code=1)
    except Exception as ex:
        _print_err(f"[bold red]Build Error:[/bold red] {ex}")
        raise typer.Exit(code=1)


def main() -> None:
    """Main CLI entrypoint with transparent 'ent <file>' support."""
    args = sys.argv[1:]
    known_commands = {"run", "check", "repl", "build", "version"}
    known_flags = {"--help", "-h", "--version", "-v"}

    # Handle --version flag directly
    if "--version" in args or "-v" in args:
        _print_out(f"ENT Programming Language v{__version__}")
        sys.exit(0)

    # If first arg is not a subcommand or flag, assume 'run'
    if args and args[0] not in known_commands and not args[0].startswith("-"):
        sys.argv.insert(1, "run")

    app()


if __name__ == "__main__":
    main()
