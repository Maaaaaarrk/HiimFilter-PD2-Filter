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
        {"code": "gpv", "name": "Perfect Amethyst", "flags": ["NMAG"], "legend": "Perfect gem"},
        {"code": "gcr", "name": "Chipped Ruby", "flags": ["NMAG"], "legend": "Chipped gem"},
        {"code": "wss", "name": "Worldstone Shard", "flags": ["NMAG"], "legend": "Worldstone Shard"},
        {"code": "lbox", "name": "Larzuk's Puzzlebox", "flags": ["NMAG"], "legend": "Larzuk's Puzzlebox"},
        {"code": "pk1", "name": "Key of Terror", "flags": ["NMAG"], "legend": "Uber key"},
    ]),
    ("Unidentified uniques & sets", [
        {"code": "uar", "name": "Sacred Armor", "flags": ["UNI", "ARMOR", "CHEST", "ELT"],
         "legend": "Unid unique Sacred Armor (4-star)"},
        {"code": "7p7", "name": "War Pike", "flags": ["UNI", "ETH", "WEAPON", "POLEARM", "ELT", "2H"],
         "legend": "Unid ETH unique War Pike (ETH 4-star)"},
        {"code": "uap", "name": "Shako", "flags": ["UNI", "ARMOR", "HELM", "ELT"],
         "legend": "Unid unique Shako (3-star)"},
        {"code": "xea", "name": "Serpentskin Armor", "flags": ["UNI", "ARMOR", "CHEST", "EXC"],
         "legend": "Unid unique Serpentskin (2-star)"},
        {"code": "9di", "name": "Rondel", "flags": ["UNI", "WEAPON", "DAGGER", "EXC", "1H"],
         "legend": "Unid unique Rondel (0-star)"},
        {"code": "rin", "name": "Ring", "flags": ["UNI", "JEWELRY"], "legend": "Unid unique ring"},
        {"code": "lbt", "name": "Boots", "flags": ["SET", "ARMOR", "BOOTS", "NORM"],
         "legend": "Unid set Boots (4-star set)"},
        {"code": "7ws", "name": "Caduceus", "flags": ["SET", "WEAPON", "SCEPTER", "ELT", "1H"],
         "legend": "Unid set Caduceus (3-star set)"},
        {"code": "vbt", "name": "Heavy Boots", "flags": ["SET", "ARMOR", "BOOTS", "NORM"],
         "legend": "Unid set Heavy Boots (2-star set)"},
    ]),
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
        {"code": "xvg", "name": "Sharkskin Gloves", "flags": ["MAG", "ARMOR", "GLOVES", "EXC"],
         "legend": "Unid magic gloves"},
        {"code": "ci2", "name": "Tiara", "flags": ["RARE", "ARMOR", "CIRC", "EXC"],
         "legend": "Unid rare circlet"},
        {"code": "xpl", "name": "Russet Armor", "flags": ["RARE", "ARMOR", "CHEST", "EXC"],
         "legend": "Unid rare body armor"},
    ]),
    ("Bases & runewords", [
        {"code": "7vo", "name": "Colossus Voulge", "flags": ["NMAG", "ETH", "WEAPON", "POLEARM", "ELT", "2H"],
         "num": {"SOCK": 4, "EDAM": 20}, "legend": "ETH 4os Colossus Voulge, 20% ED"},
        {"code": "7wa", "name": "Berserker Axe", "flags": ["NMAG", "ETH", "WEAPON", "AXE", "ELT", "1H"],
         "num": {"SOCK": 0, "EDAM": 18}, "legend": "ETH 0os Berserker Axe, 18% ED"},
        {"code": "uit", "name": "Monarch", "flags": ["NMAG", "ARMOR", "SHIELD", "ELT"],
         "num": {"SOCK": 4}, "legend": "4os Monarch"},
        {"code": "uui", "name": "Dusk Shroud", "flags": ["NMAG", "ARMOR", "CHEST", "ELT"],
         "num": {"SOCK": 3, "EDEF": 15}, "legend": "3os Dusk Shroud, 15% ED"},
        {"code": "7cr", "name": "Phase Blade", "flags": ["NMAG", "WEAPON", "SWORD", "ELT", "1H"],
         "num": {"SOCK": 0}, "legend": "0os Phase Blade"},
        {"code": "uui", "name": "Enigma", "flags": ["RW", "ID", "ARMOR", "CHEST", "ELT"], "color": "GOLD",
         "num": {"SOCK": 3}, "legend": "Runeword: Enigma"},
        {"code": "ssd", "name": "Short Sword", "flags": ["NMAG", "WEAPON", "SWORD", "NORM", "1H"],
         "num": {"ILVL": 20}, "legend": "Plain Short Sword (junk)"},
        {"code": "lbt", "name": "Boots", "flags": ["MAG", "ARMOR", "BOOTS", "NORM"],
         "num": {"ILVL": 20}, "legend": "Unid magic Boots (junk)"},
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

ALL_ITEMS = [it for _, items in CATEGORIES for it in items]
