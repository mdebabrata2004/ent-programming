# Changelog

All notable changes to the ENT Programming Language project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-10-25

### Added
- **Language Core**:
  - Deterministic Lexer with line/column tracking, bracket pairing, comments (`#` and `//`), and escape sequences.
  - Recursive-descent Pratt parser enforcing mandatory program delimiters `[ ... ]` and rejecting forbidden curly braces `{ }`.
  - Structured Abstract Syntax Tree (AST) representations.
  - Safe tree-walking interpreter with execution step limits and recursion depth protection.
  - Variable declaration and assignment: `remember(name = value)` and `name = value`.
  - Beginner-friendly console output: `say(...)`.
  - Operators: Arithmetic (`+`, `-`, `*`, `/`, `%`), comparison (`==`, `!=`, `<`, `<=`, `>`, `>=`), logical (`and`, `or`, `not`).
  - Control flow: `if (...) [ ... ] otherwise [ ... ]`, `while (...) [ ... ]`, `repeat (count as i) [ ... ]`, and `for (item in list) [ ... ]`.
  - User-defined functions: `function name(params) [ ... ]` and `give` / `return`.
  - Standard library: Math helpers (`round`, `abs`, `min`, `max`, `power`, `square_root`), string helpers (`uppercase`, `lowercase`, `split`, `join`, `replace`, `contains`), and list helpers (`push`, `pop`, `first`, `last`, `reverse`, `range`).
- **Command-Line Interface (CLI)**:
  - `ent <file>`: Direct script execution.
  - `ent check <file>`: Fast syntax validation.
  - `ent repl`: Interactive read-eval-print loop with multiline bracket matching.
  - `ent build <file>`: Static website compiler.
  - `ent --version` and `ent --help`.
- **Static Website Generation**:
  - Web built-in primitives: `page`, `heading`, `paragraph`, `button`, `link`, `image`, `section`, `style`.
  - Automatic XSS sanitization and semantic HTML5/CSS generation.
- **ENT Studio Web IDE**:
  - Modern web IDE built with React, TypeScript, Vite, and Monaco Editor.
  - Custom Monaco syntax highlighting for ENT and keyword autocompletion.
  - Real-time execution console, live sandboxed web preview iframe, and structured error diagnostics.
  - Local FastAPI execution engine with zero host pollution.
- **Testing & Documentation**:
  - 57 automated tests covering unit, integration, and security sandboxing.
  - Comprehensive documentation in `docs/`: language spec, grammar, architecture, CLI, IDE, web development, security, roadmap, and FAQ.
