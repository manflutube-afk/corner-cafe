# Builds a clean vector floor plan of Par Market, redrawn from the market's plan.
# Units: viewBox 0 0 1000 540

STALL = []   # (x, y, w, h, label, kind)

def add(x, y, w, h, label="", kind="stall"):
    STALL.append((x, y, w, h, label, kind))

def row(y, h, spec, kind="stall"):
    """spec: list of (x1, x2, label)"""
    for x1, x2, lab in spec:
        add(x1, y, x2 - x1, h, lab, kind)

# ---------------- top band ----------------
row(40, 36, [(145,215,"7"),(225,355,"8"),(358,382,"9A"),(385,415,"9B"),
             (425,452,"10"),(455,482,"11"),(485,508,"12"),(511,600,"13"),
             (630,710,"14"),(713,742,"15"),(745,812,"16")])

# stall 6 — L shape, drawn as two rects (highlighted separately)
add(60, 40, 32, 128, "6", "here")
add(92, 40, 38, 36, "", "here")

add(60, 175, 32, 78, "5")
add(60, 256, 32, 24, "4")

# right hand column
row(82, 26, [(782,815,"17")])
row(111, 26, [(782,815,"18")])
row(140, 26, [(782,815,"19A")])
row(169, 26, [(782,815,"19B")])

# ---------------- row B ----------------
row(92, 32, [(118,190,"47A"),(193,217,"47B"),(220,243,"48A"),(246,269,"48B"),
             (272,295,"48C"),(298,318,"49A"),(321,341,"49B"),(344,364,"49C"),(367,395,"50")])
row(92, 32, [(415,443,"51"),(446,468,"52"),(471,528,"53"),(531,566,"54"),
             (569,589,"55A"),(592,612,"55B"),(615,643,"56"),(646,690,"57A"),
             (693,730,"57B"),(733,765,"58A")])

# ---------------- row C ----------------
row(127, 32, [(118,140,"46"),(143,163,"71"),(166,222,"70"),(225,248,"69B"),
              (251,274,"69A"),(277,395,"68")])
row(127, 32, [(415,490,"65"),(493,516,"64"),(519,542,"63"),(545,568,"62"),
              (571,591,"61"),(594,617,"60"),(640,700,"59B"),(703,726,"59A"),(729,765,"58B")])

# ---------------- row D ----------------
row(180, 28, [(258,290,"34"),(293,335,"33"),(338,382,"32"),(385,420,"31"),
              (432,478,"30"),(481,540,"29"),(543,563,"28B"),(566,586,"28A"),
              (589,625,"27"),(628,660,"26B"),(663,683,"26A"),(686,772,"25")])

# left blocks
add(118,180,34,24,"45"); add(118,207,34,30,"44"); add(118,240,34,34,"43"); add(118,277,34,24,"42")
add(155,180,35,36,"72"); add(155,219,35,26,"73"); add(155,248,35,24,"74")
add(155,275,35,30,"75"); add(155,308,35,30,"76")
add(118,304,34,46,"41"); add(118,353,34,18,"40B"); add(118,374,72,58,"40A")
add(205,180,40,26,"35A"); add(205,209,40,22,"35B"); add(205,234,40,22,"36A"); add(205,259,40,24,"36B")

# right blocks
add(700,211,85,26,"24")
add(758,240,26,30,"23")
add(790,200,30,20,"20"); add(790,223,30,40,"21"); add(790,266,30,20,"22")

# ---------------- food hall (green) ----------------
row(212, 30, [(258,298,""),(301,341,""),(344,381,""),(384,420,"")], "unit")
add(423,212,26,30,"", "blue")
row(245, 30, [(258,290,"81"),(293,325,"82"),(328,352,"83"),(355,378,"84A")], "unit")
add(381,245,30,32,"SEATING","seat")
add(413,252,32,28,"84B","unit")
add(398,285,44,16,"85","unit")
add(250,303,68,26,"37A"); add(250,332,68,52,"37B"); add(250,387,68,18,"38")
add(321,303,42,16,"80","unit"); add(321,322,42,14,"79","unit"); add(321,339,44,54,"78","unit")
add(372,303,19,14,"90A","unit"); add(393,303,19,14,"90B","unit")
add(372,319,40,14,"SEATING","seat")
add(372,335,19,24,"88","unit"); add(393,335,19,24,"89","unit")
add(372,362,40,16,"SEATING","seat")
add(428,328,34,54,"86","unit"); add(424,386,40,46,"87","unit")
add(300,415,50,33,"77","unit")

# kidzworld + escape room
add(462,240,253,185,"", "kidz")
add(470,430,48,42,"", "dark")

# entrances / outdoor
add(118,428,40,32,"1"); add(118,452,112,20,"", "stall")
add(250,432,36,16,"39")
add(252,455,17,18,"98","pink"); add(273,455,17,18,"91","pink")
add(360,400,58,40,"SEATING","seat")
add(360,443,58,27,"OUTDOOR SEATING","seat")
add(40,428,20,22,"100","pink"); add(62,458,24,26,"97","pink")
add(110,486,56,16,"96","pink")
add(235,486,20,16,"95","pink"); add(258,486,20,16,"92","pink")
add(320,486,20,16,"93","pink"); add(343,486,20,16,"94","pink")

