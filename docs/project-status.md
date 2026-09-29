# resume_img_gen project status

## Classification

Closed milestone: a small, dependency-light Python package that generates resume
images — HTML, PNG, and PDF — from structured data and reusable HTML templates.

## Status

Closed as a milestone (2026-09-29). The three-stage pipeline (render/shot/pdf)
is complete; no further development is planned unless the project's inputs or
goals change.

## Evidence

- CLI: `resume_img_gen render | shot | pdf`.
- Dependency-free template engine and eight bundled design canvases under
  `resume_img_gen/templates/`.
- Tests under `tests/`; fictional sample data under `examples/`.
- Reference-to-design workflow: [`../docs/PLAYBOOK.md`](../docs/PLAYBOOK.md).

## Boundaries

Text lives in the data file; templates are content-free design canvases. `shot`
needs a headless browser and `pdf` needs pandoc plus WeasyPrint or `uv`. Data is
trusted and `{{...}}` is not HTML-escaped.
