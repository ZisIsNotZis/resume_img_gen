"""Smoke tests: template engine + bundled templates. Run with `python3 -m pytest`
or plain `python3 tests/test_render.py`."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from resume_img_gen import render as R  # noqa: E402

DATA = json.loads((ROOT / "examples" / "example.json").read_text(encoding="utf-8"))


def test_variable_and_dotted_path():
    assert R.render("{{name}} / {{jobs.0.org}}", DATA) == \
        "示例人物 Example Person / 示例科技公司"


def test_list_section_and_index():
    out = R.render("{{#skills}}{{@index}}:{{name}} {{/skills}}", DATA)
    assert out.startswith("0:推理与系统")


def test_inverted_section():
    assert R.render("{{^missing}}none{{/missing}}", DATA) == "none"
    assert R.render("{{^name}}none{{/name}}", DATA) == ""


def test_all_bundled_templates_render():
    for name in R.list_templates():
        html, _ = R.render_file(name, ROOT / "examples" / "example.json")
        assert "<html" in html.lower() and "{{" not in html.split("{%")[0], name


def test_templates_have_no_personal_literals():
    import re
    for p in (ROOT / "resume_img_gen" / "templates").glob("*.html"):
        text = p.read_text(encoding="utf-8")
        assert not re.search(r"[0-9]{11}|@[a-z0-9.-]+\.(com|cn|org)", text, re.I), p


if __name__ == "__main__":
    for fn in [test_variable_and_dotted_path, test_list_section_and_index,
               test_inverted_section, test_all_bundled_templates_render,
               test_templates_have_no_personal_literals]:
        fn()
        print("ok", fn.__name__)
