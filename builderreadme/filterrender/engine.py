"""Evaluate a built .filter for a sample item and return its on-ground label.

This is a renderer's model of PD2 loot-filter semantics, good enough to illustrate a
filter: rules are matched top to bottom, %CONTINUE% chains them (%NAME% is the text built
so far), the first matching rule without %CONTINUE% ends the chain, and an empty output
hides the item. Conditions or stats the item doesn't define evaluate as 0 / false.
Tooltips ({...}) are parsed out but not drawn.
"""
import math
import re

# PD2 / D2 text colors (approximate in-game RGB).
COLORS = {
    "WHITE": (232, 232, 232), "GRAY": (125, 125, 125), "LIGHT_GRAY": (175, 175, 175),
    "BLUE": (110, 110, 255), "YELLOW": (255, 255, 100), "GOLD": (199, 179, 119),
    "GREEN": (0, 252, 0), "DARK_GREEN": (0, 128, 64), "ORANGE": (255, 168, 0),
    "RED": (255, 77, 77), "TAN": (165, 145, 105), "BLACK": (40, 40, 40),
    "PURPLE": (174, 0, 255), "CORAL": (255, 128, 128), "SAGE": (155, 205, 140),
    "TEAL": (0, 210, 210),
}
QUALITY_COLOR = {"NMAG": "WHITE", "MAG": "BLUE", "RARE": "YELLOW", "SET": "GREEN",
                 "UNI": "GOLD", "CRAFT": "ORANGE"}

_TOKEN = re.compile(r"%([A-Za-z0-9_]+)(?:-([0-9A-Fa-f]+))?%")
_WORD = re.compile(r"(?<![A-Za-z0-9_])([A-Za-z0-9_]*[A-Za-z_][A-Za-z0-9_]*)(?![A-Za-z0-9_])")  # aliases may start with a digit (4_STAR_UNIQUE)
_CMP = re.compile(r"^(.+?)(<=|>=|<|>|=|~)(.+)$")


class Filter:
    def __init__(self, path):
        self.aliases, self.rules = {}, []
        with open(path, encoding="utf-8") as f:
            for raw in f:
                # The game reads each row with everything from // stripped, then trimmed.
                line = raw.split("//", 1)[0].strip()
                m = re.match(r"^Alias\[([^\]]+)\]:\s?(.*)$", line)
                if m:
                    self.aliases.setdefault(m.group(1), m.group(2))
                    continue
                if line.startswith("ItemDisplay["):
                    i = line.find("]:")
                    if i > 0:
                        self.rules.append((line[len("ItemDisplay["):i], line[i + 2:]))
        self._cond_cache = {}
        self._out_cache = {}

    # ---- alias expansion -----------------------------------------------------------
    def _expand_cond(self, text, depth=0):
        if depth > 12:
            return text

        def repl(m):
            name = m.group(1)
            if name not in self.aliases:
                return name
            val = self._expand_cond(self.aliases[name].strip(), depth + 1)
            return val if re.fullmatch(r"-?\d+(\.\d+)?", val) or val.startswith("(") else f"({val})"
        return _WORD.sub(repl, text)

    def _expand_out(self, text, depth=0):
        if depth > 12:
            return text
        return _TOKEN.sub(lambda m: self._expand_out(self.aliases[m.group(1)], depth + 1)
                          if m.group(1) in self.aliases and m.group(2) is None else m.group(0), text)

    def cond(self, raw):
        if raw not in self._cond_cache:
            self._cond_cache[raw] = _parse_cond(self._expand_cond(raw))
        return self._cond_cache[raw]

    def out(self, raw):
        if raw not in self._out_cache:
            self._out_cache[raw] = self._expand_out(raw)
        return self._out_cache[raw]

    # ---- evaluation ----------------------------------------------------------------
    def label(self, item, filtlvl, trace=None):
        """Return (segments, border, shown). segments: list of lines top to bottom as drawn in
        game, each a list of (text, rgb). Lines are built in string order and the game draws
        them bottom-up (each new line pushes the earlier text up), so they are reversed at the
        end. trace, if a list, collects (condition, label text) for every matching rule."""
        ctx = Context(item, filtlvl)
        color = COLORS[item_color(item)]
        name = [[(item.get("name", item["code"]), color)]]
        if item.get("base_line"):  # runewords: the base name sits under the runeword name
            name = [[(item["base_line"], color)], [(item.get("name", item["code"]), color)]]
        border = None
        matched = False
        for cond_raw, out_raw in self.rules:
            if not ctx.eval(self.cond(cond_raw)):
                continue
            matched = True
            text = self.out(out_raw)
            label_part, _tooltip = _split_tooltip(text)
            if trace is not None:
                trace.append((cond_raw, label_part))
            cont = "%CONTINUE%" in label_part
            new, b = _render_label(label_part, name, ctx, item)
            border = b or border
            name = new
            if not cont:
                break
        name = _trim(_resolve_conditionals(name))
        shown = matched is False or bool(name)
        return name[::-1], border, shown


