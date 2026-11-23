#!/usr/bin/env python3
"""Render 22 November 2026's world news as one 1024x1024 front-page image.

Reads news.json next to this script and writes /output/entry.png
(or $MAKEFUN_OUTPUT_PATH). Deterministic: fixed geometry, fixed fonts,
no clock, no randomness, no network. Each story card carries a picture
panel drawn procedurally with Pillow (no image assets) above its tag,
headline and summary. If Pillow cannot be imported, the bundled
entry.png is copied to the output path instead.

The six stories are a mixed set — climate, conflict, politics, power,
space and sport — with only one war story, per the reader's request.
"""

import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.environ.get("MAKEFUN_OUTPUT_PATH") or "/output/entry.png"

W, H = 1024, 1024
PAGE_BG = (14, 26, 43)
CARD_BG = (22, 39, 62)
CARD_LINE = (42, 63, 92)
CREAM = (242, 232, 201)
GOLD = (201, 168, 106)
HEADLINE = (242, 237, 227)
SUMMARY = (185, 194, 207)
FOOTER = (138, 148, 164)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# One accent colour per story, in news.json order.
ACCENTS = [
    (217, 164, 65),   # COP31: gold
    (95, 168, 107),   # Bahrain: green
    (91, 141, 201),   # House: blue
    (198, 91, 78),    # Asia Power: red
    (142, 124, 195),  # Mercury: purple
    (217, 123, 63),   # Sport: orange
]


def load_font(path, size):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if not cur or draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, text, font_path, size, max_w, max_lines, min_size):
    """Shrink the font until the text fits in max_lines; return (font, lines)."""
    while size > min_size:
        font = load_font(font_path, size)
        lines = wrap(draw, text, font, max_w)
        if len(lines) <= max_lines:
            return font, lines
        size -= 1
    font = load_font(font_path, min_size)
    return font, wrap(draw, text, font, max_w)[:max_lines]


def sky(draw, x, y, w, h, top, bottom, bands=12):
    for i in range(bands):
        t = i / (bands - 1)
        c = tuple(int(top[j] + (bottom[j] - top[j]) * t) for j in range(3))
        y0 = y + i * h // bands
        y1 = y + (i + 1) * h // bands
        draw.rectangle([x, y0, x + w, y1], fill=c)


def stars(draw, x, y, points, color=(232, 236, 244)):
    for fx, fy, r in points:
        draw.ellipse([x + fx - r, y + fy - r, x + fx + r, y + fy + r], fill=color)


def scene_cop31(draw, x, y, w, h):
    """Climate summit at dusk: sun over a globe."""
    sky(draw, x, y, w, h, (58, 38, 84), (224, 120, 64))
    draw.ellipse([x + 322, y + 14, x + 388, y + 80], fill=(245, 197, 66))
    draw.ellipse([x + 334, y + 26, x + 376, y + 68], fill=(250, 214, 110))
    # globe
    cx, cy, r = x + 96, y + 58, 42
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(46, 111, 176))
    draw.ellipse([cx - 26, cy - 26, cx + 4, cy - 6], fill=(62, 155, 79))
    draw.ellipse([cx + 2, cy + 6, cx + 30, cy + 26], fill=(62, 155, 79))
    draw.ellipse([cx - 20, cy + 14, cx - 2, cy + 30], fill=(62, 155, 79))
    draw.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(214, 228, 240), width=2)
    # ground silhouette
    draw.rectangle([x, y + 92, x + w, y + h], fill=(36, 26, 51))
    for bx in (180, 205, 232, 258, 286, 312):
        bh = 8 + (bx % 3) * 4
        draw.rectangle([x + bx, y + 92 - bh, x + bx + 14, y + 92], fill=(36, 26, 51))


