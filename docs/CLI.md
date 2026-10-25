# ENT Command-Line Interface (CLI) Guide

The `ent` CLI provides a developer experience for executing, validating, building, and interactively experimenting with ENT code.

---

## 1. Installation

Install the package in development mode:

```bash
pip install -e .
```

Verify installation:

```bash
ent --version
```

---

## 2. Command Reference

### Run a Script

Execute an ENT source file:

```bash
# Direct run
ent hello.ent

# Or using the run subcommand
ent run hello.ent
```

Output is sent to `stdout`. Any runtime or syntax errors are formatted and sent to `stderr` with exit code `1`.

### Check Syntax

Lex and parse a file without executing it:

```bash
ent check script.ent
```

- **Exit Code 0**: Syntax is valid.
- **Exit Code 1**: Syntax error found with line, column, and suggestion.

### Interactive REPL

Start an interactive session:

```bash
ent repl
```

Example session:

```
ENT Interactive REPL (v0.1.0)
Type your ENT code, or 'exit' / 'quit' to leave. End blocks with ']'.

ent> say("Hello from REPL!")
Hello from REPL!
ent> remember(x = 10, y = 20)
ent> say(x + y)
30
ent> exit
Goodbye!
```

### Build a Website

Compile a static website into inspectable HTML and CSS:

```bash
ent build website.ent -o dist/
```

Generated files:
- `dist/index.html`
- `dist/style.css`

---

## 3. Exit Codes

| Exit Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Error (File not found, syntax error, runtime error, build failure) |
| `2` | Invalid CLI arguments |
