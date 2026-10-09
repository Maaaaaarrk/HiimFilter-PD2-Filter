# hiimvanillaplus
## Last updated October 9th Season 14 - build 14
## [Compare the Hiim styles side by side](../HIIM_STYLES.md)

## Filters
* Vanilla Plus: All-in-one filter without item re-naming (e.g. identified rares and unidentified uniques show their original names). [Hiim_Vanilla_Plus.filter]
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

## Filter Preview — Vanilla Plus
Rendered by `builderreadme/render_readme_images.py` from the filter on every build. Rows are sample items, columns are filter-level groups; a cell split into notes (e.g. `level 3 | level 4`) changes inside its group. Unique and set samples are picked per star tier from `builderfilter/data/unique-set-tiers.json`. Compare all Hiim styles side by side: [Hiim styles](../HIIM_STYLES.md)

[![Vanilla Plus](../../examples/render/Hiim_Vanilla_Plus.png?raw=true)](../../examples/render/Hiim_Vanilla_Plus.png?raw=true)

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

Cumulative list of unidentified uniques visible at each filter level. Higher (stricter) levels show fewer items; each block below adds **new** items not already listed in the level above. Unidentified uniques only reveal their base, so each unique is listed at its base's tier (source: `builderfilter/data/unique-set-tiers.json`).

### Level 11 — most strict

*None.* All unidentified uniques outside town are hidden.

### Level 10-9 — 4-star uniques

- Alma Negra (Sacred Rondache)
- Andariel's Visage (Demonhead)
- Arachnid Mesh (Spiderweb Sash) — non-ETH
- Arkaine's Valor (Balrog Skin) — non-ETH
- Astreon's Iron Ward (Caduceus)
- Azurewrath (Phase Blade)
- Bloodtree Stump (War Club) — ETH
- Crown of Ages (Corona)
- Death Cleaver (Berserker Axe) — ETH
- Death's Web (Unearthed Wand)
- Doombringer (Champion Sword) — ETH
- Dracul's Grasp (Vampirebone Gloves)
- Earth Shifter (Thunder Maul) — ETH
- Ghostflame (Legend Spike)
- Giant Skull (Bone Visage)
- Gore Rider (War Boots)
- Griffon's Eye (Diadem)
- Guardian Angel (Templar Coat) — ETH
- Halaberd's Reign (Conqueror Crown)
- Kira's Guardian (Tiara) — non-ETH
- Lacerator (Winged Axe) — ETH
- Lightsabre (Phase Blade)
- Mang Song's Lesson (Archon Staff)
- Nightwing's Veil (Spired Helm)
- Occultist (Crusader Gauntlets)
- Purgatory (Archon Plate) — ETH
- Ravenlore (Sky Spirit) — non-ETH
- Ribcracker (Quarterstaff) — ETH
- Schaefer's Hammer (Legendary Mallet)
- Siggard's Staunch (Colossus Girdle)
- Silks of the Victor (Ancient Armor) — ETH
- Skywarden (Vortex Shield)
- Soul Drainer (Vambraces)
- Spirit Keeper (Earth Spirit)
- Spirit Ward (Ward) — non-ETH
- Steel Carapace (Shadow Plate)
- Steel Pillar (War Pike) — ETH
- Steel Shade (Armet) — non-ETH
- Steelrend (Ogre Gauntlets)
- Stone Crusher (Legendary Mallet)
- Stoneraven (Matriarchal Spear)
- Templar's Might (Sacred Armor)
- The Cranium Basher (Thunder Maul) — ETH
- The Gavel of Pain (Martel de Fer) — ETH
- The Grandfather (Colossus Blade) — ETH
- Thunderstroke (Matriarchal Javelin)
- Titan's Revenge (Ceremonial Javelin) — ETH
- Tomb Reaver (Cryptic Axe)
- Tyrael's Might (Sacred Armor)
- Veil of Steel (Spired Helm)
- Verdungo's Hearty Cord (Mithril Coil)
- Warlord's Trust (Military Axe) — ETH
- Waterwalk (Sharkskin Boots)
- Windhammer (Ogre Maul) — ETH
- Wraithskin (Diamond Mail)
- Zerae's Resolve (Matriarchal Pike) — ETH

### Level 8 — adds 3-star uniques

