# Security Model & Guarantees

ENT is designed with a defense-in-depth security model to treat all ENT source code as untrusted user input.

---

## 1. Core Security Guarantees

### 1.1 No Host Evaluation
ENT **never** uses Python's `eval()` or `exec()`.
Source code is parsed into a structured Abstract Syntax Tree (AST) using a deterministic hand-written parser and evaluated strictly within a managed lexical environment.

### 1.2 No Host Pollution
ENT programs cannot:
- Access Python's `__builtins__`, `__globals__`, or `__class__`.
- Import arbitrary Python modules (`os`, `sys`, `subprocess`, `importlib`).
- Execute arbitrary system shell commands.
- Read or write arbitrary files on the host filesystem.
- Open network sockets or perform unauthorized HTTP requests.

### 1.3 Execution Sandboxing & Resource Quotas
To prevent accidental or malicious Denial of Service (DoS):
- **Step Limits**: By default, an execution quota of `100,000` AST operations is enforced per program execution. Exceeding this limit terminates execution with an `EntLimitExceededError`.
- **Recursion Limits**: Function call depth is bounded (default `256` frames) to prevent stack overflows.
- **Source Size Limits**: The API service rejects source payloads exceeding 1 MB.

### 1.4 Web Builder & XSS Protection
- All text rendered into static HTML elements is automatically escaped using `html.escape()`.
- URL attributes (`href`, `src`) reject dangerous schemes (`javascript:`, `data:`, `vbscript:`).
- Web preview iframes in ENT Studio are sandboxed (`sandbox="allow-scripts"`).

### 1.5 Localhost Binding
The FastAPI execution server binds strictly to `127.0.0.1` by default to avoid exposing code execution endpoints to the public network.
