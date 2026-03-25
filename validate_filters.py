#!/usr/bin/env python3
"""
PD2 Filter Validator
Checks .filter files against the Project Diablo 2 item filtering spec.
Reference: https://wiki.projectdiablo2.com/wiki/Item_Filtering

Usage:
    python validate_filters.py                  # checks all *.filter in script dir
    python validate_filters.py Hiim.filter      # check specific files
    python validate_filters.py --all            # check builderfilter/ subdirs too
    python validate_filters.py --errors-only    # suppress warnings
"""

import re
import sys
import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Known valid tokens
# ---------------------------------------------------------------------------

COLOR_CODES = {
    'WHITE', 'GRAY', 'BLUE', 'YELLOW', 'GOLD', 'GREEN', 'DARK_GREEN',
    'TAN', 'BLACK', 'PURPLE', 'RED', 'ORANGE', 'CORAL', 'SAGE', 'TEAL',
    'LIGHT_GRAY',
}

VALUE_KEYWORDS = {
    # Standard display keywords
    'NAME', 'ILVL', 'ALVL', 'PRICE', 'SELLPRICE', 'BUYPRICE',
    'SOCKETS', 'DEF', 'ED', 'AR',
    'RUNENAME', 'MAXSOCKETS', 'QTY', 'BASENAME', 'CODE',
    'BASEMAXONEH', 'BASEMINONEH', 'BASEMAXTWOH', 'BASEMINTWOH',
    'BASEMINTHROW', 'BASEMAXTHROW', 'BASEMINKICK', 'BASEMAXKICK',
    'BASEMINSMITE', 'BASEMAXSMITE',
    # Requirements
    'REQDEX', 'REQSTR', 'REQLVL', 'LVLREQ',
    'UPDEX', 'UPSTR', 'UPLVL',
    # Inventory
    'HEIGHT', 'WIDTH', 'AREA',
    # Gem info
    'GEMLEVEL', 'GEMTYPE',
    # Stats
    'MAXRES', 'ALLATTRIB', 'BASEBLOCK', 'MINDMG',
    'STR', 'DEX', 'FBR',
    # Resistances
    'FRES', 'CRES', 'LRES', 'PRES',
    # PD2 stat display tokens (show the live value of the stat on ground/tooltip)
    'RES', 'EDAM', 'EDEF', 'RUNENUM', 'PLR',
    'FCR', 'FRW', 'FHR', 'IAS', 'MFIND', 'MANA', 'LIFE',
    'REPLIFE', 'WPNSPD', 'RANGE', 'REROLLALVL', 'CRAFTALVL',
}

SPECIAL_KEYWORDS = {
    'CONTINUE', 'NL', 'CL', 'CS',
    'NOTIFY-DEAD',   # PD2 extension (also covered by _RE_NOTIFY below)
    'MAP',           # %MAP% shorthand (no color) — valid but unusual
}

# Boolean condition flags (no operator needed)
BOOL_CONDITIONS = {
    'NMAG', 'MAG', 'RARE', 'UNI', 'SET', 'CRAFT',
    'NORM', 'EXC', 'ELT',
    'ID', 'INF', 'SUP', 'ETH', 'RW', 'GEMMED',
    # Armor slots
    'HELM', 'CHEST', 'SHIELD', 'GLOVES', 'BOOTS', 'BELT', 'CIRC', 'ARMOR', 'WEAPON',
    # Item categories
    'JEWELRY', 'CHARM', 'MISC', 'QUIVER',
    # Weapon types
    'AXE', 'MACE', 'SWORD', 'DAGGER', 'THROWING', 'JAV', 'SPEAR', 'POLEARM',
    'BOW', 'XBOW', 'STAFF', 'WAND', 'SCEPTER',
    'CLUB', 'TMACE', 'HAMMER',
    '1H', '2H',
    # Class-restricted items
    'DRU', 'BAR', 'DIN', 'NEC', 'SIN', 'SOR', 'ZON', 'CLASS',
    # Class names (full)
    'AMAZON', 'ASSASSIN', 'BARBARIAN', 'DRUID', 'NECROMANCER', 'PALADIN', 'SORCERESS',
    # Location
    'SHOP', 'EQUIPPED', 'MERC', 'INVENTORY', 'CUBE', 'STASH', 'GROUND',
    # Constants
    'TRUE', 'FALSE',
}