- Abyssal Ward (War Bolts)
- Aetherwing (Razor Arrows)
- Arachnid Mesh (Spiderweb Sash) — ETH
- Arkaine's Valor (Balrog Skin) — ETH
- Bannerlord's Call (War Bolts)
- Basilisk's Quill (Razor Arrows)
- Brimstone Rain (Shillelagh)
- Demon Machine (Chu-Ko-Nu)
- Doom's Finger (Razor Arrows)
- Doombringer (Champion Sword) — non-ETH
- Earth Shifter (Thunder Maul) — non-ETH
- Executioner's Justice (Glorious Axe)
- Firelizard's Talons (Feral Claws)
- Frozen Sorrow (War Bolts)
- Gerke's Sanctuary (Pavise)
- Guardian Angel (Templar Coat) — non-ETH
- Harlequin Crest (Shako) — non-ETH
- Herald of Zakarum (Gilded Shield)
- Kira's Guardian (Tiara) — ETH
- Lava Gout (Battle Gauntlets)
- Lidless Wall (Grim Shield)
- Magefist (Light Gauntlets)
- Martyrdom (Overseer Skull) — non-ETH
- Medusa's Gaze (Aegis)
- Nosferatu's Coil (Vampirefang Belt)
- Ormus' Robes (Dusk Shroud) — non-ETH
- Pus Spitter (Siege Crossbow)
- Ravenlore (Sky Spirit) — ETH
- Sacred Totem (Hellspawn Skull)
- Shaftstop (Mesh Armor)
- Silkweave (Mesh Boots)
- Skyfall (Vortex Orb)
- Snowclash (Battle Belt) — non-ETH
- Spirit Ward (Ward) — ETH
- Steel Pillar (War Pike) — non-ETH
- Steel Shade (Armet) — ETH
- Stormshield (Monarch) — non-ETH
- Stormspire (Giant Thresher)
- String of Ears (Demonhide Sash)
- The Cranium Basher (Thunder Maul) — non-ETH
- The Grandfather (Colossus Blade) — non-ETH
- The Reaper's Toll (Thresher)
- Thundergod's Vigor (War Belt) — non-ETH
- Valkyrie Wing (Winged Helm)
- Vampire Gaze (Grim Helm)
- War Traveler (Battle Boots)
- Whispering Mirage (War Fist)
- Widowmaker (Ward Bow)
- Windforce (Hydra Bow)
- Zerae's Resolve (Matriarchal Pike) — non-ETH

### Level 7 — adds 2-star uniques

- Anvilguard Strap (Heavy Bolts)
- Arioc's Needle (Hyperion Spear)
- Arm of King Leoric (Tomb Wand)
- Arreat's Face (Slayer Guard)
- Athena's Wrath (Battle Scythe)
- Atma's Wail (Embossed Plate)
- Bartuc's Cut-Throat (Greater Talons)
- Blackhand Key (Grave Wand)
- Blade of Ali Baba (Tulwar)
- Blood Raven's Charge (Matriarchal Bow)
- Bloodtree Stump (War Club) — non-ETH
- Boneflame (Succubus Skull)
- Boneshade (Lich Wand)
- Cerebus' Bite (Blood Spirit)
- Cyclopean Roar (Jawbone Visor)
- Darkforce Spawn (Bloodlord Skull)
- Death Cleaver (Berserker Axe) — non-ETH
- Death's Fathom (Dimensional Shard)
- Demonhorn's Edge (Destroyer Helm)
- Denmother (Sun Spirit)
- Dragonscale (Zakarum Shield)
- Ebonbane (Grand Matron Bow)
- Embersworn (Demon Heart)
- Ephemeral (Sacred Targe)
- Eschuta's Temper (Eldritch Orb)
- Fenris (Alpha Helm)
- Flamebellow (Balrog Blade)
- Gargoyle's Bite (Winged Harpoon)
- Ghoulhide (Heavy Bracers)
- Giant Maimer (Colossus Voulge)
- Goldwrap (Heavy Belt)
- Gravepalm (Sharkskin Gloves)
- Grim's Burning Dead (Grim Scythe)
- Harlequin Crest (Shako) — ETH
- Head Hunter's Glory (Troll Nest)
- Heavenly Garb (Light Plate)
- Hellmouth (War Gauntlets)
- Hellslayer (Decapitator)
- Horizon's Tornado (Scourge)
- Infernostride (Demonhide Boots)
- Jade Talon (Wrist Sword)
- Jalal's Mane (Totemic Mask)
- Leviathan (Kraken Shell)
- Marrowwalk (Boneweave Boots)
- Martyrdom (Overseer Skull) — ETH
- Merman's Sprocket (Wyrmhide Boots)
- Ormus' Robes (Dusk Shroud) — ETH
- Peasant Crown (War Hat)
- Plague Bearer (Rune Sword)
- Que-Hegan's Wisdom (Mage Plate)
- Raekor's Virtue (Guardian Crown)
- Razortail (Sharkskin Belt)
- Ribcracker (Quarterstaff) — non-ETH
- Sage's Defiance (Giant Conch)
- Sandstorm Trek (Scarabshell Boots)
- Shadow Dancer (Myrmidon Greaves)
- Shatterhead (Heavy Bolts)
- Skin of the Vipermagi (Serpentskin Armor)
- Skull Collector (Rune Staff)
- Skullder's Ire (Russet Armor)
- Snowclash (Battle Belt) — ETH
- Spike Thorn (Blade Barrier)
- Stormlash (Scourge)
- Stormshield (Monarch) — ETH
- Suicide Branch (Burnt Wand)
- Swiftwind Needle (Sharp Arrows)
- The Gladiator's Bane (Wire Fleece)
- The Oculus (Swirling Crystal)
- The Patriarch (Great Sword)
- Thundergod's Vigor (War Belt) — ETH
- Titan's Grip (Bramble Mitts)
- Tombsong (Sharp Arrows)
- Twilight's Reflection (Hyperion)
- Venom Grip (Demonhide Gloves)
- Windhammer (Ogre Maul) — non-ETH

