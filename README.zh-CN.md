[English](README.md) | **简体中文**

![resume_img_gen](assets/logo.svg)

数据进来，设计好的简历出去 —— HTML、PNG 与可直接打印的 PDF。

**一份 JSON 简历文案，配上八套手工打磨的 HTML 设计画布中的任意一套，就能得到排版一致的 HTML 页面、按像素裁切的 PNG，或 A4 尺寸的 PDF；不需要渲染服务，不需要浏览器自动化库，也没有任何 Python 依赖。** 版式与内容彼此独立：模板拥有设计的每一个像素，数据文件拥有每一个字，因此一个人的文字可以驱动任意多套设计，一套设计也可以给任意多个人使用。

## 快速开始

```sh
git clone https://github.com/ZisIsNotZis/resume_img_gen
cd resume_img_gen
pipx install .            # 或：pip install .   （也可以直接在仓库里运行：python3 -m resume_img_gen）
```

然后在仓库根目录：

```sh
resume-img-gen render --list                       # 列出 8 套内置设计
resume-img-gen render -t clean-teal-ribbon \
    -d examples/example.json -o resume.html       # JSON + 模板 -> HTML
resume-img-gen shot resume.html -o resume.png \
    --width 1760 --height 2400                     # HTML -> PNG
```

安装本包和使用 `render` 都不需要任何第三方 Python 包。另外两个阶段用到你系统里可能已经有的工具：

- `shot`（HTML → PNG/PDF）需要一个可无头运行的 Chrome、Chromium、Edge，或 Playwright 的 `chrome-headless-shell`。它会在 `PATH` 以及 Playwright/Puppeteer 常见的缓存目录里查找；如果浏览器在别处，用 `--chrome PATH` 指定。
- `pdf`（Markdown → PDF）需要 `pandoc`，以及 `weasyprint` 或 `uv` 之一（未全局安装 WeasyPrint 时，会通过 `uv tool run` 调用）。

`examples/example.json` 与 `examples/example.md` 是**虚构的示例数据**（虚构的人、公司、联系方式），只用于演示流程。请换成你自己的内容。

## 现在能做什么

- **`render`** —— 零依赖的 mustache 风格引擎：`{{key}}` 支持点号路径（`{{jobs.0.org}}`），`{{#key}}…{{/key}}` 区段可遍历列表／字典／真值标量，`{{^key}}…{{/key}}` 反向区段，区段可嵌套，循环内可用 `{{.}}` 与 `{{@index}}`。
- **八套内置设计画布** —— `classic-sidebar`、`clean-teal-columns`、`clean-teal-ribbon`、`dark-hud-circuit`、`dark-hud-dossier`、`dark-hud-radar`、`paper-orange-timeline`、`warm-paper-timeline`。固定尺寸画布，按窗口宽度等比缩放、纵向可滚动，打印出来正好是一页 A4。
- **自己的模板** —— 把 `*.html` 放进任意目录并用 `--templates-dir` 指过去，`--list` 也会一并列出你的模板。
- **`shot`** —— 按 `--width`/`--height` 精确截取视口（`--scale` 支持高分屏），或用 `--out file.pdf` 走浏览器打印且不带页眉页脚。
- **`pdf`** —— Markdown 经 pandoc 转换，套用内置的中文友好 A4 样式（页脚页码），并可用 `--until "# Appendix"` 从同一份源文件生成精简版。
- **中文优先的默认值** —— 内置设计与 PDF 样式都是围绕中文简历排版调的；英文同样适用。
- **一套成文的方法论**，用于把参考图克隆成可复用模板：[`docs/PLAYBOOK.md`](docs/PLAYBOOK.md)。

## 各部分如何协作

三个阶段可以各自独立使用，另加一份样式表。阶段之间只通过磁盘上的文件交接，所以你可以停在任意一步。

```
resume_img_gen/
  resume_img_gen/
    cli.py                  # argparse：render | shot | pdf
    render.py               # 模板引擎 + JSON 读取，无依赖
    shot.py                 # 找到无头浏览器并调用，产出 PNG/PDF
    pdf.py                  # pandoc -> HTML -> WeasyPrint
    resume.css              # A4 / 中文的 WeasyPrint 样式表
    templates/*.html        # 8 套设计画布，每个字符串都是 {{token}}
  examples/                 # 虚构的示例数据（JSON 与 Markdown）
  docs/PLAYBOOK.md          # 参考 PNG -> HTML -> 对比的迭代流程
  docs/project-status.md    # 范围、边界，以及为何此设计已封版
  tests/test_render.py      # 引擎与全部模板的冒烟测试
```

`render` 读取模板与 JSON，展开 token，写出 HTML。`shot` 把 HTML 转成 `file://` URL 交给浏览器二进制。`pdf` 读取 Markdown，经 pandoc 转换，套上样式表，再交给 WeasyPrint。三者唯一的共同假设是：一个模板就是一张自包含的页面。

**让模板可复用只需一条规矩：模板可以承载设计，但不得承载内容。** 如果姓名、电话或公司名以字面字符串出现在 HTML 里，这套设计就不可复用了 —— 那里应该是一个 `{{token}}`。`tests/` 会对内置模板强制检查这一点。

## 模板语法

```
{{key}}                变量（支持点号路径：{{job.org}}）
{{#key}} ... {{/key}}  区段 —— 列表 → 循环（{{.}} 为元素，{{@index}} 为下标），
                       字典 → 合并后渲染一次，真值标量 → 渲染一次
{{^key}} ... {{/key}}  反向区段 —— 值为假或缺失时渲染
```

区段可嵌套。**数据是可信的，因此 `{{...}}` 不会做 HTML 转义** —— 不可信的值请先自行转义。

## 开发

```sh
python3 -m pytest tests/           # 或者，在没装 pytest 时：
python3 tests/test_render.py       # 每个测试打印一行 ok
```

仓库里没有 linter 或 formatter 配置；请沿用现有风格（只用标准库、保留 `from __future__ import annotations`）。评审标准与模板验收方式见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

## 参与贡献

欢迎提交问题报告和新的设计画布，详见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。新模板唯一的硬性要求在 [`docs/PLAYBOOK.md`](docs/PLAYBOOK.md#acceptance-test-for-a-new-reusable-template)：换一份数据渲染，输出只应在内容不同处不同。

## 路线图

**已实现**

- 模板引擎、JSON → HTML 渲染，以及 `render`/`shot`/`pdf` 三个子命令，含 `--list`、`--templates-dir`、`--chrome`、`--scale`、`--until`。
- 八套可复用设计画布，覆盖浅色、纸感与深色 HUD 三个系列。
- 用于 Markdown → PDF 路径的中文 A4 样式表。
- 覆盖引擎与每一套内置模板的冒烟测试。
- 从参考图克隆设计的完整流程文档。

**计划中**

- 无。本仓库是一个**已封版的里程碑**：三阶段流水线已经完整，除非项目输入或目标发生变化，否则不再继续开发（记录见 [`docs/project-status.md`](docs/project-status.md)）。

如果将来重启，最自然的方向是在同一套「数据 + 模板」接口背后增加更多设计画布与更多导出目标 —— 毕竟各阶段已经用文件隔离好了。这只是方向，不是承诺。

## 许可证

LGPL-3.0-or-later，见 [`LICENSE`](LICENSE)。`COPYING` 为 LGPL-3.0 所基于的 GNU GPL-3.0 全文。版权所有 (C) ZisIsNotZis。
