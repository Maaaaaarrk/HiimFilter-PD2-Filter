import datetime
import json
import os
import re

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR  = os.path.dirname(SCRIPT_DIR)

VERSION_TXT     = os.path.join(OUTPUT_DIR, "version.txt")
VERSION_FILTER  = os.path.join(SCRIPT_DIR, "01-header", "01-Version[ALL].filter")


def _ordinal(n):
    if 11 <= (n % 100) <= 13:
        return f"{n}th"
    return f"{n}" + {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def update_version():
    """Increment version.txt and rewrite the version header filter."""
    with open(VERSION_TXT, encoding="utf-8") as f:
        version = int(f.read().strip())

    season = "Season 13"

    today = datetime.date.today()
    date_str = f"{today.strftime('%B')} {_ordinal(today.day)}"
    with open(VERSION_FILTER, "w", encoding="utf-8") as f:
        f.write(f"Last updated {date_str}%CL%{season} - build {version}")

    print(f"Version: {season} - build {version} ({date_str})")

_LINE_COMMENT = re.compile(r"//[^\n]*")


def load_config():
    """Read filters.json. Supports JSONC-style // line comments for section markers."""
    with open(os.path.join(SCRIPT_DIR, "filters.json"), encoding="utf-8") as f:
        text = f.read()
    text = _LINE_COMMENT.sub("", text)
    data = json.loads(text)
    return data["filters"], data.get("groups", {}), data.get("beta", False)


def output_dir_for(entry):
    """Return the directory the entry's filter (and its filter_definitions.json) is written to."""
    if entry.get("filterdir"):
        return os.path.join(OUTPUT_DIR, "filtergroups", entry["filterdir"])
    return OUTPUT_DIR


def order_for_definitions(entries):
    """Sort: entries with explicit 'order' first (ascending), then alphanumeric by display_name."""
    pinned = sorted((e for e in entries if "order" in e), key=lambda e: e["order"])
    rest = sorted((e for e in entries if "order" not in e), key=lambda e: e["display_name"])
    return pinned + rest


def generate_filter_definitions(filters, beta):
    """Write filter_definitions.json into root and each filtergroups/<filterdir>."""
    by_dir = {}
    for entry in filters:
        if entry.get("hidden"):
            continue
        by_dir.setdefault(output_dir_for(entry), []).append(entry)

    for out_dir, group_entries in by_dir.items():
        defs = {"filter_info": {}}
        for idx, entry in enumerate(order_for_definitions(group_entries), start=1):
            info = {
                "display_name": entry["display_name"],
                "description": entry["description"],
                "file_name": entry["file"],
            }
            if beta:
                info["file_name_beta"] = entry["file"].replace(".filter", "_beta.filter")
            defs["filter_info"][str(idx)] = info

        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "filter_definitions.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(defs, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  wrote {out_path}")


def cleanup_beta_files(filters):
    """Delete leftover *_beta.filter files when beta is turned off."""
    for entry in filters:
        beta_file = entry["file"].replace(".filter", "_beta.filter")
        path = os.path.join(output_dir_for(entry), beta_file)
        if os.path.exists(path):
            os.remove(path)
            print(f"  removed {beta_file}")


def extract_bracket_tag(filename):
    """Return the content inside [...] in a filename, or None if absent."""
    m = re.search(r'\[([^\]]+)\]', filename)
    return m.group(1) if m else None


AUTO_HEADER_TAG = "AUTO_HEADER"


FAMILY_TAGS = ("Hiim", "Kassahi")


