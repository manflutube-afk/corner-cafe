# Corner Café website

A site for Corner Café, stall 6, Par Market, Cornwall — deployed as a static
site on Cloudflare Pages. No framework: plain HTML, CSS and vanilla JS,
split into separate files under `src/` so it's easy to work on in an editor.

## Layout

```
src/
  pages.py               THE page list — slugs, titles, descriptions.
                         Edit this to change a page title or add a page.
  page.template.html     the shell every page is poured into
  partials/
    header.html          top bar          (shared by every page)
    nav.html             nav shell        (links generated from pages.py)
    footer.html          ticker + footer  (shared by every page)
    home.html  visit.html  menu.html
    roasts.html  about.html  find.html    one file per page
    404.html             the not-found page
  css/style.css          all styles
  fonts/                 self-hosted woff2 files + generated fonts.css
  js/main.js             all behaviour (menu tabs, reveals, ticker, countdown)
images/                  every source image, the floor plan and favicons,
                         referenced as real paths (/images/hero.jpg)
build.py                 assembles src/ + images/ into public/
public/                  generated deploy root (gitignored — see below)
make_map.py              regenerates images/plan.svg, the Par Market floor plan
```

`public/` is a **build artifact**, not source — regenerated on every build and
gitignored. Never hand-edit anything in it; edit `src/` instead.

## Pages and SEO

Every entry in `src/pages.py` is built as its own real URL:

| URL | partial |
| --- | --- |
| `/` | `home.html` |
| `/why-visit/` | `visit.html` |
| `/menu/` | `menu.html` |
| `/roasts/` | `roasts.html` |
| `/who-we-are/` | `about.html` |
| `/find-us/` | `find.html` |

Each is a standalone HTML file with its own `<title>`, meta description,
canonical URL and og/twitter tags, so search engines index them separately.
The build also writes `sitemap.xml` (all six URLs), `robots.txt` pointing at
it, and a `404.html` marked `noindex`.

This replaced an earlier version where all six sections lived at one URL and
were switched with `#hash` links. Search engines ignore everything after a
`#`, so only the homepage could ever be indexed and a sitemap was impossible.
`main.js` still redirects the old `#menu`-style links to the real pages, so
anything shared before the change keeps working — don't remove that.

**Trailing slashes matter.** Cloudflare Pages serves `/menu/` and
308-redirects `/menu` to it. Nav links, canonical tags and the sitemap all use
the trailing-slash form so they match what actually answers 200 — `path_for()`
in `build.py` is the single place that decides this.

### Adding a page

1. Write `src/partials/<name>.html` — just the
   `<section class="page is-active" id="page-<name>">` markup.
2. Add an entry to `PAGES` in `src/pages.py` with its slug, nav label, title
   and description.
3. Run `python build.py`.

The nav, the sitemap and the page itself all come from that one entry, so
there is nothing else to keep in sync.

## Working on this in VS Code

Open this folder in VS Code. Edit whichever partial you're touching —
`src/partials/menu.html` for the menu, `src/css/style.css` for styling,
`src/js/main.js` for behaviour — then rebuild:

```bash
python build.py
```

`npm run dev` and `npm run deploy` rebuild automatically first, so day to day
you just run one of those.

### Adding or replacing an image

Drop the file in `images/`, reference it from the partial as
`/images/<filename>` (leading slash — pages live at `/menu/index.html`, so a
relative path would resolve wrongly), and rebuild.

## Local development

```bash
npm run dev
```

Rebuilds `public/`, then runs `wrangler pages dev public` — the local
Cloudflare Pages emulator. Prefer it over a plain static server: it reproduces
Cloudflare's real trailing-slash redirects and 404 handling, which a generic
server does not.

## Deploy

```bash
npm run deploy
```