# Value conditions (require an operator)
VALUE_CONDITIONS = {
    # Economy / drops
    'GOLD', 'ILVL', 'ALVL', 'CLVL', 'RUNE', 'GEMLEVEL', 'GEM', 'GEMTYPE',
    'SOCKETS', 'SOCK', 'FILTLVL', 'DIFF', 'MAPID', 'MAPTIER', 'QTY',
    'LVLREQ', 'QLVL', 'AUTOMOD',
    # Resistances
    'FRES', 'CRES', 'LRES', 'PRES', 'RES',
    # Stats
    'ED', 'AR', 'DEF', 'PRICE', 'EDAM', 'EDEF', 'MAXDMG', 'MINDMG',
    'MAXRES', 'ALLATTRIB', 'BASEBLOCK',
    # Character stats
    'DEX', 'STR', 'MANA', 'LIFE',
    # Rates
    'FRW', 'FHR', 'IAS', 'FCR', 'MFIND', 'FBR',
    # Requirements
    'REQDEX', 'REQSTR', 'REQLVL', 'UPDEX', 'UPSTR', 'UPLVL',
    # Crafting/rerolling
    'CRAFTALVL', 'REROLLALVL',
    # Inventory
    'HEIGHT', 'WIDTH', 'AREA',
    # Base damage
    'BASEMINTHROW', 'BASEMAXTHROW', 'BASEMINKICK', 'BASEMAXKICK',
    'BASEMINSMITE', 'BASEMAXSMITE',
    # Misc stats
    'GFIND', 'MAEK', 'DTM', 'REPAIR', 'ARPER', 'FOOLS', 'MAXDUR',
    # Affix codes
    'PREFIX', 'SUFFIX',
    # Misc
    'STAT118',  # used directly sometimes
}

MAX_FILTER_LEVELS = 12   # Levels 1–12; 0 is always "Show All Items"
MAX_STAT_ID = 504

# Compiled patterns
_HEX2         = r'[0-9A-Fa-f]{2}'
_RE_STAT      = re.compile(r'^STAT(\d+)$')
_RE_CHARSTAT  = re.compile(r'^CHARSTAT(\d+)$')   # character stats (CBF count etc.)
_RE_TABSK     = re.compile(r'^TABSK(\d+)$')       # tab skill bonuses
_RE_CLSK      = re.compile(r'^CLSK(\d+)$')        # class skill bonuses
_RE_SK        = re.compile(r'^SK(\d+)$')           # skill level conditions
_RE_MULTI     = re.compile(                        # PD2 compound multi-stat conditions
    r'^MULTI\d+,\d+(\+MULTI\d+,\d+)*(\+STAT\d+(=[0-9]+)?)?$'
)
_RE_TIER      = re.compile(r'^TIER-(\d+)$')
_RE_MAP       = re.compile(r'^MAP-(' + _HEX2 + r')$')
_RE_DOT       = re.compile(r'^DOT-(' + _HEX2 + r')$')
_RE_BORDER    = re.compile(r'^BORDER-(' + _HEX2 + r')$')
_RE_PX        = re.compile(r'^PX-(' + _HEX2 + r')$')
_RE_SOUND     = re.compile(r'^SOUNDID-(\d+)$')
_RE_NOTIFY    = re.compile(r'^NOTIFY-([0-9A-Fa-f]|DEAD)$')  # %NOTIFY-F% or %NOTIFY-DEAD%
# Tokens that look like keyword attempts (all-caps + digits + hyphen/underscore)
_RE_KEYWORD   = re.compile(r'^[A-Z][A-Z0-9_-]*$')


# ---------------------------------------------------------------------------
# Issue dataclass
# ---------------------------------------------------------------------------

class Issue:
    __slots__ = ('filename', 'lineno', 'level', 'message', 'line_text')

    def __init__(self, filename, lineno, level, message):
        self.filename  = filename
        self.lineno    = lineno
        self.level     = level    # 'ERROR' or 'WARNING'
        self.message   = message
        self.line_text = ''

    def __str__(self):
        out = f"  [{self.level:7}] line {self.lineno:>5}: {self.message}"
        if self.line_text:
            out += f"\n             {self.line_text}"
        return out


# ---------------------------------------------------------------------------
# Token validators
# ---------------------------------------------------------------------------

