import json
import os
import re
import sys

SCRIPT_DIR        = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR          = os.path.dirname(SCRIPT_DIR)

TEMPLATE          = os.path.join(SCRIPT_DIR, "README.md")
FILTER_LEVELS_TPL = os.path.join(SCRIPT_DIR, "filter_levels.md")
OUTPUT            = os.path.join(ROOT_DIR, "README.md")
VERSION_FILTER    = os.path.join(ROOT_DIR, "builderfilter", "01-header", "01-Version[ALL].filter")
FILTER_DEFS       = os.path.join(ROOT_DIR, "filter_definitions.json")
FILTERGROUPS_DIR  = os.path.join(ROOT_DIR, "filtergroups")
# Star tiers come from builderfilter/data/unique-set-tiers.json (via builderfilter/tier_aliases.py).
sys.path.insert(0, os.path.join(ROOT_DIR, "builderfilter"))
import tier_aliases  # noqa: E402

# README sections, best -> worst; each lists the uniques whose base first shows at that level.
LEVEL_SECTIONS = [
    ("4", "Level 10-9 — 4-star uniques"),
    ("3", "Level 8 — adds 3-star uniques"),
    ("2", "Level 7 — adds 2-star uniques"),
    ("1", "1-star"), ("0", "0-star"), ("no-star", "NO-star"),
]


def uniques_by_tier():
    """tier -> sorted display names. A unique is listed at its base's tier (unidentified items
    only reveal the base); when ETH and non-ETH copies differ it is listed once per variant."""
    data = tier_aliases.load()
    bases = tier_aliases.unique_code_tiers(data)
    out = {t: [] for t, _ in LEVEL_SECTIONS}
    for e in data["uniques"]:
        b = bases[e["code"]]
        label = f"{e['name']} ({e.get('base') or e['code']})"
        n, et = b["noneth"], b["eth"]
        if n == et:
            if n is not None:
                out[n].append(label)
            continue
        if n is not None:
            out[n].append(f"{label} — non-ETH")
        if et is not None:
            out[et].append(f"{label} — ETH")
    return {t: sorted(set(v), key=str.lower) for t, v in out.items()}


def build_uniques_by_level_section():
    tiers = uniques_by_tier()

    def bullets(items):
        return "\n".join(f"- {item}" for item in items) if items else "*(none defined)*"

    lines = []
    lines.append("## Uniques Shown by Filter Level")
    lines.append("")
    lines.append(
        "Cumulative list of unidentified uniques visible at each filter level. "
        "Higher (stricter) levels show fewer items; each block below adds **new** items "
        "not already listed in the level above. Unidentified uniques only reveal their base, "
        "so each unique is listed at its base's tier "
        "(source: `builderfilter/data/unique-set-tiers.json`)."
    )
    lines.append("")
    lines.append("### Level 11 — most strict")
    lines.append("")
    lines.append("*None.* All unidentified uniques outside town are hidden.")
    lines.append("")
    for tier, title in LEVEL_SECTIONS[:3]:
        lines.append(f"### {title}")
        lines.append("")
        lines.append(bullets(tiers[tier]))
        lines.append("")
    lines.append("### Level 6-5 — adds 1-star, 0-star, and NO-star uniques")
    lines.append("")
    for tier, title in LEVEL_SECTIONS[3:]:
        if tiers[tier]:
            lines.append(f"**{title}:**")
            lines.append("")
            lines.append(bullets(tiers[tier]))
            lines.append("")
    lines.append("### Level 1-4 — most permissive")
    lines.append("")
    lines.append("*All uniques are shown.*")
    lines.append("")
    return "\n".join(lines)


def get_version_string():
    with open(VERSION_FILTER, encoding="utf-8") as f:
        line = f.read().strip()
    return line.replace("%CL%", " ")


def get_filter_levels():
    with open(FILTER_LEVELS_TPL, encoding="utf-8") as f:
        return f.read().rstrip() + "\n"


def build_filters_section(defs_path):
    with open(defs_path, encoding="utf-8") as f:
        data = json.load(f)
    lines = []
    for entry in data["filter_info"].values():
        lines.append(f"* {entry['display_name']}: {entry['description']} [{entry['file_name']}]")
    return "\n".join(lines)


def write_root_readme(version_str, filter_levels, uniques_by_level):
    filters_section = build_filters_section(FILTER_DEFS)
    with open(TEMPLATE, encoding="utf-8") as f:
        content = f.read()

    content = content.replace("{{REPLACE_ME}}", version_str)
    content = content.replace("{{REPLACE_FILTERS}}", filters_section)
    content = content.replace("{{REPLACE_FILTER_LEVELS}}", filter_levels)
    content = content.replace("{{REPLACE_UNIQUES_BY_LEVEL}}", uniques_by_level)

    with open(OUTPUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"README.md written with version: {version_str}")


def write_bucket_readme(bucket_dir, version_str, filter_levels, uniques_by_level):
    defs_path = os.path.join(bucket_dir, "filter_definitions.json")
    if not os.path.exists(defs_path):
        return

    bucket_name = os.path.basename(bucket_dir)
    filters_section = build_filters_section(defs_path)
    content = (
        f"# {bucket_name}\n"
        f"## {version_str}\n"
        f"\n"
        f"## Filters\n"
        f"{filters_section}\n"
        f"\n"
        f"{filter_levels}\n"
        f"\n"
        f"{uniques_by_level}\n"
    )

    out_path = os.path.join(bucket_dir, "README.md")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"  wrote {out_path}")


def main():
    version_str       = get_version_string()
    filter_levels     = get_filter_levels()
    uniques_by_level  = build_uniques_by_level_section()

    write_root_readme(version_str, filter_levels, uniques_by_level)

    if os.path.isdir(FILTERGROUPS_DIR):
        for name in sorted(os.listdir(FILTERGROUPS_DIR)):
            sub = os.path.join(FILTERGROUPS_DIR, name)
            if os.path.isdir(sub):
                write_bucket_readme(sub, version_str, filter_levels, uniques_by_level)


if __name__ == "__main__":
    main()
