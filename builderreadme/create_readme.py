import json
import os

SCRIPT_DIR        = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR          = os.path.dirname(SCRIPT_DIR)

TEMPLATE          = os.path.join(SCRIPT_DIR, "README.md")
FILTER_LEVELS_TPL = os.path.join(SCRIPT_DIR, "filter_levels.md")
OUTPUT            = os.path.join(ROOT_DIR, "README.md")
VERSION_FILTER    = os.path.join(ROOT_DIR, "builderfilter", "01-header", "01-Version[ALL].filter")
FILTER_DEFS       = os.path.join(ROOT_DIR, "filter_definitions.json")
FILTERGROUPS_DIR  = os.path.join(ROOT_DIR, "filtergroups")


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


def write_root_readme(version_str, filter_levels):
    filters_section = build_filters_section(FILTER_DEFS)
    with open(TEMPLATE, encoding="utf-8") as f:
        content = f.read()

    content = content.replace("{{REPLACE_ME}}", version_str)
    content = content.replace("{{REPLACE_FILTERS}}", filters_section)
    content = content.replace("{{REPLACE_FILTER_LEVELS}}", filter_levels)

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
    version_str   = get_version_string()
    filter_levels = get_filter_levels()

    write_root_readme(version_str, filter_levels)

    if os.path.isdir(FILTERGROUPS_DIR):
        for name in sorted(os.listdir(FILTERGROUPS_DIR)):
            sub = os.path.join(FILTERGROUPS_DIR, name)
            if os.path.isdir(sub):
                write_bucket_readme(sub, version_str, filter_levels)


if __name__ == "__main__":
    main()
