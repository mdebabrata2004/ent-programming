# ENT Studio

**ENT Studio** is the official web-based IDE for the ENT programming language.
It uses Monaco Editor, React, TypeScript, and Vite, and communicates directly with the shared ENT compiler and runtime engine.

---

## Features

- **Monaco Code Editor**: Professional editing experience with line numbers, code folding, bracket pair matching, and indentation.
- **ENT Syntax Highlighting**: Custom Monarch tokenizer highlighting ENT keywords, numbers, strings, comments, and built-ins.
- **IntelliSense & Autocompletion**: Built-in keyword and snippet completions (`remember`, `say`, `if`, `repeat`, `page`, etc.).
- **Live Execution & Output**: Run code directly against the genuine Python ENT interpreter backend.
- **Live Web Preview**: Instant sandboxed preview iframe for static websites written in ENT.
- **Structured Error Diagnostics**: Visual red underlines in the editor and a dedicated Diagnostics panel showing source line pointer and beginner tips.
- **File Management**: Open, create, import, export, and reset sample ENT files.
- **Theme Support**: Seamless dark and light mode toggle.

---

## Quick Start

### 1. Start the ENT Execution Backend

From the repository root:

```bash
python -m ent.web.server
```

The API service starts at `http://127.0.0.1:8000`.

### 2. Start the Frontend IDE

From the `ide/` directory:

```bash
cd ide
npm install
npm run dev
```

Open `http://localhost:3000` in your web browser.

---

## Production Build

To build the static production bundle:

```bash
cd ide
npm run build
```

The compiled assets will be written to `ide/dist/`.
