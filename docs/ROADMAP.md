# ENT Language Roadmap

This document outlines the evolutionary milestones for ENT Programming.

---

## Phase 1 — Core Language & CLI (Completed in v0.1.0)
- [x] Hand-written Lexer with line/col tracking and bracket pair matching.
- [x] Deterministic Pratt Parser rejecting curly braces `{ }`.
- [x] Safe tree-walking interpreter with execution quotas.
- [x] Variables (`remember`), arithmetic, logic, and conditions (`if / otherwise`).
- [x] Bounded loops (`repeat`, `while`, `for`) and functions (`function`, `give`).
- [x] Rich standard library for math, strings, and lists.
- [x] Full-featured `ent` CLI (`run`, `check`, `repl`, `build`, `version`).
- [x] ENT Studio Web IDE with Monaco Editor and live preview.
- [x] Automated test suites (57 tests passing).

---

## Phase 2 — Web Enhancements (Planned)
- [ ] CSS layout abstractions (Grid and Flexbox primitives).
- [ ] Multi-page static routing (`page("About", path = "/about")`).
- [ ] Reusable UI components (`component Card(title, body) [ ... ]`).
- [ ] Asset pipeline (automatic image optimization and bundling).
- [ ] Form handling and client-side validation built-ins.

---

## Phase 3 — Tooling & Desktop IDE (Planned)
- [ ] Language Server Protocol (LSP) implementation for VS Code and Neovim.
- [ ] Standalone desktop package using Tauri / Electron.
- [ ] Native WebAssembly (Wasm) interpreter build for client-side evaluation without a local Python server.
- [ ] Interactive step-through debugger with breakpoints and variable inspection.
- [ ] Package manager for ENT community modules.

---

## Phase 4 — Experimental Grammar Features (Future Evaluation)
- [ ] Controlled natural-language query syntax (`what is x?`) mapped onto deterministic AST queries.
- [ ] Type annotations for optional static typing checks.