def is_valid_percent_token(token: str, defined_aliases: set) -> bool:
    """Return True if %token% is a known valid output keyword or defined alias."""
    if token in COLOR_CODES:
        return True
    if token in VALUE_KEYWORDS:
        return True
    if token in SPECIAL_KEYWORDS:
        return True
    if token in defined_aliases:
        return True
    if _RE_MAP.match(token):
        return True
    if _RE_DOT.match(token):
        return True
    if _RE_BORDER.match(token):
        return True
    if _RE_PX.match(token):
        return True
    if _RE_SOUND.match(token):
        return True
    m = _RE_TIER.match(token)
    if m:
        tier_val = int(m.group(1))
        if tier_val > MAX_FILTER_LEVELS:
            return False  # out-of-range — let caller report unknown token
        return True
    if _RE_NOTIFY.match(token):
        return True
    # PD2 dynamic output tokens: display stat/skill values
    if _RE_STAT.match(token):
        return True
    if _RE_CHARSTAT.match(token):
        return True
    if _RE_TABSK.match(token):
        return True
    if _RE_CLSK.match(token):
        return True
    return False


def validate_output(output: str, filename, lineno, issues, defined_aliases):
    """Validate the output portion of an ItemDisplay or Alias rule."""
    # --- Check %...% tokens with brace-depth tracking ---
    # Only validate tokens that look like keyword attempts (all-uppercase, no spaces).
    # Tokens with spaces / mixed case are literal '%' signs used in tooltip text.
    brace_depth = 0
    pos = 0
    while pos < len(output):
        ch = output[pos]
        if ch == '{':
            brace_depth += 1
            pos += 1
        elif ch == '}':
            brace_depth -= 1
            pos += 1
        elif ch == '%':
            end = output.find('%', pos + 1)
            if end == -1:
                break
            token = output[pos + 1:end]
            if _RE_KEYWORD.match(token):
                if token == 'CONTINUE' and brace_depth > 0:
                    issues.append(Issue(filename, lineno, 'ERROR',
                        "%CONTINUE% must appear outside tooltip braces {}"))
                elif not is_valid_percent_token(token, defined_aliases):
                    issues.append(Issue(filename, lineno, 'ERROR',
                        f"Unknown output token: %{token}%"))
            pos = end + 1
        else:
            pos += 1

    # --- Check balanced tooltip braces ---
    opens  = output.count('{')
    closes = output.count('}')
    if opens != closes:
        issues.append(Issue(filename, lineno, 'ERROR',
            f"Unmatched braces in output: {opens} '{{' vs {closes} '}}'"))


def validate_condition_token(token: str, filename, lineno, issues, defined_aliases):
    """Validate a single (already-stripped) condition token."""
    if not token or token in ('OR', 'AND', 'NOT'):
        return

    # A bare '!' comes from a negated group pattern like !(A OR B) — skip it
    if token == '!':
        return

    neg = token.startswith('!')
    if neg:
        token = token[1:]
    if not token:
        return

    # PD2 compound multi-stat condition: MULTI<id>,<param>+...+STAT<n>=<v>
    if _RE_MULTI.match(token):
        return

    # Match value conditions: NAME[+NAME...] OP VALUE
    vm = re.match(
        r'^([A-Z][A-Z0-9]*(?:\+[A-Z][A-Z0-9]*)*)'   # possibly additive names
        r'([<>=~])'                                    # operator
        r'(.+)$',
        token
    )
    if vm:
        names_raw, op, val = vm.group(1), vm.group(2), vm.group(3)
        names = names_raw.split('+')

        # Validate range operator syntax
        if op == '~' and not re.match(r'^\d+-\d+$', val):
            issues.append(Issue(filename, lineno, 'WARNING',
                f"Range operator '~' expects N-M format, got: '{val}'"))

        # Validate each name in an additive expression
        for name in names:
            sm = _RE_STAT.match(name)
            if sm:
                stat_id = int(sm.group(1))
                if stat_id > MAX_STAT_ID:
                    issues.append(Issue(filename, lineno, 'ERROR',
                        f"STAT{stat_id} exceeds maximum stat ID {MAX_STAT_ID}"))
            elif (_RE_CHARSTAT.match(name) or _RE_TABSK.match(name)
                  or _RE_CLSK.match(name) or _RE_SK.match(name)):
                pass  # valid PD2 dynamic conditions
            elif name not in VALUE_CONDITIONS and name not in BOOL_CONDITIONS:
                # Unknown – might be an item code used with operator, which is unusual
                if len(name) > 8:
                    issues.append(Issue(filename, lineno, 'WARNING',
                        f"Unrecognized condition name with operator: '{name}'"))

        # Validate FILTLVL bounds
        if names_raw == 'FILTLVL':
            try:
                fval = int(val)
                if fval < 0 or fval > MAX_FILTER_LEVELS:
                    issues.append(Issue(filename, lineno, 'WARNING',
                        f"FILTLVL={fval} outside expected range 0–{MAX_FILTER_LEVELS}"))
            except ValueError:
                pass
        return

    # Pure boolean condition or item code
    upper = token.upper()
    if upper in BOOL_CONDITIONS:
        return  # known keyword

    # Alias name used as a boolean condition (PD2 supports this for group aliases)
    if token in defined_aliases:
        return

    # Item codes: 2–4 char alphanumeric strings, may start with digit (e.g. 9la, 7fb, hp1, amu)
    if re.match(r'^[0-9a-z][a-z0-9]{1,3}$', token):
        return  # treat as item code — valid

    # Short uppercase codes are also fine (ELT, ETH…) – already caught above
    if re.match(r'^[A-Z0-9][A-Z0-9]{1,3}$', token):
        return

    # Flag anything else that doesn't look like a reasonable token
    if not re.match(r'^[A-Za-z][A-Za-z0-9_-]*$', token):
        issues.append(Issue(filename, lineno, 'WARNING',
            f"Suspicious condition token: '{token}'"))


