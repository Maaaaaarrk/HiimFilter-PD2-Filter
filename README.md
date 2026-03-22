# Project Diablo 2 (PD2) Hiim Loot Filters
* by *Maaaark
* by *Hiimdave
## Last updated March 18th Season 12 - build 111
## [Hiim PD2 Resources](https://maaaaaarrk.github.io/Hiim-PD2-Resources/)
## Put all feedback in the PD2 Discord #lootfilter channel
## NOTE MANY Images below have been taken across many seasons and may not be 100% up to date but show general functionality
* To confirm installation check tool tip on the Cube
![cube](examples/cube.png?raw=true)
## Filters
* Hiim.filter - All in one filter
* Hiim_Crafting.filter - Same as all in one filter, but good crafting bases are not limited to filter level 3/4
* Hiim_Crafting_-Class Name-.filter - Will show items and crafting bases targeted to this class at higher filter levels
* Hiim_Grail.filter - All in one filter & Always shows Uniques & Set items on level 1-8
* Hiim_Hyper.filter - All in one filter - Hyper themed
* Hiim_LLD_Focused.filter - Filter that will show LLD relevant items at higher filter levels
* Hiim_Mystery.filter - Same as all in one filter, but Runes Pul(21)+ and GG uniques are renamed
* Hiim_Only_Fitler.filter - All in one filter - No item display changes only filtering
* Hiim_TalRasha_Themed.filter - All in one filter - TalRasha Color Themed
* Hiim_Vanilla_Plus.filter - All in one filter - but without all of the item re-naming (example identified rares or unidentified uniques)
## Filter Levels
Cube will state current filter version & chosen filter level information.

**This breakdown applies to the standard `Hiim.filter` only.** All variant filters (Crafting, class-specific, Grail, Hyper, LLD, etc.) show *more* than the baseline — never less. They are tuned to surface more of what their specific audience cares about at higher filter levels.

**Always hidden regardless of level:** Inferior items, ears, small gold piles, junk 10s (after CLVL 80)

* **0: Off** — Filter disabled, all items visible

* **1: Base** — Minimal filtering. Recommended for Normal difficulty or new players getting started

* **2: Semi-Strict**
  * Scrolls hidden at high level
  * Throwing potions hidden outside town
  * Stamina, thawing, antidote, and oil potions hidden
  * Staffmod annotations reduced

* **3: Strict**
  * HP pots 1–4 and MP pots 1–5 hidden
  * Gems hidden
  * Magic rings and amulets hidden
  * Most unidentified rares hidden (characters CLVL 86+)
  * Rune number labels removed from display

* **4: Strict + No HP/MP** — Everything from level 3, plus HP5 and MP5 potions hidden

* **5: Stricter**
  * HP/MP potions restored
  * Low-value unidentified uniques and sets hidden
  * Class-specific rare item decorations end
  * Eth magic crafting bases reduced
  * Specific rare bows hidden

* **6: Stricter + No HP/MP** — Everything from level 5, plus HP5 and MP5 potions hidden again

* **7: Extremely Strict**
  * Bad-rolled charms hidden on ground
  * Most unidentified uniques and sets hidden
  * Eth rare gloves, boots, belts, and chests(< ALVL 85) hidden
  * Class-specific rares hidden (necro heads, sorc orbs, druid pelts, barb helms, paladin shields)
  * Magic jewel decorations reduced
  * Low rune decorations removed

* **8: High Roller**
  * Low runes (El through Amn) hidden outside town
  * Small rejuvs hidden
  * Rare rings hidden
  * Flawless gem removed
  * Magic jewels hidden

* **9: 3 Minute Mapper & Rejuvs**
  * Full rejuvs still shown
  * Rare necro heads, rare boots, and rare chests hidden
  * Grand charms heavily reduced

* **10: 3 Minute Mapper**
  * Full rejuvs hidden
  * Rare quivers (Amazon and non-Amazon) hidden
  * Grand charms show minimal label only

* **11: No Items Out of Town** — Everything outside town hidden except desecrated items, slammed items, and runeword items
## Helper text
* Check Tooltip on Boss mats for help on Uber Bosses
* Check Tooltip on keys tooltip for pathing help
* Many items have helper text, if you need any help just ask in the official discord loot filter channel
## Charm Stats on Ground
Charms on ground will show important stats
![charms1](examples/charms1.PNG?raw=true)
## Magic / Rare / Crafted items
These items also show important stats on the ground. This applies to many gear slots not just the ones in the example.
Rings & Amulets also have points implemented:
* Range: 2pt, 3Pt, 4Pt, 5pt, 6pt
* Evaluation includes crafts & a few slams
* Each Pt of Value = high roll of a valuable stat
* Evaluation takes into account partial rolls
* Evaluation includes crafts & a few slams
![magicrares1](examples/magicrares1.PNG?raw=true)
![magicrares2](examples/magicrares2.PNG?raw=true)
![magicrares3](examples/magicrares3.PNG?raw=true)
![magicrares4](examples/magicrares4.PNG?raw=true)
## LLD
Set/Unique items that are valuable to LLD community carry the LLD tag
LLD Jewels have points implemented:
* Range: 2pt, 2.5 Pt, 3Pt, 3.3 Pt, 3.6 Pt, 4Pt
* Each Pt of Value = high roll of a valuable stat
* Evaluation takes into account partial rolls
![lld1](examples/lld1.PNG?raw=true)
![lld2](examples/lld2.png?raw=true)
## UNIDS
All UNID Set/Unique items show their identified name options
![unid1](examples/unid1.PNG?raw=true)
![unid2](examples/unid2.PNG?raw=true)
## Map rolling
* T1,T2,T3 Maps will tell you when the rolls are good
* Both MF & XP focused calculations are made
* Base mob immunites are shown for each map
* Various warnings about map rolls, examples but not limited to: Dolls & Souls
![maps1](examples/maps1.png?raw=true)
![maps2](examples/maps2.png?raw=true)
## Item hints
* Utility items have useful notes tool tips for boss fights.
* Runewords on item bases.
* Advisement to upgrade an item for more sockets before slam
* Gamble screens show what you can get
![runewords1](examples/runewords1.png?raw=true)
![hints1](examples/hints1.PNG?raw=true)
![hints2](examples/hints2.PNG?raw=true)
![hints3](examples/hints3.PNG?raw=true)
![hints4](examples/hints4.PNG?raw=true)
## Crafting help
* Crafting in PD2 can create the most powerful items in the game.
* Notes about crafting are on bases, infusions, and gems
* Typical craft are denoted by *
* Notes about Alvl are on the crafting bases
![craft1](examples/craft1.PNG?raw=true)
![craft2](examples/craft2.PNG?raw=true)
![craft3](examples/craft3.PNG?raw=true)
![craft4](examples/craft4.PNG?raw=true)
## Disclaimer and Credits
Use at your own risk - I don't promise there will not be bugs, or that you may miss drops you personally may have wanted if we hid or made it less obvious.
There are no maliciously hidden items or drops.
Based off parts of Kryszard's PD2 Loot Filter from PD2 Season 1 - twitch.tv/kryszard
Based off parts of Wolfie's PD2 Loot Fitlers from PD2 Season 1 - github.com/WolfieeifloW/pd2filter
Runeword Section from EQN - github.com/eqNj/eqN-PD2-Filter
See install.png for picture manual install directions, please use in launcher for automated updates.
For testing preview in launcher or: https://betweenwalls.github.io/filterbird/?v=PD2