def scene_bahrain(draw, x, y, w, h):
    """Coastal refinery at night, flare burning, tankers in the Gulf."""
    sky(draw, x, y, w, h, (10, 16, 32), (24, 34, 60))
    # crescent moon
    draw.ellipse([x + 396, y + 10, x + 428, y + 42], fill=(232, 228, 210))
    draw.ellipse([x + 406, y + 6, x + 438, y + 38], fill=(24, 34, 60))
    # shore, then a strip of sea along the bottom
    draw.rectangle([x, y + 94, x + w, y + 100], fill=(10, 18, 32))
    draw.rectangle([x, y + 100, x + w, y + h], fill=(14, 32, 52))
    # distillation towers
    draw.polygon([(x + 80, y + 26), (x + 95, y + 12), (x + 110, y + 26)],
                 fill=(30, 42, 58))
    draw.rectangle([x + 80, y + 26, x + 110, y + 94], fill=(30, 42, 58))
    draw.rectangle([x + 130, y + 40, x + 152, y + 94], fill=(30, 42, 58))
    draw.polygon([(x + 130, y + 40), (x + 141, y + 30), (x + 152, y + 40)],
                 fill=(30, 42, 58))
    for wy in (48, 62, 76):
        draw.rectangle([x + 86, y + wy, x + 92, y + wy + 4], fill=(232, 163, 61))
    # storage tanks
    draw.rounded_rectangle([x + 180, y + 66, x + 240, y + 94], radius=6, fill=(36, 52, 74))
    draw.rounded_rectangle([x + 258, y + 70, x + 308, y + 94], radius=6, fill=(36, 52, 74))
    draw.line([x + 180, y + 70, x + 240, y + 70], fill=(90, 110, 132), width=2)
    draw.line([x + 258, y + 74, x + 308, y + 74], fill=(90, 110, 132), width=2)
    # flare stack with flame
    draw.rectangle([x + 348, y + 30, x + 356, y + 94], fill=(30, 42, 58))
    draw.polygon([(x + 342, y + 30), (x + 352, y + 4), (x + 362, y + 30)],
                 fill=(240, 138, 36))
    draw.polygon([(x + 347, y + 30), (x + 352, y + 14), (x + 357, y + 30)],
                 fill=(245, 197, 66))
    draw.ellipse([x + 347, y + 18, x + 357, y + 28], fill=(245, 197, 66))
    # pipe run and smoke
    draw.line([x + 110, y + 88, x + 348, y + 88], fill=(52, 66, 86), width=3)
    draw.ellipse([x + 118, y + 22, x + 132, y + 36], fill=(120, 124, 130))
    draw.ellipse([x + 128, y + 12, x + 140, y + 24], fill=(136, 140, 146))
    # two tanker silhouettes on the sea, light slate so they read
    for tx in (24, 368):
        draw.polygon([(x + tx, y + 97), (x + tx + 52, y + 97),
                      (x + tx + 46, y + 107), (x + tx + 6, y + 107)],
                     fill=(58, 76, 98))
        draw.line([x + tx, y + 97, x + tx + 52, y + 97],
                  fill=(140, 160, 180), width=1)
        draw.rectangle([x + tx + 34, y + 90, x + tx + 44, y + 97],
                       fill=(58, 76, 98))
        draw.ellipse([x + tx + 37, y + 87, x + tx + 41, y + 91],
                     fill=(232, 163, 61))
        draw.line([x + tx - 12, y + 105, x + tx + 2, y + 105],
                  fill=(90, 120, 150), width=1)
    for wx in (120, 200, 280):
        draw.line([x + wx, y + 104, x + wx + 18, y + 104],
                  fill=(90, 120, 150), width=1)


def scene_capitol(draw, x, y, w, h):
    """US Capitol dome under stars."""
    sky(draw, x, y, w, h, (18, 38, 74), (38, 72, 120))
    stars(draw, x, y, [(40, 16, 2), (110, 28, 1), (180, 12, 2), (300, 20, 1),
                       (370, 14, 2), (420, 30, 1), (70, 44, 1), (250, 8, 1)], (232, 236, 244))
    draw.rectangle([x, y + 96, x + w, y + h], fill=(18, 32, 58))
    draw.line([x, y + 96, x + w, y + 96], fill=(60, 80, 110), width=2)
    # dome
    draw.pieslice([x + 186, y + 4, x + 264, y + 64], 180, 360, fill=(242, 238, 226))
    draw.rectangle([x + 196, y + 28, x + 254, y + 54], fill=(242, 238, 226))
    draw.rectangle([x + 221, y - 2, x + 229, y + 8], fill=(242, 238, 226))
    draw.ellipse([x + 220, y - 4, x + 230, y + 6], fill=(242, 238, 226))
    # entablature, columns, base
    draw.rectangle([x + 150, y + 52, x + 300, y + 60], fill=(232, 228, 216))
    for col in range(5):
        cx0 = x + 162 + col * 26
        draw.rectangle([cx0, y + 60, cx0 + 8, y + 88], fill=(232, 228, 216))
    draw.rectangle([x + 150, y + 88, x + 300, y + 96], fill=(232, 228, 216))


