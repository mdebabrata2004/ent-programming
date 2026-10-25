# ENT Studio Web IDE Guide

**ENT Studio** is the dedicated development environment for the ENT programming language.

---

## 1. Architecture

ENT Studio uses a decoupled, secure client-server model:
- **Frontend**: React + TypeScript + Monaco Editor + Vite.
- **Backend Service**: FastAPI local execution service (`ent.web.server`).
- **Engine**: Shares the identical AST parser and tree-walking interpreter as the `ent` CLI.

---

## 2. Running ENT Studio Locally

### Option 1: Single Command (Recommended)

When `ide/dist` has been built (`npm run build` in `ide/`), the FastAPI backend serves both the API and the web UI directly:

```bash
python -m ent.web.server
```

Open `http://127.0.0.1:8000` in your web browser.

### Option 2: Full Development Mode (Hot Reloading)

1. Start the API service:
   ```bash
   python -m ent.web.server
   ```
2. In a separate terminal, start Vite:
   ```bash
   cd ide
   npm run dev
   ```
3. Open `http://localhost:3000`.

---

## 3. Key IDE Features

- **Monaco Editor Integration**: Custom Monarch grammar for ENT, bracket matching, and intelligent snippets.
- **Keyboard Shortcuts**:
  - `Ctrl + Enter` (or `Cmd + Enter`): Run current ENT program.
- **Execution Output Panel**: Live display of all output from `say(...)` calls.
- **Live Sandboxed Web Preview**: Instant preview of websites generated from `page(...) [ ... ]` definitions.
- **Diagnostics Panel**: Clear explanations of errors with source pointers and beginner tips.
- **File Management**: Load built-in examples, create new scripts, import `.ent` files from your computer, or download edited scripts.
- **Dark & Light Themes**: One-click toggle with accessible high-contrast color palettes.
