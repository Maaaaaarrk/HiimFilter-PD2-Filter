"""Render the filter preview grids embedded in the READMEs (run by CI after build.py).

One grid per general Hiim filter: the root Hiim filter plus the first (general) filter of each
group in PREVIEW_GROUPS. While a beta is building, the *_beta.filter is rendered since the
release file is not rebuilt. Images go to examples/render/<release file stem>.png so README
links stay stable. A style comparison (all four side by side at STYLES_LEVEL) goes to
examples/render/Hiim_Styles.png for filtergroups/HIIM_STYLES.md.
"""
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
OUT_DIR = os.path.join(ROOT_DIR, "examples", "render")
PREVIEW_GROUPS = ["hiimhyper", "hiimtalrasha", "hiimvanillaplus"]
STYLES_LEVEL = 5
STYLES_IMAGE = "examples/render/Hiim_Styles.png"

sys.path.insert(0, SCRIPT_DIR)
from filterrender.engine import Filter  # noqa: E402
import render_examples  # noqa: E402


def general_filter(defs_dir):
    """(display_name, release file, path to render) for the first filter in defs_dir."""
    with open(os.path.join(defs_dir, "filter_definitions.json"), encoding="utf-8") as f:
        entry = next(iter(json.load(f)["filter_info"].values()))
    path = os.path.join(defs_dir, entry["file_name"])
    beta = entry.get("file_name_beta")
    if beta and os.path.exists(os.path.join(defs_dir, beta)):
        path = os.path.join(defs_dir, beta)
    return entry["display_name"], entry["file_name"], path


def previews():
    """[(group dir or None for root, display_name, image path relative to ROOT_DIR, filter path)]"""
    out = []
    for group in [None] + PREVIEW_GROUPS:
        defs_dir = ROOT_DIR if group is None else os.path.join(ROOT_DIR, "filtergroups", group)
        name, release, path = general_filter(defs_dir)
        image = f"examples/render/{os.path.splitext(release)[0]}.png"
        out.append((group, name, image, path))
    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    named = []
    for _, name, image, path in previews():
        flt = Filter(path)
        named.append((name, flt))
        render_examples.render_grid(flt, os.path.join(ROOT_DIR, image), name)
        print(f"  wrote {image} from {os.path.relpath(path, ROOT_DIR)}")
    render_examples.render_styles(named, STYLES_LEVEL, os.path.join(ROOT_DIR, STYLES_IMAGE),
                                  f"Hiim styles at filter level {STYLES_LEVEL}")
    print(f"  wrote {STYLES_IMAGE}")


if __name__ == "__main__":
    main()
