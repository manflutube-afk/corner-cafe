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

    for page in PAGES:
        target = PUBLIC / "index.html" if not page["slug"] \
            else PUBLIC / page["slug"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(build_page(page), encoding="utf-8")
        print("  %-12s -> %s" % (path_for(page["slug"]),
                                 target.relative_to(ROOT).as_posix()))

    (PUBLIC / "404.html").write_text(build_page(NOT_FOUND), encoding="utf-8")
    print("  %-12s -> %s" % ("(404)", "public/404.html"))

    (PUBLIC / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8")
    (PUBLIC / "robots.txt").write_text(build_robots(), encoding="utf-8")

    (PUBLIC / "css").mkdir()
    shutil.copyfile(SRC / "css" / "style.css", PUBLIC / "css" / "style.css")

    (PUBLIC / "js").mkdir()
    shutil.copyfile(SRC / "js" / "main.js", PUBLIC / "js" / "main.js")

    shutil.copytree(IMAGES, PUBLIC / "images")
    shutil.copyfile(SRC / "sitemap.xml", PUBLIC / "sitemap.xml")

    print("built %d pages + sitemap.xml into public/" % len(PAGES))


if __name__ == "__main__":
    main()
