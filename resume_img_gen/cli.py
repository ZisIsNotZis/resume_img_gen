"""Command-line entry point for resume_img_gen.

  resume-img-gen render --template clean-teal-ribbon --data examples/example.json --out out.html
  resume-img-gen shot out.html --out out.png --width 1760
  resume-img-gen shot out.html --out out.pdf
  resume-img-gen pdf examples/example.md --out out.pdf
  resume-img-gen render --list
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import render as render_mod
from . import pdf as pdf_mod
from . import shot as shot_mod


def _cmd_render(a) -> int:
    if a.list:
        for name in render_mod.list_templates(a.templates_dir):
            print(name)
        return 0
    if not a.template:
        print("error: --template is required (or use --list)", file=sys.stderr)
        return 2
    if not a.data:
        print("error: --data is required", file=sys.stderr)
        return 2
    try:
        html, tpl = render_mod.render_file(a.template, a.data, a.templates_dir)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except Exception as e:  # noqa: BLE001 - surface data errors plainly
        print(f"error: cannot load data {a.data}: {e}", file=sys.stderr)
        return 1
    if a.out:
        Path(a.out).write_text(html, encoding="utf-8")
        print(f"wrote {a.out}  (template: {tpl.name})")
    else:
        sys.stdout.write(html)
    return 0


def _cmd_shot(a) -> int:
    try:
        if a.out.lower().endswith(".pdf"):
            shot_mod.shot_pdf(a.html, a.out, chrome=a.chrome)
        else:
            shot_mod.shot_png(a.html, a.out, width=a.width, height=a.height,
                              chrome=a.chrome, scale=a.scale)
    except Exception as e:  # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"wrote {a.out}")
    return 0


def _cmd_pdf(a) -> int:
    try:
        md = Path(a.markdown).read_text(encoding="utf-8")
        pdf_mod.markdown_to_pdf(md, Path(a.out), css_path=a.css, title=a.title,
                                until=a.until)
    except Exception as e:  # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"wrote {a.out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="resume-img-gen",
                                description="Structured resume data -> HTML / PDF / PNG.")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("render", help="JSON + template -> HTML")
    r.add_argument("--template", "-t")
    r.add_argument("--data", "-d")
    r.add_argument("--out", "-o")
    r.add_argument("--templates-dir", default=str(render_mod.DEFAULT_TEMPLATES))
    r.add_argument("--list", action="store_true", help="list bundled templates")
    r.set_defaults(func=_cmd_render)

    s = sub.add_parser("shot", help="HTML -> PNG or PDF (headless Chromium)")
    s.add_argument("html")
    s.add_argument("--out", "-o", required=True)
    s.add_argument("--width", type=int, default=1760)
    s.add_argument("--height", type=int, default=1200, help="canvas height (<=0 -> 1200)")
    s.add_argument("--scale", type=float, default=1.0, help="device scale factor")
    s.add_argument("--chrome", default=None, help="explicit browser binary")
    s.set_defaults(func=_cmd_shot)

    d = sub.add_parser("pdf", help="Markdown -> PDF (pandoc + WeasyPrint)")
    d.add_argument("markdown")
    d.add_argument("--out", "-o", required=True)
    d.add_argument("--css", default=str(pdf_mod.DEFAULT_CSS))
    d.add_argument("--title", default="Resume")
    d.add_argument("--until", default=None,
                   help="drop content from this literal line onward (short edition)")
    d.set_defaults(func=_cmd_pdf)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
