"""Generate the unique/set star-tier aliases from builderfilter/data/unique-set-tiers.json.

The JSON is the source of truth; 02-alias/05-unid-unique-set-stars[ALL].filter is a
generated file (build.py rewrites it on every build).

JSON model (one entry per unique or set item):
    {"code": "7p7", "name": "Steel Pillar", "base": "War Pike",
     "current": "3", "floor": null,
     "eth": {"current": "4", "floor": "4"},    # optional: ETH copies differ
     "lld": true,                              # optional: LLD catch list
     "locked": true}                           # optional: automation never changes it

Tiers (best -> worst): uniques "4" "3" "2" "1" "0" "no-star", sets "4" "3" "2" "1" "0".
"current": null means the item is not starred (it can still be on the LLD list).
"floor" is the lowest tier the automated tier-down may set (null = no floor).
Without an "eth" block, ETH copies use "current" / "floor".

Unidentified items only reveal their base, so a base code's tier is the best tier
of any unique (or set item) on it, per variant (ETH / non-ETH).

The generated aliases keep the names the 06-unidfiltering rules use. ETH vs non-ETH
differences map onto them like this (first matching row):
    non-ETH 4, ETH 4          -> 4_STAR_UNIQUE
    non-ETH 4, ETH 3          -> 4_STAR_NO_ETH_UNIQUE
    ETH 4 (non-ETH lower)     -> 4_STAR_ETH_UNIQUE + the non-ETH tier's alias
    non-ETH 3, ETH 2          -> 3_STAR_NO_ETH_UNIQUE
    same tier                 -> that tier's alias
Anything else cannot be expressed by the current rules and fails the build.
"""
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TIERS_JSON = os.path.join(SCRIPT_DIR, "data", "unique-set-tiers.json")
ALIAS_FILE = os.path.join(SCRIPT_DIR, "02-alias", "05-unid-unique-set-stars[ALL].filter")

UNIQUE_SCALE = ["4", "3", "2", "1", "0", "no-star"]          # best -> worst
SET_SCALE = ["4", "3", "2", "1", "0"]
UNIQUE_ALIAS = {"4": "4_STAR_UNIQUE", "3": "3_STAR_UNIQUE", "2": "2_STAR_UNIQUE",
                "1": "1_STAR_UNIQUE", "0": "0_STAR_UNIQUE", "no-star": "NO_STAR_UNIQUE"}
SET_ALIAS = {"4": "4_STAR_SET", "3": "3_STAR_SET", "2": "2_STAR_SET", "1": "1_STAR_SET", "0": "0_STAR_SET"}

# Alias output order and section titles (matches the rule order in 06-unidfiltering).
UNIQUE_BLOCKS = [
    ("4_STAR_UNIQUE", "4 Star Unique Callouts"),
    ("4_STAR_NO_ETH_UNIQUE", "4 Star Unique Callouts only when not ETH (ETH copies show as 3 star)"),
    ("4_STAR_ETH_UNIQUE", "4 Star Unique Callouts only when ETH"),
    ("3_STAR_UNIQUE", "3 Star Unique Callouts"),
    ("3_STAR_NO_ETH_UNIQUE", "3 Star Unique Callouts only when not ETH (ETH copies show as 2 star)"),
    ("2_STAR_UNIQUE", "2 Star Unique Callouts"),
    ("1_STAR_UNIQUE", "1 Star Unique Callouts"),
    ("0_STAR_UNIQUE", "0 Star Unique Callouts"),
    ("NO_STAR_UNIQUE", "NO Star Unique Callouts"),
    ("LLD_UNIQUE", "LLD Unique Callouts"),
]
SET_BLOCKS = [
    ("4_STAR_SET", "Set 4 star (GG) Callouts"),
    ("3_STAR_SET", "Set 3 star Callouts"),
    ("2_STAR_SET", "Set 2 star Callouts"),
    ("1_STAR_SET", "Set 1 star Callouts"),
    ("0_STAR_SET", "Set 0 star Callouts"),
    ("LLD_SET", "Set LLD Callouts"),
]


class TierError(ValueError):
    pass


def _rank(scale, tier):
    """Higher is better; None (not starred) ranks below every tier."""
    return -1 if tier is None else len(scale) - scale.index(tier)


def _best(scale, tiers):
    tiers = [t for t in tiers if t is not None]
    return max(tiers, key=lambda t: _rank(scale, t)) if tiers else None


def load(path=TIERS_JSON):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    validate(data)
    return data


def validate(data):
    problems = []
    for kind, scale in (("uniques", UNIQUE_SCALE), ("sets", SET_SCALE)):
        seen = set()
        for e in data.get(kind, []):
            where = f"{kind}: {e.get('name')!r} ({e.get('code')})"
            if not e.get("code") or not e.get("name"):
                problems.append(f"{where}: needs code and name")
            key = (e.get("code"), e.get("name"))
            if key in seen:
                problems.append(f"{where}: duplicate entry")
            seen.add(key)
            variants = [("", e)] + ([("eth.", e["eth"])] if "eth" in e else [])
            if "eth" in e and kind == "sets":
                problems.append(f"{where}: sets have no eth block")
            for prefix, v in variants:
                for field in ("current", "floor"):
                    t = v.get(field)
                    if t is not None and t not in scale:
                        problems.append(f"{where}: {prefix}{field} {t!r} is not one of {scale}")
                cur, flo = v.get("current"), v.get("floor")
                if cur is not None and flo is not None and _rank(scale, flo) > _rank(scale, cur):
                    problems.append(f"{where}: {prefix}current {cur} is below its floor {flo}")
    if problems:
        raise TierError("unique-set-tiers.json:\n  " + "\n  ".join(problems))


