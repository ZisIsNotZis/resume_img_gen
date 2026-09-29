"""Markdown -> PDF through pandoc + WeasyPrint, with a bundled A4 stylesheet.

Generalised from the private resume pipeline so it works for any Markdown file
(all CJK-friendly defaults kept).  WeasyPrint is run through ``uv`` if it is not
installed globally, so no system install is needed.

Split pages / two outputs: pass ``--until`` a marker line to drop everything
from that line onwards (e.g. ``--until "# Appendix"``) to build a short edition
from the same source.  A convenience ``--short-marker`` does this for you.
"""
from __future__ import annotations

import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_CSS = PACKAGE_DIR / "resume.css"


def pandoc_html(md_text: str) -> str:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("pandoc not found (install it, or use the `shot` command on HTML)")
    return subprocess.run(
        [pandoc, "-f", "markdown-subscript-superscript", "-t", "html5", "--wrap=none"],
        input=md_text, check=True, capture_output=True, text=True,
    ).stdout


def decorate(body: str) -> str:
    """Give appendix h1s a class so the CSS can page-break before each of them."""
    return re.sub(r'<h1([^>]*)>(附录[^<]*)</h1>',
                  r'<h1 class="appendix-title"\1>\2</h1>', body)


def wrap(body: str, css: str, title: str) -> str:
    return ("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>"
            f"<title>{html.escape(title)}</title><style>{css}</style></head>"
            f"<body>{body}</body></html>")


def weasyprint(html_path: Path, pdf_path: Path) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    if shutil.which("weasyprint"):
        cmd = ["weasyprint", str(html_path), str(pdf_path)]
    elif shutil.which("uv"):
        cmd = ["uv", "tool", "run", "--from", "weasyprint",
               "weasyprint", str(html_path), str(pdf_path)]
    else:
        raise RuntimeError("neither weasyprint nor uv found")
    subprocess.run(cmd, check=True)


def markdown_to_pdf(md_text: str, out: Path, css_path=DEFAULT_CSS,
                    title="Resume", until: str | None = None) -> Path:
    if until and until in md_text:
        md_text = md_text[: md_text.index(until)].rstrip() + "\n"
    css = Path(css_path).read_text(encoding="utf-8")
    doc = wrap(decorate(pandoc_html(md_text)), css, title)
    tmp = Path("/tmp/resume_img_gen_render.html")
    tmp.write_text(doc, encoding="utf-8")
    weasyprint(tmp, out)
    return out
