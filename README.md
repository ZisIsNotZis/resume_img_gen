**English** | [简体中文](README.zh-CN.md)

![resume_img_gen](assets/logo.svg)

Data in, designed resume out — HTML, PNG, and print-ready PDF.

**One JSON file of resume text plus any of eight hand-built HTML design
canvases produces a matching HTML page, a pixel-cropped PNG, or an A4 PDF, with
no rendering service, no browser-automation library, and no Python
dependencies.** Layout and content stay independent: the template owns every
pixel of the design, the data file owns every word, so one person's text can
drive any number of looks and one look can be reused by any number of people.

## Quick start

```sh
git clone https://github.com/ZisIsNotZis/resume_img_gen
cd resume_img_gen
pipx install .            # or: pip install .   (or run in place: python3 -m resume_img_gen)
```

Then, from the repository root:

```sh
resume-img-gen render --list                       # the 8 bundled designs
resume-img-gen render -t clean-teal-ribbon \
    -d examples/example.json -o resume.html       # JSON + template -> HTML
resume-img-gen shot resume.html -o resume.png \
    --width 1760 --height 2400                     # HTML -> PNG
```

No third-party Python package is needed for `render` or for installing the
package. The other two stages use tools you may already have:

- `shot` (HTML → PNG/PDF) needs a headless-capable Chrome, Chromium, Edge, or
  Playwright's `chrome-headless-shell`. It searches `PATH` and the usual
  Playwright/Puppeteer cache locations; pass `--chrome PATH` if yours is
  elsewhere.
- `pdf` (Markdown → PDF) needs `pandoc`, plus either `weasyprint` or `uv` on
  `PATH` (WeasyPrint is run through `uv tool run` when it is not installed).

`examples/example.json` and `examples/example.md` are **fictional sample data**
(fake person, employers, contacts) that only demonstrates the pipeline. Replace
them with your own.

## What it can do now

- **`render`** — a dependency-free mustache-like engine: `{{key}}` with dotted
  paths (`{{jobs.0.org}}`), `{{#key}}…{{/key}}` sections over lists/dicts/truthy
  scalars, `{{^key}}…{{/key}}` inverted sections, nesting, `{{.}}` and
  `{{@index}}` inside loops.
- **Eight bundled design canvases** — `classic-sidebar`, `clean-teal-columns`,
  `clean-teal-ribbon`, `dark-hud-circuit`, `dark-hud-dossier`, `dark-hud-radar`,
  `paper-orange-timeline`, `warm-paper-timeline`. Fixed-size canvases that
  scale to fit the window width, scroll vertically, and print as one A4 page.
- **Your own templates** — drop `*.html` into a directory and pass
  `--templates-dir`; `--list` then lists yours too.
- **`shot`** — viewport screenshot at exactly `--width`/`--height` (plus
  `--scale` for HiDPI), or `--out file.pdf` for a browser print with no
  header/footer.
- **`pdf`** — Markdown through pandoc and a bundled CJK-safe A4 stylesheet
  (page numbers in the footer), with `--until "# Appendix"` to build a short
  edition from the same source.
- **CJK-first defaults** — the bundled designs and the PDF stylesheet are built
  around Chinese resume typography; English works the same way.
- **A written method** for cloning a reference image into a reusable template:
  [`docs/PLAYBOOK.md`](docs/PLAYBOOK.md).

## How the pieces fit

Three stages that can be used independently, plus one stylesheet. Nothing calls
across a stage boundary except through a file on disk, so you can stop after any
of them.

```
resume_img_gen/
  resume_img_gen/
    cli.py                  # argparse: render | shot | pdf
    render.py               # template engine + JSON loading, no dependencies
    shot.py                 # find a headless browser, exec it for PNG/PDF
    pdf.py                  # pandoc -> HTML -> WeasyPrint
    resume.css              # A4 / CJK WeasyPrint stylesheet
    templates/*.html        # 8 design canvases, every string a {{token}}
  examples/                 # fictional sample data (JSON and Markdown)
  docs/PLAYBOOK.md          # reference PNG -> HTML -> compare loop
  docs/project-status.md    # scope, boundaries, and why the design is closed
  tests/test_render.py      # smoke tests for the engine and all templates
```

`render` reads the template and the JSON, expands the tokens, and writes HTML.
`shot` resolves the HTML to a `file://` URL and hands it to a browser binary.
`pdf` reads Markdown, converts it with pandoc, wraps it in the stylesheet, and
runs WeasyPrint. The only shared assumption is that a template is a
self-contained page.

**One rule keeps templates reusable:** a template may contain design, never
content. If a name, phone number, or employer appears as a literal string in the
HTML, the design is not reusable — put a `{{token}}` there instead. `tests/`
enforces this for the bundled set.

## Template syntax

```
{{key}}                 variable (dotted paths: {{job.org}})
{{#key}} ... {{/key}}   section — list → loop ({{.}} item, {{@index}} index),
                        dict → render once merged, truthy scalar → once
{{^key}} ... {{/key}}   inverted section — render when falsy/missing
```

Sections nest. **Data is trusted, so `{{...}}` is not HTML-escaped** — escape
untrusted values before rendering.

## Development

```sh
python3 -m pytest tests/           # or, without pytest installed:
python3 tests/test_render.py       # prints ok per test
```

There is no linter or formatter configuration in this repository; keep the
existing style (standard library only, `from __future__ import annotations`).
See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the review bar and the template
acceptance test.

## Contributing

Bug reports and new design canvases are welcome — see
[`CONTRIBUTING.md`](CONTRIBUTING.md). The one hard requirement for a new
template is in [`docs/PLAYBOOK.md`](docs/PLAYBOOK.md#acceptance-test-for-a-new-reusable-template):
render it against different data, and the output must differ only where the
content differs.

## Roadmap

**Implemented**

- Template engine, JSON → HTML rendering, and the `render`/`shot`/`pdf`
  subcommands, with `--list`, `--templates-dir`, `--chrome`, `--scale`, and
  `--until`.
- Eight reusable design canvases across light, paper, and dark-HUD families.
- A4 CJK stylesheet for the Markdown → PDF path.
- Smoke tests covering the engine and every bundled template.
- The reference-image cloning playbook.

**Planned**

- Nothing. This repository is a **closed milestone**: the three-stage pipeline
  is complete and no further development is planned unless the project's inputs
  or goals change (recorded in [`docs/project-status.md`](docs/project-status.md)).

If it is ever reopened, the natural direction is more design canvases and more
export targets behind the same `data + template` interface, since the stages are
already isolated behind files. That is a direction, not a promise.

## License

LGPL-3.0-or-later — see [`LICENSE`](LICENSE). `COPYING` holds the GNU GPL-3.0
text that LGPL-3.0 builds on. Copyright (C) ZisIsNotZis.
