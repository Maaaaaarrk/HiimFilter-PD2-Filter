"""Find items a filter hides but still marks on the minimap.

The game reads a filter twice. The display pass stops at the first matching rule without
%CONTINUE%; when that rule shows no text (": " or ": {%NAME%}") the item is hidden. The map
pass walks the same chain but does not stop at a hiding rule: a hiding rule drops the
markers collected so far, and the minimap markers (%MAP-..%, %DOT-..%, %PX-..%) of the later
%CONTINUE% rules and of the first later matching rule that shows text are drawn, so an item
hidden by one rule can still be marked by a later one.

For every marker rule this builds sample items that match it (one branch of each OR, on a
real base whose keywords fit), runs both passes at every filter level, and reports each
pair of hiding rule and marker rule that meet on a hidden item. Items are modelled with the
label checker (builderreadme/filterrender), so stats a rule doesn't name are 0. Unidentified
items have no readable stats (the client doesn't get their affixes), and white items only
carry staffmods on class items and caster bases.

    python validate_map_icons.py                 # the main filter of every group
    python validate_map_icons.py Hiim.filter     # given files
    python validate_map_icons.py --all           # every root and group filter
"""
import argparse
import glob
import json
import os
import random
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "builderreadme"))
from filterrender import engine  # noqa: E402

MARKER = re.compile(r"%(MAP|DOT|PX)-[0-9A-Fa-f]+%")
CODE = re.compile(r"[0-9a-z]{2,6}")
QUALITIES = ["NMAG", "MAG", "RARE", "UNI", "SET", "CRAFT"]
TIERS = {"NORM", "EXC", "ELT"}
TYPE_FLAGS = {"WEAPON", "ARMOR", "HELM", "CIRC", "CHEST", "SHIELD", "GLOVES", "BOOTS", "BELT", "AXE",
              "MACE", "CLUB", "TMACE", "HAMMER", "SCEPTER", "SWORD", "DAGGER", "THROWING", "JAV",
              "SPEAR", "POLEARM", "BOW", "XBOW", "STAFF", "WAND", "SOR", "SIN", "BAR", "DRU", "DIN",
              "NEC", "QUIVER", "1H", "2H"} | TIERS
INTRINSIC_FIELDS = {"FILTLVL", "CLVL", "DIFF", "MAPID", "AREALVL", "ILVL", "ALVL", "LVLREQ", "SOCK",
                    "SOCKETS", "QTY", "PRICE", "DEF", "CHARSTAT0", "CHARSTAT2", "CHARSTAT12", "WP4",
                    "WP11", "WP12", "WP13"}
STAFFMOD_BASES = {"BAR", "DRU", "DIN", "NEC", "SOR", "SIN", "STAFF", "WAND", "SCEPTER", "BOW", "JAV", "SPEAR"}
STAFFMOD = re.compile(r"(SK|TABSK|CLSK)\d+$")
ONE_KIND_FIELDS = {"RUNE", "GEM", "GEMTYPE", "GEMLEVEL", "MAPTIER", "MAPID_ITEM", "GOLD"}
CONTEXTS = [{}, {"CLVL": 10, "DIFF": 0, "ILVL": 8, "ALVL": 8, "LVLREQ": 5, "MAPID": 2}]
BASES = json.load(open(os.path.join(ROOT, "builderreadme", "filterrender", "bases.json"), encoding="utf-8"))
CMP = re.compile(r"^([A-Z][A-Z0-9_]*)(<=|>=|<|>|=|~)(-?\d+)(?:-(\d+))?$")


