"""Render illustration images of how a built filter shows sample items.

Layouts:
  grid        one image: sample items (rows) x filter levels (columns), hidden items marked
  categories  one image per item category, at a single filter level (like the old screenshots)
  sheet       one image with every category stacked, at a single filter level

Usage:
  python builderreadme/render_examples.py --filter Hiim_beta.filter --layouts grid,categories,sheet \
      --levels 1,5,8,10 --level 5 --out temp/render-mock
"""
import argparse
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from filterrender.engine import Filter  # noqa: E402
from filterrender.items import CATEGORIES  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "fonts", "Cinzel.ttf")
LABEL_SIZE = 20
LINE_GAP = 2
PAD_X, PAD_Y = 10, 4
HIDDEN_RGB = (90, 90, 90)


def fonts():
    label = ImageFont.truetype(FONT_PATH, LABEL_SIZE)
    try:
        label.set_variation_by_name("Bold")
    except Exception:
        pass
    small = ImageFont.truetype(FONT_PATH, 14)
    head = ImageFont.truetype(FONT_PATH, 22)
    try:
        head.set_variation_by_name("Bold")
    except Exception:
        pass
    return label, small, head


def ground(w, h, seed=7):
    """Deterministic dark 'ground' texture so images only change when labels do."""
    rnd = random.Random(seed)
    small = Image.new("RGB", (max(1, w // 8), max(1, h // 8)))
    px = small.load()
    for y in range(small.height):
        for x in range(small.width):
            g = rnd.randint(18, 42)
            px[x, y] = (g - 4, g + rnd.randint(0, 10), g - 8)
    return small.resize((w, h), Image.BILINEAR)


# ---- labels ------------------------------------------------------------------------------
def measure(lines, font):
    widths, height = [], 0
    for line in lines:
        w = sum(font.getlength(t) for t, _ in line)
        widths.append(w)
        height += LABEL_SIZE + LINE_GAP
    return (int(max(widths or [0])) + 2 * PAD_X, height - LINE_GAP + 2 * PAD_Y)


def draw_label(img, cx, y, lines, border, font):
    """Draw a ground label centred on cx with its top at y. Returns its height."""
    w, h = measure(lines, font)
    box = Image.new("RGBA", (w, h), (0, 0, 0, 170))
    img.paste(box, (int(cx - w / 2), y), box)
    d = ImageDraw.Draw(img)
    if border:
        d.rectangle([int(cx - w / 2), y, int(cx + w / 2) - 1, y + h - 1], outline=border, width=2)
    ty = y + PAD_Y
    for line in lines:
        lw = sum(font.getlength(t) for t, _ in line)
        x = cx - lw / 2
        for text, rgb in line:
            d.text((x + 1, ty + 1), text, font=font, fill=(0, 0, 0))
            d.text((x, ty), text, font=font, fill=rgb)
            x += font.getlength(text)
        ty += LABEL_SIZE + LINE_GAP
    return h


def hidden_lines():
    return [[("hidden", HIDDEN_RGB)]]


# ---- layouts -----------------------------------------------------------------------------
def render_grid(flt, levels, out_path, title):
    label_f, small_f, head_f = fonts()
    legend_w = 300
    rows = []  # (kind, payload)
    for cat, items in CATEGORIES:
        rows.append(("cat", cat))
        for it in items:
            cells = []
            for lvl in levels:
                lines, border, shown = flt.label(it, lvl)
                cells.append((lines, border) if shown else (hidden_lines(), None))
            rows.append(("item", (it["legend"], cells)))
    col_w = [0] * len(levels)
    for kind, p in rows:
        if kind == "item":
            for i, (lines, _) in enumerate(p[1]):
                col_w[i] = max(col_w[i], measure(lines, label_f)[0] + 24)
    col_w = [max(w, 160) for w in col_w]
    heights = []
    for kind, p in rows:
        heights.append(34 if kind == "cat" else max(measure(lines, label_f)[1] for lines, _ in p[1]) + 10)
    W = legend_w + sum(col_w) + 20
    H = 70 + sum(heights) + 20
    img = ground(W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.text((16, 12), title, font=head_f, fill=(199, 179, 119))
    x = legend_w
    for lvl, w in zip(levels, col_w):
        d.text((x + w / 2, 50), f"Filter level {lvl}", font=small_f, fill=(200, 200, 200), anchor="mm")
        x += w
    y = 70
    for (kind, p), h in zip(rows, heights):
        if kind == "cat":
            d.line([(12, y + h - 6), (W - 12, y + h - 6)], fill=(90, 80, 60), width=1)
            d.text((16, y + 6), p, font=head_f, fill=(165, 145, 105))
        else:
            legend, cells = p
            d.text((16, y + h / 2), legend, font=small_f, fill=(170, 170, 170), anchor="lm")
            x = legend_w
            for (lines, border), w in zip(cells, col_w):
                lh = measure(lines, label_f)[1]
                draw_label(img, x + w / 2, int(y + (h - lh) / 2), lines, border, label_f)
                x += w
        y += h
    img.convert("RGB").save(out_path, optimize=True)
    return [out_path]


def _stack(flt, items, level, label_f):
    labels = []
    for it in items:
        lines, border, shown = flt.label(it, level)
        if shown:
            labels.append((lines, border))
    return labels


def render_categories(flt, level, out_dir, stem, title):
    label_f, small_f, head_f = fonts()
    paths = []
    for cat, items in CATEGORIES:
        labels = _stack(flt, items, level, label_f)
        if not labels:
            continue
        W = max(measure(l, label_f)[0] for l, _ in labels) + 120
        H = 60 + sum(measure(l, label_f)[1] + 8 for l, _ in labels) + 20
        img = ground(W, H, seed=len(cat)).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.text((14, 10), f"{title} — {cat} (level {level})", font=small_f, fill=(199, 179, 119))
        y = 44
        for lines, border in labels:
            y += draw_label(img, W / 2, y, lines, border, label_f) + 8
        slug = "".join(ch if ch.isalnum() else "_" for ch in cat.lower()).strip("_")
        p = os.path.join(out_dir, f"{stem}_{slug}.png")
        img.convert("RGB").save(p, optimize=True)
        paths.append(p)
    return paths


def render_sheet(flt, level, out_path, title):
    label_f, small_f, head_f = fonts()
    blocks = [(cat, _stack(flt, items, level, label_f)) for cat, items in CATEGORIES]
    blocks = [(c, ls) for c, ls in blocks if ls]
    W = max(measure(l, label_f)[0] for _, ls in blocks for l, _ in ls) + 160
    H = 60 + sum(40 + sum(measure(l, label_f)[1] + 8 for l, _ in ls) for _, ls in blocks) + 20
    img = ground(W, H, seed=3).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.text((16, 12), f"{title} — level {level}", font=head_f, fill=(199, 179, 119))
    y = 56
    for cat, ls in blocks:
        d.text((16, y + 6), cat, font=small_f, fill=(165, 145, 105))
        d.line([(12, y + 30), (W - 12, y + 30)], fill=(90, 80, 60), width=1)
        y += 40
        for lines, border in ls:
            y += draw_label(img, W / 2, y, lines, border, label_f) + 8
    img.convert("RGB").save(out_path, optimize=True)
    return [out_path]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--filter", required=True)
    ap.add_argument("--layouts", default="grid")
    ap.add_argument("--levels", default="1,5,8,10")
    ap.add_argument("--level", type=int, default=5)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    flt = Filter(a.filter)
    stem = os.path.splitext(os.path.basename(a.filter))[0]
    title = a.title or stem
    levels = [int(x) for x in a.levels.split(",")]
    made = []
    for layout in a.layouts.split(","):
        if layout == "grid":
            made += render_grid(flt, levels, os.path.join(a.out, f"{stem}_grid.png"), title)
        elif layout == "categories":
            made += render_categories(flt, a.level, a.out, f"{stem}_cat", title)
        elif layout == "sheet":
            made += render_sheet(flt, a.level, os.path.join(a.out, f"{stem}_sheet.png"), title)
    for p in made:
        print("wrote", p)


if __name__ == "__main__":
    main()