def scene_chart(draw, x, y, w, h):
    """Asia Power Index: two bars, US 78.9 ahead of China 73.6."""
    draw.rectangle([x, y, x + w, y + h], fill=(16, 26, 44))
    label_font = load_font(SANS_BOLD, 11)
    # axis and gridlines
    draw.line([x + 44, y + 16, x + 44, y + 94], fill=(60, 76, 100), width=2)
    draw.line([x + 44, y + 94, x + w - 12, y + 94], fill=(60, 76, 100), width=2)
    for gy in (34, 54, 74):
        draw.line([x + 44, y + gy, x + w - 12, y + gy], fill=(34, 48, 68), width=1)
    # dotted trend line sloping gently down
    for dx in range(60, 400, 14):
        ty = 30 + (dx - 60) * 8 // 340
        draw.line([x + dx, y + ty, x + dx + 7, y + ty], fill=(201, 168, 106), width=2)
    # bars: 78.9 -> 63px, 73.6 -> 59px
    num_font = load_font(SANS_BOLD, 15)
    name_font = load_font(SANS_BOLD, 12)
    draw.rectangle([x + 150, y + 31, x + 205, y + 94], fill=(70, 110, 180))
    draw.rectangle([x + 150, y + 31, x + 205, y + 37], fill=(110, 150, 210))
    draw.rectangle([x + 255, y + 35, x + 310, y + 94], fill=(198, 91, 78))
    draw.rectangle([x + 255, y + 35, x + 310, y + 41], fill=(224, 130, 116))
    for bx, val, name in ((150, "78.9", "US"), (255, "73.6", "CN")):
        vw = draw.textlength(val, font=num_font)
        draw.text((x + bx + (55 - vw) / 2, y + 12), val, font=num_font,
                  fill=(242, 237, 227))
        nw = draw.textlength(name, font=name_font)
        draw.text((x + bx + (55 - nw) / 2, y + 96), name, font=name_font,
                  fill=(185, 194, 207))
    draw.text((x + 330, y + 60), "gap 5.3", font=label_font, fill=(201, 168, 106))


def scene_mercury(draw, x, y, w, h):
    """BepiColombo approaching cratered Mercury."""
    draw.rectangle([x, y, x + w, y + h], fill=(5, 7, 13))
    stars(draw, x, y, [(24, 16, 2), (70, 30, 1), (150, 12, 2), (200, 26, 1),
                       (260, 14, 2), (330, 22, 1), (390, 12, 2), (420, 44, 1),
                       (40, 60, 1), (180, 84, 1), (300, 84, 1), (240, 92, 2)], (235, 238, 245))
    # Mercury disc with craters
    cx, cy, r = x + 108, y + 55, 44
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(185, 138, 90))
    draw.pieslice([cx - r, cy - r, cx + r, cy + r], 270, 90, fill=(156, 116, 72))
    for ccx, ccy, cr in ((cx - 18, cy - 14, 8), (cx + 10, cy - 20, 6),
                         (cx + 18, cy + 8, 9), (cx - 6, cy + 16, 6),
                         (cx - 26, cy + 6, 5), (cx + 2, cy - 2, 4)):
        draw.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], fill=(138, 106, 68))
    # trajectory dashes toward the planet
    for start in (300, 316, 332, 348):
        draw.arc([x + 180, y - 14, x + 380, y + 110], start, start + 12,
                 fill=(107, 124, 147), width=2)
    # spacecraft: body, solar panels, thruster glow
    draw.ellipse([x + 292, y + 30, x + 316, y + 54], fill=(240, 138, 36))
    draw.rectangle([x + 296, y + 34, x + 312, y + 48], fill=(200, 204, 212))
    draw.rectangle([x + 266, y + 37, x + 294, y + 45], fill=(46, 95, 163))
    draw.rectangle([x + 314, y + 37, x + 342, y + 45], fill=(46, 95, 163))
    draw.line([x + 280, y + 37, x + 280, y + 45], fill=(120, 160, 210), width=1)
    draw.line([x + 328, y + 37, x + 328, y + 45], fill=(120, 160, 210), width=1)