KIND = {
  "stall": ("#cfe0ec", "#5b7288"),
  "here":  ("#2f9e5f", "#1d6b3f"),
  "unit":  ("#cfe4d0", "#5f8468"),
  "blue":  ("#8fbfe0", "#4a7ea5"),
  "seat":  ("#f0d9a8", "#a98a4e"),
  "pink":  ("#e2cfe6", "#8b6f96"),
  "kidz":  ("#faf0cd", "#c9b479"),
  "dark":  ("#2b3138", "#2b3138"),
}

def esc(s):
    return s.replace("&","&amp;").replace("<","&lt;")

def build():
    parts = []
    parts.append('<svg class="plan-svg" viewBox="0 -32 800 516" xmlns="http://www.w3.org/2000/svg" role="img" '
                 'aria-label="Floor plan of Par Market with the Corner Cafe at stall 6 highlighted in green">')
    parts.append('<defs><filter id="glow" x="-60%" y="-60%" width="220%" height="220%">'
                 '<feGaussianBlur stdDeviation="7" result="b"/>'
                 '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')
    parts.append('<rect x="0" y="-32" width="800" height="516" fill="none"/>')

    here = []
    for (x, y, w, h, lab, kind) in STALL:
        fill, stroke = KIND[kind]
        g = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="1.5" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (x-30, y-25, w, h, fill, stroke))
        if kind == "here":
            here.append((x-30, y-25, w, h))
        parts.append(g)
        if lab:
            fs = 8.5 if len(lab) <= 3 else 5.6
            col = "#ffffff" if kind in ("here","dark") else "#2b3138"
            weight = "700" if kind == "here" else "600"
            parts.append('<text x="%.1f" y="%.1f" font-size="%.1f" font-weight="%s" fill="%s" '
                         'text-anchor="middle" dominant-baseline="central" font-family="Inter,Barlow,sans-serif">%s</text>'
                         % (x-30+w/2, y-25+h/2, fs, weight, col, esc(lab)))

    # pulsing ring + callout on stall 6
    hx, hy, hw, hh = here[0]
    cx, cy = hx + hw/2, hy + 18
    parts.append('<g filter="url(#glow)"><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="none" '
                 'stroke="#2f9e5f" stroke-width="2.5" opacity=".9"/></g>' % (hx, hy, hw, hh))
    parts.append('<circle class="ping" cx="%.1f" cy="%.1f" r="12" fill="none" stroke="#2f9e5f" stroke-width="2"/>' % (cx, cy))
    parts.append('<circle cx="%.1f" cy="%.1f" r="6" fill="#2f9e5f" stroke="#ffffff" stroke-width="2"/>' % (cx, cy))

    # callout label
    parts.append('<g class="callout">')
    parts.append('<line x1="%.1f" y1="%.1f" x2="122" y2="-9" stroke="#2f9e5f" stroke-width="1.6" stroke-dasharray="3 3"/>' % (cx+7, cy-6))
    parts.append('<rect x="118" y="-24" width="222" height="30" rx="4" fill="#2f9e5f"/>')
    parts.append('<text x="229" y="-8" font-size="11" font-weight="700" fill="#ffffff" text-anchor="middle" '
                 'dominant-baseline="central" font-family="Inter,Barlow,sans-serif" letter-spacing="0.5">'
                 'STALL 6 — THE CORNER CAFÉ</text>')
    parts.append('</g>')

    # entrance labels
    for tx, ty, t in [(105, 448, "MARKET ENTRANCE"), (300, 452, "FOOD HALL ENTRANCE")]:
        parts.append('<text x="%d" y="%d" font-size="7" font-weight="700" fill="#5b6672" text-anchor="middle" '
                     'font-family="Inter,Barlow,sans-serif">%s</text>' % (tx, ty, t))
    parts.append('<text x="558" y="315" font-size="13" font-weight="700" fill="#b09a5c" text-anchor="middle" '
                 'font-family="Inter,Barlow,sans-serif" letter-spacing="1">KIDZWORLD</text>')
    parts.append('<text x="558" y="331" font-size="8" fill="#b09a5c" text-anchor="middle" '
                 'font-family="Inter,Barlow,sans-serif">Adventure Play</text>')
    parts.append('<text x="464" y="425" font-size="6" font-weight="700" fill="#ffffff" text-anchor="middle" '
                 'font-family="Inter,Barlow,sans-serif">ESCAPE</text>')
    parts.append('<text x="464" y="433" font-size="6" font-weight="700" fill="#ffffff" text-anchor="middle" '
                 'font-family="Inter,Barlow,sans-serif">ROOM</text>')
    parts.append('</svg>')
    return "".join(parts)

if __name__ == "__main__":
    from pathlib import Path
    out = Path(__file__).resolve().parent / "images" / "plan.svg"
    svg = build()
    out.write_text(svg, encoding="utf-8")
    print("svg written", len(svg), "bytes ->", out)