class Rules:
    def __init__(self, path):
        self.filter = engine.Filter(path)
        lines = [n for n, raw in enumerate(open(path, encoding="utf-8"), 1)
                 if raw.split("//", 1)[0].strip().startswith("ItemDisplay[")
                 and "]:" in raw.split("//", 1)[0]]
        self.rules = []
        for (cond, out), line in zip(self.filter.rules, lines):
            label = engine._split_tooltip(self.filter.out(out))[0]
            self.rules.append({"line": line, "cond": cond, "node": self.filter.cond(cond),
                               "cont": "%CONTINUE%" in label, "label": label,
                               "marker": bool(MARKER.search(label))})
        self.markers = [r for r in self.rules if r["marker"]]

    def hiding_rule(self, item, level):
        ctx = engine.Context(item, level)
        for rule in self.rules:
            if rule["cont"] or not ctx.eval(rule["node"]):
                continue
            if "%NAME%" in rule["label"]:
                return None
            text, _ = engine._render_label(rule["label"], [[("x", (0, 0, 0))]], ctx, item)
            return None if engine._trim(engine._resolve_conditionals(text)) else rule
        return None

    def is_hiding(self, rule, ctx, item):
        if rule["cont"] or "%NAME%" in rule["label"]:
            return False
        text, _ = engine._render_label(rule["label"], [[("x", (0, 0, 0))]], ctx, item)
        return not engine._trim(engine._resolve_conditionals(text))

    def marker_rule(self, item, level):
        """The map pass: the display chain past hiding rules, which drop earlier markers."""
        ctx = engine.Context(item, level)
        drawn = None
        for rule in self.rules:
            if not ctx.eval(rule["node"]):
                continue
            if self.is_hiding(rule, ctx, item):
                drawn = None
                continue
            if rule["marker"]:
                drawn = rule
            if not rule["cont"]:
                break
        return drawn


def literals(node, want, rng):
    kind = node[0]
    if kind == "const":
        return [] if bool(node[1]) == want else None
    if kind == "not":
        return literals(node[1], not want, rng)
    if kind == "atom":
        return [(node[1], want)]
    every = (kind == "and") == want
    if every:
        out = []
        for child in node[1]:
            got = literals(child, want, rng)
            if got is None:
                return None
            out += got
        return out
    for child in rng.sample(node[1], len(node[1])):
        got = literals(child, want, rng)
        if got is not None:
            return got
    return None


def build_item(lits, rng):
    codes_in, codes_out, flags_in, flags_out, num = set(), set(), set(), set(), {}
    for atom, want in lits:
        neg = atom.startswith("!")
        if neg:
            atom, want = atom.lstrip("!"), not want
        if CODE.fullmatch(atom) and any(c.isalpha() for c in atom):
            (codes_in if want else codes_out).add(atom)
            continue
        m = CMP.match(atom)
        if m:
            field, op, a, b = m.group(1), m.group(2), int(m.group(3)), m.group(4)
            if field == "FILTLVL":
                continue
            lo, hi = num.get(field, (-10**6, 10**6))
            if op == "~":
                rng_lo, rng_hi = a, int(b) if b else a
                if want:
                    lo, hi = max(lo, rng_lo), min(hi, rng_hi)
            elif op == "=":
                if want:
                    lo, hi = max(lo, a), min(hi, a)
                elif lo == a:
                    lo = a + 1
            elif (op == ">") == want or (op == ">=" and want) or (op == "<=" and not want):
                bound = a + 1 if op in (">", "<=") else a
                lo = max(lo, bound)
            else:
                bound = a - 1 if op in ("<", ">=") else a
                hi = min(hi, bound)
            num[field] = (lo, hi)
            continue
        if atom in ("TRUE", "FALSE"):
            if (atom == "TRUE") != want:
                return None
            continue
        if re.fullmatch(r"[A-Z][A-Z0-9_]*", atom):
            (flags_in if want else flags_out).add(atom)
    if len(codes_in) > 1 or codes_in & codes_out or flags_in & flags_out:
        return None
    if any(lo > hi for lo, hi in num.values()):
        return None
    if any(field in num for field in ONE_KIND_FIELDS - {"RUNE"}):
        return None
    rune = num.get("RUNE", (0, 0))[0]
    if rune > 0:
        if codes_in - {f"r{rune:02d}"} or flags_in & (TYPE_FLAGS | set(QUALITIES) - {"NMAG"}):
            return None
        return {"code": f"r{rune:02d}", "name": f"Rune {rune}", "rune": rune, "flags": ["NMAG"],
                "num": {k: v[0] for k, v in num.items() if k != "RUNE" and v[0] > -10**6}}
    num.pop("RUNE", None)
    types_in, types_out = flags_in & TYPE_FLAGS, flags_out & TYPE_FLAGS
    if codes_in:
        code = next(iter(codes_in))
        base_flags = set(BASES.get(code, {}).get("flags", [])) | types_in
    else:
        fits = [c for c, b in BASES.items() if c not in codes_out
                and types_in <= set(b["flags"]) and not types_out & set(b["flags"])]
        if not fits:
            return None
        code = rng.choice(fits)
        base_flags = set(BASES[code]["flags"])
    if base_flags & types_out:
        return None
    allowed = BASES.get(code, {}).get("qualities", QUALITIES if code in BASES else ["NMAG"])
    quality = [q for q in QUALITIES if q in flags_in] or [q for q in allowed if q not in flags_out]
    if not quality or any(q not in allowed for q in quality):
        return None
    if len(quality) != 1 and any(q in flags_in for q in QUALITIES):
        return None
    chosen = rng.choice(quality)
    flags = (base_flags | (flags_in - set(QUALITIES))) | {chosen}
    if chosen == "NMAG":
        if "ID" in flags_out:
            return None
        flags.add("ID")
    values = {}
    for field, (lo, hi) in num.items():
        if lo <= 0 <= hi:
            values[field] = 0 if lo == -10**6 and hi == 10**6 else max(lo, 0)
        else:
            values[field] = lo if lo > -10**6 else hi
    for field, value in values.items():
        if not value or field in INTRINSIC_FIELDS:
            continue
        if "ID" not in flags:
            return None
        if chosen == "NMAG" and STAFFMOD.match(field) and not base_flags & STAFFMOD_BASES:
            return None
    return {"code": code, "name": BASES.get(code, {}).get("name", code), "flags": sorted(flags), "num": values}


