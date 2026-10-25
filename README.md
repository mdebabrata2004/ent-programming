# ENT Programming

<p align="center">
  <strong>A beginner-friendly, English-readable programming language for website development.</strong>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#language-syntax">Language Syntax</a> •
  <a href="#cli-usage">CLI Usage</a> •
  <a href="#ent-studio-ide">ENT Studio IDE</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#license">License</a>
</p>

---

## ⚡ What is ENT?

**ENT** is an authentic, independent programming language designed to make coding accessible, intuitive, and readable. Unlike conventional languages laden with intimidating syntax, curly braces, and tedious boilerplate, ENT uses simple English-inspired syntax, built-in standard libraries that work out-of-the-box, and a native compiler for creating static websites.

### Core Highlights

- 📖 **English-Readable**: Code reads like natural sentences: `say("Hello!")`, `remember(age = 20)`.
- 🛡️ **Genuine Compiler & Interpreter**: Real hand-written Lexer, recursive-descent Pratt Parser, AST, and Sandboxed Interpreter. Zero Python `eval()` or `exec()`.
- 🚫 **No Curly Braces**: All program blocks use square brackets `[ ... ]`. Curly braces `{ }` are strictly forbidden.
- 🌐 **Static Website Engine**: Native built-in web primitives (`page`, `heading`, `paragraph`, `button`, `link`, `image`, `section`) compiling directly to clean HTML5 and CSS.
- 💻 **ENT Studio IDE**: Web-based development environment with Monaco Editor, syntax highlighting, autocompletion, live execution output, and sandboxed web previews.
- 🔒 **Defense-in-Depth Security**: Execution step quotas, recursion depth limits, XSS escaping, and zero host-system pollution.

---

## 📊 Feature Status

| Feature | Status | Notes |
|---|---|---|
| **Lexer & Pratt Parser** | ✅ Stable | Line/col tracking, bracket pairing, comments, escape sequences. |
| **Interpreter & Runtime** | ✅ Stable | Tree-walking evaluator with step counters and lexical scoping. |
| **Variables & Arithmetic** | ✅ Stable | `remember(x = 10)`, reassignment, string concatenation, math operators. |
| **Conditionals & Loops** | ✅ Stable | `if / otherwise`, `repeat`, `while`, `for-in`. |
| **User Functions** | ✅ Stable | `function name(args) [ ... ]` and `give` / `return`. |
| **Standard Built-ins** | ✅ Stable | Math, string, and collection operations without explicit imports. |
| **CLI Tool (`ent`)** | ✅ Stable | `ent <file>`, `ent check`, `ent repl`, `ent build`, `ent --version`. |
| **Static Web Builder** | ✅ Stable | HTML5 & CSS generation with automatic XSS sanitization. |
| **ENT Studio IDE** | ✅ Stable | Monaco Editor, React, TypeScript, live iframe preview, error diagnostics. |
| **Test Suite** | ✅ 57/57 Passing | Unit, integration, CLI, API, and security sandboxing tests. |

---

## 📸 Screenshots & IDE Preview

> [!NOTE]
> Below is a preview walkthrough of **ENT Studio** running locally:

```
+---------------------------------------------------------------------------------------+
|  ⚡ ENT Studio v0.1.0     [▶ Run (Ctrl+Enter)]   [✔ Check]   [🌐 Preview Web]    (🌙/☀) |
+-----------------------+---------------------------------------------------------------+
| EXPLORER & EXAMPLES   | 1 [                                                           |
| --------------------- | 2     page(title = "Welcome to ENT") [                        |
| • hello.ent           | 3         heading("Build Websites with Simple English")       |
| • variables.ent       | 4         paragraph("ENT is readable and intuitive.")         |
| • math.ent            | 5         button("Get Started", onclick = "alert('Hi!')")    |
| • conditions.ent      | 6     ]                                                       |
| • loops.ent           | 7 ]                                                           |
| • functions.ent       +---------------------------------------------------------------+
| • website.ent         | [Terminal Console]   [🌐 Web Preview]   [⚠ Diagnostics]       |
|                       | ------------------------------------------------------------- |
|                       | > Success: Built website at 'dist/index.html' (42 steps)      |
+-----------------------+---------------------------------------------------------------+
```

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install the project in editable mode:

```bash
git clone https://github.com/debabrata/ent-programming.git
cd ent-programming

# Install ENT CLI and dependencies
pip install -e ".[dev]"
```

Verify your installation:

```bash
ent --version
```

### 2. Run Your First ENT Program

Create `hello.ent`:

```ent
[
    say("Hello, World!")
]
```

Run it via the CLI:

```bash
ent hello.ent
```

**Output:**
```
Hello, World!
```

---

## 📝 Language Syntax

### Hello World
```ent
[
    say("Hello, World!")
]
```

