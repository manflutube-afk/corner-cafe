#!/usr/bin/env python3
"""Assemble src/ into public/, the Cloudflare Pages deploy root.

Every entry in src/pages.py becomes its own real URL — /menu, /roasts and so
on — each a standalone HTML file with its own title, description and canonical
tag, all listed in sitemap.xml. That is what lets search engines index the
pages separately; a single page with #hash sections cannot be.

Source layout (edit these):
    src/pages.py              the page list: slugs, titles, descriptions
    src/page.template.html    the shell every page is poured into
    src/partials/*.html       shared chunks (header, nav, footer) and one
                              file per page section (home, menu, roasts, ...)
    src/css/style.css
    src/js/main.js
    images/                   source images, served as real files

Output (generated, don't hand-edit):
    public/index.html         plus public/<slug>/index.html per page
    public/sitemap.xml, public/robots.txt
    public/css, public/js, public/images

Run after any edit under src/ or images/:

    python build.py
"""

import datetime
import hashlib
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
PARTIALS = SRC / "partials"
IMAGES = ROOT / "images"
PUBLIC = ROOT / "public"

sys.path.insert(0, str(SRC))
from pages import PAGES, SITE_URL  # noqa: E402

TOKEN_RE = re.compile(r"__[A-Z0-9_:]+__")


def hashed_name(stem, suffix, data):
    """style.css -> style.<content hash>.css

    The HTML is served with max-age=0 but CSS and JS are cached for hours, so
    a fresh page could otherwise be styled by a stale stylesheet — which is not
    theoretical: it shipped a badge stretched to triple height. Changing the
    filename whenever the contents change makes that impossible, and lets the
    assets be cached hard (see the _headers file).
    """
    digest = hashlib.sha256(data).hexdigest()[:8]
    return "%s.%s%s" % (stem, digest, suffix)


# The fonts are self-hosted rather than fetched from Google, so visitors'
# IP addresses never reach a third party. src/fonts/fonts.css holds the
# generated @font-face block and rides in the same stylesheet.
CSS_TEXT = ((SRC / "fonts" / "fonts.css").read_text(encoding="utf-8")
            + (SRC / "css" / "style.css").read_text(encoding="utf-8"))
JS_TEXT = (SRC / "js" / "main.js").read_text(encoding="utf-8")

CSS_NAME = hashed_name("style", ".css", CSS_TEXT.encode("utf-8"))
JS_NAME = hashed_name("main", ".js", JS_TEXT.encode("utf-8"))

HEADERS = """\
/css/*
  Cache-Control: public, max-age=31536000, immutable
/js/*
  Cache-Control: public, max-age=31536000, immutable
/fonts/*
  Cache-Control: public, max-age=31536000, immutable
"""


def read(path):
    if not path.exists():
        sys.exit("missing file: %s" % path)
    return path.read_text(encoding="utf-8")


def esc(text):
    """Escape text going into an HTML attribute or element."""
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def path_for(slug):
    """URL path for a page, with the trailing slash.

    Cloudflare Pages serves public/menu/index.html at /menu/ and 308-redirects
    /menu to it — verified against `wrangler pages dev`, not assumed. Canonical
    tags, nav links and the sitemap must all use the form that answers 200, or
    every link costs a redirect and the sitemap disagrees with the canonical.
    """
    return "/" if not slug else "/" + slug + "/"


def nav_links(current):
    """The nav is generated from PAGES so it can never drift out of sync with
    the pages that actually exist. The current page gets aria-current, which
    is what both the highlight and the sliding indicator key off."""
    return "\n      ".join(
        '<a class="navbtn" href="%s"%s>%s</a>' % (
            path_for(page["slug"]),
            ' aria-current="page"' if page["slug"] == current else "",
            esc(page["nav"]),
        )
        for page in PAGES
    )


