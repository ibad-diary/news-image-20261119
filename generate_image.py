#!/usr/bin/env python3
"""Round-2 front page for news-image-20261119: 36 stories, one image.

Reads stories.json next to this file and draws a dense 1024x1024
newspaper front page with Pillow: a date-check top line, a big serif
masthead, a three-story kicker, region chips, a numbers strip, three
illustrated lead cards, ten illustrated feature cards, a two-column
list of 23 one-line briefs, and a date-check footer. Every picture on
the page is drawn in code (rectangles, circles, arcs, polylines) --
no photos, no network, no randomness. The layout is measured first
and stepped down through three size presets until everything fits
between the top line and the footer, so text can never overlap.
Run:  python3 generate_image.py   (writes entry.png beside itself)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = 1024
EDGE = 26
W = PAGE - 2 * EDGE

CREAM = (250, 247, 238)
CARD = (255, 253, 246)
INK = (20, 20, 20)
BODY = (58, 56, 50)
FAINT = (96, 92, 84)
RED = (172, 34, 26)
DARKRED = (122, 20, 16)
NAVY = (31, 58, 96)
GOLD = (176, 124, 24)
TEAL = (14, 110, 110)
GREEN = (34, 122, 60)
BROWN = (122, 74, 30)
PURPLE = (96, 52, 130)
RULE = (178, 172, 156)
SOFT = (226, 221, 206)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

REGIONS = [
    ("Europe", (31, 58, 96)),
    ("Mideast", (14, 110, 110)),
    ("Asia", (176, 124, 24)),
    ("Africa", (122, 74, 30)),
    ("Americas", (96, 52, 130)),
    ("Oceania", (14, 110, 110)),
    ("World", (90, 88, 80)),
]
REGION_COLOUR = dict(REGIONS)


def face(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, font, width, limit):
    """Greedy word wrap, capped at `limit` lines with an ellipsis."""
    rows, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= width:
            cur = trial
        else:
            rows.append(cur)
            cur = word
    if cur:
        rows.append(cur)
    if len(rows) > limit:
        rows = rows[:limit]
        while rows and d.textlength(rows[-1] + " ...", font=font) > width:
            rows[-1] = rows[-1].rsplit(" ", 1)[0]
        rows[-1] = rows[-1] + " ..."
    return rows


def text_lines(d, text, font, width, limit):
    return wrap(d, text, font, width, limit)


# --- small vector pictures, all drawn in code ---------------------------

def art_summit(d, x, y, w, h):
    """Three leaders at one table: three coloured panels, busts, names."""
    panels = [(NAVY, "TRUMP"), (DARKRED, "XI"), ((52, 72, 110), "PUTIN")]
    pw = w // 3
    for i, (col, name) in enumerate(panels):
        px = x + i * pw
        d.rectangle([px, y, px + pw - 2, y + h], fill=col)
        cx = px + pw // 2
        d.ellipse([cx - 13, y + 16, cx + 13, y + 42], fill=(232, 205, 180))
        d.pieslice([cx - 22, y + 40, cx + 22, y + 86], 180, 360,
                   fill=(245, 245, 240))
        d.rectangle([px + 4, y + h - 20, px + pw - 6, y + h - 4], fill=INK)
        f = face(SANS_B, 11)
        d.text((cx, y + h - 18), name, font=f, fill=(255, 255, 255),
               anchor="ma")


def art_court(d, x, y, w, h):
    """A courthouse: pediment, columns, steps, red 9-6 badge."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 196, 160))
    d.polygon([(x + 8, y + 34), (x + w // 2, y + 6), (x + w - 8, y + 34)],
              fill=(140, 110, 80))
    for i in range(4):
        cx = x + 24 + i * ((w - 48) // 3)
        d.rectangle([cx - 6, y + 36, cx + 6, y + h - 22], fill=(245, 240, 225))
    d.rectangle([x + 6, y + h - 22, x + w - 6, y + h - 14], fill=(120, 92, 66))
    d.rectangle([x + 2, y + h - 13, x + w - 2, y + h - 5], fill=(100, 76, 54))
    d.rounded_rectangle([x + w - 62, y + 8, x + w - 8, y + 40], radius=4,
                        fill=RED)
    f = face(SANS_B, 18)
    d.text((x + w - 35, y + 11), "9–6", font=f, fill=(255, 255, 255),
           anchor="ma")


def art_sunset(d, x, y, w, h):
    """GTA VI sunset: orange-to-purple bands, sun, skyline, big VI."""
    bands = [(232, 120, 40), (214, 84, 96), (128, 72, 140), (64, 48, 110)]
    bh = h // 4
    for i, col in enumerate(bands):
        d.rectangle([x, y + i * bh, x + w, y + (i + 1) * bh], fill=col)
    d.ellipse([x + w // 2 - 26, y + 12, x + w // 2 + 26, y + 64],
              fill=(252, 214, 110))
    base = y + h - 26
    for i, bh2 in enumerate([34, 52, 28, 62, 40, 48]):
        bx = x + 8 + i * ((w - 16) // 6)
        d.rectangle([bx, base - bh2, bx + (w - 16) // 6 - 4, base],
                    fill=(24, 18, 44))
    d.rectangle([x, base, x + w, y + h], fill=(24, 18, 44))
    f = face(SERIF_B, 44)
    d.text((x + w - 12, y + 8), "VI", font=f, fill=(255, 255, 255),
           anchor="ra")


def art_mini(d, kind, x, y, w, h, colour):
    """Small banner picture for a feature card."""
    d.rectangle([x, y, x + w, y + h], fill=colour)
    cx, cy = x + w // 2, y + h // 2
    white = (255, 255, 255)
    if kind == "bridge":
        d.arc([x + 8, y - 18, x + w - 8, y + h + 6], 180, 360, fill=white,
              width=3)
        d.line([x + 6, y + h - 8, x + w - 6, y + h - 8], fill=white, width=3)
        for px in (x + w // 4, x + w // 2, x + 3 * w // 4):
            d.line([px, y + 8, px, y + h - 8], fill=white, width=2)
    elif kind == "globe":
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], outline=white, width=3)
        d.line([cx - 16, cy, cx + 16, cy], fill=white, width=2)
        d.arc([cx - 8, cy - 16, cx + 8, cy + 16], 90, 270, fill=white, width=2)
    elif kind == "spiral":
        for r in (18, 13, 8):
            d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=white,
                  width=3)
    elif kind == "rocket":
        d.polygon([(cx, y + 6), (cx + 8, cy + 6), (cx, y + h - 8),
                   (cx - 8, cy + 6)], fill=white)
    elif kind == "flag":
        d.line([x + 14, y + 6, x + 14, y + h - 6], fill=white, width=3)
        d.polygon([(x + 14, y + 6), (x + w - 12, y + 12), (x + 14, y + 20)],
                  fill=white)
    elif kind == "vote":
        f = face(SANS_B, 20)
        d.text((cx, cy - 12), "109–0", font=f, fill=white, anchor="ma")
    elif kind == "gavel":
        d.line([x + 10, y + h - 10, x + w - 10, y + 10], fill=white, width=4)
        d.rectangle([cx - 14, cy - 8, cx + 14, cy + 2], fill=white)
    elif kind == "calendar":
        d.rectangle([x + 12, y + 8, x + w - 12, y + h - 8], outline=white,
                    width=2)
        d.line([x + 12, y + 16, x + w - 12, y + 16], fill=white, width=2)
        for i in range(3):
            d.rectangle([x + 18 + i * 12, y + 22, x + 26 + i * 12, y + 30],
                        fill=white)
    elif kind == "chart":
        d.line([(x + 8, y + h - 12), (x + w // 3, y + 18),
                (x + 2 * w // 3, y + 26), (x + w - 8, y + 8)],
               fill=white, width=3)
        d.polygon([(x + w - 14, y + 4), (x + w - 6, y + 8), (x + w - 14, y + 12)],
                  fill=white)
    elif kind == "bars":
        for i, bh in enumerate([14, 22, 30]):
            bx = x + 14 + i * 18
            d.rectangle([bx, y + h - 8 - bh, bx + 12, y + h - 8], fill=white)


ART = {"summit": art_summit, "court": art_court, "sunset": art_sunset}


def region_counts(data):
    counts = {name: 0 for name, _ in REGIONS}
    for s in data["leads"] + data["features"] + data["briefs"]:
        counts[s["region"]] += 1
    return counts


def measure(d, data, p):
    """Return total page height needed for size preset p, or None."""
    lead_art, feat_art, brief_lead = p
    y = 14 + 14 + 4
    y += 56 + 4                      # masthead
    y += 22 + 6                      # kicker
    y += 26 + 6                      # region chips
    y += 74 + 8                      # numbers strip
    y += lead_art + 138 + 8          # leads
    y += 2 * (feat_art + 98) + 8
    y += 20 + 4                      # briefs header
    y += 12 * brief_lead + 4
    y += 56                          # footer
    return y


def render(data):
    page = Image.new("RGB", (PAGE, PAGE), CREAM)
    d = ImageDraw.Draw(page)
    counts = region_counts(data)
    total = len(data["leads"]) + len(data["features"]) + len(data["briefs"])
    assert total == 36, total

    for preset in [(96, 42, 13), (88, 38, 13), (80, 36, 12)]:
        if measure(d, data, preset) <= PAGE - 8:
            lead_art, feat_art, brief_lead = preset
            break
    else:
        sys.exit("layout does not fit even at smallest preset")

    y = 14
    # --- top line ------------------------------------------------------
    f_top = face(SANS_B, 10)
    d.text((EDGE, y), data["topline_left"], font=f_top, fill=INK)
    d.text((PAGE - EDGE, y), data["topline_right"], font=f_top, fill=INK,
           anchor="ra")
    y += 16
    d.line([(EDGE, y), (PAGE - EDGE, y)], fill=INK, width=2)
    y += 6

    # --- masthead ------------------------------------------------------
    # Shrink the title until it clears the red date badge on the right.
    # Title is centred on the page, so its half-width must clear the
    # badge whose left edge is at PAGE-EDGE-78; keep 8 px of air.
    mast_size = 46
    while True:
        f_mast = face(SERIF_B, mast_size)
        if d.textlength(data["masthead"], font=f_mast) <= 2 * (
                PAGE - EDGE - 78 - 8 - PAGE // 2):
            break
        mast_size -= 1
    d.text((PAGE // 2, y), data["masthead"], font=f_mast, fill=INK,
           anchor="ma")
    d.rounded_rectangle([PAGE - EDGE - 78, y + 4, PAGE - EDGE, y + 46],
                        radius=4, fill=RED)
    f_badge = face(SANS_B, 12)
    d.text((PAGE - EDGE - 39, y + 9), "THURSDAY", font=f_badge,
           fill=(255, 255, 255), anchor="ma")
    d.text((PAGE - EDGE - 39, y + 26), "19 NOV 2026", font=f_badge,
           fill=(255, 255, 255), anchor="ma")
    y += 56
    d.text((PAGE // 2, y), data["kicker"], font=face(SERIF_I, 15),
           fill=DARKRED, anchor="ma")
    y += 24
    d.line([(EDGE, y), (PAGE - EDGE, y)], fill=INK, width=2)
    y += 6

    # --- region chips --------------------------------------------------
    f_chip = face(SANS_B, 12)
    x = EDGE
    for name, col in REGIONS:
        label = "%s %d" % (name.upper(), counts[name])
        cw = d.textlength(label, font=f_chip) + 18
        d.rounded_rectangle([x, y, x + cw, y + 24], radius=3, fill=col)
        d.text((x + 9, y + 4), label, font=f_chip, fill=(255, 255, 255))
        x += cw + 6
    y += 30

    # --- numbers strip -------------------------------------------------
    f_big = face(SERIF_B, 27)
    f_cap = face(SANS, 10)
    cell = W // 6
    top = y
    for i, num in enumerate(data["numbers"]):
        cx = EDGE + i * cell + cell // 2
        d.text((cx, top), num["big"], font=f_big, fill=RED, anchor="ma")
        rows = wrap(d, num["cap"], f_cap, cell - 12, 3)
        cy = top + 32
        for row in rows:
            d.text((cx, cy), row, font=f_cap, fill=BODY, anchor="ma")
            cy += 12
        if i:
            d.line([(EDGE + i * cell, top + 2), (EDGE + i * cell, top + 70)],
                   fill=RULE, width=1)
    y = top + 74
    d.line([(EDGE, y), (PAGE - EDGE, y)], fill=RULE, width=1)
    y += 8

    # --- lead cards ----------------------------------------------------
    f_lead_k = face(SANS_B, 10)
    f_lead_h = face(SANS_B, 18)
    f_lead_s = face(SANS, 12)
    gap = 10
    cw = (W - 2 * gap) // 3
    lead_top = y
    for i, s in enumerate(data["leads"]):
        x0 = EDGE + i * (cw + gap)
        d.rectangle([x0, y, x0 + cw, y + lead_art + 138], outline=RULE,
                    width=1, fill=CARD)
        ART[s["art"]](d, x0 + 1, y + 1, cw - 2, lead_art)
        cy = y + lead_art + 8
        d.text((x0 + 10, cy), s["place"], font=f_lead_k,
               fill=REGION_COLOUR[s["region"]])
        d.text((x0 + cw - 10, cy), str(s["n"]), font=f_lead_k, fill=RED,
               anchor="ra")
        cy += 14
        for row in wrap(d, s["headline"], f_lead_h, cw - 20, 3):
            d.text((x0 + 10, cy), row, font=f_lead_h, fill=INK)
            cy += 22
        for row in wrap(d, s["summary"], f_lead_s, cw - 20, 3):
            d.text((x0 + 10, cy), row, font=f_lead_s, fill=BODY)
            cy += 16
    y = lead_top + lead_art + 138 + 8

    # --- feature cards -------------------------------------------------
    f_f_k = face(SANS_B, 9)
    f_f_h = face(SANS_B, 13)
    f_f_s = face(SANS, 10)
    fgap = 8
    fw = (W - 4 * fgap) // 5
    frow_h = feat_art + 98
    for r in range(2):
        for c in range(5):
            s = data["features"][r * 5 + c]
            x0 = EDGE + c * (fw + fgap)
            y0 = y + r * (frow_h + fgap)
            d.rectangle([x0, y0, x0 + fw, y0 + frow_h], outline=RULE,
                        width=1, fill=CARD)
            art_mini(d, s["art"], x0 + 1, y0 + 1, fw - 2, feat_art,
                     REGION_COLOUR[s["region"]])
            cy = y0 + feat_art + 6
            d.text((x0 + 8, cy), s["place"], font=f_f_k,
                   fill=REGION_COLOUR[s["region"]])
            d.text((x0 + fw - 8, cy), str(s["n"]), font=f_f_k, fill=RED,
                   anchor="ra")
            cy += 13
            for row in wrap(d, s["headline"], f_f_h, fw - 16, 3):
                d.text((x0 + 8, cy), row, font=f_f_h, fill=INK)
                cy += 16
            for row in wrap(d, s["summary"], f_f_s, fw - 16, 2):
                d.text((x0 + 8, cy), row, font=f_f_s, fill=BODY)
                cy += 13
    y += 2 * frow_h + fgap + 8

    # --- briefs --------------------------------------------------------
    f_bh = face(SANS_B, 12)
    d.text((EDGE, y), "ALSO ON THURSDAY 19 NOVEMBER — 23 MORE STORIES",
           font=f_bh, fill=INK)
    d.text((PAGE - EDGE, y), "place · what happened · source", font=f_bh,
           fill=FAINT, anchor="ra")
    y += 20
    d.line([(EDGE, y), (PAGE - EDGE, y)], fill=INK, width=2)
    y += 4
    f_b = face(SANS, 11)
    f_bb = face(SANS_B, 11)
    col_w = (W - 24) // 2
    half = (len(data["briefs"]) + 1) // 2
    for col, group in enumerate((data["briefs"][:half],
                                 data["briefs"][half:])):
        x0 = EDGE + col * (col_w + 24)
        cy = y
        for b in group:
            d.text((x0, cy), "■ ", font=f_b, fill=RED)
            bx = x0 + 12
            d.text((bx, cy), b["place"] + " — ", font=f_bb, fill=INK)
            off = d.textlength(b["place"] + " — ", font=f_bb)
            line = b["text"] + "  (" + b["source"] + ")"
            rows = wrap(d, line, f_b, col_w - 12 - off, 2)
            ry = cy
            for j, row in enumerate(rows):
                if j == 0:
                    d.text((bx + off, ry), row, font=f_b, fill=BODY)
                else:
                    d.text((bx, ry), row, font=f_b, fill=BODY)
                ry += brief_lead
            cy += max(brief_lead, len(rows) * brief_lead)
        if col == 0:
            left_end = cy
    y = max(left_end, cy) + 6

    # --- footer --------------------------------------------------------
    d.line([(EDGE, y), (PAGE - EDGE, y)], fill=INK, width=2)
    y += 6
    f_foot = face(SANS, 9)
    for row in wrap(d, data["date_check"], f_foot, W, 2):
        d.text((EDGE, y), row, font=f_foot, fill=BODY)
        y += 12
    for row in wrap(d, data["sources"], f_foot, W, 2):
        d.text((EDGE, y + 2), row, font=f_foot, fill=FAINT)
        y += 12
    if y > PAGE - 4:
        sys.exit("footer overflows the page bottom (y=%d)" % y)
    return page


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    page = render(data)
    out = os.path.join(HERE, "entry.png")
    page.save(out, "PNG", optimize=True)
    print("wrote %s (%dx%d, %d bytes)"
          % (out, page.width, page.height, os.path.getsize(out)))


if __name__ == "__main__":
    main()
