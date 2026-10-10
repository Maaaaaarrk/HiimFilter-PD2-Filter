"""Sample items used to illustrate a filter.

Each item: code, name (what the game shows before any filter rule), flags (condition
keywords that are true for it), num (numeric condition fields; anything missing is 0,
except FILTLVL / CLVL / DIFF / MAPID / ILVL defaults set by the engine), and a short
label for the image's legend. Categories group the items into sheets.
"""


def _rune(num, name):
    return {"code": f"r{num:02d}", "name": f"{name} Rune", "rune": num, "rune_name": name,
            "color": "ORANGE", "flags": [], "num": {"QTY": 1}, "legend": f"{name} rune (#{num})"}


CATEGORIES = [
    ("Runes & currency", [
        _rune(1, "El"),
        _rune(8, "Ral"),
        _rune(24, "Ist"),
        _rune(26, "Vex"),
        _rune(30, "Ber"),
        {"code": "gpvs", "name": "Perfect Amethyst", "flags": ["NMAG"], "num": {"QTY": 1, "GEM": 5, "GEMLEVEL": 5, "GEMTYPE": 1}, "legend": "Perfect gem (stack)"},
        {"code": "wss", "name": "Worldstone Shard", "flags": ["NMAG"], "legend": "Worldstone Shard"},
        {"code": "lbox", "name": "Larzuk's Puzzlebox", "flags": ["NMAG"], "legend": "Larzuk's Puzzlebox"},
        {"code": "pk1", "name": "Key of Terror", "flags": ["NMAG"], "legend": "Uber key"},
        {"code": "tes", "name": "Twisted Essence of Suffering", "flags": ["NMAG"], "legend": "Essence"},
        {"code": "skzs", "name": "Perfect Skull", "flags": ["NMAG"], "num": {"QTY": 1, "GEM": 5, "GEMLEVEL": 5, "GEMTYPE": 7}, "legend": "Perfect skull (stack)"},
    ]),
    ("Unidentified uniques & sets", "STAR_SAMPLES"),  # filled from unique-set-tiers.json at render time
    ("Magic & rare", [
        {"code": "rin", "name": "Doom Coil", "flags": ["RARE", "ID", "JEWELRY"],
         "num": {"FCR": 10, "STR": 15, "LIFE": 30, "FRES": 20, "CRES": 20, "LRES": 20, "PRES": 20, "LVLREQ": 45},
         "legend": "Rare ring: 10 FCR, 15 str, 30 life, 20 all res"},
        {"code": "amu", "name": "Raven Torc", "flags": ["RARE", "ID", "JEWELRY"],
         "num": {"CLSK1": 2, "FCR": 10, "STR": 20, "LIFE": 35, "LVLREQ": 60},
         "legend": "Rare amulet: +2 Sorceress, 10 FCR, 20 str, 35 life"},
        {"code": "cm3", "name": "Grand Charm", "flags": ["MAG", "ID", "CHARM"],
         "num": {"TABSK17": 1, "LIFE": 40, "STAT7": 40},
         "legend": "Skiller GC: +1 Necro Summoning, 40 life"},
        {"code": "cm1", "name": "Small Charm", "flags": ["MAG", "ID", "CHARM"],
         "num": {"LIFE": 20, "STAT7": 20, "FRES": 5, "CRES": 5, "LRES": 5, "PRES": 5, "RES": 5},
         "legend": "Small charm: 20 life, 5 all res"},
        {"code": "jew", "name": "Jewel", "flags": ["MAG", "ID"],
         "num": {"EDAM": 40, "IAS": 15}, "legend": "Magic jewel: 40% ED, 15 IAS"},
        {"code": "xvg", "name": "Sharkskin Gloves", "flags": ["MAG", "ARMOR", "GLOVES", "EQ4", "EXC"],
         "legend": "Unid magic gloves"},
        {"code": "ci2", "name": "Tiara", "flags": ["RARE", "ARMOR", "CIRC", "EQ7", "EXC"],
         "legend": "Unid rare circlet"},
        {"code": "utp", "name": "Archon Plate", "flags": ["RARE", "ARMOR", "CHEST", "EQ2", "ELT"],
         "num": {"ILVL": 85, "ALVL": 75}, "legend": "Unid rare body armor, ilvl 85, alvl 75"},
        {"code": "utp", "name": "Archon Plate", "flags": ["RARE", "ARMOR", "CHEST", "EQ2", "ELT"],
         "num": {"ILVL": 85, "ALVL": 85}, "legend": "Unid rare body armor, ilvl 85, alvl 85"},
    ]),
    ("Bases & runewords", [
        {"code": "7vo", "name": "Colossus Voulge", "flags": ["NMAG", "ETH", "WEAPON", "POLEARM", "ELT", "2H"],
         "num": {"SOCK": 4, "EDAM": 20}, "legend": "ETH 4os Colossus Voulge, 20% ED"},
        {"code": "7wa", "name": "Berserker Axe", "flags": ["NMAG", "ETH", "WEAPON", "AXE", "ELT", "1H"],
         "num": {"SOCK": 0, "EDAM": 18}, "legend": "ETH 0os Berserker Axe, 18% ED"},
        {"code": "6ws", "name": "Archon Staff", "flags": ["NMAG", "WEAPON", "STAFF", "ELT", "2H"],
         "num": {"SOCK": 4, "SK48": 3, "SK63": 3}, "legend": "4os Archon Staff, +3 Nova, +3 Lightning Mastery"},
        {"code": "uit", "name": "Monarch", "flags": ["NMAG", "ARMOR", "SHIELD", "EQ3", "ELT"],
         "num": {"SOCK": 4}, "legend": "4os Monarch"},
        {"code": "uui", "name": "Dusk Shroud", "flags": ["NMAG", "ARMOR", "CHEST", "EQ2", "ELT"],
         "num": {"SOCK": 3, "EDEF": 15}, "legend": "3os Dusk Shroud, 15% ED"},
        {"code": "7cr", "name": "Phase Blade", "flags": ["NMAG", "WEAPON", "SWORD", "ELT", "1H"],
         "num": {"SOCK": 0}, "legend": "0os Phase Blade"},
        {"code": "uui", "name": "Enigma", "base_line": "Dusk Shroud", "flags": ["RW", "ID", "ARMOR", "CHEST", "EQ2", "ELT"], "color": "GOLD",
         "num": {"SOCK": 3}, "legend": "Runeword: Enigma"},
        {"code": "ssd", "name": "Short Sword", "flags": ["NMAG", "WEAPON", "SWORD", "NORM", "1H"],
         "num": {"ILVL": 85}, "legend": "Plain Short Sword (junk)"},
        {"code": "lbt", "name": "Boots", "flags": ["MAG", "ARMOR", "BOOTS", "EQ5", "NORM"],
         "num": {"ILVL": 85}, "legend": "Unid magic Boots (junk)"},
    ]),
    ("Consumables", [
        {"code": "rvl", "name": "Full Rejuvenation Potion", "flags": ["NMAG"], "legend": "Full rejuv"},
        {"code": "rvs", "name": "Rejuvenation Potion", "flags": ["NMAG"], "legend": "Small rejuv"},
        {"code": "hp5", "name": "Super Healing Potion", "flags": ["NMAG"], "legend": "Super healing"},
        {"code": "mp5", "name": "Super Mana Potion", "flags": ["NMAG"], "legend": "Super mana"},
        {"code": "isc", "name": "Scroll of Identify", "flags": ["NMAG"], "legend": "ID scroll"},
        {"code": "tsc", "name": "Scroll of Town Portal", "flags": ["NMAG"], "legend": "TP scroll"},
    ]),
]