### Variables & Strings
```ent
[
    remember(name = "ENT")
    remember(version = "0.1.0")

    say("Welcome to " + name)
    say("Version: " + version)
]
```

### Arithmetic & Expressions
```ent
[
    say(2 + 2 - 9 + 3) # Evaluates to -2
]
```

### Conditions (`if / otherwise`)
```ent
[
    remember(age = 20)

    if (age >= 18) [
        say("Adult")
    ] otherwise [
        say("Minor")
    ]
]
```

### Bounded Loops
```ent
[
    # Counted repeat loop
    repeat (3 as i) [
        say("Repeat count: " + i)
    ]

    # While loop with condition
    remember(c = 0)
    while (c < 3) [
        say("While count: " + c)
        c = c + 1
    ]
]
```

### User Functions
```ent
[
    function add(a, b) [
        give a + b
    ]

    remember(result = add(10, 25))
    say("10 + 25 = " + result) # Outputs: 10 + 25 = 35
]
```

### Static Website Definition
```ent
[
    page(title = "My ENT Website") [
        heading("Welcome to ENT", level = 1)
        paragraph("This website was created using the ENT programming language.")

        section() [
            heading("Getting Started", level = 2)
            paragraph("Write simple English code and compile to production HTML & CSS.")
            button("Click Me", onclick = "alert('Welcome!')")
            link("Read Documentation", url = "https://github.com/debabrata/ent-programming")
        ]
    ]
]
```

---

## 🛠️ CLI Usage

```bash
# Run a file
ent script.ent

# Validate syntax without execution
ent check script.ent

# Launch interactive REPL
ent repl

# Compile static website
ent build website.ent -o my_site/

# Show version & help
ent --version
ent --help
```

---

## 🎨 ENT Studio Web IDE

ENT Studio is the official web-based IDE for ENT, featuring Monaco Editor, live sandboxed preview iframes, and diagnostic markers.

### Starting ENT Studio

1. **Start the Execution Engine:**
   ```bash
   python -m ent.web.server
   ```
2. Open `http://127.0.0.1:8000` in your web browser.

*(For frontend development with hot-reload, run `npm run dev` in `ide/` and visit `http://localhost:3000`.)*

---

## 🏗️ Architecture

```
       +---------------------------------------------+
       |             ENT Source Code (.ent)          |
       +---------------------------------------------+
                              │
                              ▼
       +---------------------------------------------+
       |             Lexer (lexer.py)                |
       |  - Tokenization, line & column tracking     |
       |  - Rejects '{' and '}', validates '[ ]'     |
       +---------------------------------------------+
                              │
                              ▼
       +---------------------------------------------+
       |             Parser (parser.py)              |
       |  - Recursive-descent Pratt parser           |
       |  - Structured AST construction              |
       |  - Friendly diagnostic error reporting      |
       +---------------------------------------------+
                              │
                              ▼
       +---------------------------------------------+
       |          AST (Abstract Syntax Tree)         |
       +---------------------------------------------+
                       /              \
                      ▼                ▼
       +-----------------------+  +-----------------------+
       | Interpreter (runtime) |  | Web Builder (web/)    |
       | - Scopes & memory     |  | - HTML5 & CSS gen     |
       | - Step quota limits   |  | - XSS Sanitization    |
       | - Allowlist built-ins |  | - Standalone bundle   |
       +-----------------------+  +-----------------------+
                   │                          │
                   ▼                          ▼
       +-----------------------+  +-----------------------+
       |       CLI (ent)       |  |    ENT Studio (IDE)   |
       +-----------------------+  +-----------------------+
```

---

## 🧪 Running Automated Tests

Run the full automated test suite (57 passing tests):

```bash
pytest
```

Run test suites individually:

```bash
# Unit tests: Lexer, Parser, Interpreter, Web Builder, Errors
pytest tests/unit/

# Integration tests: CLI and Backend API
pytest tests/integration/

# Security tests: Sandbox boundaries, step limits, recursion limits
pytest tests/security/
```

---

## 📚 Documentation Index

Detailed guides are located in the [`docs/`](docs/) directory:

- [Language Specification](docs/LANGUAGE_SPEC.md)
- [Formal Grammar (EBNF)](docs/GRAMMAR.md)
- [CLI Reference Guide](docs/CLI.md)
- [ENT Studio IDE Guide](docs/IDE.md)
- [Web Development Guide](docs/WEB_DEVELOPMENT.md)
- [Architecture & Internals](docs/ARCHITECTURE.md)
- [Security Model](docs/SECURITY.md)
- [Project Roadmap](docs/ROADMAP.md)
- [Frequently Asked Questions (FAQ)](docs/FAQ.md)

---

## 🤝 Contributing

Contributions are warmly welcomed! Please read our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CONTRIBUTING.md#code-of-conduct) before submitting a pull request.

---

## 📄 License

ENT Programming is released under the [MIT License](LICENSE).
