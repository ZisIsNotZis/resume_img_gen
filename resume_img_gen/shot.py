"""HTML -> PNG / PDF using a headless Chromium (chrome-headless-shell, Chrome,
Chromium, or Edge).  No Playwright/Puppeteer module is required — we just exec
the browser binary.

This is the "img" half of resume_img_gen: point it at an HTML file and get a
pixel image (or a PDF) back.

Usage via the CLI:
  python -m resume_img_gen shot page.html --out page.png --width 1760
  python -m resume_img_gen shot page.html --out page.pdf
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
from pathlib import Path

# Common install locations for a headless-capable Chromium (playwright/puppeteer).
_CANDIDATE_GLOBS = [
    "~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell",
    "~/.cache/ms-playwright/chromium-*/chrome-linux/chrome",
    "~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome",
    "~/.cache/puppeteer/chrome/*/chrome-linux64/chrome",
    "~/.cache/puppeteer/chrome-headless-shell/*/chrome-headless-shell-linux64/chrome-headless-shell",
]

_NAMES = [
    "chrome-headless-shell", "chrome", "chromium", "chromium-browser",
    "google-chrome", "google-chrome-stable", "microsoft-edge", "msedge",
]


def _glob(pattern: str):
    return sorted(glob.glob(os.path.expanduser(pattern)))


def find_chrome(explicit: str | None = None) -> str | None:
    """Locate a headless-capable browser binary, or None."""
    if explicit:
        return explicit if Path(explicit).exists() else None
    for name in _NAMES:
        p = shutil.which(name)
        if p:
            return p
    for pattern in _CANDIDATE_GLOBS:
        hits = _glob(pattern)
        if hits:
            return hits[-1]
    return None


def shot_png(html_path, out_path, width=1760, height=1200, chrome=None, scale=1.0):
    """Screenshot ``html_path`` to ``out_path`` (PNG).

    ``chromium --screenshot`` captures the *viewport* (``--window-size``), not the
    full page, so pass the design-canvas dimensions you want.  ``height <= 0``
    falls back to 1200 rather than emitting an invalid ``--window-size``.
    """
    if height <= 0:
        height = 1200
    exe = find_chrome(chrome)
    if not exe:
        raise RuntimeError(
            "no Chromium/Chrome found; install chrome-headless-shell or pass --chrome")
    url = Path(html_path).resolve().as_uri()
    args = [exe, "--headless", "--disable-gpu", "--no-sandbox",
            "--hide-scrollbars", f"--force-device-scale-factor={scale}",
            f"--screenshot={out_path}", f"--window-size={int(width)},{int(height)}",
            "--virtual-time-budget=3000", url]
    subprocess.run(args, check=True)
    return out_path


def shot_pdf(html_path, out_path, chrome=None):
    """Print ``html_path`` to a PDF."""
    exe = find_chrome(chrome)
    if not exe:
        raise RuntimeError(
            "no Chromium/Chrome found; install chrome-headless-shell or pass --chrome")
    url = Path(html_path).resolve().as_uri()
    args = [exe, "--headless", "--disable-gpu", "--no-sandbox",
            f"--print-to-pdf={out_path}", "--no-pdf-header-footer",
            "--virtual-time-budget=3000", url]
    subprocess.run(args, check=True)
    return out_path
