# Corner Café website

A site for Corner Café, stall 6, Par Market, Cornwall — deployed as a static
site on Cloudflare Pages. No framework: plain HTML, CSS and vanilla JS,
split into separate files under `src/` so it's easy to work on in an editor.

## Layout

```
src/
  index.template.html   page shell — head, header, nav, main, footer, script tag
  head-meta.html         <head> meta tags: title, description, favicons, og/twitter
  partials/
    header.html          top bar
    nav.html              main nav + mobile drawer
    home.html             HOME section
    visit.html            WHY VISIT section
    menu.html              MENU section
    roasts.html           ROASTS section
    about.html             WHO WE ARE section
    find.html               FIND US section
    footer.html            bottom ticker + footer
  css/style.css           all styles
  js/main.js              all behaviour (routing, reveals, ticker, countdown, etc.)
images/                  every source image, the floor-plan SVG, and favicons —
                         the master copies; referenced by real relative paths
                         (e.g. `images/hero.jpg`), not embedded as data URIs
build.py                 assembles src/ + images/ into public/
public/                  generated deploy root (gitignored — see below)
make_map.py              regenerates images/plan.svg, the floor plan of Par
                         Market with stall 6 highlighted
```

`public/` is a **build artifact**, not source — it's regenerated from
`src/` and `images/` every time you build, and it's gitignored. Don't
hand-edit anything under `public/`; edit the files under `src/` instead.

## Working on this in VS Code

Open this folder in VS Code. Edit whichever partial you're touching — e.g.
`src/partials/menu.html` for the menu, `src/css/style.css` for styling,
`src/js/main.js` for behaviour — then rebuild:

```bash
python build.py
```

`npm run dev` and `npm run deploy` rebuild automatically before running, so
in normal use you don't need to run `build.py` by hand — just run one of
those.

### Adding a page section

1. Add `src/partials/<name>.html` (just the `<section class="page" id="page-<name>" ...>` markup).
2. Reference it from `src/index.template.html` with `__PARTIAL:<name>__`.
3. Add a nav link in `src/partials/nav.html` (both the desktop nav and the
   mobile drawer list the same links).
4. Add `<name>` to the `PAGES`/`TITLES` lists in `src/js/main.js` so the
   hash router (`#<name>`) picks it up.

### Adding/replacing an image

Drop the file in `images/`, reference it from the relevant partial as
`images/<filename>`, and rebuild. No base64, no token — it's a normal
static asset served straight from Cloudflare Pages.

## Local development

```bash
npm install
npm run dev
```

This rebuilds `public/` then runs `wrangler pages dev public`, a local
Cloudflare Pages emulator.

## Deploy

```bash
npm run deploy
```

Rebuilds `public/` then runs `wrangler pages deploy public`. First deploy
will prompt you to log in to Cloudflare and will create the `corner-cafe`
Pages project. Point your custom domain at it from the Cloudflare dashboard
afterwards.

## Design system

- Colours, fonts, and spacing are all CSS custom properties at the top
  of `src/css/style.css` (`--ink`, `--baby`, `--blue`, etc.) — change
  the palette from one place.
- `Anton` (headings), `Barlow` (body), `Caveat` (handwritten accents)
  loaded from Google Fonts.
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
- Pages are switched client-side via `#hash` routing (see the
  `PAGES`/`TITLES`/`show()` logic in `src/js/main.js`). Each has its own
  title and updates the URL hash, so links like `#menu` jump straight to
  that section.

## Known gotchas (don't reintroduce these)

- **Scoping**: the whole home page `<section>` carries class `hero` for
  layout. CSS rules meant only for the dark banner must target
  `.hero-stage` (the actual dark box), never a bare `.hero <tag>` —
  a `.hero p` or `.hero .btn` rule will leak onto *every* paragraph or
  button anywhere else on the home page and silently override its
  colour. This has bitten this project twice already.
- **Social image**: `og:image`/`twitter:image` point at the relative
  path `images/social-share.jpg`. Social platforms fetch that over
  HTTP — no preview will render until the site is actually live at a
  public URL with that file reachable next to the HTML.
- **Floor plan stays inline**: `__MAP_SVG__` in `src/partials/find.html`
  is replaced with the raw contents of `images/plan.svg`, not a file
  reference — the page's CSS animates the plan's `.ping` and `.callout`
  elements, which only works for inline `<svg>`, not `<img src="...">`.
  If the market layout changes, edit `make_map.py` and re-run it, then
  re-run `build.py`.
- **Reduced motion**: everything animated checks
  `prefers-reduced-motion`. Keep that check on any new animation.
