#!/usr/bin/env python3
"""Draw entry.png (1024x1024) for make.fun news-image-20261119.

Reads stories.json beside this script and lays out a one-page newspaper
front page: serif masthead, subtitle, a large red date line, then seven
stories, each with a dark tag chip, a bold one-line headline and a
two-line summary. Before drawing anything, every story is measured with
the real fonts and the headline/summary sizes are stepped down until
the whole block fits between the date rule and the footer, so no two
text lines can ever overlap. Pillow + stdlib only.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
CANVAS = (1024, 1024)

PAPER = (250, 247, 238)
INK = (18, 18, 18)
BODY = (52, 50, 46)
RED = (168, 32, 26)
GREY = (90, 86, 78)
RULE = (150, 145, 132)
CHIP = (18, 18, 18)
CHIP_TEXT = (250, 247, 238)
NUMERAL = (36, 68, 120)

FONTS = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_BOLD = "DejaVuSans-Bold.ttf"

MARGIN = 46
SOURCES_LINE = ("Sources: Reuters  ·  BBC  ·  Polygon  ·  Federal Reserve  ·  "
                "TechCrunch  ·  IMD  ·  PIB India")


def load(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def flow_text(draw, text, font, width, limit):
    """Greedy word wrap, capped at `limit` lines with an ellipsis tail."""
    rows = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            rows.append(current)
            current = word
    if current:
        rows.append(current)
    if len(rows) > limit:
        rows = rows[:limit]
        while rows and draw.textlength(rows[-1] + " ...", font=font) > width:
            rows[-1] = rows[-1].rsplit(" ", 1)[0]
        rows[-1] = rows[-1] + " ..."
    return rows


def lay_out(draw, stories, head_font, sum_font, width):
    """Measure every story; return (per-story rows, total height)."""
    total = 0
    laid = []
    for story in stories:
        head_rows = flow_text(draw, story["headline"], head_font, width, 1)
        sum_rows = flow_text(draw, story["summary"], sum_font, width, 2)
        laid.append((head_rows, sum_rows))
        block = (24 + 4                       # tag chip + gap
                 + len(head_rows) * (head_font.size + 4)
                 + len(sum_rows) * (sum_font.size + 5)
                 + 6)                         # breathing room + divider
        total += block
    return laid, total


def main():
    with open(os.path.join(BASE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)

    page = Image.new("RGB", CANVAS, PAPER)
    draw = ImageDraw.Draw(page)

    masthead_font = load(SERIF_BOLD, 56)
    subtitle_font = load(SANS, 22)
    date_font = load(SANS_BOLD, 40)
    chip_font = load(SANS_BOLD, 16)
    numeral_font = load(SANS_BOLD, 22)
    footer_font = load(SANS, 15)

    left = MARGIN
    right = CANVAS[0] - MARGIN
    text_w = right - left

    # --- Masthead + date -------------------------------------------------
    y = 22
    draw.text((CANVAS[0] // 2, y), data["title"], font=masthead_font,
              fill=INK, anchor="ma")
    y += 68
    draw.text((CANVAS[0] // 2, y), data["subtitle"], font=subtitle_font,
              fill=GREY, anchor="ma")
    y += 36
    draw.line([(left, y), (right, y)], fill=INK, width=3)
    y += 10
    draw.text((CANVAS[0] // 2, y), data["date_label"], font=date_font,
              fill=RED, anchor="ma")
    y += 54
    draw.line([(left, y), (right, y)], fill=INK, width=3)
    y += 16

    stories_top = y
    footer_rule_y = CANVAS[1] - 70
    room = footer_rule_y - stories_top

    # --- Pick the largest headline/summary sizes that still fit ---------
    head_size, sum_size = 24, 17
    while True:
        head_font = load(SANS_BOLD, head_size)
        sum_font = load(SANS, sum_size)
        laid, needed = lay_out(draw, data["stories"], head_font, sum_font,
                               text_w)
        if needed <= room or (head_size <= 20 and sum_size <= 15):
            break
        head_size -= 1
        sum_size -= 1
    print("fit: headline=%d summary=%d needed=%d room=%d"
          % (head_size, sum_size, needed, room), file=sys.stderr)
    if needed > room:
        sys.exit("stories do not fit even at minimum font sizes")

    # --- Stories ----------------------------------------------------------
    y = stories_top
    for idx, story in enumerate(data["stories"]):
        head_rows, sum_rows = laid[idx]
        top = y

        chip_w = draw.textlength(story["tag"], font=chip_font) + 18
        draw.rounded_rectangle([left, top, left + chip_w, top + 24],
                               radius=4, fill=CHIP)
        draw.text((left + 9, top + 2), story["tag"], font=chip_font,
                  fill=CHIP_TEXT)
        draw.text((right, top + 1), str(story["n"]), font=numeral_font,
                  fill=NUMERAL, anchor="ra")

        cursor = top + 24 + 4
        for row in head_rows:
            draw.text((left, cursor), row, font=head_font, fill=INK)
            cursor += head_size + 4
        for row in sum_rows:
            draw.text((left, cursor), row, font=sum_font, fill=BODY)
            cursor += sum_size + 5

        y = cursor + 6
        if idx < len(data["stories"]) - 1:
            draw.line([(left, y - 3), (right, y - 3)], fill=RULE, width=1)

    # --- Footer -----------------------------------------------------------
    draw.line([(left, footer_rule_y), (right, footer_rule_y)],
              fill=INK, width=2)
    foot_rows = flow_text(draw, data["footer"], footer_font, text_w, 2)
    fy = footer_rule_y + 8
    for row in foot_rows:
        draw.text((CANVAS[0] // 2, fy), row, font=footer_font, fill=GREY,
                  anchor="ma")
        fy += 19
    draw.text((CANVAS[0] // 2, fy + 2), SOURCES_LINE, font=footer_font,
              fill=GREY, anchor="ma")

    out_path = os.path.join(BASE, "entry.png")
    page.save(out_path, "PNG", optimize=True)
    print("wrote %s (%d bytes)" % (out_path, os.path.getsize(out_path)))


if __name__ == "__main__":
    main()