def parse_conditions(cond_str: str, filename, lineno, issues, defined_aliases):
    """Parse and validate the full condition string of an ItemDisplay rule."""
    # --- Check balanced parentheses ---
    depth = 0
    for ch in cond_str:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth < 0:
                issues.append(Issue(filename, lineno, 'ERROR',
                    "Unmatched closing ')' in conditions"))
                return  # stop further paren checks
    if depth > 0:
        issues.append(Issue(filename, lineno, 'ERROR',
            f"Unclosed '(' in conditions ({depth} unclosed)"))

    # Flatten and tokenise for individual token validation
    flat = re.sub(r'[()]', ' ', cond_str)
    for token in re.split(r'\s+', flat.strip()):
        validate_condition_token(token.strip(), filename, lineno, issues, defined_aliases)


# ---------------------------------------------------------------------------
# Per-file validator
# ---------------------------------------------------------------------------

def validate_file(filepath: Path, errors_only: bool = False):
    """Validate a single .filter file. Returns (issues, filter_level_count)."""
    issues = []
    fname  = filepath.name
    filter_level_count = 0
    defined_aliases: set = set()

    # --- Pass 1: collect all alias names (enables forward references) ---
    try:
        raw_lines = filepath.read_text(encoding='utf-8', errors='replace').splitlines()
    except Exception as exc:
        return [Issue(fname, 0, 'ERROR', f"Cannot read file: {exc}")], 0

    alias_line_map: dict = {}   # name -> first lineno it was defined
    for lineno_0, raw in enumerate(raw_lines, 1):
        m = re.match(r'^Alias\[([^\]]+)\]:', raw.strip())
        if m:
            name = m.group(1)
            defined_aliases.add(name)
            if name not in alias_line_map:
                alias_line_map[name] = lineno_0
            else:
                issues.append(Issue(fname, lineno_0, 'ERROR',
                    f"Alias '{name}' is already defined at line {alias_line_map[name]}"))

    # --- Alias substring conflict check ---
    # Sort longest-first so we always report the *shorter* name as the problem
    alias_names = sorted(alias_line_map.keys(), key=len, reverse=True)
    for i, longer in enumerate(alias_names):
        for shorter in alias_names[i + 1:]:
            if shorter in longer:
                issues.append(Issue(fname, alias_line_map[shorter], 'ERROR',
                    f"Alias name '{shorter}' is a substring of alias '{longer}' — "
                    f"this can cause ambiguous token matching"))

    # --- Pass 2: full validation ---
    for lineno, raw in enumerate(raw_lines, 1):
        line     = raw.rstrip('\r\n')
        stripped = line.strip()

        if not stripped or stripped.startswith('//'):
            continue

        # ItemDisplayFilterName[]: Level Name
        if stripped.startswith('ItemDisplayFilterName'):
            m = re.match(r'^ItemDisplayFilterName\[\s*\]:\s*(.+)$', stripped)
            if not m:
                issues.append(Issue(fname, lineno, 'ERROR',
                    "Malformed ItemDisplayFilterName — expected: ItemDisplayFilterName[]: Name"))
            else:
                filter_level_count += 1
                if filter_level_count > MAX_FILTER_LEVELS:
                    issues.append(Issue(fname, lineno, 'WARNING',
                        f"More than {MAX_FILTER_LEVELS} filter levels defined "
                        f"(this is level {filter_level_count})"))
            continue

        # Alias[NAME]: value
        if stripped.startswith('Alias['):
            m = re.match(r'^Alias\[([^\]]+)\]:\s*(.*)$', stripped)
            if not m:
                issues.append(Issue(fname, lineno, 'ERROR',
                    "Malformed Alias — expected: Alias[NAME]: value"))
            else:
                alias_val = m.group(2)
                # Strip inline comment (outside braces) before validating
                bd, cs = 0, -1
                for i, ch in enumerate(alias_val):
                    if ch == '{':
                        bd += 1
                    elif ch == '}':
                        bd -= 1
                    elif bd == 0 and alias_val[i:i+2] == '//':
                        cs = i
                        break
                validate_output(alias_val[:cs].rstrip() if cs >= 0 else alias_val,
                                fname, lineno, issues, defined_aliases)
            continue

        # ItemDisplay[CONDITIONS]: output
        if stripped.startswith('ItemDisplay['):
            m = re.match(r'^ItemDisplay\[([^\]]*)\]:\s*(.*)$', stripped)
            if not m:
                issues.append(Issue(fname, lineno, 'ERROR',
                    "Malformed ItemDisplay — expected: ItemDisplay[CONDITIONS]: output"))
                continue

            conditions = m.group(1)
            output_raw = m.group(2)

            # Strip inline comment outside tooltip braces
            brace_depth   = 0
            comment_start = -1
            for i, ch in enumerate(output_raw):
                if ch == '{':
                    brace_depth += 1
                elif ch == '}':
                    brace_depth -= 1
                elif brace_depth == 0 and output_raw[i:i+2] == '//':
                    comment_start = i
                    break
            output = output_raw[:comment_start].rstrip() if comment_start >= 0 else output_raw

            if conditions.strip():
                parse_conditions(conditions, fname, lineno, issues, defined_aliases)

            if output.strip():
                validate_output(output, fname, lineno, issues, defined_aliases)
            continue

        # Anything else that looks like it starts a rule is suspicious
        if re.match(r'^[A-Za-z]', stripped):
            issues.append(Issue(fname, lineno, 'WARNING',
                f"Unrecognized line format: {stripped[:80]}"))

    if errors_only:
        issues = [i for i in issues if i.level == 'ERROR']

    # Attach the raw source line to each issue for context
    for issue in issues:
        if 1 <= issue.lineno <= len(raw_lines):
            issue.line_text = raw_lines[issue.lineno - 1].rstrip()

    return issues, filter_level_count


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args       = sys.argv[1:]
    errors_only = '--errors-only' in args
    include_all = '--all' in args
    args = [a for a in args if a not in ('--errors-only', '--all')]

    script_dir = Path(__file__).parent

    if args:
        filter_files = [Path(a) for a in args]
    elif include_all:
        filter_files = sorted(script_dir.rglob('*.filter'))
    else:
        filter_files = sorted(script_dir.glob('*.filter'))

    if not filter_files:
        print("No .filter files found.")
        return 0

    total_errors   = 0
    total_warnings = 0
    files_with_issues = 0

    for fp in filter_files:
        issues, level_count = validate_file(fp, errors_only=errors_only)
        errors   = sum(1 for i in issues if i.level == 'ERROR')
        warnings = sum(1 for i in issues if i.level == 'WARNING')

        if issues:
            files_with_issues += 1
            tag = f"{errors} error(s)" + (f", {warnings} warning(s)" if not errors_only else "")
            print(f"\n{'-'*60}")
            print(f"  {fp.name}  [{tag}]  ({level_count} filter level(s))")
            print(f"{'-'*60}")
            for issue in sorted(issues, key=lambda x: x.lineno):
                print(str(issue))
        else:
            print(f"  {fp.name:<45}  OK  ({level_count} filter level(s))")

        total_errors   += errors
        total_warnings += warnings

    print()
    print('=' * 60)
    print(f"Total: {total_errors} error(s), {total_warnings} warning(s)"
          f"  |  {files_with_issues}/{len(filter_files)} file(s) have issues")
    print('=' * 60)


    return 1 if total_errors > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