def scene_sports(draw, x, y, w, h):
    """Tennis on the left, motorsport on the right."""
    mid = x + w // 2
    # --- tennis half: green court, blue playing area, net, ball, trophy
    draw.rectangle([x, y, mid, y + h], fill=(38, 96, 62))
    draw.rectangle([x + 18, y + 16, mid - 18, y + 92], fill=(52, 110, 168))
    draw.rectangle([x + 18, y + 16, mid - 18, y + 92], outline=(240, 240, 240), width=2)
    draw.line([x + 18, y + 54, mid - 18, y + 54], fill=(240, 240, 240), width=2)
    # net: vertical white band with mesh ticks
    draw.rectangle([x + 104, y + 16, x + 120, y + 92], fill=(232, 232, 228))
    for ny in range(20, 92, 8):
        draw.line([x + 104, y + ny, x + 120, y + ny], fill=(160, 160, 156), width=1)
    draw.line([x + 104, y + 16, x + 120, y + 16], fill=(242, 242, 238), width=3)
    # tennis ball
    draw.ellipse([x + 168, y + 24, x + 186, y + 42], fill=(214, 226, 63))
    draw.arc([x + 168, y + 24, x + 186, y + 42], 300, 60, fill=(255, 255, 255), width=2)
    # small gold trophy, bottom left of the court
    draw.polygon([(x + 30, y + 66), (x + 52, y + 66), (x + 48, y + 80),
                  (x + 34, y + 80)], fill=(232, 183, 70))
    draw.arc([x + 24, y + 66, x + 34, y + 78], 90, 270, fill=(232, 183, 70), width=2)
    draw.arc([x + 48, y + 66, x + 58, y + 78], 270, 90, fill=(232, 183, 70), width=2)
    draw.rectangle([x + 38, y + 80, x + 44, y + 88], fill=(232, 183, 70))
    draw.rectangle([x + 30, y + 88, x + 52, y + 92], fill=(232, 183, 70))
    # --- motorsport half: asphalt, track curve, checkered flag, bike
    draw.rectangle([mid, y, x + w, y + h], fill=(28, 28, 34))
    draw.arc([mid + 10, y - 40, x + w + 60, y + 120], 40, 130,
             fill=(200, 200, 205), width=6)
    draw.arc([mid + 10, y - 40, x + w + 60, y + 120], 40, 130,
             fill=(120, 120, 125), width=2)
    # checkered flag on a pole, top right
    fx, fy = x + w - 78, y + 10
    draw.line([fx, fy + 4, fx, fy + 40], fill=(220, 220, 220), width=3)
    for r in range(3):
        for c in range(4):
            fill = (20, 20, 20) if (r + c) % 2 == 0 else (240, 240, 240)
            draw.rectangle([fx + 2 + c * 9, fy + r * 9, fx + 11 + c * 9, fy + 9 + r * 9],
                           fill=fill)
    # motorcycle silhouette: two wheels, frame, rider hint
    wx1, wx2, wy = mid + 48, mid + 108, y + 78
    draw.ellipse([wx1 - 11, wy - 11, wx1 + 11, wy + 11], outline=(210, 210, 215), width=3)
    draw.ellipse([wx2 - 11, wy - 11, wx2 + 11, wy + 11], outline=(210, 210, 215), width=3)
    draw.line([wx1, wy, mid + 78, wy - 16], fill=(210, 210, 215), width=3)
    draw.line([mid + 78, wy - 16, wx2, wy], fill=(210, 210, 215), width=3)
    draw.line([mid + 78, wy - 16, mid + 66, wy - 26], fill=(210, 210, 215), width=3)
    draw.line([mid + 66, wy - 26, mid + 92, wy - 22], fill=(210, 210, 215), width=3)
    draw.ellipse([mid + 88, wy - 34, mid + 100, wy - 22], fill=(240, 138, 36))
    # speed lines behind the bike
    for sx in (mid + 8, mid + 18, mid + 28):
        draw.line([sx, wy + 4, sx + 16, wy + 4], fill=(140, 140, 148), width=2)
    # divider between the two halves
    draw.line([mid, y, mid, y + h], fill=(120, 128, 140), width=2)