def unique_code_tiers(data):
    """code -> {"noneth": tier|None, "eth": tier|None, "lld": bool}"""
    out = {}
    for e in data["uniques"]:
        c = out.setdefault(e["code"], {"noneth": [], "eth": [], "lld": False})
        c["noneth"].append(e.get("current"))
        c["eth"].append(e["eth"].get("current") if "eth" in e else e.get("current"))
        c["lld"] = c["lld"] or bool(e.get("lld"))
    return {code: {"noneth": _best(UNIQUE_SCALE, c["noneth"]), "eth": _best(UNIQUE_SCALE, c["eth"]),
                   "lld": c["lld"]} for code, c in out.items()}


def set_code_tiers(data):
    out = {}
    for e in data["sets"]:
        c = out.setdefault(e["code"], {"tier": [], "lld": False})
        c["tier"].append(e.get("current"))
        c["lld"] = c["lld"] or bool(e.get("lld"))
    return {code: {"tier": _best(SET_SCALE, c["tier"]), "lld": c["lld"]} for code, c in out.items()}


def unique_aliases_for(n, e):
    """Alias names a base needs so the rules show non-ETH tier n and ETH tier e."""
    if n is None and e is None:
        return []
    if n == "4" and e == "4":
        return ["4_STAR_UNIQUE"]
    if n == "4" and e == "3":
        return ["4_STAR_NO_ETH_UNIQUE"]
    if e == "4":
        return ["4_STAR_ETH_UNIQUE"] + ([UNIQUE_ALIAS[n]] if n is not None else [])
    if n == "3" and e == "2":
        return ["3_STAR_NO_ETH_UNIQUE"]
    if n == e:
        return [UNIQUE_ALIAS[n]]
    raise TierError(f"non-ETH {n} / ETH {e} cannot be expressed by the tier aliases")


def build_alias_lists(data):
    lists = {name: [] for name, _ in UNIQUE_BLOCKS + SET_BLOCKS}
    for code, t in unique_code_tiers(data).items():
        try:
            names = unique_aliases_for(t["noneth"], t["eth"])
        except TierError as err:
            raise TierError(f"unique base {code}: {err}") from None
        for a in names:
            lists[a].append(code)
        if t["lld"]:
            lists["LLD_UNIQUE"].append(code)
    for code, t in set_code_tiers(data).items():
        if t["tier"] is not None:
            lists[SET_ALIAS[t["tier"]]].append(code)
        if t["lld"]:
            lists["LLD_SET"].append(code)
    return lists


def _label(e, alias):
    s = f"{e['name']} - {e.get('base') or e['code']}"
    notes = []
    if "eth" in e and alias.endswith("_UNIQUE"):
        n, et = e.get("current"), e["eth"].get("current")
        notes.append(f"non-ETH {n or 'unstarred'}, ETH {et or 'unstarred'}")
    if e.get("locked"):
        notes.append("locked")
    else:
        flo = e.get("floor"), (e["eth"].get("floor") if "eth" in e else None)
        if flo[0] is not None:
            notes.append(f"floor {flo[0]}")
        if flo[1] is not None:
            notes.append(f"ETH floor {flo[1]}")
    return s + (f" ({'; '.join(notes)})" if notes else "")


def render(data):
    lists = build_alias_lists(data)
    by_code = {}
    for kind in ("uniques", "sets"):
        for e in data[kind]:
            by_code.setdefault((kind, e["code"]), []).append(e)
    out = [
        "//-----------------------------------------------------------------------------------",
        "// Star Ratings - GENERATED by builderfilter/tier_aliases.py from",
        "// builderfilter/data/unique-set-tiers.json. Do not edit; change the JSON instead.",
        "//-----------------------------------------------------------------------------------",
        "",
    ]
    for kind, blocks in (("uniques", UNIQUE_BLOCKS), ("sets", SET_BLOCKS)):
        for alias, title in blocks:
            codes = sorted(lists[alias])
            out.append(f"// {title}")
            out.append("//-----------------------------------------------------------------------------------")
            for code in codes:
                for e in sorted(by_code[(kind, code)], key=lambda x: x["name"].lower()):
                    out.append(f"// {_label(e, alias)}")
            if codes:
                out.append(f"Alias[{alias}]: ({' OR '.join(codes)})")
            else:  # keep the alias defined so the rules stay valid; matches nothing
                out.append(f"Alias[{alias}]: (FALSE)")
            out.append("")
    return "\r\n".join(out)


def generate(json_path=TIERS_JSON, alias_path=ALIAS_FILE):
    """Rewrite the alias file from the JSON. Returns True if the file changed."""
    text = render(load(json_path))
    old = None
    if os.path.exists(alias_path):
        with open(alias_path, encoding="utf-8", newline="") as f:
            old = f.read()
    if old == text:
        return False
    with open(alias_path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return True


if __name__ == "__main__":
    changed = generate()
    print(("wrote " if changed else "unchanged: ") + os.path.relpath(ALIAS_FILE))