def auto_header_line(entry):
    """Auto-generated header line: %CL%<Brand> - TAG1 - TAG2 - ... -}%CONTINUE%

    The brand prefix is chosen by which family tag is present:
      - "HiimFilter" for entries tagged "Hiim"
      - "Kassahi"    for entries tagged "Kassahi"
    Family tags themselves are dropped from the displayed list (implied by the
    prefix), and a leading "Kassahi" is stripped from disambiguated tag names so
    "KassahiHyper" / "KassahiMystery" display as "Hyper" / "Mystery".
    """
    tags = entry["tags"]
    brand = "Kassahi" if "Kassahi" in tags else "HiimFilter"

    def _display(tag):
        if tag.startswith("Kassahi") and tag != "Kassahi":
            return tag[len("Kassahi"):]
        return tag

    visible_tags = [_display(t) for t in tags if t not in FAMILY_TAGS]
    tag_str = " - ".join(visible_tags)
    suffix = f" - {tag_str}" if tag_str else ""
    return f"%CL%{brand}{suffix} -}}%CONTINUE%\n"


def token_matches_filter(token, entry, groups):
    """Return True if a single tag token applies to the given filter entry."""
    # Expand group name to its member list
    if token in groups:
        members = groups[token]
        return entry["name"] in members or any(t in members for t in entry["tags"])
    # Direct match against filter name or tags
    return token == entry["name"] or token in entry["tags"]


def _clause_matches(clause, entry, groups):
    """Evaluate a single bracket-tag clause against a filter entry."""
    if clause == "ALL" or clause == AUTO_HEADER_TAG:
        return True

    if clause.startswith("ONLY="):
        tokens = clause[5:].split("+")
        return any(token_matches_filter(t, entry, groups) for t in tokens)

    if clause.startswith("ALL-EXCEPT="):
        tokens = clause[11:].split("+")
        return not any(token_matches_filter(t, entry, groups) for t in tokens)

    # No keyword prefix — treat as implicit ONLY (e.g. [CRAFTING+LLD])
    tokens = clause.split("+")
    return any(token_matches_filter(t, entry, groups) for t in tokens)


def source_included(bracket_tag, entry, groups):
    """Decide whether a source file should be concatenated into the given filter.

    A bracket tag may be a single clause or a comma-separated AND of clauses, e.g.
    [Hiim,ALL-EXCEPT=OnlyFilter] requires both the Hiim tag AND the not-OnlyFilter
    condition. Inside a clause, '+' remains the OR separator.
    """
    clauses = [c.strip() for c in bracket_tag.split(",")]
    return all(_clause_matches(c, entry, groups) for c in clauses)


def sorted_walk(root):
    """
    Yield file paths under root in a depth-first, alphanumerically sorted walk.
    Directories and files at each level are sorted together so that a file named
    '05-foo.filter' and a subdirectory named '05-bar/' interleave correctly.
    """
    entries = sorted(os.listdir(root))
    for name in entries:
        path = os.path.join(root, name)
        if os.path.isdir(path):
            yield from sorted_walk(path)
        elif os.path.isfile(path):
            yield path


def build_filter(entry, groups):
    parts = []
    # Iterate every subdirectory of builder2 in sorted order
    subdirs = sorted(
        d for d in os.listdir(SCRIPT_DIR)
        if os.path.isdir(os.path.join(SCRIPT_DIR, d))
    )
    for subdir in subdirs:
        for filepath in sorted_walk(os.path.join(SCRIPT_DIR, subdir)):
            if not filepath.endswith(".filter"):
                continue
            tag = extract_bracket_tag(os.path.basename(filepath))
            if tag is None:
                continue  # template / untagged file — skip
            if not source_included(tag, entry, groups):
                continue
            if tag == AUTO_HEADER_TAG:
                parts.append(auto_header_line(entry))
            else:
                with open(filepath, encoding="utf-8") as f:
                    parts.append(f.read())
    return "".join(parts)


def main():
    update_version()
    filters, groups, beta = load_config()

    if not beta:
        cleanup_beta_files(filters)

    for entry in filters:
        out_file = entry["file"].replace(".filter", "_beta.filter") if beta else entry["file"]
        print(f"Building {out_file} ...")
        content = build_filter(entry, groups)
        out_dir = output_dir_for(entry)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, out_file)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  wrote {len(content):,} chars -> {out_path}")

    print("Generating filter_definitions.json ...")
    generate_filter_definitions(filters, beta)

    print("All filters built.")


if __name__ == "__main__":
    main()
