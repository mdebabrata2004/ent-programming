# Contributing to ENT Programming

Thank you for your interest in contributing to **ENT Programming**!
ENT is an open-source, beginner-friendly programming language designed for readability and website development.

---

## Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free environment for everyone. Please be respectful and constructive in all interactions.

---

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- Git

### 1. Clone & Set Up Python Environment

```bash
git clone https://github.com/mdebabrata2004/ent-programming.git
cd ent-programming

# Create virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable development mode with test dependencies
pip install -e ".[dev]"
```

### 2. Set Up Web IDE

```bash
cd ide
npm install
npm run build
cd ..
```

---

## Running Tests

We maintain 100% passing automated tests across unit, integration, and security test suites.

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test suites
pytest tests/unit/
pytest tests/integration/
pytest tests/security/
```

---

## Project Structure

- `src/ent/`: Core language implementation (Lexer, Parser, AST, Interpreter, Runtime, Built-ins).
- `src/ent/web/`: Static website builder and FastAPI local execution server.
- `ide/`: ENT Studio web IDE (React, TypeScript, Monaco Editor, Vite).
- `examples/`: Canonical sample `.ent` programs.
- `tests/`: Automated unit, integration, and security test suites.
- `docs/`: Comprehensive technical documentation and specifications.

---

## Pull Request Guidelines

1. **Keep Grammar Unambiguous**: ENT syntax changes must be accompanied by updates to `docs/GRAMMAR.md` and `docs/LANGUAGE_SPEC.md`.
2. **Add Tests**: All bug fixes and features require automated pytest coverage.
3. **No Unsafe Execution**: Never use Python `eval()` or `exec()`.
4. **Follow Formatting**: Keep code clean, type-hinted, and well-documented.
