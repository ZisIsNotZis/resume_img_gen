# resume_img_gen

Generate resume **images** — HTML, PNG, and PDF — from structured data and
reusable HTML templates.

Three independent stages, one small dependency-light Python package:

| stage | input | output | backend |
|-------|-------|--------|---------|
| `render` | JSON data + HTML template | HTML | pure Python (no deps) |
| `shot`   | HTML | PNG or PDF | headless Chromium / Chrome / Edge |
| `pdf`    | Markdown | PDF | pandoc + WeasyPrint (via `uv` if missing) |

Text lives in your data file; templates are pure design canvases whose every
content string is a `{{token}}`. That keeps layout and content independent, so
one data file can drive many looks.

## Install

No required third-party Python packages.

```sh
git clone https://github.com/zisisnotzis/resume_img_gen
cd resume_img_gen
pipx install .        # or: pip install .
# or run in place:  python3 -m resume_img_gen <command> ...
```

External tools, only for the stage that needs them:

- `shot` needs a headless-capable browser (Chrome, Chromium, Edge, or Playwright's
  `chrome-headless-shell`). It is auto-detected.
- `pdf` needs `pandoc`, and either `weasyprint` or `uv` on `PATH`.

## Quickstart

```sh
# 1. list the bundled templates
python3 -m resume_img_gen render --list

# 2. JSON + template -> HTML
python3 -m resume_img_gen render \
    --template clean-teal-ribbon \
    --data examples/example.json \
    --out /tmp/resume.html

# 3. HTML -> PNG (viewport crop of the design canvas)
python3 -m resume_img_gen shot /tmp/resume.html --out /tmp/resume.png \
    --width 1760 --height 2400

# 4. ...or straight to PDF
python3 -m resume_img_gen shot /tmp/resume.html --out /tmp/resume.pdf

# Markdown -> PDF (optional front matter, appendix page breaks built in)
python3 -m resume_img_gen pdf examples/example.md --out /tmp/resume_md.pdf
```

`examples/example.json` and `examples/example.md` are **fictional sample data**
(fake person, fake employers, fake contacts) used only to demonstrate the
pipeline. Replace them with your own.

## Template syntax

A mustache-like mini-language, implemented in ~120 lines with no dependencies:

```
{{key}}                 variable (dotted paths: {{job.org}})
{{#key}} ... {{/key}}   section — list → loop ({{.}} item, {{@index}} index),
                        dict → render once merged, truthy scalar → once
{{^key}} ... {{/key}}   inverted section — render when falsy/missing
```

Sections nest. **Data is trusted, so `{{...}}` is not HTML-escaped** — escape
untrusted values before rendering.

Put your own templates in a directory and point `--templates-dir` at it. A
template is accepted as a reusable design when, after rendering with different
data, the output differs only where content differs and the template contains no
hard-coded personal strings (grep it).

Bundled designs: `classic-sidebar`, `clean-teal-columns`, `clean-teal-ribbon`,
`dark-hud-circuit`, `dark-hud-dossier`, `dark-hud-radar`,
`paper-orange-timeline`, `warm-paper-timeline`.

## Recreating a design from a reference image

See [`docs/PLAYBOOK.md`](docs/PLAYBOOK.md) for the proven **reference PNG → HTML
→ render → compare** loop, including the gotchas that cost hours to find once:
scroll-killing `overflow: hidden`, unequal `1fr` grid columns, CJK fonts, and
"match line counts, not colors."

## Layout

```
resume_img_gen/
  resume_img_gen/
    cli.py        # `render` / `shot` / `pdf` subcommands
    render.py     # dependency-free template engine
    shot.py       # headless-browser PNG/PDF
    pdf.py        # pandoc + WeasyPrint
    resume.css    # A4 WeasyPrint stylesheet (CJK-friendly)
    templates/    # 8 bundled design canvases
  examples/       # fictional sample data
  docs/PLAYBOOK.md
```

## License

LGPL-3.0-or-later — see [`LICENSE`](LICENSE).
