# Web Development with ENT

ENT is designed from the ground up for beginner-friendly website creation.
It eliminates the complexity of learning HTML, CSS syntax, and server configurations simultaneously.

---

## 1. Quick Example

```ent
[
    page(title = "My First ENT Website") [
        heading("Welcome to ENT!", level = 1)
        paragraph("This page was built with readable English syntax.")

        section() [
            heading("About Me", level = 2)
            paragraph("I am learning to program with ENT.")
            button("Contact Me", onclick = "alert('Thanks for visiting!')")
            link("Visit GitHub", url = "https://github.com/debabrata/ent-programming")
        ]
    ]
]
```

---

## 2. Web Primitives Reference

### `page(title = "...") [ ... ]`
Top-level container defining a web page. Generates an HTML5 document with metadata and modern responsive styling.

### `heading(text, level = 1)`
Renders an HTML heading (`<h1>` to `<h6>`).

### `paragraph(text)`
Renders a text paragraph (`<p>`).

### `button(text, onclick = "...")`
Renders an interactive button (`<button>`) with clean modern styling.

### `link(text, url = "...")`
Renders a hyperlink (`<a>`). Dangerous URI schemes like `javascript:` are automatically sanitized to prevent XSS.

### `image(src, alt = "...")`
Renders an image tag (`<img>`).

### `section() [ ... ]` / `container() [ ... ]`
Renders a styled section container (`<div class="ent-section">`).

### `style(css_rules)`
Appends custom CSS rules to the generated stylesheet.

---

## 3. Building for Production

Compile your ENT website using the CLI:

```bash
ent build website.ent -o my_site/
```

This generates:
- `my_site/index.html`
- `my_site/style.css`

Deploy these static files to any web host (GitHub Pages, Vercel, Netlify, Cloudflare Pages, S3).
