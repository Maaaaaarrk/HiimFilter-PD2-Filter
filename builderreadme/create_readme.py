import json
import os

SCRIPT_DIR       = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR         = os.path.dirname(SCRIPT_DIR)

TEMPLATE         = os.path.join(SCRIPT_DIR, "README.md")
OUTPUT           = os.path.join(ROOT_DIR, "README.md")
VERSION_FILTER   = os.path.join(ROOT_DIR, "builderfilter", "01-header", "01-Version[ALL].filter")
FILTER_DEFS      = os.path.join(ROOT_DIR, "filter_definitions.json")


def get_version_string():
    with open(VERSION_FILTER, encoding="utf-8") as f:
        line = f.read().strip()
    return line.replace("%CL%", " ")


def build_filters_section():
    with open(FILTER_DEFS, encoding="utf-8") as f:
        data = json.load(f)
    lines = []
    for entry in data["filter_info"].values():
        lines.append(f"* {entry['display_name']}: {entry['description']} [{entry['file_name']}]")
    return "\n".join(lines)


def main():
    version_str     = get_version_string()
    filters_section = build_filters_section()

    with open(TEMPLATE, encoding="utf-8") as f:
        content = f.read()

    content = content.replace("{{REPLACE_ME}}", version_str)
    content = content.replace("{{REPLACE_FILTERS}}", filters_section)

    with open(OUTPUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

    print(f"README.md written with version: {version_str}")


if __name__ == "__main__":
    main()
