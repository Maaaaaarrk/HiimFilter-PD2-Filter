"""Render illustration images of how a built filter shows sample items.

Layouts:
  grid        one image: sample items (rows) x filter-level ranges (columns), hidden items marked
  categories  one image per item category, at a single filter level (like the old screenshots)
  sheet       one image with every category stacked, at a single filter level

Usage:
  python builderreadme/render_examples.py --filter Hiim_beta.filter --layouts grid,categories,sheet \
      --level 5 --out temp/render-mock

The README preview grids are made by render_readme_images.py.
"""
import argparse
import json
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from filterrender.engine import Filter  # noqa: E402
from filterrender.items import categories  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "fonts", "Cinzel.ttf")
LABEL_SIZE = 20
LINE_GAP = 2
PAD_X, PAD_Y = 10, 4
HIDDEN_RGB = (90, 90, 90)
# Grid columns: the README's filter-level groups, with 1-4 split at 2. When an item looks different
# inside a range (e.g. potions shown at 3 but hidden at 4) the cell shows each variant side by side
# under a small level note.
LEVEL_RANGES = [(1, 2), (3, 4), (5, 6), (7, 7), (8, 8), (9, 10), (11, 11)]
CATS = categories()


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
    """Deterministic dark 'ground' texture so images only change when labels do. Soft, coarse
    blotches rather than fine noise keep the committed PNGs small (~1.5 MB vs ~6 MB)."""
    rnd = random.Random(seed)
    small = Image.new("RGB", (max(1, w // 48), max(1, h // 48)))
    px = small.load()
    for y in range(small.height):
        for x in range(small.width):
            g = rnd.randint(22, 36)
            px[x, y] = (g - 4, g + 4, g - 8)
    return small.resize((w, h), Image.BICUBIC)


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
def _cell(flt, it, lvl):
    lines, border, shown = flt.label(it, lvl)
    return (lines, None) if shown else (hidden_lines(), None)


def _look(lines):
    """What a player would notice: visible text and its colors, ignoring padding spaces."""
    return tuple(tuple((" ".join(t.split()), rgb) for t, rgb in line if t.strip()) for line in lines)


def _range_cell(flt, it, lo, hi):
    """[(note, lines)] for one grid cell: one entry when the item looks the same at every level
    of lo..hi, else one per run of identical levels, noted with its levels."""
    runs = []
    for lvl in range(lo, hi + 1):
        lines = _cell(flt, it, lvl)[0]
        if runs and _look(runs[-1][2]) == _look(lines):
            runs[-1][1] = lvl
        else:
            runs.append([lvl, lvl, lines])
    if len(runs) == 1:
        return [(None, runs[0][2])]
    return [(f"level {a}" if a == b else f"levels {a}-{b}", lines) for a, b, lines in runs]


NOTE_H = 16
CELL_GAP = 12


def _cell_size(cell, font):
    w = sum(measure(lines, font)[0] for _, lines in cell) + CELL_GAP * (len(cell) - 1)
    h = max(measure(lines, font)[1] for _, lines in cell) + (NOTE_H if len(cell) > 1 else 0)
    return w, h


def render_grid(flt, out_path, title):
    """Sample items (rows) x README level ranges (columns) for one filter."""
    heads = [f"Level {lo}" if lo == hi else f"Levels {lo}-{hi}" for lo, hi in LEVEL_RANGES]
    return _render_table(heads, lambda it: [_range_cell(flt, it, lo, hi) for lo, hi in LEVEL_RANGES],
                         out_path, title)


def render_styles(named_filters, level, out_path, title):
    """Sample items (rows) x filters (columns) at one filter level, to compare styles."""
    heads = [name for name, _ in named_filters]
    return _render_table(heads, lambda it: [[(None, _cell(flt, it, level)[0])] for _, flt in named_filters],
                         out_path, title)


def _render_table(heads, cells_for, out_path, title):
    label_f, small_f, head_f = fonts()
    rows = []  # (kind, payload)
    for cat, items in CATS:
        rows.append(("cat", cat))
        for it in items:
            rows.append(("item", (it["legend"], cells_for(it))))
    legend_w = int(max(small_f.getlength(p[0]) for k, p in rows if k == "item")) + 40
    col_w = [0] * len(heads)
    for kind, p in rows:
        if kind == "item":
            for i, cell in enumerate(p[1]):
                col_w[i] = max(col_w[i], _cell_size(cell, label_f)[0] + 24)
    col_w = [max(w, 160, int(small_f.getlength(hd)) + 24) for w, hd in zip(col_w, heads)]
    heights = []
    for kind, p in rows:
        heights.append(34 if kind == "cat" else max(_cell_size(c, label_f)[1] for c in p[1]) + 10)
    W = legend_w + sum(col_w) + 20
    H = 70 + sum(heights) + 20
    img = ground(W, H).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.text((16, 12), title, font=head_f, fill=(199, 179, 119))
    x = legend_w
    for head, w in zip(heads, col_w):
        d.text((x + w / 2, 50), head, font=small_f, fill=(200, 200, 200), anchor="mm")
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
            for cell, w in zip(cells, col_w):
                cw, ch = _cell_size(cell, label_f)
                cx, cy = x + (w - cw) / 2, int(y + (h - ch) / 2)
                for note, lines in cell:
                    lw = measure(lines, label_f)[0]
                    ly = cy
                    if note:
                        d.text((cx + lw / 2, cy + NOTE_H / 2), note, font=small_f, fill=(160, 150, 120), anchor="mm")
                        ly += NOTE_H
                    draw_label(img, cx + lw / 2, ly, lines, None, label_f)
                    cx += lw + CELL_GAP
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
    for cat, items in CATS:
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
    blocks = [(cat, _stack(flt, items, level, label_f)) for cat, items in CATS]
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


def display_name(filter_path):
    """The filter's display_name from the filter_definitions.json next to it (beta builds
    share their release entry), or None."""
    defs = os.path.join(os.path.dirname(os.path.abspath(filter_path)), "filter_definitions.json")
    if not os.path.exists(defs):
        return None
    fname = os.path.basename(filter_path).replace("_beta.filter", ".filter")
    with open(defs, encoding="utf-8") as f:
        info = json.load(f)["filter_info"].values()
    return next((e["display_name"] for e in info if e["file_name"] == fname), None)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--filter", required=True)
    ap.add_argument("--layouts", default="grid")
    ap.add_argument("--level", type=int, default=5)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    flt = Filter(a.filter)
    stem = os.path.splitext(os.path.basename(a.filter))[0]
    title = a.title or display_name(a.filter) or stem
    made = []
    for layout in a.layouts.split(","):
        if layout == "grid":
            made += render_grid(flt, os.path.join(a.out, f"{stem}_grid.png"), title)
        elif layout == "categories":
            made += render_categories(flt, a.level, a.out, f"{stem}_cat", title)
        elif layout == "sheet":
            made += render_sheet(flt, a.level, os.path.join(a.out, f"{stem}_sheet.png"), title)
    for p in made:
        print("wrote", p)


if __name__ == "__main__":
    main()
