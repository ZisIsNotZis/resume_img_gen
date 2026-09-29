# Playbook: reference image → HTML resume (visual clone + multimodal fix loop)

A proven procedure for turning a **reference PNG** (an AI-generated or designed
resume/poster) into matching, editable HTML. Follow it directly; don't
re-derive. It was refined over a batch of 7 designs.

## Workflow

1. **Read the target PNG** (use a multimodal model / image viewer). Note: layout
   structure, color palette (sample exact hexes by eye: background, panel,
   accent, border, text), section-header style (badges / skew / trails), card
   style, decorations (corner brackets, hatch strips, dividers, dots).
2. **Find a text authority.** AI-generated images often contain corrupted or
   garbled text. If a sibling `.md` / `.txt` / document exists, use it as the
   text source of truth — never copy corrupted glyphs. If none exists,
   transcribe carefully and normalise obvious corruption.
3. **Check CJK fonts** before the first render: `fc-list :lang=zh family`. Use a
   fallback chain such as `"Noto Sans CJK SC", sans-serif`.
4. **Write the HTML** as a fixed-size design canvas matching the reference
   pixels (get the size with
   `python3 -c "from PIL import Image; print(Image.open(p).size)"`). Position
   decorations absolutely; use CSS grid for columns; `clip-path` for skewed
   badges; `repeating-linear-gradient` for hatch strips.
5. **Render** with a headless browser (no Playwright/Puppeteer module needed):
   ```sh
   chrome-headless-shell --headless --disable-gpu --no-sandbox \
     --hide-scrollbars --window-size=W,H \
     --screenshot=out.png "file://$PWD/page.html"
   ```
   (`resume_img_gen shot page.html --out out.png --width W --height H` wraps this.)
6. **Compare loop**: view the render (multimodal) against the target PNG. Fix
   the top diffs, re-render. 2–4 iterations typical. Judge by: line-wrap counts
   per block, one-line vs two-line elements, vertical rhythm / column bottoms,
   color temperature.

## Gotchas (each cost real time once — do it right the first time)

- **`overflow: hidden` on a fixed-size `body` kills ALL scrolling** —
  out-of-screen content becomes unreachable. Never ship it. Instead: a fixed
  canvas inside a `#scaler` wrapper plus a 3-line script that sets
  `scaler.style.zoom = min(1, clientWidth / CANVAS_W)` on load and resize
  (scale-to-fit width, vertical scroll free). Add
  `@media print { #scaler { zoom: <A4_W / CANVAS_W> !important } @page { size: A4; margin: 0 } }`
  for a clean Ctrl-P.
- **Unequal grid columns from long unbreakable strings**: `grid-template-columns:
  1fr 1fr` means `minmax(auto, 1fr)` — a long URL inflates that column's
  min-content width and silently shrinks the sibling. Always use
  `minmax(0, 1fr)` for equal columns containing URLs.
- **Dates/tokens splitting across lines** (`2018.09-` / `2020.12`): give date
  spans `white-space: nowrap` so they wrap as a unit.
- **Hero/highlight cards wrapping to more lines than the target** = font ~2px
  too big. Shrink the font (e.g. 29–31px range) rather than reducing padding.
- **Match each block's line count to the target** — that is the strongest
  visual-match signal, stronger than exact colors.
- View the render at full size, then crop suspicious regions with PIL for detail
  checks. A full-page view hides single-line defects.
- If you delegate the compare loop to a model, it **must be image-capable**.
  A text-only reviewer cannot judge a render. Launch at most a few workers at a
  time; a large parallel burst trips provider rate limits. For transient
  failures, **requeue the failed worker to the back of the batch** (each retry
  then naturally spaces itself after a full sibling run) rather than giving up —
  and keep a `.then(ok, fail)` around each run so one rejection doesn't abort the
  batch.
- **Beware stale renders**: if the HTML and the render disagree, re-render before
  diagnosing.

## Division of labour & fidelity

- A worker may not have the tools it needs in every spawn. A worker without
  image reading can still build from a **written design spec** (the parent views
  the PNG, writes layout / palette / content spec to a file) plus programmatic
  color sampling; the parent then does the multimodal render-compare itself and
  steers fixes. Structural-only verification by workers is **not** sufficient.
- **Fidelity contract: clone the TEMPLATE, not a corrected document.** Quirks in
  the reference (duplicated rows, mismatched labels, garbled pill text) are part
  of the template — reproduce their structure even when the text is nonsense.
  Only fix what the owner explicitly asks to fix. Don't "normalise" content
  unless told to.

## Deliverable checklist

- [ ] HTML opens in a normal browser: scales to fit width, vertical scroll
      works, nothing clipped.
- [ ] Print → a single A4 page.
- [ ] Text is clean (from the text authority); all links are real text.
- [ ] Final render saved next to the HTML; intermediates deleted.

## Acceptance test for a new reusable template

- Rendered PNG vs the reference differs only at anti-aliasing level
  (mean RGB diff ≲ 2.5/255 for near-identical, or a documented visual match).
- Grep the template for content literals (name, phone, orgs) → empty.
