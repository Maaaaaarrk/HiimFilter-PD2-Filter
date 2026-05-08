# hiimhyper
## Last updated May 8th Season 13 - build 111

## Filters
* Style — Hyper: All-in-one filter with a Hyper visual theme. [Hiim_Hyper.filter]
* Class — Amazon: Class filter tuned for Amazon. Shows Amazon-relevant items and crafting bases at higher filter levels. [Hiim_Crafting_Amazon_Focused.filter]
* Class — Assassin: Class filter tuned for Assassin. Shows Assassin-relevant items and crafting bases at higher filter levels. [Hiim_Crafting_Assassin_Focused.filter]
* Class — Barbarian: Class filter tuned for Barbarian. Shows Barbarian-relevant items and crafting bases at higher filter levels. [Hiim_Crafting_Barbarian_Focused.filter]
* Class — Druid: Class filter tuned for Druid. Shows Druid-relevant items and crafting bases at higher filter levels. [Hiim_Crafting_Druid_Focused.filter]
* Class — Necromancer: Class filter tuned for Necromancer. Shows Necromancer-relevant items and crafting bases at higher filter levels. [Hiim_Crafting_Necromancer_Focused.filter]
* Class — Paladin: Class filter tuned for Paladin. Shows Paladin-relevant items and crafting bases at higher filter levels. [Hiim_Crafting_Paladin_Focused.filter]
* Class — Sorceress: Class filter tuned for Sorceress. Shows Sorceress-relevant items and crafting bases at higher filter levels. [Hiim_Crafting_Sorceress_Focused.filter]
* Crafting: Same as the standard filter, but good crafting bases are not limited in higher filter levels. [Hiim_Crafting.filter]
* Grail Friendly: All-in-one filter that always shows Uniques and Set items on filter levels 1–8. [Hiim_Grail.filter]
* LLD: Shows LLD-relevant items at higher filter levels. Includes LLD jewel point evaluation and LLD tags on valuable Set/Unique items. [Hiim_LLD_Focused.filter]
* Mystery: All-in-one filter where Runes Pul (21)+ and GG uniques are renamed to hide their identity. [Hiim_Mystery.filter]

## Filter Levels
Cube will state current filter version & chosen filter level information.

**This breakdown applies to the standard `Hiim.filter` only.** All variant filters (Crafting, class-specific, Grail, Hyper, LLD, etc.) show *more* than the baseline — never less. They are tuned to surface more of what their specific audience cares about at higher filter levels.

**Always hidden regardless of level:** Inferior items, ears, small gold piles, junk 10s (after CLVL 80)

* **0: Off** — Filter disabled, all items visible. Use this if you want to see everything or are debugging the filter.

* **1: Base** — Minimal filtering. Recommended for Normal difficulty or new players.
  * Inferior items and absolute junk hidden
  * Everything else visible: all runes, gems, rings, amulets, rares, uniques, charms, pots
  * Tradeoff: busy ground clutter, but zero risk of missing anything valuable, good for speed runners

* **2: Semi-Strict** — Good starting point for Nightmare and early Hell. Cleans up potion and clutter without hiding anything valuable.
  * Throwing potions, stamina, thawing, antidote, and oil potions hidden outside town
  * Staffmod annotations reduced on normal bases
  * Still shows: all runes, all gems, all rings/amulets, all rares, HP/MP pots, leveling items

* **3: Strict** — Recommended for most Hell farming. Hides low-value items that experienced players rarely pick up.
  * HP pots 1–4 and MP pots 1–4 hidden
  * Bad Gems hidden (Flawless & Perfect still shown)
  * Magic rings and amulets hidden
  * Most unidentified rares hidden (CLVL 86+)
  * Rune number labels removed from display
  * Still shows: HP5/MP5, all uniques/sets, high value rares, runes, jewels, charms

* **4: Strict + No Pots** — Same as level 3 but HP5 and MP5 potions also hidden. Good for characters with life leech or high sustain who don't need to manage potions.

* **5: Stricter** — For players comfortable with the game who want a cleaner screen during fast farming.
  * HP/MP potions restored (back from level 4)
  * Low-value unidentified uniques and sets hidden (0-star tier)
  * Class-specific rare item decorations end at higher filter levels
  * Eth magic crafting bases reduced
  * Specific low-value rare bows hidden
  * Tradeoff: you may miss some marginal uniques — use Grail filter if grailing

* **6: Stricter + No Pots** — Everything from level 5, plus HP5 and MP5 hidden. Best for leech builds doing efficient Hell runs.

* **7: Extremely Strict** — For experienced endgame players. Significantly reduces ground clutter at the cost of hiding some niche items.
  * Bad-rolled charms hidden on ground
  * Most unidentified uniques and sets hidden (only high-tiers shown)
  * ETH rare armor (chests) hidden; non-ETH rare gloves, boots, and belts hidden; Chests (ALVL<85) hidden
  * Class-specific items hidden: sorc orbs, druid pelts, paladin shields, magic necro heads (barb helms already hidden since level 5; rare necro heads not hidden until level 9)
  * Magic jewel decorations reduced, low rune decorations removed
  * Still shows: high-star uniques/sets, GG rares, HR runes, good charms, jewels

* **8: High Roller** — Built for players farming high-end content where low-value pickups waste time. Assumes self-sustain (no pots needed).
  * Low runes (El–Amn) hidden outside town
  * Small rejuvs hidden
  * Rare rings hidden
  * Flawless gems and magic jewels hidden
  * Tradeoff: you will walk past low runes and small rejuvs — intentional for speed

* **9: 3 Minute Mapper + Rejuvs** — Aggressive map-running level. Full rejuvs still shown for safety; most other clutter gone.
  * Rejuvs shown
  * Rare necro heads, rare boots, and rare chests hidden
  * Grand charms heavily reduced (only notable rolls shown)
  * Tradeoff: Only consider this filter if you would double back for a WSS

* **10: 3 Minute Mapper** — Maximum speed farming. Almost nothing shows outside of high-value items.
  * Rejuvs hidden
  * Tradeoff: no safety net on potions — best for group play or near-immortal builds

* **11: No Items Out of Town** — Extreme clutter removal. Almost nothing shows outside of town.
  * Only desecrated items, slammed items, and runeword bases visible outside town - in case of miss click
  * Tradeoff: you will miss nearly everything — intended for carry runs, group content, or testing

