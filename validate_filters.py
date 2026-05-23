#!/usr/bin/env python3
"""
PD2 Filter Validator
Checks .filter files against the Project Diablo 2 item filtering spec.
Reference: https://wiki.projectdiablo2.com/wiki/Item_Filtering

Usage:
    python validate_filters.py                  # checks root *.filter AND filtergroups/ outputs
    python validate_filters.py Hiim.filter      # check specific files
    python validate_filters.py --root-only      # skip filtergroups/ outputs
    python validate_filters.py --errors-only    # suppress warnings
    python validate_filters.py --length-check   # also run the display-name length report (slow, opt-in)
"""

import re
import sys
import os
import json
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
    'GFIND',
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
    'GFIND',
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
    # Base 1H/2H damage (conditions)
    'BASEMINONEH', 'BASEMAXONEH', 'BASEMINTWOH', 'BASEMAXTWOH',
    # Max sockets
    'MAXSOCKETS',
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
    r'^MULTI\d+,\d+([<>=~]\d+)?(\+MULTI\d+,\d+([<>=~]\d+)?)*(\+STAT\d+(=[0-9]+)?)?$'
)
_RE_TIER      = re.compile(r'^TIER-(\d+)$')
_RE_MAP       = re.compile(r'^MAP-(' + _HEX2 + r')$')
_RE_DOT       = re.compile(r'^DOT-(' + _HEX2 + r')$')
_RE_BORDER    = re.compile(r'^BORDER-(' + _HEX2 + r')$')
_RE_PX        = re.compile(r'^PX-(' + _HEX2 + r')$')
_RE_SOUND     = re.compile(r'^SOUNDID-(\d+)$')
_RE_SOUND_TAG = re.compile(r'%SOUNDID-\d+%')   # for counting %SOUNDID-N% tags in expanded output
# Map/minimap/border/pixel marker tags — at most one of each per rendered line.
# MAP matches both the bare %MAP% shorthand and the colored %MAP-XX% form.
_RE_DOT_TAG    = re.compile(r'%DOT-[0-9A-Fa-f]{2}%')
_RE_BORDER_TAG = re.compile(r'%BORDER-[0-9A-Fa-f]{2}%')
_RE_MAP_TAG    = re.compile(r'%MAP(?:-[0-9A-Fa-f]{2})?%')
_RE_PX_TAG     = re.compile(r'%PX-[0-9A-Fa-f]{2}%')
_RE_NOTIFY    = re.compile(r'^NOTIFY-([0-9A-Fa-f]|DEAD)$')  # %NOTIFY-F% or %NOTIFY-DEAD%
_RE_FORMULA   = re.compile(r'^FORMULA([A-Z][A-Z0-9_]*)$')   # explicit formula refs: FORMULADPS
_RE_ISLAND    = re.compile(r'^ISLAND_([A-Z]+)$')             # auto-generated inline formula tokens
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
    if _RE_SK.match(token):
        return True
    # Explicit formula references: %FORMULADPS%, %FORMULAA%, etc.
    if _RE_FORMULA.match(token):
        return True
    # Auto-generated inline formula tokens: %ISLAND_A%, %ISLAND_B%, etc.
    if _RE_ISLAND.match(token):
        return True
    return False


def _strip_inline_comment(text: str) -> str:
    """Strip a trailing // comment that sits outside any tooltip braces."""
    bd = 0
    for i, ch in enumerate(text):
        if ch == '{':
            bd += 1
        elif ch == '}':
            bd -= 1
        elif bd == 0 and text[i:i+2] == '//':
            return text[:i].rstrip()
    return text


_RE_ALIAS_REF = re.compile(r'%([A-Za-z][A-Za-z0-9_-]*)%')


def _expand_aliases(text: str, alias_values: dict, _visited=frozenset()) -> str:
    """Recursively expand %aliasname% references using alias_values map.

    Tokens that aren't defined aliases (e.g. %NAME%, %SOUNDID-X%, %WHITE%) are
    left untouched. Cycles are guarded via _visited.
    """
    def repl(m):
        name = m.group(1)
        if name in _visited or name not in alias_values:
            return m.group(0)
        return _expand_aliases(alias_values[name], alias_values, _visited | {name})
    return _RE_ALIAS_REF.sub(repl, text)


def _strip_inline_formulas(text: str) -> str:
    """Replace $f(...) inline formula expressions with a neutral placeholder.

    Handles nested parentheses so that $f(min(a,b)+max(c,d)) is fully matched.
    In output strings the engine replaces these with %ISLAND_X% tokens at runtime.
    """
    result = []
    i = 0
    while i < len(text):
        if text[i:i+3] == '$f(' :
            # Walk forward to find the matching closing paren
            depth = 1
            j = i + 3
            while j < len(text) and depth > 0:
                if text[j] == '(':
                    depth += 1
                elif text[j] == ')':
                    depth -= 1
                j += 1
            if depth == 0:
                # Replace entire $f(...) with an inert placeholder
                result.append('0')
                i = j
            else:
                # Unclosed $f( — leave as-is, will likely trigger other errors
                result.append(text[i])
                i += 1
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)