# %CL% / %CS% markers carried through the %CONTINUE% chain (a later rule can fill the text
# around them), resolved on the finished label.
_CL, _CS = "\x01", "\x02"


def _resolve_conditionals(lines):
    """%CL% becomes a line break only with visible text on both sides of it on its line, so it
    never makes a blank line or two breaks in a row; %CS% becomes a space only between two
    visible characters, so it never doubles a space or starts / ends a line."""
    def visible(segs):
        return "".join(t for t, _ in segs if t not in (_CL, _CS))

    out = []
    for line in lines:
        cur = [[]]
        for k, (t, c) in enumerate(line):
            rest = visible(line[k + 1:])
            if t == _CL:
                if visible(cur[-1]).strip() and rest.strip():
                    while cur[-1] and cur[-1][-1][0] == " ":  # a %CS% right before the break
                        cur[-1].pop()
                    cur.append([])
            elif t == _CS:
                before = visible(cur[-1])
                if before and not before[-1].isspace() and rest and not rest[0].isspace():
                    cur[-1].append((" ", c))
            else:
                cur[-1].append((t, c))
        out.extend(cur)
    return out


def _trim(lines):
    """The game trim()s the finished label: whitespace (spaces and line breaks) at its very
    start and end is dropped; spacing inside it stays."""
    flat = []  # (line index, text, rgb)
    for k, line in enumerate(lines):
        flat.extend((k, t, c) for t, c in line)
        flat.append((k, "\n", None))
    text = "".join(t for _, t, _ in flat)
    lead = len(text) - len(text.lstrip())
    keep = len(text.rstrip())
    out, pos = [[]], 0
    for _, t, c in flat:
        lo, hi = max(lead - pos, 0), min(keep - pos, len(t))
        pos += len(t)
        if hi <= lo:
            continue
        piece = t[lo:hi]
        if c is None:
            out.append([])
        else:
            out[-1].append((piece, c))
    return out if any(out) else []


def item_color(item):
    if item.get("color"):
        return item["color"]
    for q, c in QUALITY_COLOR.items():
        if q in item.get("flags", ()):
            if q == "NMAG" and ("ETH" in item["flags"] or item.get("num", {}).get("SOCK", 0) > 0):
                return "GRAY"
            return c
    return "WHITE"


# ---- conditions ------------------------------------------------------------------------
def _tokenize(cond):
    toks, i, n = [], 0, len(cond)
    while i < n:
        c = cond[i]
        if c.isspace():
            i += 1
        elif c in "()":
            toks.append(c)
            i += 1
        elif cond.startswith("$f(", i) or cond.startswith("!$f(", i):
            j = i + (4 if c == "!" else 3)
            depth = 1
            while j < n and depth:
                depth += cond[j] == "("
                depth -= cond[j] == ")"
                j += 1
            k = j
            while k < n and not cond[k].isspace() and cond[k] not in "()":
                k += 1
            toks.append(cond[i:k])
            i = k
        else:
            j = i
            while j < n and not cond[j].isspace() and cond[j] not in "()":
                j += 1
            # an atom like "!(" is split: '!' then '('
            word = cond[i:j]
            if word == "!" and j < n and cond[j] == "(":
                toks.append("!")
            else:
                toks.append(word)
            i = j
    return toks


def _parse_cond(text):
    toks = _tokenize(text)
    pos = 0

    def peek():
        return toks[pos] if pos < len(toks) else None

    def p_or():
        nonlocal pos
        terms = [p_and()]
        while peek() == "OR":
            pos += 1
            terms.append(p_and())
        return terms[0] if len(terms) == 1 else ("or", terms)

    def p_and():
        nonlocal pos
        terms = [p_not()]
        while peek() not in (None, "OR", ")"):
            if peek() == "AND":
                pos += 1
                continue
            terms.append(p_not())
        return terms[0] if len(terms) == 1 else ("and", terms)

    def p_not():
        nonlocal pos
        if peek() == "!":
            pos += 1
            return ("not", p_not())
        return p_prim()

    def p_prim():
        nonlocal pos
        t = peek()
        pos += 1
        if t == "(":
            v = p_or()
            if peek() == ")":
                pos += 1
            return v
        if t is None or t == ")":
            return ("const", True)
        return ("atom", t)

    return p_or() if toks else ("const", True)