### Level 6-5 — adds 1-star, 0-star, and NO-star uniques

**1-star:**

- Black Hades (Chaos Armor)
- Bloodfist (Heavy Gloves)
- Buriza-Do Kyanon (Ballista)
- Chance Guards (Chain Gloves)
- Chromatic Ire (Cedar Staff)
- Corpsemourn (Ornate Plate)
- Crown of Thieves (Grand Crown)
- Frostburn (Gauntlets)
- Frostwind (Cryptic Sword)
- Gimmershred (Flying Axe)
- Homunculus (Hierophant Trophy)
- Humongous (Giant Axe)
- Nethercrux (Ghost Wand)
- Ondal's Wisdom (Elder Staff)
- Purgatory (Archon Plate) — non-ETH
- Rune Master (Ettin Axe)
- Shatterblade (Mithril Point)
- Silks of the Victor (Ancient Armor) — non-ETH
- Spirit Shroud (Ghost Armor)
- Stalker's Cull (Runic Talons)
- Swordguard (Executioner Sword)
- The Gavel of Pain (Martel de Fer) — non-ETH
- Titan's Revenge (Ceremonial Javelin) — non-ETH
- Toothrow (Sharktooth Armor)
- Ursa's Nightmare (Dream Spirit)
- Viperfork (Mancatcher)
- Wildspeaker (Lion Helm)
- Witchwild String (Short Siege Bow)
- Wizardspike (Bone Knife)

**0-star:**

- Blackbog's Sharp (Cinquedeas)
- Crow Caw (Tigulated Mail)
- Endlesshail (Double Bow)
- Gorefoot (Heavy Boots)
- Heart Carver (Rondel)
- Lacerator (Winged Axe) — non-ETH
- Odium (Colossus Sword)
- Radament's Sphere (Ancient Shield)
- Rockstopper (Sallet)
- The Jade Tan Do (Kris)
- Treads of Cthon (Chain Boots)
- Venom Ward (Breast Plate)
- Wizendraw (Long Battle Bow)
- Wolfhowl (Fury Visor)

**NO-star:**

- Baezil's Vortex (Knout)
- Biggin's Bonnet (Cap)
- Blackoak Shield (Luna)
- Cloudcrack (Gothic Sword)
- Djinn Slayer (Ataghan)
- Duskdeep (Full Helm)
- Eaglehorn (Crusader Bow)
- Gull (Dagger)
- Kuko Shakaku (Cedar Bow)
- Magewrath (Rune Bow)
- The Hand of Broc (Leather Gloves)
- The Impaler (War Spear)
- Warlord's Trust (Military Axe) — non-ETH

### Level 1-4 — most permissive

*All uniques are shown.*

