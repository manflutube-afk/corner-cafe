# Every page on the site.
#
# Each entry becomes its own real URL with its own <title>, description and
# canonical tag, and gets listed in sitemap.xml — which is what lets search
# engines find and rank each page separately.
#
# To add a page: write src/partials/<partial>.html, add an entry here, and
# run `python build.py`. The nav is generated from this list, so the new page
# appears in it automatically.

SITE_URL = "https://cornercafeparmarket.uk"

PAGES = [
    {
        "slug": "",  # empty slug = the homepage, served at /
        "partial": "home",
        "nav": "Home",
        "title": "Corner Café — Par Market, Cornwall",
        "description": "Home-cooked food at stall 6, Par Market. Big breakfasts, roasts on Wednesday and Sunday, scones with clotted cream. Open Wed, Sat & Sun, 9am–5pm.",
        "priority": "1.0",
    },
    {
        "slug": "why-visit",
        "partial": "visit",
        "nav": "Why visit",
        "title": "Why visit — Corner Café, Par Market",
        "description": "Corner Café sits in the corner of one of the biggest indoor markets in the South West — here's what Par Market is like, and why stall 6 is worth finding.",
        "priority": "0.8",
    },
    {
        "slug": "menu",
        "partial": "menu",
        "nav": "Menu",
        "title": "Menu — Corner Café, Par Market",
        "description": "The full Corner Café menu — breakfasts served all day, main meals, jackets, paninis, burgers, puddings and drinks, with prices. Stall 6, Par Market.",
        "priority": "0.9",
    },
    {
        "slug": "roasts",
        "partial": "roasts",
        "nav": "Roasts",
        "title": "Roast days — Corner Café, Par Market",
        "description": "Roast dinners every Wednesday and Sunday at the Corner Café — beef, pork or turkey with all the trimmings, served until it runs out. Stall 6, Par Market.",
        "priority": "0.9",
    },
    {
        "slug": "who-we-are",
        "partial": "about",
        "nav": "Who we are",
        "title": "Who we are — Corner Café, Par Market",
        "description": "The famous café in the corner of Par Market — a hot cabinet full of pasties and pies, a proper sit-down seating area, and a kitchen happy to rebuild any plate.",
        "priority": "0.7",
    },
    {
        "slug": "find-us",
        "partial": "find",
        "nav": "Find us",
        "title": "Find us — Corner Café, stall 6, Par Market",
        "description": "Find the Corner Café at stall 6, Par Market & Food Hall, Par Moor Road, Par PL25 3RP. In through the market entrance, then keep going to the far corner.",
        "priority": "0.8",
    },
]
