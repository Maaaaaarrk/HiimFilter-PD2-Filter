import os
import re

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR     = os.path.dirname(SCRIPT_DIR)

TEMPLATE     = os.path.join(SCRIPT_DIR, "README.md")
OUTPUT       = os.path.join(ROOT_DIR, "README.md")
VERSION_FILTER = os.path.join(ROOT_DIR, "builderfilter", "01-header", "01-Version[ALL].filter")


def get_version_string():
    with open(VERSION_FILTER, encoding="utf-8") as f:
        line = f.read().strip()
    # %CL% is a newline token in filter syntax — render as space in plain text
    return line.replace("%CL%", " ")


def main():
    version_str = get_version_string()

    with open(TEMPLATE, encoding="utf-8") as f:
        content = f.read()

    content = content.replace("{{REPLACE_ME}}", version_str)

    with open(OUTPUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

    print(f"README.md written with version: {version_str}")


if __name__ == "__main__":
    main()