class Context:
    def __init__(self, item, filtlvl):
        self.item = item
        self.flags = set(item.get("flags", ())) | {"GROUND"}
        self.num = {"FILTLVL": filtlvl, "CLVL": 86, "DIFF": 2, "MAPID": 2, "QTY": 1, "ILVL": 85,
                    "ALVL": 85, "LVLREQ": 60, "CHARSTAT12": 90}
        self.num.update(item.get("num", {}))
        if item.get("rune"):
            self.num["RUNE"] = item["rune"]
        # Friendly stat names and their D2 stat ids are interchangeable (STR == STAT0 ...).
        for name, sid in STAT_IDS.items():
            key = f"STAT{sid}"
            if name in self.num and key not in self.num:
                self.num[key] = self.num[name]
            elif key in self.num and name not in self.num:
                self.num[name] = self.num[key]
        res = [self.num.get(k, 0) for k in ("FRES", "CRES", "LRES", "PRES")]
        if "RES" not in self.num and min(res) > 0:
            self.num["RES"] = min(res)
        self.num.setdefault("SOCKETS", self.num.get("SOCK", 0))

    def eval(self, node):
        kind = node[0]
        if kind == "const":
            return node[1]
        if kind == "not":
            return not self.eval(node[1])
        if kind == "and":
            return all(self.eval(x) for x in node[1])
        if kind == "or":
            return any(self.eval(x) for x in node[1])
        return self.atom(node[1])

    def value(self, name):
        if name in self.num:
            return self.num[name]
        if name == "RUNE":
            return self.item.get("rune", 0)
        return 0

    def expr(self, text):
        """Numeric expression: fields joined by + - * /, or a $f(...) formula."""
        text = text.strip()
        if text.startswith("$f("):
            return self.formula(text[3:-1])
        return self.formula(text)

    def formula(self, text):
        def ident(m):
            w = m.group(1)
            if w in _FUNCS:
                return f"_{w}"
            if w in ("TRUE", "FALSE"):
                return "1" if w == "TRUE" else "0"
            return repr(self.value(w))
        py = _WORD.sub(ident, text.replace(",", " , "))
        py = py.replace("<>", "!=")
        py = re.sub(r"(?<![<>!=])=(?!=)", "==", py)
        try:
            v = eval(py, {"__builtins__": {}}, _FUNC_IMPL)
            return float(v)
        except Exception:
            return 0.0

    def atom(self, t):
        neg = False
        while t.startswith("!"):
            neg, t = not neg, t[1:]
        v = self._atom(t)
        return (not v) if neg else v

    def _atom(self, t):
        if t == "TRUE":
            return True
        if t == "FALSE":
            return False
        if t.startswith("$f(") and t.endswith(")"):
            return self.formula(t[3:-1]) != 0
        m = _CMP.match(t)
        if m and not re.fullmatch(r"[0-9a-z]+", t):
            lhs, op, rhs = m.groups()
            # Fields that only exist on one kind of item (gold piles, maps, gems): a
            # comparison on an item without the field never matches.
            if lhs in _TYPE_FIELDS and lhs not in self.num:
                return False
            if lhs.startswith("$f("):
                left = self.formula(lhs[3:lhs.rfind(")")])
            elif "," in lhs:                       # MULTIa,b: not modelled
                left = 0
            else:
                left = sum(self.value(p) if not re.fullmatch(r"-?\d+", p) else int(p)
                           for p in lhs.split("+"))
            if op == "~":
                lo, _, hi = rhs.partition("-")
                return _num(lo) <= left <= _num(hi)
            right = _num(rhs) if re.fullmatch(r"-?\d+(\.\d+)?", rhs) else self.formula(rhs)
            return {"<": left < right, ">": left > right, "=": left == right,
                    "<=": left <= right, ">=": left >= right}[op]
        if re.fullmatch(r"[0-9a-z]{2,6}", t) and any(ch.isalpha() for ch in t):
            return self.item["code"] == t
        if t == "RUNE":
            return bool(self.item.get("rune"))
        return t in self.flags


_TYPE_FIELDS = {"GOLD", "MAPTIER", "MAPID_ITEM", "GEM", "GEMTYPE", "RUNE"}

# Friendly condition names <-> D2 item stat ids (both spellings appear in the filters).
STAT_IDS = {"STR": 0, "ENE": 1, "DEX": 2, "VIT": 3, "LIFE": 7, "MANA": 9, "EDEF": 16, "EDAM": 18,
            "AR": 19, "MINDMG": 21, "MAXDMG": 22, "FRES": 39, "LRES": 41, "CRES": 43, "PRES": 45,
            "LL": 60, "ML": 62, "GFIND": 79, "MFIND": 80, "IAS": 93, "FRW": 96, "FHR": 99,
            "FCR": 105, "SOCK": 194}


def _num(s):
    try:
        return float(s)
    except ValueError:
        return 0.0


