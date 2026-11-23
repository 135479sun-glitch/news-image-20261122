#!/usr/bin/env python3
"""Render 22 November 2026's world news as one 1024x1024 front-page image.

Reads news.json (title, subtitle, sources and six stories) from the same
directory as this script and writes a PNG to /output/entry.png
(or $MAKEFUN_OUTPUT_PATH when set).

Layout: a masthead with the title and date line, a 2x3 grid of story
cards, and a sources footer. Deterministic by construction: fixed
geometry, fixed fonts, no clock, no randomness, no network, so two runs
produce byte-identical output.

If Pillow is not installed, the bundled entry.png sitting next to this
script is copied to the output path instead, so the entry still yields
an image.
"""

import json
import os
import shutil
import sys

try:
    from PIL import Image, ImageDraw, ImageFont

    PIL_OK = True
except ImportError:  # pragma: no cover - exercised only without Pillow
    PIL_OK = False

WIDTH = 1024
HEIGHT = 1024
MARGIN = 32
GUTTER = 24
HEADER_H = 168
FOOTER_H = 64

BG = (13, 22, 38)          # deep navy page
PANEL = (24, 40, 64)       # card face
PANEL_EDGE = (52, 74, 104)  # card border
INK = (240, 238, 230)      # near-white text
MUTED = (176, 188, 204)    # grey-blue secondary text
RULE = (212, 175, 55)      # gold rule / masthead accent

# One accent colour per card, in story order.
ACCENTS = [
    (212, 175, 55),   # gold
    (198, 66, 60),    # red
    (66, 135, 200),   # blue
    (74, 160, 110),   # green
    (146, 110, 190),  # purple
    (214, 130, 55),   # orange
]

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


def here():
    return os.path.dirname(os.path.abspath(__file__))


def output_path():
    return os.environ.get("MAKEFUN_OUTPUT_PATH", "/output/entry.png")


def load_news():
    with open(os.path.join(here(), "news.json"), encoding="utf-8") as f:
        return json.load(f)


def wrap(font, text, max_width):
    """Greedy word wrap; returns lines each no wider than max_width."""
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if font.getlength(trial) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_lines(font_path, start_size, text, max_width, max_lines, min_size=14):
    """Largest font size (shrinking to min_size) whose wrapped text fits
    in max_lines lines. Returns (font, lines); lines are truncated to
    max_lines with an ellipsis when even the smallest size overflows."""
    size = start_size
    while size > min_size:
        font = ImageFont.truetype(font_path, size)
        lines = wrap(font, text, max_width)
        if len(lines) <= max_lines:
            return font, lines
        size -= 2
    font = ImageFont.truetype(font_path, min_size)
    lines = wrap(font, text, max_width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and font.getlength(last + "…") > max_width:
            last = last.rsplit(" ", 1)[0] if " " in last else ""
        lines[-1] = last + "…" if last else "…"
    return font, lines


def line_height(font):
    return int(font.size * 1.3)


def draw_header(draw, news):
    title_font = ImageFont.truetype(SERIF_BOLD, 52)
    sub_font = ImageFont.truetype(SANS, 23)
    title = news["title"]
    tw = draw.textlength(title, font=title_font)
    draw.text(((WIDTH - tw) / 2, 30), title, font=title_font, fill=INK)
    sub = news["subtitle"]
    sw = draw.textlength(sub, font=sub_font)
    draw.text(((WIDTH - sw) / 2, 104), sub, font=sub_font, fill=MUTED)
    draw.line([(MARGIN, 150), (WIDTH - MARGIN, 150)], fill=RULE, width=3)


def draw_footer(draw, news):
    draw.line(
        [(MARGIN, HEIGHT - FOOTER_H), (WIDTH - MARGIN, HEIGHT - FOOTER_H)],
        fill=PANEL_EDGE,
        width=2,
    )
    font, lines = fit_lines(SANS, 16, news["sources"], WIDTH - 2 * MARGIN, 2, 13)
    y = HEIGHT - FOOTER_H + 12
    for line in lines:
        lw = draw.textlength(line, font=font)
        draw.text(((WIDTH - lw) / 2, y), line, font=font, fill=MUTED)
        y += line_height(font)


def draw_card(draw, box, story, accent):
    x, y, w, h = box
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10,
                           fill=PANEL, outline=PANEL_EDGE, width=2)
    # Accent bar across the top of the card.
    draw.rounded_rectangle([x + 2, y + 2, x + w - 2, y + 8], radius=3, fill=accent)
    pad = 22
    inner_w = w - 2 * pad
    cx = x + pad
    cy = y + 20
    content_bottom = y + h - 14

    tag_font = ImageFont.truetype(SANS_BOLD, 19)
    draw.text((cx, cy), story["tag"], font=tag_font, fill=accent)
    cy += line_height(tag_font) + 8

    head_font, head_lines = fit_lines(
        SANS_BOLD, 30, story["headline"], inner_w, max_lines=2, min_size=18)
    for line in head_lines:
        draw.text((cx, cy), line, font=head_font, fill=INK)
        cy += line_height(head_font)
    cy += 8

    # Whatever vertical room is left goes to the summary.
    room = content_bottom - cy
    max_summary_lines = max(2, room // line_height(
        ImageFont.truetype(SANS, 21)))
    sum_font, sum_lines = fit_lines(
        SANS, 21, story["summary"], inner_w,
        max_lines=max_summary_lines, min_size=14)
    for line in sum_lines:
        draw.text((cx, cy), line, font=sum_font, fill=MUTED)
        cy += line_height(sum_font)


def render(news):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    draw_header(draw, news)

    grid_top = HEADER_H + 8
    grid_bottom = HEIGHT - FOOTER_H - 16
    grid_w = WIDTH - 2 * MARGIN
    grid_h = grid_bottom - grid_top
    card_w = (grid_w - GUTTER) // 2
    card_h = (grid_h - 2 * GUTTER) // 3
    for i, story in enumerate(news["stories"]):
        row, col = divmod(i, 2)
        box = (
            MARGIN + col * (card_w + GUTTER),
            grid_top + row * (card_h + GUTTER),
            card_w,
            card_h,
        )
        draw_card(draw, box, story, ACCENTS[i % len(ACCENTS)])

    draw_footer(draw, news)
    return img


def fallback_copy(out):
    """No Pillow: copy the bundled entry.png to the output path."""
    src = os.path.join(here(), "entry.png")
    if not os.path.exists(src):
        raise SystemExit("Pillow is not installed and no bundled entry.png found")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    shutil.copyfile(src, out)


def main():
    out = output_path()
    if not PIL_OK:
        fallback_copy(out)
        return 0
    news = load_news()
    img = render(news)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    img.save(out, format="PNG")
    return 0


if __name__ == "__main__":
    sys.exit(main())