Rebuilds and runs `wrangler pages deploy public`. The site is also connected
to GitHub, so pushing to `main` triggers a Cloudflare build automatically —
its build command is `python3 build.py` (note `python3`; Cloudflare's build
servers are Linux) with output directory `public`.

## Design system

- Colours, fonts, and spacing are all CSS custom properties at the top
  of `src/css/style.css` (`--ink`, `--baby`, `--blue`, etc.) — change
  the palette from one place.
- `Anton` (headings), `Barlow` (body), `Caveat` (handwritten accents),
  self-hosted from `src/fonts/` — see the privacy note below.
- Scroll-reveal system: any element with class `r` fades up into view;
  `r-left`/`r-right`/`r-zoom` vary the entrance direction. Timing is
  tuned so the fade always finishes *before* an element is scrolled
  into view (see `armReveals()` in `src/js/main.js` — don't loosen the
  `rootMargin` back down or text can visibly fade in mid-scroll again).
- Mobile-only "scroll acts like hover" system (`watchInView()`) applies
  `.in-view` to buttons/cards/tiles as they pass through the middle of
  the screen, since touch devices have no `:hover`.
- The reviews carousel on mobile (`#reviewsTrack` / `#reviewsDots`) uses
  native CSS scroll-snap plus a small JS layer just to sync the dots.
- Each page is a real document at its own URL — there is no client-side
  router. The nav is plain links, and the current page is marked with
  `aria-current="page"` at build time, which is what both the highlight and
  the sliding nav indicator key off.

## Known gotchas (don't reintroduce these)

- **Scoping**: the whole home page `<section>` carries class `hero` for
  layout. CSS rules meant only for the dark banner must target
  `.hero-stage` (the actual dark box), never a bare `.hero <tag>` —
  a `.hero p` or `.hero .btn` rule will leak onto *every* paragraph or
  button anywhere else on the home page and silently override its
  colour. This has bitten this project twice already.
- **Social image**: `og:image`/`twitter:image` are built as absolute URLs
  (`https://cornercafeparmarket.uk/images/social-share.jpg`) from `SITE_URL`
  in `src/pages.py`. They have to be absolute — social platforms fetch them
  over HTTP and can't resolve a relative path. If the domain ever changes,
  change `SITE_URL` and everything else follows.
- **Page-specific elements**: `main.js` runs on every page, but the menu
  tabs, roast countdown, hours table and review carousel each exist on only
  one of them. Every lookup for those is null-guarded — keep it that way when
  adding anything new, or one missing element breaks the script site-wide.
- **Floor plan stays inline**: `__MAP_SVG__` in `src/partials/find.html`
  is replaced with the raw contents of `images/plan.svg`, not a file
  reference — the page's CSS animates the plan's `.ping` and `.callout`
  elements, which only works for inline `<svg>`, not `<img src="...">`.
  If the market layout changes, edit `make_map.py` and re-run it, then
  re-run `build.py`.
- **Cache busting**: `build.py` writes `style.<hash>.css` / `main.<hash>.js`
  and points the pages at those. Cloudflare serves the HTML with
  `max-age=0` but assets for hours, so without this a fresh page can be
  styled by a stale stylesheet — which shipped a badge stretched to triple
  height before this was added. Don't go back to fixed asset filenames; the
  `_headers` file caches the hashed ones for a year on the strength of it.
- **Fonts are self-hosted, deliberately**: they used to come from Google,
  which meant every visitor's IP address was sent to Google on every page
  load. `src/fonts/` holds the woff2 files and a generated `fonts.css` of
  `@font-face` rules, which `build.py` prepends to the stylesheet. Don't
  reintroduce the Google Fonts `<link>` — the site currently makes no
  third-party requests at all, which is why it needs no cookie banner.
  Each face is split by `unicode-range` into latin and latin-ext, so a
  browser only downloads the subsets a page actually uses (six files, not
  sixteen).
- **Reduced motion**: everything animated checks
  `prefers-reduced-motion`. Keep that check on any new animation.
