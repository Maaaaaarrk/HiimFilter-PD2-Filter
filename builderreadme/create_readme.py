import json
import os
import re

SCRIPT_DIR        = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR          = os.path.dirname(SCRIPT_DIR)

TEMPLATE          = os.path.join(SCRIPT_DIR, "README.md")
FILTER_LEVELS_TPL = os.path.join(SCRIPT_DIR, "filter_levels.md")
OUTPUT            = os.path.join(ROOT_DIR, "README.md")
VERSION_FILTER    = os.path.join(ROOT_DIR, "builderfilter", "01-header", "01-Version[ALL].filter")
FILTER_DEFS       = os.path.join(ROOT_DIR, "filter_definitions.json")
FILTERGROUPS_DIR  = os.path.join(ROOT_DIR, "filtergroups")
UNIQUE_TIER_FILE  = os.path.join(ROOT_DIR, "builderfilter", "02-alias", "05-unid-unique-set-stars[ALL].filter")
UNIQUE_NAME_FILE  = os.path.join(ROOT_DIR, "builderfilter", "03-unidformatting", "18-Unid_UniquesSet_Name[ALL-EXCEPT=Vanilla+OnlyFilter].filter")

UNIQUE_TIERS = [
    "4_STAR_UNIQUE",
    "4_STAR_NO_ETH_UNIQUE",
    "4_STAR_ETH_UNIQUE",
    "3_STAR_UNIQUE",
    "3_STAR_NO_ETH_UNIQUE",
    "2_STAR_UNIQUE",
    "1_STAR_UNIQUE",
    "0_STAR_UNIQUE",
    "NO_STAR_UNIQUE",
]


def parse_unique_tier_lists(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    result = {}
    for tier in UNIQUE_TIERS:
        m = re.search(rf"^Alias\[{tier}\]:\s*\(([^)]+)\)", text, re.MULTILINE)
        if not m:
            continue
        codes = [c.strip() for c in re.split(r"\s+OR\s+", m.group(1), flags=re.IGNORECASE) if c.strip()]
        result[tier] = codes
    return result


def parse_unique_names(path):
    """Return dict: base_code -> friendly unique name (stripped of ' - <base>' suffix)."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    # Manual overrides for entries with malformed data or no entry in the source file
    out = {
        "9wc":  "Grim's Burning Dead",
        "aqv2": "Exceptional Arrows",
        "aqv3": "Elite Arrows",
        "cqv2": "Exceptional Bolts",
        "cqv3": "Elite Bolts",
        "utu":  "The Gladiator's Bane",
    }
    # Match base code (first \S after !ID) followed by any number of extra conditions
    pattern = re.compile(
        r"^ItemDisplay\[UNI\s+!ID\s+([a-z0-9]+)\b[^\]]*\]:\s*%CONTINUE%(.+)$",
        re.MULTILINE,
    )
    for m in pattern.finditer(text):
        base, raw = m.group(1), m.group(2)
        if "(No Unique" in raw:
            continue
        # First-match-wins: don't overwrite manual overrides, and don't overwrite
        # the broader (non-ETH-conditional) entry with a narrower ETH-only one.
        if base in out:
            continue
        # Strip the `// <base>` or ` - <base>` suffix. Some unique names contain
        # hyphens (Bartuc's Cut-Throat, Buriza-Do Kyanon, Que-Hegans), so split on
        # the LAST ` - ` not the first.
        cleaned = re.sub(r"//.*$", "", raw).rstrip()
        last_sep = cleaned.rfind(" - ")
        if last_sep >= 0:
            cleaned = cleaned[:last_sep]
        cleaned = cleaned.strip()
        if cleaned:
            out[base] = cleaned
    return out


def lookup_names(codes, name_map, suffix=""):
    """Resolve base codes to display names, sorted alphabetically."""
    items = []
    for c in codes:
        items.append(f"{name_map.get(c, c)}{suffix}")
    return sorted(items, key=str.lower)


def build_uniques_by_level_section():
    tiers = parse_unique_tier_lists(UNIQUE_TIER_FILE)
    names = parse_unique_names(UNIQUE_NAME_FILE)

    four_any   = lookup_names(tiers.get("4_STAR_UNIQUE", []), names)
    four_eth   = lookup_names(tiers.get("4_STAR_ETH_UNIQUE", []), names, " (ETH only)")
    four_noeth = lookup_names(tiers.get("4_STAR_NO_ETH_UNIQUE", []), names, " (non-ETH only)")
    three_any  = lookup_names(tiers.get("3_STAR_UNIQUE", []), names)
    three_noeth = lookup_names(tiers.get("3_STAR_NO_ETH_UNIQUE", []), names, " (non-ETH only)")
    two_star   = lookup_names(tiers.get("2_STAR_UNIQUE", []), names)
    one_star   = lookup_names(tiers.get("1_STAR_UNIQUE", []), names)
    zero_star  = lookup_names(tiers.get("0_STAR_UNIQUE", []), names)
    no_star    = lookup_names(tiers.get("NO_STAR_UNIQUE", []), names)

    four_all  = sorted(four_any + four_eth + four_noeth, key=str.lower)
    three_all = sorted(three_any + three_noeth, key=str.lower)

    lines = []
    lines.append("## Uniques Shown by Filter Level")
    lines.append("")
    lines.append(
        "Cumulative list of unidentified uniques visible at each filter level. "
        "Higher (stricter) levels show fewer items; each block below adds **new** items "
        "not already listed in the level above."
    )
    lines.append("")
    lines.append("### Level 11 — most strict")
    lines.append("")
    lines.append("*None.* All unidentified uniques outside town are hidden.")
    lines.append("")
    lines.append("### Level 10–9 — 4-star uniques")
    lines.append("")
    lines.append(", ".join(four_all) if four_all else "*(none defined)*")
    lines.append("")
    lines.append("### Level 8 — adds 3-star uniques")
    lines.append("")
    lines.append(", ".join(three_all) if three_all else "*(none defined)*")
    lines.append("")
    lines.append("### Level 7 — adds 2-star, 1-star, and 0-star uniques")
    lines.append("")
    if two_star:
        lines.append("**2-star:** " + ", ".join(two_star))
        lines.append("")
    if one_star:
        lines.append("**1-star:** " + ", ".join(one_star))
        lines.append("")
    if zero_star:
        lines.append("**0-star:** " + ", ".join(zero_star))
        lines.append("")
    lines.append("### Level 6 and below — adds NO-star uniques")
    lines.append("")
    lines.append(", ".join(no_star) if no_star else "*(none defined)*")
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


def write_bucket_readme(bucket_dir, version_str, filter_levels):
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
                write_bucket_readme(sub, version_str, filter_levels)


if __name__ == "__main__":
    main()