def build_page(page):
    html = read(SRC / "page.template.html")
    canonical = SITE_URL + path_for(page["slug"] or "")

    html = html.replace("__TITLE__", esc(page["title"]))
    html = html.replace("__DESCRIPTION__", esc(page["description"]))
    html = html.replace("__CANONICAL__", canonical)
    if page["slug"] is None:
        html = html.replace('<link rel="canonical" href="%s">' % canonical,
                            '<meta name="robots" content="noindex">')
    html = html.replace("__SITE_URL__", SITE_URL)
    html = html.replace("__CSS__", "/css/" + CSS_NAME)
    html = html.replace("__JS__", "/js/" + JS_NAME)

    for name in re.findall(r"__PARTIAL:([a-z]+)__", html):
        html = html.replace("__PARTIAL:%s__" % name,
                            read(PARTIALS / ("%s.html" % name)).strip())

    html = html.replace("__NAVLINKS__", nav_links(page["slug"]))
    html = html.replace("__CONTENT__",
                        read(PARTIALS / ("%s.html" % page["partial"])).strip())

    # The floor plan is inlined as raw SVG markup, not a file reference,
    # because the page's CSS animates its .ping and .callout elements — that
    # only works for inline SVG, not an <img src="...">.
    html = html.replace("__MAP_SVG__", read(IMAGES / "plan.svg").strip())

    check_images(html, "page %r" % (page["slug"] or "/"))

    leftover = sorted(set(TOKEN_RE.findall(html)))
    if leftover:
        sys.exit("unreplaced tokens on page %r: %s"
                 % (page["slug"] or "/", ", ".join(leftover)))

    return html


NOT_FOUND = {
    "slug": None,          # not a real URL: kept out of the nav and the sitemap
    "partial": "404",
    "title": "Page not found — Corner Café, Par Market",
    "description": "That page could not be found. The Corner Café is still at "
                   "stall 6, Par Market, Cornwall.",
}


def image_refs(html):
    """Every /images/... filename a page actually asks for."""
    return set(re.findall(r"/images/([A-Za-z0-9._-]+)", html))


def check_images(html, where):
    """Fail the build if a page references an image that isn't in images/.

    A missing image is invisible in the build output and only shows up as a
    broken picture on the live site, so it's worth catching here.
    """
    missing = sorted(ref for ref in image_refs(html) if not (IMAGES / ref).exists())
    if missing:
        sys.exit("%s references images that are not in images/: %s"
                 % (where, ", ".join(missing)))


def build_sitemap():
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for page in PAGES:
        # lastmod comes from the partial's own mtime, so it reflects when that
        # page's content actually changed rather than when the build ran.
        mtime = (PARTIALS / ("%s.html" % page["partial"])).stat().st_mtime
        lastmod = datetime.date.fromtimestamp(mtime).isoformat()
        lines.append(
            "  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>"
            % (SITE_URL + path_for(page["slug"]), lastmod, page.get("priority", "0.8"))
        )
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def build_robots():
    return "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE_URL


def empty(directory):
    """Delete everything inside a directory, but not the directory itself.

    On Windows a running dev server (or an open Explorer window) holds a
    handle on the folder, so removing public/ outright fails with
    PermissionError. Emptying it in place works regardless.
    """
    for child in directory.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def main():
    if PUBLIC.exists():
        empty(PUBLIC)
    else:
        PUBLIC.mkdir(parents=True)

    used = set()

    for page in PAGES:
        target = PUBLIC / "index.html" if not page["slug"] \
            else PUBLIC / page["slug"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        html = build_page(page)
        used.update(image_refs(html))
        target.write_text(html, encoding="utf-8")
        print("  %-12s -> %s" % (path_for(page["slug"]),
                                 target.relative_to(ROOT).as_posix()))

    html = build_page(NOT_FOUND)
    used.update(image_refs(html))
    (PUBLIC / "404.html").write_text(html, encoding="utf-8")
    print("  %-12s -> %s" % ("(404)", "public/404.html"))

    (PUBLIC / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8")
    (PUBLIC / "robots.txt").write_text(build_robots(), encoding="utf-8")

    (PUBLIC / "css").mkdir()
    (PUBLIC / "css" / CSS_NAME).write_text(CSS_TEXT, encoding="utf-8")

    (PUBLIC / "js").mkdir()
    (PUBLIC / "js" / JS_NAME).write_text(JS_TEXT, encoding="utf-8")

    shutil.copytree(SRC / "fonts", PUBLIC / "fonts",
                    ignore=shutil.ignore_patterns("*.css"))

    # hashed names can never go stale, so let them be cached hard
    (PUBLIC / "_headers").write_text(HEADERS, encoding="utf-8")

    # Only the images the pages actually ask for. Raw camera drops waiting to
    # be processed sit in images/ too, and deploying megabytes of them would be
    # pure waste. plan.svg is inlined into the page, so it isn't needed here.
    (PUBLIC / "images").mkdir()
    for name in sorted(used):
        shutil.copyfile(IMAGES / name, PUBLIC / "images" / name)

    print("built %d pages + sitemap.xml, %d images into public/"
          % (len(PAGES), len(used)))


if __name__ == "__main__":
    main()
