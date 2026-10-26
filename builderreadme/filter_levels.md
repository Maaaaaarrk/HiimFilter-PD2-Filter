## Filter Levels
Cube will state current filter version & chosen filter level information.

**This breakdown applies to the standard `Hiim.filter` only.** All variant filters (Crafting, class-specific, Grail, Hyper, LLD, etc.) show *more* than the baseline — never less. They are tuned to surface more of what their specific audience cares about at higher filter levels.

**Always hidden regardless of level:** Inferior items, ears, small gold piles, junk 10s (after CLVL 80)

**HP5 / MP5 potions are never hidden by filter level** — show or hide them with the in-game potion settings.

* **0: Off** — Filter disabled, all items visible. Use this if you want to see everything or are debugging the filter.

* **1: Campaign** — Minimal filtering. Recommended for Normal difficulty or new players.
  * Inferior items and absolute junk hidden
  * Everything else visible: all runes, gems, rings, amulets, rares, uniques, charms, pots
  * Tradeoff: busy ground clutter, but zero risk of missing anything valuable, good for speed runners

* **2: Campaign-Strict** — Good starting point for Nightmare and early Hell. Cleans up potion and clutter without hiding anything valuable.
  * Throwing potions, stamina, thawing, antidote, and oil potions hidden outside town
  * Staffmod annotations reduced on normal bases
  * Still shows: all runes, all gems, all rings/amulets, all rares, HP/MP pots, leveling items

* **3: Base** — Recommended for most Hell farming. Hides low-value items that experienced players rarely pick up.
  * HP pots 1–4 and MP pots 1–4 hidden
  * Bad Gems hidden (Flawless & Perfect still shown)
  * Magic rings hidden
  * Most unidentified rares hidden (CLVL 86+)
  * Rune number labels removed from display
  * Hell: unidentified ETH magic weapons and armor that aren't crafting bases hidden (ETH chests included)
  * Still shows: all uniques/sets, high value rares, runes, jewels, charms

* **4: Semi-Strict** — Everything from level 3, plus:
  * Unrated unidentified uniques and sets (no star tier) hidden (CLVL 85+)
  * Crafting bases: second-tier ETH weapons (Thunder Maul, Phase Blade, Berserker Axe, Glorious Axe, Legendary Mallet, Stygian Pilum, Balrog Spear, Winged Harpoon, Scourge, Feral Axe) and other classes' bases (sorc orbs, Amazon bows, paladin shields, Divine Scepters, druid pelts, barb helms) hidden

* **5: Strict** — For players comfortable with the game who want a cleaner screen during fast farming.
  * Magic amulets hidden
  * NO-star unidentified uniques hidden
  * Class-specific rare item decorations end at higher filter levels
  * Crafting bases: magic necro heads, ETH claws and your own class's crafting bases hidden
  * Specific low-value rare bows hidden
  * Tradeoff: you may miss some marginal uniques — use Grail filter if grailing

* **6: Stricter** — Everything from level 5, plus:
  * 0-star unidentified uniques and sets hidden; LLD callouts end
  * ETH uniques/sets and elite uniques no longer shown regardless of tier
  * Unidentified set rings and amulets lose their tier callout (still shown)
  * Normal Matriarchal / Grand Matron Bows with +3 Bow skills and under 15% ED hidden

* **7: Extremely Strict** — For experienced endgame players. Significantly reduces ground clutter at the cost of hiding some niche items.
  * Bad-rolled charms hidden on ground
  * Small rejuvs hidden
  * 1-star unidentified uniques and sets hidden (2-star and up shown)
  * Crafting bases: the last ones go — ETH Ghost Glaive, War Pike, Ogre Maul, War Fist, Champion Axe, Hyperion Spear, Colossus Blade, Colossus Sword, and 4-socket shields
  * ETH rare armor (chests) hidden; non-ETH rare gloves, boots, and belts hidden; Chests (ALVL<85) hidden
  * Class-specific rare items hidden: sorc orbs, druid pelts, paladin shields (barb helms already hidden since level 5; rare necro heads not hidden until level 9)
  * Magic jewel decorations reduced, low rune decorations removed
  * Still shows: high-star uniques/sets, GG rares, HR runes, good charms, jewels

* **8: Extremely Strict+** — Everything from level 7, trimmed further for players farming high-end content where low-value pickups waste time.
  * 2-star unidentified uniques and sets hidden
  * Rare rings hidden
  * Flawless gems and magic jewels hidden

* **9: High Roller** — Aggressive map-running level. Full rejuvs still shown for safety; most other clutter gone.
  * Low runes (El–Lum) hidden outside town
  * Rare necro heads, rare boots, and rare chests hidden
  * Grand charms heavily reduced (only notable rolls shown)
  * Tradeoff: you will walk past low runes — only consider this filter if you would double back for a WSS

* **10: 3 Minute Mapper** — Everything from level 9, plus:
  * 3-star unidentified uniques and sets hidden (only 4-star shown)
  * Crafting, class and LLD filters: low runes (below Pul) hidden outside town

* **11: No Items Out of Town** — Extreme clutter removal. Almost nothing shows outside of town.
  * Only desecrated items, slammed items, and runeword bases visible outside town - in case of miss click
  * Tradeoff: you will miss nearly everything — intended for carry runs, group content, or testing
