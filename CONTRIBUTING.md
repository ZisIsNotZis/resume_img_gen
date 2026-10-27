# Contributing

Small package, small process.

**Scope.** `resume_img_gen` has three independent stages — `render` (JSON +
template → HTML), `shot` (HTML → PNG/PDF via a headless browser), `pdf`
(Markdown → PDF via pandoc + WeasyPrint) — plus the bundled design canvases.
The package is a closed milestone: new design canvases, bug fixes, and
better documentation are in scope; a redesign of the stage boundaries or a
switch to a template-engine dependency is not — those need a discussion first
and a reason the dependency earns its weight.

**Before you open a PR**

```sh
python3 -m pytest tests/        # or: python3 tests/test_render.py
```

Both must pass. There is no linter or formatter config; match the existing style
and keep the standard library only for `render`/`shot`/`pdf` themselves.

**The one hard rule for a template** is the acceptance test in
[`docs/PLAYBOOK.md`](docs/PLAYBOOK.md#acceptance-test-for-a-new-reusable-template):
render your template against two different data files, and the outputs must
differ only where the content differs. No name, phone number, employer or URL
may appear as a literal string in a template — use a `{{token}}`. Say in the PR
which design it is modelled on and what the target medium is.

**PRs.** One change per PR, Conventional Commits subject
(`feat: add …`, `fix: …`, `docs: …`, `chore: …`), and a line on how you checked
it (which command, which template, what the output looked like). Never commit
rendered `*.png`/`*.pdf` output, caches, or real personal data — the sample data
in `examples/` is fictional on purpose.

**Issues.** Include the exact command, the Python version, the browser binary
and version for `shot`, and the pandoc/WeasyPrint versions for `pdf`, plus the
full traceback. A minimal data file that reproduces the problem is worth more
than a paragraph of description.

This project is licensed LGPL-3.0-or-later; contributions are accepted under the
same license.
