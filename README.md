# Project Diablo 2 (PD2) Hiim Loot Filters
* by *Maaaark
* by *Hiimdave
## Last updated May 31st Season 13 - build 236
## [Hiim PD2 Resources](https://maaaaaarrk.github.io/Hiim-PD2-Resources/)
## Put all feedback in the PD2 Discord #lootfilter channel

## Filters
* Hiim — Standard: All-in-one balanced filter. The standard recommendation for most players. [Hiim.filter]
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
* Only A Filter: All-in-one filter with no item display changes — filtering only, no annotations or re-naming. [Hiim_Only_Filter.filter]
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
  * Low-value unidentified sets hidden (0-star tier — uniques of the same tier don't drop off until level 7)
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
  * Small rejuvs hidden
  * Rare rings hidden
  * Flawless gems and magic jewels hidden
  * Tradeoff: you will walk past small rejuvs — intentional for speed

* **9: 3 Minute Mapper + Rejuvs** — Aggressive map-running level. Full rejuvs still shown for safety; most other clutter gone.
  * Rejuvs shown
  * Low runes (El–Lum) hidden outside town
  * Rare necro heads, rare boots, and rare chests hidden
  * Grand charms heavily reduced (only notable rolls shown)
  * Tradeoff: you will walk past low runes — only consider this filter if you would double back for a WSS

* **10: 3 Minute Mapper** — Maximum speed farming. Almost nothing shows outside of high-value items.
  * Rejuvs hidden
  * Tradeoff: no safety net on potions — best for group play or near-immortal builds

* **11: No Items Out of Town** — Extreme clutter removal. Almost nothing shows outside of town.
  * Only desecrated items, slammed items, and runeword bases visible outside town - in case of miss click
  * Tradeoff: you will miss nearly everything — intended for carry runs, group content, or testing

## Uniques Shown by Filter Level

Cumulative list of unidentified uniques visible at each filter level. Higher (stricter) levels show fewer items; each block below adds **new** items not already listed in the level above.

### Level 11 — most strict

*None.* All unidentified uniques outside town are hidden.

### Level 10-9 — 4-star uniques

- Alma Negra
- Andariels Visage
- Arachnid Mesh (non-ETH only)
- Arkaines Valor (non-ETH only)
- Astreons Iron Ward
- Bloodtree Stump (ETH only)
- Crown of Ages
- Death Cleaver (ETH only)
- Deaths Web
- Doombringer (ETH only)
- Draculs Grasp
- Earth Shifter or The Cranium Basher (ETH only)
- Ghostflame
- Giant Skull
- Gore Rider
- Griffons Eye
- Guardian Angel (ETH only)
- Halaberds Reign
- Kiras Guardian (non-ETH only)
- Lacerator (ETH only)
- Lightsabre or Azurewrath
- Mang Songs Lesson
- Purgatory (ETH only)
- Ravenlore (non-ETH only)
- Ribcracker (ETH only)
- Siggard's Staunch
- Silks of the Victor (ETH only)
- Soul Drainer
- Spirit Keeper
- Spirit Ward (non-ETH only)
- Steel Carapace
- Steel Pillar (ETH only)
- Steel Shade (non-ETH only)
- Steelrend
- Stone Crusher or Schaefers Hammer
- Stoneraven (ETH only)
- Templars Might or Tyraels Might
- The Gavel Of Pain (ETH only)
- The Grandfather (ETH only)
- Thunderstroke
- Titans Revenge (ETH only)
- Tomb Reaver
- Tomb Reaver (ETH only)
- Veil of Steel or Nightwings Veil
- Verdungos Hearty Cord
- Vortex Shield
- Warlords Trust (ETH only)
- Waterwalk
- Windhammer (ETH only)
- Wraithskin
- Zerae's Resolve (ETH only)

### Level 8 — adds 3-star uniques

- Brimstone Rain
- Doombringer
- Earth Shifter or The Cranium Basher
- Elite Bolts
- Executioners Justice
- Gerkes Sanctuary
- Guardian Angel
- Herald of Zakarum
- Lava Gout
- Lidless Wall
- Magefist
- Martyrdom (non-ETH only)
- Medusas Gaze
- Nosferatus Coil
- Occultist
- Ormus Robes (non-ETH only)
- Pus Spitter
- Sacred Totem
- Shaftstop
- SHAKO (non-ETH only)
- Silkweave
- Skyfall
- Snowclash (non-ETH only)
- Steel Pillar
- Stoneraven
- Stormshield (non-ETH only)
- Stormspire
- String of Ears
- The Grandfather
- The Reapers Toll
- Thundergods Vigor (non-ETH only)
- Valkyrie Wing
- Vampire Gaze
- War Fist
- War Traveler
- Widowmaker
- Zerae's Resolve

### Level 7 — adds 2-star uniques

- Ariocs Needle
- Arm of King Leoric
- Arreats Face
- Athenas Wrath
- Atmas Wail
- Bartucs Cut-Throat
- Blackhand Key
- Blade of Ali Baba
- Bloodravens Charge
- Bloodtree Stump
- Boneflame
- Boneshade
- Cerebus Bite
- Cyclopean Roar
- Darkforce
- Death Cleaver
- Deaths Fathom
- Demon Machine
- Demonhorns Edge
- Denmother
- Dragonscale
- Ebonbane
- Elite Arrows
- Ephemeral
- Eschutas Temper
- Exceptional Arrows
- Fenris
- Firelizards Talons
- Flamebellow
- Gargoyles Bite
- Ghoulhide
- Giant Maimer
- Goldwrap
- Gravepalm
- Grim's Burning Dead
- Head Hunters Glory
- Heavenly Garb
- Hellmouth
- Hellslayer
- Horizons Tornado or Stormlash
- Infernostride
- Jade Talon
- Leviathan
- Marrowwalk
- Merman's Sprocket
- Peasant Crown
- Plague Bearer
- Que-Hegans Wisdom
- Raekor's Virtue
- Razortail
- Ribcracker
- Sage's Defiance
- Sandstorm Trek
- Shadow Dancer
- Skin of the Vipermagi
- Skull Collector
- Skullders Ire
- Spike Thorn
- Suicide Branch
- The Gladiator's Bane
- The Oculus
- The Patriarch
- Titans Grip
- Twilights Reflection
- Ursa's Nightmare
- Venom Grip
- Windforce
- Windhammer

### Level 6-5 — adds 1-star, 0-star, and NO-star uniques

**1-star:**

- Black Hades
- Bloodfist
- Buriza-Do Kyanon
- Chance Guards
- Chromatic Ire
- Corpsemourn
- Crown of Thieves
- Embersworn
- Exceptional Bolts
- Frostburn
- Frostwind
- Homunculus
- Humongous
- Jalals Mane
- Nethercrux
- Ondals Wisdom
- Purgatory
- Rune Master
- Shatterblade
- Silks of the Victor
- Stalker's Cull
- Swordguard
- The Gavel Of Pain
- The Spirit Shroud
- Titans Revenge
- Toothrow
- Viperfork
- Wildspeaker
- Witchwild String
- Wizardspike

**0-star:**

- Blackbogs Sharp
- Crow Caw
- Endlesshail
- Gorefoot
- Heart Carver
- Lacerator
- Odium
- Radaments Sphere
- Rockstopper
- The Jade Tan Do
- Treads of Cthon
- Venom Ward
- Wizendraw
- Wolfhowl

**NO-star:**

- Baezils Vortex
- Biggins Bonnet
- Blackoak Shield
- Cloudcrack
- Djinn Slayer
- Duskdeep
- Eaglehorn
- Gimmershred
- Gull Dagger
- Kuko Shakaku
- Magewrath
- The Hand of Broc
- The Impaler
- Warlords Trust

### Level 1-4 — most permissive

*All uniques are shown.*

## NOTE MANY Images below have been taken across many seasons and may not be 100% up to date but show general functionality
To confirm installation check tool tip on the Cube
![cube](examples/cube.png?raw=true)
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
