# ENT Programming Architecture

## 1. System Overview

ENT is an interpreted, English-readable programming language built for beginners and website creation.

```
       +---------------------------------------------+
       |             ENT Source Code (.ent)          |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |             Lexer (lexer.py)                |
       |  - Tokenization, line & column tracking     |
       |  - Forbids '{' and '}', enforces brackets   |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |             Parser (parser.py)              |
       |  - Recursive-descent Pratt parser           |
       |  - AST construction (ast_nodes.py)          |
       |  - Detailed syntax diagnostic reporting     |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |          AST (Abstract Syntax Tree)         |
       +---------------------------------------------+
                       /              \
                      /                \
                     v                  v
       +-----------------------+  +-----------------------+
       | Interpreter (runtime) |  | Web Builder (web/)    |
       | - Environment & scope |  | - HTML5 & CSS gen     |
       | - Step limits & safety|  | - Safe XSS sanitizing |
       | - Builtins execution  |  | - Standalone bundle   |
       +-----------------------+  +-----------------------+
                   |                          |
                   +------------+-------------+
                                |
                   +------------+------------+
                   |                         |
                   v                         v
       +-----------------------+  +-----------------------+
       |    CLI (ent cli)      |  |    ENT Studio (IDE)   |
       | - ent <file>          |  | - Monaco Editor       |
       | - ent check <file>    |  | - Web preview iframe  |
       | - ent repl            |  | - FastAPI service     |
       | - ent build <file>    |  | - Shared engine       |
       +-----------------------+  +-----------------------+
```

---

## 2. Core Modules

| Module | Location | Purpose |
|---|---|---|
| `tokens.py` | `src/ent/tokens.py` | Token definitions, TokenType enum, source Position tracking. |
| `lexer.py` | `src/ent/lexer.py` | Character stream scanner, lexical error generator. |
| `ast_nodes.py` | `src/ent/ast_nodes.py` | Structured AST node representations (dataclasses). |
| `parser.py` | `src/ent/parser.py` | Hand-written recursive descent & Pratt parser with bracket matching. |
| `runtime.py` | `src/ent/runtime.py` | Execution environment, Scopes, ENT Value types (`EntNumber`, `EntString`, `EntBool`, `EntList`, `EntFunction`, `EntNull`). |
| `interpreter.py` | `src/ent/interpreter.py` | Tree-walking AST evaluator with step counter and safety limits. |
| `errors.py` | `src/ent/errors.py` | Structured error hierarchy (`EntError`, `EntLexicalError`, `EntSyntaxError`, `EntRuntimeError`, `EntSecurityError`). |
| `builtins/` | `src/ent/builtins/` | Core standard library functions: `say`, `remember`, string/math helpers. |
| `web/` | `src/ent/web/` | Web page AST generation, HTML/CSS builder, and local execution API. |
| `cli.py` | `src/ent/cli.py` | Typer-powered command-line interface. |

---

## 3. Sandboxing and Security Rules

1. **No Host Execution:** Never call `eval()`, `exec()`, `os.system()`, or `subprocess.Popen()` to evaluate ENT programs.
2. **Execution Quotas:**
   - Maximum evaluation steps: default 100,000 steps.
   - Maximum recursion depth: default 256 frames.
   - Maximum source length: default 1,000,000 characters.
3. **Allowlist-Only Builtins:** Only functions registered in the `BuiltinRegistry` are accessible. No Python module reflection (`__builtins__`, `__globals__`, `importlib`).
4. **HTML Output Sanitization:** All text rendered into static HTML pages is escaped via `html.escape()` unless explicitly tagged as safe.
5. **Single Engine Principle:** Both the CLI and the web IDE API call the identical `Interpreter` and `Parser` classes.
