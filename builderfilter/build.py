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

    # Preserve the season string from the existing filter line
    season = "Season 12"
    if os.path.exists(VERSION_FILTER):
        with open(VERSION_FILTER, encoding="utf-8") as f:
            existing = f.read()
        m = re.search(r'(Season\s+\d+)', existing)
        if m:
            season = m.group(1)

    today = datetime.date.today()
    date_str = f"{today.strftime('%B')} {_ordinal(today.day)}"
    with open(VERSION_FILTER, "w", encoding="utf-8") as f:
        f.write(f"Last updated {date_str}%CL%{season} - build {version}")

    print(f"Version: {season} - build {version} ({date_str})")

FILTER_DEFINITIONS = os.path.join(OUTPUT_DIR, "filter_definitions.json")


def load_config():
    with open(os.path.join(SCRIPT_DIR, "filters.json"), encoding="utf-8") as f:
        data = json.load(f)
    return data["filters"], data.get("groups", {}), data.get("beta", False)


def sync_definitions_beta(filters, beta):
    """Add or remove file_name_beta in filter_definitions.json based on the beta flag."""
    if not os.path.exists(FILTER_DEFINITIONS):
        return
    with open(FILTER_DEFINITIONS, encoding="utf-8") as f:
        defs = json.load(f)

    # Build a lookup: file_name -> definition entry
    file_to_info = {info["file_name"]: info for info in defs.get("filter_info", {}).values()}

    changed = False
    for entry in filters:
        info = file_to_info.get(entry["file"])
        if info is None:
            continue
        if beta:
            beta_name = entry["file"].replace(".filter", "_beta.filter")
            if info.get("file_name_beta") != beta_name:
                info["file_name_beta"] = beta_name
                changed = True
        else:
            if "file_name_beta" in info:
                del info["file_name_beta"]
                changed = True

    if changed:
        with open(FILTER_DEFINITIONS, "w", encoding="utf-8") as f:
            json.dump(defs, f, indent=2, ensure_ascii=False)
            f.write("\n")
        action = "added" if beta else "removed"
        print(f"  {action} file_name_beta entries in filter_definitions.json")


def cleanup_beta_files(filters):
    """Delete root *_beta.filter files when beta is turned off."""
    for entry in filters:
        beta_file = entry["file"].replace(".filter", "_beta.filter")
        path = os.path.join(OUTPUT_DIR, beta_file)
        if os.path.exists(path):
            os.remove(path)
            print(f"  removed {beta_file}")


def extract_bracket_tag(filename):
    """Return the content inside [...] in a filename, or None if absent."""
    m = re.search(r'\[([^\]]+)\]', filename)
    return m.group(1) if m else None


def token_matches_filter(token, entry, groups):
    """Return True if a single tag token applies to the given filter entry."""
    # Expand group name to its member list
    if token in groups:
        members = groups[token]
        return entry["name"] in members or any(t in members for t in entry["tags"])
    # Direct match against filter name or tags
    return token == entry["name"] or token in entry["tags"]


def source_included(bracket_tag, entry, groups):
    """Decide whether a source file should be concatenated into the given filter."""
    if bracket_tag == "ALL":
        return True

    if bracket_tag.startswith("ONLY="):
        tokens = bracket_tag[5:].split("+")
        return any(token_matches_filter(t, entry, groups) for t in tokens)

    if bracket_tag.startswith("ALL-EXCEPT="):
        tokens = bracket_tag[11:].split("+")
        return not any(token_matches_filter(t, entry, groups) for t in tokens)

    # No keyword prefix — treat as implicit ONLY (e.g. [CRAFTING+LLD])
    tokens = bracket_tag.split("+")
    return any(token_matches_filter(t, entry, groups) for t in tokens)


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
            if source_included(tag, entry, groups):
                with open(filepath, encoding="utf-8") as f:
                    parts.append(f.read())
    return "".join(parts)


def main():
    update_version()
    filters, groups, beta = load_config()

    sync_definitions_beta(filters, beta)
    if not beta:
        cleanup_beta_files(filters)

    for entry in filters:
        out_file = entry["file"].replace(".filter", "_beta.filter") if beta else entry["file"]
        print(f"Building {out_file} ...")
        content = build_filter(entry, groups)
        out_path = os.path.join(OUTPUT_DIR, out_file)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  wrote {len(content):,} chars -> {out_path}")
    print("All filters built.")


if __name__ == "__main__":
    main()