SCENES = [scene_cop31, scene_bahrain, scene_capitol,
          scene_chart, scene_mercury, scene_sports]


def render():
    from PIL import Image, ImageDraw

    with open(os.path.join(HERE, "news.json"), encoding="utf-8") as f:
        data = json.load(f)

    img = Image.new("RGB", (W, H), PAGE_BG)
    draw = ImageDraw.Draw(img)

    # masthead
    title_font = load_font(SERIF_BOLD, 44)
    title = data["title"]
    tw = draw.textlength(title, font=title_font)
    draw.text(((W - tw) / 2, 26), title, font=title_font, fill=CREAM)
    sub_font = load_font(SANS, 16)
    sub = data["subtitle"]
    sw = draw.textlength(sub, font=sub_font)
    draw.text(((W - sw) / 2, 88), sub, font=sub_font, fill=GOLD)
    draw.line([36, 120, W - 36, 120], fill=GOLD, width=2)

    # 2x3 grid of cards
    margin, gutter_x, gutter_y = 36, 20, 18
    card_w = (W - 2 * margin - gutter_x) // 2
    card_h = 258
    grid_top = 138
    for i, story in enumerate(data["stories"]):
        row, col = divmod(i, 2)
        cx = margin + col * (card_w + gutter_x)
        cy = grid_top + row * (card_h + gutter_y)
        accent = ACCENTS[i % len(ACCENTS)]
        draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h],
                               radius=10, fill=CARD_BG, outline=CARD_LINE, width=1)
        # picture panel
        px, py, pw, ph = cx + 8, cy + 8, card_w - 16, 108
        panel = Image.new("RGB", (pw, ph), CARD_BG)
        pdraw = ImageDraw.Draw(panel)
        SCENES[i % len(SCENES)](pdraw, 0, 0, pw, ph)
        mask = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw, ph], radius=8, fill=255)
        img.paste(panel, (px, py), mask)
        # tag, headline, summary
        tag_font = load_font(SANS_BOLD, 13)
        draw.text((cx + 14, cy + 124), story["tag"], font=tag_font, fill=accent)
        head_font, head_lines = fit_text(draw, story["headline"], SERIF_BOLD,
                                         20, card_w - 28, 2, 16)
        hy = cy + 143
        for line in head_lines:
            draw.text((cx + 14, hy), line, font=head_font, fill=HEADLINE)
            hy += head_font.size + 4
        sum_font, sum_lines = fit_text(draw, story["summary"], SANS,
                                       14, card_w - 28, 3, 12)
        sy = hy + 4
        for line in sum_lines:
            draw.text((cx + 14, sy), line, font=sum_font, fill=SUMMARY)
            sy += sum_font.size + 4

    # footer: sources, wrapped to two centred lines
    foot_font = load_font(SANS, 12)
    foot_lines = wrap(draw, data["sources"], foot_font, W - 2 * margin)
    fy = 962
    for line in foot_lines[:2]:
        lw = draw.textlength(line, font=foot_font)
        draw.text(((W - lw) / 2, fy), line, font=foot_font, fill=FOOTER)
        fy += 16

    out_dir = os.path.dirname(OUTPUT)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    img.save(OUTPUT, "PNG")
    os.chmod(OUTPUT, 0o644)


def main():
    try:
        import PIL  # noqa: F401
    except ImportError:
        bundled = os.path.join(HERE, "entry.png")
        out_dir = os.path.dirname(OUTPUT)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        shutil.copyfile(bundled, OUTPUT)
        os.chmod(OUTPUT, 0o644)
        return 0
    render()
    return 0


if __name__ == "__main__":
    sys.exit(main())
