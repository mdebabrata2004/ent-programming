# Frequently Asked Questions (FAQ)

### 1. What is ENT Programming?
ENT is a beginner-friendly, English-readable programming language built primarily for website development. It allows beginners to write readable code without the intimidation of curly braces, complex symbols, or confusing imports.

---

### 2. Why are curly braces `{ }` forbidden?
Curly braces are frequently a source of syntax errors and frustration for beginners. ENT establishes a clean rule: square brackets `[ ... ]` are used for program boundaries and all code blocks, while parentheses `( ... )` are used for function arguments and conditions.

---

### 3. Is ENT just a Python wrapper using `eval()`?
No! ENT is an authentic, independent programming language implementation. It includes its own tokenizer (Lexer), recursive-descent Pratt parser, Abstract Syntax Tree (AST), runtime scope system, and tree-walking interpreter. It **never** uses `eval()` or `exec()`.

---

### 4. Can I build real websites with ENT?
Yes. ENT includes a static website compilation engine. By writing `page(...) [ ... ]` definitions, ENT compiles your code into clean, semantic HTML5 and modern responsive CSS that can be hosted on GitHub Pages, Vercel, Netlify, or any static host.

---

### 5. How do the CLI and Web IDE interact?
The CLI and ENT Studio share the exact same language engine. When you click **Run** in ENT Studio, your code is sent to the local FastAPI execution service, which executes it using the exact same parser and interpreter as the `ent` command-line tool.

---

### 6. Why is `what is my age?` rejected?
ENT prioritizes unambiguous, deterministic grammar over unrestricted natural language translation. Natural language sentences often lead to subtle ambiguity and unpredictability. ENT provides clear English keywords (`say(age)`, `if (age >= 18) [ ... ]`), and natural language queries are planned as an experimental future feature with strict deterministic bounds.

---

### 7. How do I report bugs or contribute?
Please review our [CONTRIBUTING.md](../CONTRIBUTING.md) guide and submit issues or pull requests on GitHub.