def check(path, samples, seed):
    rules = Rules(path)
    rng = random.Random(seed)
    found = {}
    for marker in rules.markers:
        for _ in range(samples):
            lits = literals(marker["node"], True, rng)
            item = build_item(lits, rng) if lits is not None else None
            if not item:
                continue
            for context in CONTEXTS:
                sample = dict(item, num={**context, **item["num"]})
                for level in range(12):
                    ctx = engine.Context(sample, level)
                    if not ctx.eval(marker["node"]):
                        continue
                    hidden_by = rules.hiding_rule(sample, level)
                    if not hidden_by:
                        continue
                    drawn = rules.marker_rule(sample, level)
                    if not drawn:
                        continue
                    key = (hidden_by["line"], drawn["line"])
                    entry = found.setdefault(key, {"hide": hidden_by, "marker": drawn, "levels": set(), "item": sample})
                    entry["levels"].add(level)
    return rules, found


def short(text, size=150):
    return text if len(text) <= size else text[:size] + " ..."


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="*")
    parser.add_argument("--all", action="store_true", help="every root and group filter")
    parser.add_argument("--samples", type=int, default=12, help="sample items per marker rule")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--examples", type=int, default=5, help="marker rules listed per hiding rule")
    args = parser.parse_args()
    if args.files:
        files = args.files
    elif args.all:
        files = sorted(glob.glob(os.path.join(ROOT, "*.filter")) + glob.glob(os.path.join(ROOT, "filtergroups", "*", "*.filter")))
    else:
        groups = sorted(glob.glob(os.path.join(ROOT, "filtergroups", "*")))
        files = [os.path.join(ROOT, "Hiim.filter")] + [sorted(glob.glob(os.path.join(g, "*.filter")), key=len)[0]
                                                        for g in groups if glob.glob(os.path.join(g, "*.filter"))]
    total = 0
    for path in files:
        rules, found = check(path, args.samples, args.seed)
        name = os.path.relpath(path, ROOT)
        print(f"{name}: {len(rules.markers)} marker rules, {len(found)} hidden-but-marked pair(s)")
        by_hide = {}
        for (hide_line, marker_line), entry in sorted(found.items()):
            by_hide.setdefault(hide_line, []).append(entry)
        for hide_line, entries in by_hide.items():
            print(f"  line {hide_line} hides: {short(entries[0]['hide']['cond'])}")
            for entry in entries[:args.examples]:
                item = entry["item"]
                levels = ",".join(str(x) for x in sorted(entry["levels"]))
                kinds = "/".join(sorted(set(MARKER.findall(entry["marker"]["label"]))))
                print(f"    {kinds} from line {entry['marker']['line']}: {short(entry['marker']['cond'], 110)}")
                print(f"      e.g. {item['code']} {' '.join(item['flags'])} {item['num']} on filter level(s) {levels}")
            if len(entries) > args.examples:
                print(f"    ... and {len(entries) - args.examples} more marker rule(s)")
        total += len(found)
    print(f"Total: {total} hidden-but-marked pair(s) in {len(files)} filter(s)")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
