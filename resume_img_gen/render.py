"""Render a resume HTML from a named template + JSON data.

Usage:
  python -m resume_img_gen render --template <name> [--data data.json] [--out file]
  python -m resume_img_gen render --list [--templates-dir DIR]

Mini-template syntax (mustache-like; **data is trusted, so {{...}} is NOT
HTML-escaped** — escape untrusted input yourself before rendering):

  {{key}}                 variable (dotted paths ok: {{project.start_date}})
  {{{key}}}               same as {{key}} (kept for compatibility)
  {{#key}}...{{/key}}     section:
                            list  -> loop, item merged into context
                            dict  -> render once with the dict merged in
                            truthy scalar -> render once
                            falsy/missing -> skip
                          inside a loop: {{.}} is the raw item,
                          {{@index}} is the 0-based index
  {{^key}}...{{/key}}     inverted section: render only when key is falsy/missing

Sections may nest.  A section over a list of dicts merges each dict into the
outer context, so outer keys stay addressable inside the loop.
"""
from __future__ import annotations

import json
from pathlib import Path

# Bundled templates live next to this module.
PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_TEMPLATES = PACKAGE_DIR / "templates"

TOKEN_START = "{{"


def _lookup(context, path):
    cur = context
    for part in path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        elif isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except (ValueError, IndexError):
                return None
        else:
            return None
        if cur is None:
            return None
    return cur


def _child(context, key, item, index):
    """Build the context inside a section body."""
    ctx = dict(context)
    if isinstance(item, dict):
        ctx.update(item)
    ctx["."] = item
    ctx["@index"] = index
    return ctx


def _find_close(text, pos, key):
    """Return (body_end, after_close) for the matching {{/key}}, allowing nesting."""
    depth = 1
    i = pos
    open_t, close_t = "{{#", "{{/" + key + "}}"
    while True:
        o = text.find(open_t, i)
        c = text.find(close_t, i)
        if c < 0:
            return None
        if 0 <= o < c:
            depth += 1
            i = o + len(open_t)
        else:
            depth -= 1
            i = c + len(close_t)
            if depth == 0:
                return (c, i)


def render(text, context):
    """Expand the mini-template ``text`` against ``context``."""
    out = []
    i = 0
    n = len(text)
    while i < n:
        start = text.find(TOKEN_START, i)
        if start < 0:
            out.append(text[i:])
            break
        out.append(text[i:start])
        end = text.find("}}", start)
        if end < 0:
            out.append(text[start:])
            break
        end += 2
        token = text[start + 2:end - 2].strip()
        if token.startswith("#"):
            key = token[1:].strip()
            close = _find_close(text, end, key)
            if close is None:
                raise ValueError(f"Unclosed section {{{{{token}}}}}")
            body = text[end:close[0]]
            val = _lookup(context, key)
            if isinstance(val, list):
                for idx, item in enumerate(val):
                    out.append(render(body, _child(context, key, item, idx)))
            elif val:
                out.append(render(body, _child(context, key, val, 0)))
            i = close[1]
        elif token.startswith("^"):
            key = token[1:].strip()
            close = _find_close(text, end, key)
            if close is None:
                raise ValueError(f"Unclosed section {{{{{token}}}}}")
            body = text[end:close[0]]
            val = _lookup(context, key)
            if not val:
                out.append(render(body, context))
            i = close[1]
        else:
            val = _lookup(context, token)
            if isinstance(val, (list, dict)):
                val = json.dumps(val, ensure_ascii=False)
            out.append("" if val is None else str(val))
            i = end
    return "".join(out)


def list_templates(templates_dir=DEFAULT_TEMPLATES):
    return sorted(p.stem for p in Path(templates_dir).glob("*.html"))


def render_file(template, data_path, templates_dir=DEFAULT_TEMPLATES):
    """Return (html, template_path). Raises FileNotFoundError / json errors."""
    tpl_path = Path(templates_dir) / f"{template}.html"
    if not tpl_path.exists():
        raise FileNotFoundError(f"template not found: {tpl_path}")
    data = json.loads(Path(data_path).read_text(encoding="utf-8"))
    return render(tpl_path.read_text(encoding="utf-8"), data), tpl_path