# ---- star-tier samples, picked from builderfilter/data/unique-set-tiers.json -------------------
import os as _os
import sys as _sys

_ROOT = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.join(_ROOT, "builderfilter"))
import tier_aliases as _tiers  # noqa: E402
from .base_flags import BASE_FLAGS  # noqa: E402

_STAR = {"4": "4-star", "3": "3-star", "2": "2-star", "1": "1-star", "0": "0-star", "no-star": "no-star"}


def _base_class(code):
    """NORM / EXC / ELT for a weapon or armor code (from the game's item tables); None otherwise."""
    return next((f for f in BASE_FLAGS.get(code, ()) if f in ("NORM", "EXC", "ELT")), None)


def _sample(e, flags, legend):
    cls = _base_class(e["code"])
    return {"code": e["code"], "name": e.get("base") or e["code"],
            "flags": flags + ([cls] if cls else []), "legend": legend}


def _skip(e):
    base = (e.get("base") or "").lower()
    return any(w in base for w in ("bolt", "arrow", "ring", "amulet", "charm", "jewel"))


def star_samples():
    """One unidentified unique per star group (plus an ETH-only 4-star) and one set item per
    set star group, chosen from the current tiers so the images follow tier changes."""
    data = _tiers.load()
    ubases = _tiers.unique_code_tiers(data)
    sbases = _tiers.set_code_tiers(data)
    out = []

    def pick(entries, ok):
        # quivers and jewelry make poor examples (bolts/rings all look alike unidentified)
        cands = sorted((e for e in entries if ok(e) and not _skip(e)), key=lambda e: (bool(e.get("eth")), e["name"].lower()))
        return cands[0] if cands else None

    for tier in _tiers.UNIQUE_SCALE:
        same = lambda e: ubases[e["code"]]["noneth"] == tier == ubases[e["code"]]["eth"]
        # the no-star example should be a normal (else exceptional) base, never an elite one
        e = pick(data["uniques"], same) if tier != "no-star" else (
            pick(data["uniques"], lambda e: same(e) and _base_class(e["code"]) == "NORM")
            or pick(data["uniques"], lambda e: same(e) and _base_class(e["code"]) == "EXC"))
        if e:
            out.append(_sample(e, ["UNI"], f"Unid unique {e['name']} - {_STAR[tier]}"))
    e = pick(data["uniques"], lambda e: ubases[e["code"]]["eth"] == "4" and ubases[e["code"]]["noneth"] != "4")
    if e:
        n = ubases[e["code"]]["noneth"]
        out.append(_sample(e, ["UNI", "ETH"], f"Unid ETH {e['name']} - 4-star ETH, {_STAR.get(n, 'unstarred')} non-ETH"))
    out.append({"code": "rin", "name": "Ring", "flags": ["UNI", "JEWELRY"], "legend": "Unid unique ring"})
    for tier in _tiers.SET_SCALE:
        e = pick(data["sets"], lambda e: sbases[e["code"]]["tier"] == tier)
        if e:
            out.append(_sample(e, ["SET"], f"Unid set {e['name']} - {_STAR[tier]} set"))
    return out


def with_base_flags(item):
    """The item with its base's loot-filter flags (ARMOR / WEAPON, type and group codes, class
    item codes, 1H / 2H, NORM / EXC / ELT) added from the game's item tables."""
    add = list(BASE_FLAGS.get(item["code"], ()))
    # normal-quality items and runes are always identified in game (rules test !ID)
    if "NMAG" in item.get("flags", []) or item.get("rune"):
        add.append("ID")
    extra = [f for f in add if f not in item.get("flags", [])]
    return dict(item, flags=list(item.get("flags", [])) + extra) if extra else item


def categories():
    """CATEGORIES with the star-tier samples filled in and base flags on every item."""
    return [(name, [with_base_flags(it) for it in (star_samples() if items == "STAR_SAMPLES" else items)])
            for name, items in CATEGORIES]