def _if(c, a, b=0):
    return a if c else b


_FUNCS = {"ROUND", "MAX", "MIN", "ABS", "IF", "OR", "AND", "FLOOR", "CEIL", "NOT"}
_FUNC_IMPL = {"_ROUND": lambda x, *a: round(x), "_MAX": max, "_MIN": min, "_ABS": abs, "_IF": _if,
              "_OR": lambda *a: any(a), "_AND": lambda *a: all(a), "_FLOOR": math.floor,
              "_CEIL": math.ceil, "_NOT": lambda a: not a}


# ---- output ----------------------------------------------------------------------------
def _split_tooltip(text):
    """Split 'label{tooltip}more-label' into (label without tooltip, tooltip)."""
    out, tip, depth = [], [], 0
    for ch in text:
        if ch == "{":
            depth += 1
            continue
        if ch == "}":
            depth = max(0, depth - 1)
            continue
        (tip if depth else out).append(ch)
    return "".join(out), "".join(tip)


_VALUE_TOKENS = {"QTY", "ILVL", "ALVL", "EDAM", "EDEF", "RES", "DEF", "LIFE", "MANA", "SOCK", "LVLREQ",
                 "CRAFTALVL", "REROLLALVL", "PLR", "REPLIFE", "WPNSPD", "UPLVL", "UPSTR", "UPDEX", "FCR",
                 "IAS", "FHR", "FRW", "STR", "DEX", "MINDMG", "MAXDMG", "ED", "PRICE", "SELLPRICE",
                 "SOCKETS", "RANGE", "MFIND", "GFIND", "RUNE"}
_IGNORED = {"CONTINUE", "TIER", "SOUNDID", "MAP", "DOT", "PX", "NOTIFY", "IGNORE"}


def _fmt(v):
    v = float(v)
    return str(int(v)) if v == int(v) else f"{v:.2f}".rstrip("0").rstrip(".")


def _render_label(text, prev, ctx, item):
    """Turn one rule's label text into lines of (text, rgb). Returns (lines, border_rgb)."""
    color = COLORS[item_color(item)]
    lines = [[]]
    border = None
    i = 0
    # evaluate $f(...) in output first
    while "$f(" in text:
        s = text.index("$f(")
        j, depth = s + 3, 1
        while j < len(text) and depth:
            depth += text[j] == "("
            depth -= text[j] == ")"
            j += 1
        text = text[:s] + _fmt(ctx.formula(text[s + 3:j - 1])) + text[j:]
    for m in _TOKEN.finditer(text):
        if m.start() > i:
            lines[-1].append((text[i:m.start()], color))
        i = m.end()
        tok, arg = m.group(1), m.group(2)
        if tok == "NAME":
            for k, line in enumerate(prev):
                if k:
                    lines.append([])
                lines[-1].extend(line)
        elif tok in COLORS:
            color = COLORS[tok]
        elif tok == "NL":
            lines.append([])
        elif tok == "CL":  # conditional newline / space: decided on the finished label
            lines[-1].append((_CL, color))
        elif tok == "CS":
            lines[-1].append((_CS, color))
        elif tok == "BORDER":
            border = color_from_index(arg)
        elif tok in _IGNORED:
            pass
        elif tok == "RUNENUM":
            lines[-1].append((str(item.get("rune", "")), color))
        elif tok == "RUNENAME":
            lines[-1].append((item.get("rune_name", ""), color))
        elif tok == "BASENAME":
            lines[-1].append((item.get("base", item.get("name", "")), color))
        elif tok in _VALUE_TOKENS or re.fullmatch(r"(STAT|CHARSTAT|SK|TABSK|CLSK)\d+", tok):
            lines[-1].append((_fmt(ctx.value(tok)), color))
        else:
            pass  # unknown token: drop
    if i < len(text):
        lines[-1].append((text[i:], color))
    lines = [[(t, c) for t, c in line if t] for line in lines]
    while lines and not lines[-1]:
        lines.pop()
    return lines, border


# D2 palette indices used by %BORDER-xx%: rough hues for the common ones.
_PALETTE = {"0A": (255, 40, 40), "0B": (255, 40, 40), "0D": (255, 255, 255), "21": (255, 255, 255),
            "4A": (255, 150, 0), "55": (199, 179, 119), "68": (255, 220, 60), "84": (0, 200, 0),
            "97": (150, 60, 255), "9B": (174, 0, 255), "9D": (174, 0, 255), "62": (210, 210, 210),
            "ED": (90, 90, 255), "7D": (0, 200, 120), "D3": (255, 100, 100), "50": (230, 230, 230)}


def color_from_index(hexidx):
    return _PALETTE.get((hexidx or "").upper(), (200, 200, 200))
