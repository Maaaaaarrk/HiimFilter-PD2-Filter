"""Write bases.json (item code -> filter keywords) from hiimpd2.com's bases.json and item-types.json.

Usage: python builderreadme/filterrender/make_bases.py <dir with bases.json and item-types.json>
"""
import json
import os
import sys

TYPE_FLAGS = {
    "weap": ["WEAPON"], "armo": ["ARMOR"], "helm": ["HELM"], "circ": ["CIRC"], "tors": ["CHEST"],
    "shie": ["SHIELD"], "shld": ["SHIELD"], "glov": ["GLOVES"], "boot": ["BOOTS"], "belt": ["BELT"], "axe": ["AXE"],
    "blun": ["MACE"], "club": ["CLUB"], "mace": ["TMACE"], "hamm": ["HAMMER"], "scep": ["SCEPTER"],
    "swor": ["SWORD"], "knif": ["DAGGER"], "thro": ["THROWING"], "jave": ["JAV"], "spea": ["SPEAR"],
    "pole": ["POLEARM"], "bow": ["BOW"], "xbow": ["XBOW"], "staf": ["STAFF"], "wand": ["WAND"],
    "orb": ["SOR"], "h2h": ["SIN"], "h2h2": ["SIN"], "phlm": ["BAR"], "pelt": ["DRU"], "ashd": ["DIN"],
    "head": ["NEC"], "bowq": ["QUIVER"], "xboq": ["QUIVER"],
}
TIER = {"normal": "NORM", "exceptional": "EXC", "elite": "ELT"}
TWO_HANDED_CLASSES = {"2hs", "2ht", "stf", "bow", "xbw"}


def hands(base):
    one, two = base.get("wclass"), base.get("wclass2h", base.get("wclass"))
    found = {"2H" if one in TWO_HANDED_CLASSES else "1H"}
    if two != one:
        found.add("2H" if two in TWO_HANDED_CLASSES else "1H")
    return found


def ancestors(code, types, seen=None):
    seen = seen if seen is not None else set()
    if code in seen or code not in types:
        return seen
    seen.add(code)
    for parent in types[code].get("equiv", []):
        ancestors(parent, types, seen)
    return seen


def main(src):
    bases = json.load(open(os.path.join(src, "bases.json"), encoding="utf-8"))
    types = json.load(open(os.path.join(src, "item-types.json"), encoding="utf-8"))
    out = {}
    for base in bases:
        flags = set()
        for t in ancestors(base["type"], types):
            flags.update(TYPE_FLAGS.get(t, []))
        if base["kind"] == "weapon" and "QUIVER" not in flags:
            flags.update(hands(base))
        if base.get("tier") in TIER:
            flags.add(TIER[base["tier"]])
        entry = {"name": base["name"], "flags": sorted(flags), "sockets": base.get("sockets", 0)}
        if base["type"] == "tpot" or base["kind"] == "misc" or base["code"] == "leg":
            entry["qualities"] = ["NMAG"]
        out[base["code"]] = entry
    path = os.path.join(os.path.dirname(__file__), "bases.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=0, sort_keys=True)
    print(f"wrote {len(out)} bases to {path}")


if __name__ == "__main__":
    main(sys.argv[1])
