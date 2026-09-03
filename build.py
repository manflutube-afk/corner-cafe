#!/usr/bin/env python3
"""Assemble src/ into public/, the Cloudflare Pages deploy root.

Source layout (edit these):
    src/index.template.html   page shell, with __HEAD_META__ / __PARTIAL:name__ tokens
    src/head-meta.html        <head> meta tags (title, description, favicons, og/twitter)
    src/partials/*.html       one file per page section (header, nav, home, visit, ...)
    src/css/style.css
    src/js/main.js
    images/                   source images, referenced by real relative paths (no base64)

Output (generated, don't hand-edit):
    public/index.html
    public/css/style.css
    public/js/main.js
    public/images/*

Run after any edit under src/ or images/:

    python build.py
"""

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
PARTIALS = SRC / "partials"
IMAGES = ROOT / "images"
PUBLIC = ROOT / "public"

TOKEN_RE = re.compile(r"__[A-Z0-9_:]+__")


def read(path):
    if not path.exists():
        sys.exit("missing file: %s" % path)
    return path.read_text(encoding="utf-8")


def assemble_html():
    html = read(SRC / "index.template.html")
    html = html.replace("__HEAD_META__", read(SRC / "head-meta.html").strip())

    for match in re.findall(r"__PARTIAL:([a-z]+)__", html):
        partial = PARTIALS / ("%s.html" % match)
        html = html.replace("__PARTIAL:%s__" % match, read(partial).strip())

    # The floor plan is inlined as raw SVG markup, not a file reference, because
    # the page's CSS animates its .ping and .callout elements — that only works
    # for inline SVG, not an <img src="..."> or background-image.
    html = html.replace("__MAP_SVG__", read(IMAGES / "plan.svg").strip())

    leftover = sorted(set(TOKEN_RE.findall(html)))
    if leftover:
        sys.exit("unreplaced tokens: %s" % ", ".join(leftover))

    return html


def main():
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir(parents=True)

    (PUBLIC / "index.html").write_text(assemble_html(), encoding="utf-8")

    (PUBLIC / "css").mkdir()
    shutil.copyfile(SRC / "css" / "style.css", PUBLIC / "css" / "style.css")

    (PUBLIC / "js").mkdir()
    shutil.copyfile(SRC / "js" / "main.js", PUBLIC / "js" / "main.js")

    shutil.copytree(IMAGES, PUBLIC / "images")

    print("built public/ from src/")


if __name__ == "__main__":
    main()