def validate_output(output: str, filename, lineno, issues, defined_aliases):
    """Validate the output portion of an ItemDisplay or Alias rule."""
    # --- Strip $f() inline formulas before token scanning ---
    # These get replaced at runtime with auto-generated %ISLAND_X% tokens.
    # Replace them with a placeholder so we don't flag their internals.
    output = _strip_inline_formulas(output)

    # --- Check %...% tokens with brace-depth tracking ---
    # Only validate tokens that look like keyword attempts (all-uppercase, no spaces).
    # Tokens with spaces / mixed case are literal '%' signs used in tooltip text.
    # Also count %NAME% per bucket (main output vs. tooltip {}) — duplicates in
    # either bucket are almost always a copy-paste bug.
    brace_depth      = 0
    pos              = 0
    name_count_main  = 0   # %NAME% occurrences outside tooltip braces
    name_count_tip   = 0   # %NAME% occurrences inside tooltip braces
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
                if token == 'NAME':
                    if brace_depth > 0:
                        name_count_tip += 1
                    else:
                        name_count_main += 1
                if token == 'CONTINUE' and brace_depth > 0:
                    issues.append(Issue(filename, lineno, 'ERROR',
                        "%CONTINUE% must appear outside tooltip braces {}"))
                elif not is_valid_percent_token(token, defined_aliases):
                    issues.append(Issue(filename, lineno, 'ERROR',
                        f"Unknown output token: %{token}%"))
            elif re.match(r'^[A-Za-z][A-Za-z0-9_-]*$', token):
                # Token isn't all-uppercase but looks like a keyword attempt.
                # If its uppercase form is a known token, the casing is wrong —
                # PD2 filter tokens are case-sensitive, so %Yellow% won't render
                # as the YELLOW color.
                upper = token.upper()
                if (upper in COLOR_CODES
                        or upper in VALUE_KEYWORDS
                        or upper in SPECIAL_KEYWORDS
                        or upper in defined_aliases):
                    issues.append(Issue(filename, lineno, 'ERROR',
                        f"Mixed-case token %{token}% — filter tokens are case-sensitive (did you mean %{upper}%?)"))
            pos = end + 1
        else:
            pos += 1

    # --- Flag duplicate %NAME% per bucket ---
    if name_count_main > 1:
        issues.append(Issue(filename, lineno, 'WARNING',
            f"%NAME% appears {name_count_main}x in the main output "
            f"(outside tooltip braces) — likely a copy-paste bug"))
    if name_count_tip > 1:
        issues.append(Issue(filename, lineno, 'WARNING',
            f"%NAME% appears {name_count_tip}x inside the tooltip {{}} "
            f"— likely a copy-paste bug"))

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

    # Explicit formula references used as conditions: FORMULADPS>100
    if _RE_FORMULA.match(token):
        return
    # Auto-generated inline formula tokens used as conditions: ISLAND_A>5
    if _RE_ISLAND.match(token):
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
                  or _RE_CLSK.match(name) or _RE_SK.match(name)
                  or _RE_FORMULA.match(name) or _RE_ISLAND.match(name)):
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
    # --- Strip $f() inline formulas (replaced at runtime with ISLAND_X keys) ---
    cond_str = _strip_inline_formulas(cond_str)

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

    # --- Check for stray commas in the condition list (issue #778 class) ---
    # ItemDisplay[...] uses whitespace to separate tokens, never commas.
    # Common typo: "FHR>0, OR LIFE>0" — a stray ',' before OR/AND.
    # Also flag a trailing ',' just before a closing ')' inside a group:
    # e.g. "(A>0 OR B>0,)". Both are the same root cause.
    # Note: commas *inside* tokens (e.g. MULTI79,1>0) are legitimate, so we
    # only flag commas that are followed by whitespace + OR/AND, or by
    # optional whitespace + ')'.
    for m in re.finditer(r',\s*(OR|AND)\b', cond_str):
        issues.append(Issue(filename, lineno, 'ERROR',
            f"Stray ',' before '{m.group(1)}' in ItemDisplay condition list "
            f"(conditions are whitespace-separated, not comma-separated)"))
    for _ in re.finditer(r',\s*\)', cond_str):
        issues.append(Issue(filename, lineno, 'ERROR',
            "Stray trailing ',' before ')' in ItemDisplay condition group "
            "(conditions are whitespace-separated, not comma-separated)"))

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
    alias_values:   dict = {}   # name -> raw value (comment-stripped) for expansion
    defined_formulas: set = set()  # formula keys (uppercased, prefixed with FORMULA)
    for lineno_0, raw in enumerate(raw_lines, 1):
        stripped_raw = raw.strip()
        m = re.match(r'^Alias\[([^\]]+)\]:\s*(.*)$', stripped_raw)
        if m:
            name = m.group(1)
            defined_aliases.add(name)
            if name not in alias_line_map:
                alias_line_map[name] = lineno_0
                alias_values[name] = _strip_inline_comment(m.group(2))
            else:
                issues.append(Issue(fname, lineno_0, 'ERROR',
                    f"Alias '{name}' is already defined at line {alias_line_map[name]}"))
        # Collect explicit Formula[KEY] definitions — add as known tokens
        fm = re.match(r'^Formula\[([^\]]+)\]:', stripped_raw)
        if fm:
            formula_key = 'FORMULA' + fm.group(1).upper()
            defined_formulas.add(formula_key)
            defined_aliases.add(formula_key)

    # --- Alias substring conflict check ---
    # Sort longest-first so we always report the *shorter* name as the problem
    alias_names = sorted(alias_line_map.keys(), key=len, reverse=True)
    for i, longer in enumerate(alias_names):
        for shorter in alias_names[i + 1:]:
            if shorter in longer:
                issues.append(Issue(fname, alias_line_map[shorter], 'WARNING',
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
            m = re.match(r'^ItemDisplayFilterName\[\s*\d*\s*\]:\s*(.+)$', stripped)
            if not m:
                issues.append(Issue(fname, lineno, 'ERROR',
                    "Malformed ItemDisplayFilterName — expected: ItemDisplayFilterName[N]: Name"))
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

        # Formula[KEY]: expression  (explicit formula definitions)
        if stripped.startswith('Formula['):
            m = re.match(r'^Formula\[([^\]]+)\]:\s*(.*)$', stripped)
            if not m:
                issues.append(Issue(fname, lineno, 'ERROR',
                    "Malformed Formula — expected: Formula[KEY]: expression"))
            elif not m.group(2).strip():
                issues.append(Issue(fname, lineno, 'WARNING',
                    "Empty formula expression"))
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
                # After expanding aliases, the rendered line must have at most one
                # %SOUNDID-N% tag — the game only plays one sound per match, and
                # stacking them (often via overlapping aliases) is always a bug.
                expanded = _expand_aliases(output, alias_values)
                sound_tags = _RE_SOUND_TAG.findall(expanded)
                if len(sound_tags) > 1:
                    issues.append(Issue(fname, lineno, 'ERROR',
                        f"Line has {len(sound_tags)} %SOUNDID-N% tags after "
                        f"alias expansion ({', '.join(sound_tags)}) — only one "
                        f"is allowed per rendered line"))
                for kind, pattern in (
                    ('DOT',    _RE_DOT_TAG),
                    ('BORDER', _RE_BORDER_TAG),
                    ('MAP',    _RE_MAP_TAG),
                    ('PX',     _RE_PX_TAG),
                ):
                    tags = pattern.findall(expanded)
                    if len(tags) > 1:
                        issues.append(Issue(fname, lineno, 'ERROR',
                            f"Line has {len(tags)} %{kind}-...% tags after "
                            f"alias expansion ({', '.join(tags)}) — only one "
                            f"is allowed per rendered line"))
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
# Display-name length checker (first pass — warnings only, never fails)
# ---------------------------------------------------------------------------
#
# Goal: estimate the on-ground display-name length of items that are prone to
# truncation, so we can spot names that run too long. We check three groups:
#
#   * all runes
#   * all unidentified unique / set items (UNI/SET + !ID rules)
#   * everything declared in builderfilter/05-utility/03-PD2_items
#
# Method ("render the final line"):
#   1. Find the rule chain that applies to the item. Rules are evaluated
#      top-to-bottom, first-match-wins; a matching rule with %CONTINUE% lets
#      the scan continue, so the chain runs from the first match up to and
#      including the first matching rule WITHOUT %CONTINUE%.
#   2. The on-ground name is the text OUTSIDE the {tooltip} braces. Sound IDs
#      and other non-text marker tags (MAP/DOT/BORDER/PX/TIER/NOTIFY/CL/NL)
#      add no horizontal width and are removed.
#   3. Each %COLOR% renders in-game as a colour-escape; per project convention
#      we count it as COLOR_RENDER_WIDTH characters.
#   4. The item name (%NAME%/%RUNENAME%, or a literal like "Lycanders Flank")
#      is counted exactly ONCE — length = real-name length + the decoration /
#      colour characters contributed by every rule in the chain.
#
# Modelling notes / known approximations (acceptable for a first pass):
#   * Concatenation ORDER is irrelevant to length, so we don't reproduce the
#     engine's exact %CONTINUE% splice order — only which rules contribute.
#   * Dynamic conditions we can't resolve statically (MAPID, QTY, STAT*, item
#     category flags for uniques, etc.) are treated as satisfiable, so the
#     result is an UPPER BOUND on the rendered length. FILTLVL and ETH are
#     evaluated concretely across representative values and the max is kept.
#   * PD2_ITEM_NAMES are best-effort; a few rarely-seen codes are approximate,
#     but their on-ground output is short so they never reach the top of the
#     list.

COLOR_RENDER_WIDTH = 2   # chars each %COLOR% escape costs on screen

# Rune number (1-33) -> rune word. In-game name renders as "<word> Rune".
_RUNE_WORDS = [
    'El', 'Eld', 'Tir', 'Nef', 'Eth', 'Ith', 'Tal', 'Ral', 'Ort', 'Thul',
    'Amn', 'Sol', 'Shael', 'Dol', 'Hel', 'Io', 'Lum', 'Ko', 'Fal', 'Lem',
    'Pul', 'Um', 'Mal', 'Ist', 'Gul', 'Vex', 'Ohm', 'Lo', 'Sur', 'Ber',
    'Jah', 'Cham', 'Zod',
]
RUNE_NAMES = {i + 1: f"{w} Rune" for i, w in enumerate(_RUNE_WORDS)}

# Item code -> in-game base name for the items declared in 03-PD2_items.
# Best-effort; see modelling notes above.
PD2_ITEM_NAMES = {
    'wss':  'Worldstone Shard',
    'cwss': 'Tainted Worldstone Shard',
    'iwss': 'Catalyst Shard',
    'imrn': 'Demonic Cube',
    'jewf': 'Jewel Fragment',
    'key':  'Key',
    'rkey': 'Key',
    'lbox': "Larzuk's Puzzlebox",
    'lpp':  "Larzuk's Puzzlepiece",
    'lmal': "Larzuk's Malus",
    'llmr': "Lilith's Mirror",
    'lsvl': 'Vial of Lightsong',
    'rid':  'Horadric Almanac',
    'rtp':  'Horadric Navigator',
}

# FILTLVL bands change which formatting rules apply. These representative
# levels straddle every threshold used in the filters (<3, <5, <7, <8, <9,
# <11, and >4/>7). Level 0 is skipped: it's the "filter disabled" level that
# shows plain names, so it never produces the longest decorated render.
_REPRESENTATIVE_FILTLVLS = (1, 6, 7, 8, 10, 11)

_RE_ITEM_CODE   = re.compile(r'^[0-9a-z][a-z0-9]{1,3}$')      # 2-4 char item code
_RE_COLOR_TOKEN = re.compile(r'%(' + '|'.join(sorted(COLOR_CODES)) + r')%')
_RE_NAME_TOKEN  = re.compile(r'%(NAME|RUNENAME|BASENAME)%')

# Each colour renders as a 2-char escape in-game; in the computed-line preview
# we show a readable 2-char abbreviation (all ASCII, all exactly 2 wide, so the
# preview's length equals the counted length).
_COLOR_ABBR = {
    'WHITE': 'Wh', 'GRAY': 'Gy', 'LIGHT_GRAY': 'LG', 'BLUE': 'Bl',
    'YELLOW': 'Ye', 'GOLD': 'Go', 'GREEN': 'Gn', 'DARK_GREEN': 'DG',
    'TAN': 'Tn', 'BLACK': 'Bk', 'PURPLE': 'Pu', 'RED': 'Rd',
    'ORANGE': 'Or', 'CORAL': 'Co', 'SAGE': 'Sg', 'TEAL': 'Tl',
}
_NAME_SENTINEL = '\x00'   # marks where the item name belongs while assembling
_RE_MARKER_TOKEN = re.compile(
    r'%(?:SOUNDID-\d+|MAP(?:-[0-9A-Fa-f]{2})?|DOT-[0-9A-Fa-f]{2}'
    r'|BORDER-[0-9A-Fa-f]{2}|PX-[0-9A-Fa-f]{2}|TIER-\d+'
    r'|NOTIFY-(?:[0-9A-Fa-f]|DEAD)|CONTINUE|CL|NL|CS)%'
)
_RE_VALUE_TOKEN = re.compile(r'%[A-Z0-9_][A-Z0-9_-]*%')   # leftover dynamic value tokens
# Broad item-category / class flags. For a unique/set item we don't know the
# base's category, so we treat these as satisfiable (True) to bound the length.
_CATEGORY_FLAGS = {
    'ARMOR', 'WEAPON', 'JEWELRY', 'CHARM', 'MISC', 'QUIVER',
    'HELM', 'CHEST', 'SHIELD', 'GLOVES', 'BOOTS', 'BELT', 'CIRC',
    'AXE', 'MACE', 'SWORD', 'DAGGER', 'THROWING', 'JAV', 'SPEAR', 'POLEARM',
    'BOW', 'XBOW', 'STAFF', 'WAND', 'SCEPTER', 'CLUB', 'TMACE', 'HAMMER',
    '1H', '2H',
}

# Quality flags a synthetic unique/set/rune item can never satisfy. Treating
# these as False keeps magic/rare/craft/superior colouring rules out of the
# chain (SUP/INF are normal-item quality modifiers, never a unique/set).
_NEVER_FLAGS = {'MAG', 'NMAG', 'RARE', 'CRAFT', 'RW', 'GEMMED', 'SUP', 'INF'}

# Inventory locations other than the ground. A dropped item being filtered is
# on the GROUND, so rules gated on these never apply to our render.
_LOCATION_OFF = {'SHOP', 'EQUIPPED', 'MERC', 'INVENTORY', 'CUBE', 'STASH'}


_RE_COMPARE = re.compile(r'^([A-Za-z][A-Za-z0-9]*)([<>=~])(.+)$')


def _tokenize_cond(cond):
    """Split a condition into evaluator tokens (parens standalone)."""
    return re.sub(r'([()])', r' \1 ', cond).split()


class _Rule:
    """A single ItemDisplay rule, pre-parsed for the length checker."""
    __slots__ = ('idx', 'cond', 'toks', 'output', 'codes', 'has_category',
                 'continues', 'requires_id', 'mentions_rune',
                 'mentions_uni', 'mentions_set', 'code_dep')

    def __init__(self, cond, output):
        self.idx    = -1     # file-order index, set by _parse_rules
        self.cond   = cond
        self.toks   = _tokenize_cond(cond)   # tokenised once, reused every eval
        self.output = output
        # Item-code tokens referenced (used for cheap pre-filtering). Item codes
        # are lowercase (axe, jav, uar); condition keywords are UPPERCASE (AXE,
        # JAV) — the lowercase-only regex distinguishes them, so a code like
        # 'axe' is kept even though 'AXE' is also a boolean flag.
        words = re.findall(r'[A-Za-z0-9_+-]+', cond)
        # A code must contain a letter (so numeric literals like the 11 in
        # FILTLVL<11 or 181 in MAPID=181 are not mistaken for item codes).
        self.codes = {t for t in words
                      if _RE_ITEM_CODE.match(t) and any(c.isalpha() for c in t)}
        self.has_category = any(t in _CATEGORY_FLAGS for t in words)
        self.continues    = '%CONTINUE%' in output
        # Pre-flags for fast skipping (never affect the result, only the
        # candidate set): a positive (non-negated) ID requirement can't match an
        # unidentified item; only RUNE rules apply to runes; UNI/SET mentions
        # let us bucket formatting rules by class.
        self.requires_id   = bool(re.search(r'(?<!!)\bID\b', cond))
        self.mentions_rune = 'RUNE' in cond
        self.mentions_uni  = 'UNI' in words
        self.mentions_set  = 'SET' in words
        self.code_dep      = bool(self.codes)   # refined in _bucket_rules


def _parse_rules(raw_lines):
    """Extract (rules, alias_values) from a built filter's lines."""
    rules = []
    alias_values = {}
    for raw in raw_lines:
        s = raw.strip()
        if not s or s.startswith('//'):
            continue
        am = re.match(r'^Alias\[([^\]]+)\]:\s*(.*)$', s)
        if am:
            alias_values.setdefault(am.group(1), _strip_inline_comment(am.group(2)))
            continue
        im = re.match(r'^ItemDisplay\[([^\]]*)\]:\s*(.*)$', s)
        if im:
            rules.append(_Rule(im.group(1).strip(),
                               _strip_inline_comment(im.group(2))))
    for i, r in enumerate(rules):
        r.idx = i
    return rules, alias_values


# --- condition matcher -----------------------------------------------------

def _cond_matches(toks, facts, ax, _depth=0):
    """Boolean-evaluate pre-tokenised conditions against an item's facts.

    `ax` is the alias context (values + precomputed membership sets).
    Grammar: space/AND = conjunction, OR = disjunction, ! = negation,
    (...) = grouping. Unresolvable dynamic conditions evaluate False (base
    context) except item-type qualifiers we can't model (treated as satisfiable
    for uniques/sets — an upper bound).
    """
    if _depth > 12 or not toks:
        return True
    pos = 0

    def peek():
        return toks[pos] if pos < len(toks) else None

    def parse_or():
        nonlocal pos
        v = parse_and()
        while peek() == 'OR':
            pos += 1
            v = parse_and() or v
        return v

    def parse_and():
        nonlocal pos
        v = parse_not()
        while peek() not in (None, 'OR', ')'):
            if peek() == 'AND':
                pos += 1
            v = parse_not() and v
        return v

    def parse_not():
        nonlocal pos
        if peek() == '!':            # '!(' form
            pos += 1
            return not parse_not()
        return parse_primary()

    def parse_primary():
        nonlocal pos
        t = peek()
        if t == '(':
            pos += 1
            v = parse_or()
            if peek() == ')':
                pos += 1
            return v
        pos += 1
        return _atom(t, facts, ax, _depth)

    return parse_or()


def _atom(tok, facts, ax, depth):
    """Evaluate one condition atom (may carry a leading '!')."""
    if not tok or tok in ('AND', 'OR'):
        return True
    if tok.startswith('!'):
        return not _atom(tok[1:], facts, ax, depth)

    # Comparison: FIELD op VALUE  (op in < > = ~). Cheap pre-check first — most
    # tokens are bare flags/codes with no operator, so we skip the regex.
    cm = _RE_COMPARE.match(tok) if ('<' in tok or '>' in tok
                                    or '=' in tok or '~' in tok) else None
    if cm:
        field, op, val = cm.group(1), cm.group(2), cm.group(3)
        if field == 'RUNE':
            n = facts.get('rune')
            if n is None:
                return False
            return _num_cmp(n, op, val)
        if field == 'FILTLVL':
            return _num_cmp(facts['filtlvl'], op, val)
        if field == 'QTY':
            return _num_cmp(facts.get('qty', 1), op, val)
        # Stat values default to 0 (e.g. STAT360 LLD marker, STAT477 corrupted).
        if field.startswith('STAT'):
            return _num_cmp(0, op, val)
        # Other situational numerics (MAPID, CLVL, ILVL, GOLD, ...) default OFF
        # so we render the BASE on-ground name, not map/context-specific extras.
        return False

    # Alias used as a set-condition. Star tiers / rune sets are precomputed to
    # O(1) membership tests; anything else falls back to a full recursive eval.
    cs = ax['code_sets'].get(tok)
    if cs is not None:
        return facts.get('code') in cs
    rs = ax['rune_sets'].get(tok)
    if rs is not None:
        return facts.get('rune') in rs
    if tok in ax['values']:
        return _cond_matches(_tokenize_cond(ax['values'][tok]), facts, ax, depth + 1)

    # Boolean flags we model directly
    if tok == 'UNI':
        return facts.get('uni', False)
    if tok == 'SET':
        return facts.get('set', False)
    if tok == 'ID':
        return facts.get('id', False)
    if tok == 'ETH':
        return facts.get('eth', False)
    if tok == 'RUNE':
        return facts.get('rune') is not None

    # Quality flags our synthetic uniques/sets/runes definitely never have.
    if tok in _NEVER_FLAGS:
        return False

    # Non-ground inventory locations never apply to a dropped item.
    if tok in _LOCATION_OFF:
        return False
    if tok == 'GROUND':
        return True

    # Item code (lowercase). Checked before generic flag handling so a code
    # like 'axe' is matched against the item, not treated as the AXE flag.
    if _RE_ITEM_CODE.match(tok) and any(c.isalpha() for c in tok):
        return facts.get('code') == tok

    # Any other UPPERCASE qualifier (item category, class, base tier, location):
    # we don't model the base's type, so treat it as satisfiable for a unique/
    # set item (upper bound) and not applicable to a rune.
    return facts.get('uni', False) or facts.get('set', False)


def _num_cmp(n, op, val):
    try:
        if op == '~':
            lo, hi = val.split('-')
            return int(lo) <= n <= int(hi)
        v = int(val)
    except (ValueError, TypeError):
        return True
    return {'<': n < v, '>': n > v, '=': n == v}.get(op, True)


# --- render / length -------------------------------------------------------

def _strip_tooltips(text):
    """Drop {tooltip} blocks — only the on-ground name has a width budget."""
    out, depth = [], 0
    for ch in text:
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return ''.join(out)


def _process_output(output, name_literals, values):
    """Turn a rule's output into its on-ground text.

    Aliases are expanded; tooltips, sound id and other non-text markers are
    removed; colours become 2-char codes; leftover dynamic value tokens become
    '#'. Every place a name would appear — a %NAME% token, or ANY of this
    code's literal name variants (`name_literals`) — is replaced with a sentinel
    so the caller can place a single real name. Collapsing all variants is what
    stops a code's alternate names (e.g. base name + two rename schemes) from
    being summed together. Used by both the width count and the line preview.
    """
    s = _expand_aliases(output, values)
    s = _strip_inline_formulas(s)        # $f(...) -> '0'
    s = _strip_tooltips(s)
    s = _RE_MARKER_TOKEN.sub('', s)      # sound id + non-text markers
    s = _RE_NAME_TOKEN.sub(_NAME_SENTINEL, s)
    for lit in name_literals:            # longest-first (caller pre-sorts)
        if lit:
            s = s.replace(lit, _NAME_SENTINEL)
    s = _RE_COLOR_TOKEN.sub(lambda m: _COLOR_ABBR.get(m.group(1), '..'), s)
    s = _RE_VALUE_TOKEN.sub('#', s)      # leftover dynamic value (~1 char)
    return s


def _name_literals(item):
    """The name strings to collapse for an item, longest-first."""
    lits = set(item.get('name_literals') or ())
    lits.add(item['name'])
    return sorted((l for l in lits if l), key=len, reverse=True)


def _decoration_width(output, name_literals, values):
    """On-ground character count a rule adds, EXCLUDING the item name itself."""
    return len(_process_output(output, name_literals, values)
               .replace(_NAME_SENTINEL, ''))


def _render_chain(item, rules, values):
    """Assemble the computed on-ground line from a chain of rules.

    Concatenates each rule's processed output (file order) and places the real
    item name at the first sentinel, dropping the rest. By construction
    len(result) == name length + sum of the rules' decoration widths, i.e. it
    equals the number reported for the item.
    """
    name = item['name']
    lits = _name_literals(item)
    s = ''.join(_process_output(r.output, lits, values) for r in rules)
    first = s.find(_NAME_SENTINEL)
    if first < 0:
        return name + s            # no name slot found; show name up front
    return s[:first] + name + s[first + 1:].replace(_NAME_SENTINEL, '')


def _context_cache(broad, kind, ax):
    """For one class, precompute which code-independent broad rules match in
    each (eth, filtlvl) context. Returns {(eth, filtlvl): frozenset(idx)}.

    Code-independent rules give the same result for every item of the class, so
    evaluating them once per context (instead of once per item) is the main
    speed-up. Code-dependent rules are still evaluated live per item.
    """
    cache = {}
    base = {'kind': kind, 'uni': kind == 'uni', 'set': kind == 'set',
            'id': False, 'rune': None, 'code': None}
    indep = [r for r in broad if not r.code_dep]
    for eth in (False, True):
        for fl in _REPRESENTATIVE_FILTLVLS:
            facts = dict(base, filtlvl=fl, eth=eth, qty=1)
            cache[(eth, fl)] = frozenset(
                r.idx for r in indep if _cond_matches(r.toks, facts, ax))
    return cache


def _resolve_chain(item, candidates, ax, indep_cache=None):
    """Return (length, rendered_preview) for the longest applicable render.

    `candidates` is the pre-filtered, file-order list of rules that could match
    this item (see _candidate_rules). We walk it for each representative
    context, summing decoration until the first terminal (no-%CONTINUE%) match,
    and keep the longest total. `indep_cache` (if given) supplies precomputed
    match results for code-independent rules, keyed by (eth, filtlvl).
    """
    best_len, best_chain = -1, []
    if item.get('uni') or item.get('set'):
        eth_options = item.get('eth_opts', (False, True))
    else:
        eth_options = (False,)
    name_len = len(item['name'])
    values = ax['values']
    lits = _name_literals(item)
    deco_cache = {}    # r.idx -> decoration width (constant per item)
    for filtlvl in _REPRESENTATIVE_FILTLVLS:
        for eth in eth_options:
            facts = dict(item, filtlvl=filtlvl, eth=eth, qty=1)
            indep = indep_cache[(eth, filtlvl)] if indep_cache else None
            deco = 0
            chain = []
            for r in candidates:
                if r.code_dep or indep is None:
                    if not _cond_matches(r.toks, facts, ax):
                        continue
                elif r.idx not in indep:
                    continue
                w = deco_cache.get(r.idx)
                if w is None:
                    w = _decoration_width(r.output, lits, values)
                    deco_cache[r.idx] = w
                deco += w
                chain.append(r)
                if not r.continues:
                    break      # terminal rule — chain ends here
            if name_len + deco > best_len:
                best_len = name_len + deco
                best_chain = chain
    return best_len, _render_chain(item, best_chain, values)


def _alias_membership_sets(alias_values):
    """Precompute O(1) membership sets for OR-list aliases.

    Returns (code_sets, rune_sets):
      * code_sets[name] = frozenset of item codes  (e.g. 4_STAR_UNIQUE)
      * rune_sets[name] = frozenset of rune numbers (e.g. CRAFTING_RUNES_SET)
    Only aliases whose value is a pure OR-list are captured; others fall back
    to recursive evaluation in the matcher.
    """
    code_sets, rune_sets = {}, {}
    for name, val in alias_values.items():
        parts = re.findall(r'[^\s()]+', val)
        if not parts or 'OR' not in parts:
            continue
        atoms = [p for p in parts if p != 'OR']
        if atoms and all(_RE_ITEM_CODE.match(p) and any(c.isalpha() for c in p)
                         for p in atoms):
            code_sets[name] = frozenset(atoms)
            continue
        rune_nums = [re.match(r'^RUNE=(\d+)$', p) for p in atoms]
        if atoms and all(rune_nums):
            rune_sets[name] = frozenset(int(m.group(1)) for m in rune_nums)
    return code_sets, rune_sets


def _bucket_rules(rules, ax):
    """Pre-split a file's rules into candidate buckets, computed once.

    Returns (broad_uni, broad_set, by_code, rune):
      * broad_uni/broad_set — code-agnostic (or category-gated) formatting rules
        that can actually apply to a unique / set item. A rule is relevant to a
        class if it mentions that class, or mentions neither (a universal !ID
        rule). ID-gated rules are excluded, and code-independent rules that
        never match the class in any context are pruned (they only cost time).
      * by_code — code -> rules that name that specific code
      * rune    — rules mentioning RUNE
    """
    cs, rs, vals = ax['code_sets'], ax['rune_sets'], ax['values']

    def code_dependent(r):
        # Its match can depend on the item's code (specific codes or any alias
        # condition), so it can never be pruned class-wide or context-cached.
        r.code_dep = bool(r.codes) or any(t in cs or t in rs or t in vals
                                          for t in r.toks)
        return r.code_dep

    def can_match(r, kind):
        if code_dependent(r):
            return True
        base = {'kind': kind, 'uni': kind == 'uni', 'set': kind == 'set',
                'id': False, 'rune': None, 'code': None}
        return any(_cond_matches(r.toks, dict(base, filtlvl=fl, eth=eth, qty=1), ax)
                   for fl in _REPRESENTATIVE_FILTLVLS for eth in (False, True))

    broad_uni, broad_set, by_code, rune = [], [], {}, []
    for r in rules:
        if r.mentions_rune:
            rune.append(r)
        if r.requires_id:
            continue
        if not r.codes or r.has_category:
            universal = not r.mentions_uni and not r.mentions_set
            if (r.mentions_uni or universal) and can_match(r, 'uni'):
                broad_uni.append(r)
            if (r.mentions_set or universal) and can_match(r, 'set'):
                broad_set.append(r)
        for c in r.codes:
            by_code.setdefault(c, []).append(r)
    return broad_uni, broad_set, by_code, rune


def _candidate_rules(item, broad_uni, broad_set, by_code, rune):
    """Build the file-order candidate list for one item from the buckets."""
    kind = item['kind']
    if kind == 'rune':
        return rune
    if kind == 'pd2':
        # PD2 items render from their own code rules only — they aren't uniques
        # or sets, so the class formatting buckets don't apply to them.
        return by_code.get(item['code'], [])
    broad = broad_uni if kind == 'uni' else broad_set
    specific = by_code.get(item.get('code'), [])
    if not specific:
        return broad
    seen = {r.idx for r in broad}
    extra = [r for r in specific if r.idx not in seen]
    return sorted(broad + extra, key=lambda r: r.idx)


def _decoration_text_only(output, alias_values):
    """Extract the literal display text of a rule (no tokens, no tooltip)."""
    s = _strip_tooltips(output)
    s = _RE_MARKER_TOKEN.sub('', s)
    s = re.sub(r'%[A-Za-z0-9_][A-Za-z0-9_-]*%', '', s)   # drop all %tokens%
    return s.strip()


def _looks_like_name(text):
    """True if text is real name text, not pure decoration (stars, [C], etc.)."""
    if not text:
        return False
    letters = sum(c.isalpha() for c in text)
    # Needs real words and shouldn't be dominated by decoration symbols.
    return letters >= 3 and '[C]' not in text and text.strip('*  ') != ''


def _file_length_ranking(fp, top_n):
    """Return the top-N longest items for one filter file.

    Each entry: (length, kind, code, name, computed_line). Deduped by name,
    keeping the longest render.
    """
    try:
        raw_lines = fp.read_text(encoding='utf-8', errors='replace').splitlines()
    except Exception:
        return []
    rules, alias_values = _parse_rules(raw_lines)
    if not rules:
        return []
    code_sets, rune_sets = _alias_membership_sets(alias_values)
    ax = {'values': alias_values, 'code_sets': code_sets, 'rune_sets': rune_sets}
    broad_uni, broad_set, by_code, rune = _bucket_rules(rules, ax)
    uni_cache = _context_cache(broad_uni, 'uni', ax)
    set_cache = _context_cache(broad_set, 'set', ax)

    rows = {}   # name -> (length, kind, code, name, computed_line)
    for item in _collect_items_with_aliases(rules, alias_values):
        cands = _candidate_rules(item, broad_uni, broad_set, by_code, rune)
        cache = uni_cache if item['kind'] == 'uni' else (
                set_cache if item['kind'] == 'set' else None)
        length, line = _resolve_chain(item, cands, ax, cache)
        if length <= 0:
            continue
        name = item['name']
        prev = rows.get(name)
        if prev is None or length > prev[0]:
            rows[name] = (length, item['kind'],
                          item.get('code') or item.get('rune'), name, line)
    return sorted(rows.values(), key=lambda r: r[0], reverse=True)[:top_n]


def analyze_lengths(filter_files, top_n=5):
    """Print the top-N longest estimated on-ground display names, per file."""
    # Theme decoration uses non-ASCII glyphs; don't let a narrow console
    # encoding crash the report — replace anything it can't encode.
    try:
        sys.stdout.reconfigure(errors='replace')
    except Exception:
        pass

    sections = [(fp, _file_length_ranking(fp, top_n)) for fp in filter_files]
    if not any(rows for _, rows in sections):
        return

    print()
    print('=' * 70)
    print(f"  DISPLAY-NAME LENGTH CHECK - top {top_n} longest per filter (first pass)")
    print(f"  warnings only; nothing fails. Length = on-ground chars, each")
    print(f"  colour counts as {COLOR_RENDER_WIDTH}. '=>' shows the computed line "
          f"(colours as 2-char codes).")
    print('=' * 70)
    for fp, rows in sections:
        if not rows:
            continue
        print(f"\n  {fp.name}")
        for length, kind, code, name, line in rows:
            print(f"    [WARNING] {length:>4}  {kind:<4} {str(code):<5} \"{name}\"")
            print(f"              => {line}")


def _collect_items_with_aliases(rules, alias_values):
    """Build the items to length-check: 33 runes, every unique/set !ID name
    (one item per ETH context, using the longest name variant), and the named
    PD2_items codes."""
    items = {}

    for n, name in RUNE_NAMES.items():
        items[('rune', n)] = {'kind': 'rune', 'rune': n, 'name': name}

    # Gather literal-name rules. A single code can have several name variants
    # (a base name plus one or more rename schemes, or a caps callout); the game
    # shows one at a time, so we collect every variant per code (`lit_by_code`)
    # to collapse them to a single name slot when rendering, and group the
    # unique/set ones by ETH context to report the LONGEST as the worst case.
    lit_by_code = {}     # code -> set of every literal name seen for it
    groups = {}          # (kind, code, eth_opts) -> set of uni/set literals
    for r in rules:
        if len(r.codes) != 1:
            continue
        # A literal-name rule's output, once tokens/tooltips are stripped, is
        # real alphabetic name text (not just decoration like "*  [C] *").
        literal = _decoration_text_only(_expand_aliases(r.output, alias_values),
                                        alias_values)
        if not _looks_like_name(literal):
            continue
        code = next(iter(r.codes))
        lit_by_code.setdefault(code, set()).add(literal)
        cond = r.cond
        is_uni = re.search(r'\bUNI\b', cond) is not None
        is_set = re.search(r'\bSET\b', cond) is not None
        if (is_uni or is_set) and re.search(r'!\s*ID\b', cond):
            kind = 'uni' if is_uni else 'set'
            if re.search(r'!\s*ETH\b', cond):
                eth_opts = (False,)
            elif re.search(r'\bETH\b', cond):
                eth_opts = (True,)
            else:
                eth_opts = (False, True)
            groups.setdefault((kind, code, eth_opts), set()).add(literal)

    for (kind, code, eth_opts), literals in groups.items():
        items.setdefault((kind, code, eth_opts), {
            'kind': kind, 'code': code,
            'name': max(literals, key=len),       # worst case for truncation
            'uni': kind == 'uni', 'set': kind == 'set', 'id': False,
            'eth_opts': eth_opts,
            'name_literals': lit_by_code[code],
        })

    for r in rules:
        for code in r.codes:
            if code in PD2_ITEM_NAMES:
                items.setdefault(('pd2', code), {
                    'kind': 'pd2', 'code': code, 'name': PD2_ITEM_NAMES[code],
                    'name_literals': lit_by_code.get(code, set())})
    return list(items.values())


def _order1_filter_files(script_dir):
    """Return the 'order 1' filter from each folder's filter_definitions.json.

    Each theme group (root/standard, hyper, talrasha, vanilla, kassahi,
    phil777) lists its filters in a filter_definitions.json; the entry keyed
    "1" is that group's top/representative filter. Length-checking just these
    instead of every built .filter keeps the pass fast while still covering
    each distinct visual theme. The upstream clone under temp/ is skipped.
    """
    files, seen = [], set()
    for defs in sorted(script_dir.rglob('filter_definitions.json')):
        rel = defs.relative_to(script_dir)
        if rel.parts and rel.parts[0] in ('temp', '.venv'):
            continue
        try:
            info = json.loads(defs.read_text(encoding='utf-8')).get('filter_info', {})
        except Exception:
            continue
        entry = info.get('1') or {}
        fp = defs.parent / entry.get('file_name', '')
        if entry.get('file_name') and fp.exists() and fp not in seen:
            seen.add(fp)
            files.append(fp)
    return files


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args       = sys.argv[1:]
    errors_only  = '--errors-only' in args
    root_only    = '--root-only' in args
    length_check = '--length-check' in args   # opt-in; off by default
    # '--all' is retained as a no-op for backwards compatibility (it's now the default)
    args = [a for a in args
            if a not in ('--errors-only', '--root-only', '--all', '--length-check')]

    script_dir = Path(__file__).parent

    if args:
        filter_files = [Path(a) for a in args]
    else:
        # Default: root output filters + filtergroups/ outputs (skip builderfilter
        # source fragments and any cloned upstream repos under temp/).
        # --root-only skips the filtergroups/ scan.
        filter_files = sorted(script_dir.glob('*.filter'))
        if not root_only:
            fg = script_dir / 'filtergroups'
            if fg.is_dir():
                filter_files += sorted(fg.rglob('*.filter'))

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

    # Display-name length check (first pass, warnings only — never fails CI).
    # Opt-in via --length-check; scans the order-1 filter of each theme group
    # (see _order1_filter_files). Off by default because it is comparatively slow.
    if length_check:
        analyze_lengths(_order1_filter_files(script_dir))

    return 1 if total_errors > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
