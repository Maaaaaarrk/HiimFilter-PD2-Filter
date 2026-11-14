# kassahi
## Last updated November 14th Season 14 - build 232
## [Compare the Hiim styles side by side](../HIIM_STYLES.md)

## Filters
* Regular — Standard: Kassahi's all-in-one balanced filter. The standard recommendation for most players. [Kassahi.filter]
* Meme — Hyper: Meme filter with a Hyper visual theme. [Kassahi_Meme_Hyper.filter]
* Meme — Standard: Standard filter with meme item names for a humorous experience. [Kassahi_Meme.filter]
* Mystery — Hyper: Mystery filter with a Hyper visual theme. [Kassahi_Mystery_Hyper.filter]
* Mystery — Standard: Filter where high-value items are renamed to hide their identity. [Kassahi_Mystery.filter]
* Regular — Hyper: Standard filter with a Hyper visual theme. [Kassahi_Hyper.filter]

## Filter Preview — Kassahi — Standard
**[See Kassahi — Standard at every filter level on FilterForge](https://maaaaaarrk.github.io/FilterForge/compare.html?only=kassahi@2,kassahi@4,kassahi@6,kassahi@7,kassahi@8,kassahi@10)** — the same drops as the filter shows them in game, one column per filter level (2, 4, 6, 7, 8, 10). Compare all Hiim styles side by side: [Hiim styles](../HIIM_STYLES.md)

## Filter Levels
Cube will state current filter version & chosen filter level information.

**This breakdown applies to `Kassahi.filter` for a level 86+ character in Hell** (several rules relax for lower character levels and difficulties).

**Always hidden regardless of level:** Inferior items, ears, small gold piles, junk 10s (after CLVL 80), HP and MP potions 1–4 (after CLVL 80), throwing, stamina, thawing and oil potions

**HP5 / MP5 potions and full rejuvs are never hidden by filter level** — show or hide the potions with the in-game potion settings.

* **0: Off** — Filter disabled, all items visible.

* **1: Campaign** — Minimal filtering.
  * Everything of value visible: all runes, all gems, rings, amulets, rares, uniques, sets, charms, jewels
  * Item names show every stat tag, including the low (dark green) tiers and +3 staffmods on magic, rare and crafted items

* **2: Campaign-Strict**
  * Chipped, flawed and normal gems and skulls hidden
  * Magic non-ETH elite crafting bases hidden

* **3: Base**
  * Low (dark green) stat tags and +3 staffmod tags on magic, rare and crafted items removed from item names (normal bases keep their +3 tags)
  * Antidote potions hidden
  * Magic rings hidden
  * Magic ETH elite armor, sorceress orbs, paladin shields and most ETH weapon crafting bases hidden

* **4: Semi-Strict** — Everything from level 3, plus:
  * More crafting bases hidden (magic ETH Berserker Axe, Thunder Maul and similar second-tier bases)

* **5: Strict**
  * Magic amulets hidden
  * Unidentified rare amulets, chests, helms and paladin shields hidden
  * NO-star unidentified uniques hidden
  * Bad-rolled small, large and grand charms hidden on the ground

* **6: Stricter** — Everything from level 5, plus:
  * 0-star unidentified uniques and sets hidden

* **7: Extremely Strict**
  * 1-star unidentified uniques and sets hidden (2-star and up shown)
  * Magic jewels below item level 85 hidden; item level 85+ jewels (double affix) kept through level 10
  * Small rejuvs hidden
  * Unidentified rare gloves, sorceress orbs, druid pelts and barbarian helms hidden
  * Last crafting bases hidden (magic ETH Ghost Glaive, Ogre Maul and similar)

* **8: Extremely Strict+** — Everything from level 7, plus:
  * 2-star unidentified uniques and sets hidden
  * Flawless gems hidden (flawless skulls still shown)
  * Unidentified rare rings, belts, shields and most rare weapons hidden
  * Still shows: unidentified rare boots, necro heads and circlets

* **9: High Roller**
  * Low runes (El–Lum) hidden outside town; Ko and up still shown
  * Perfect gems and flawless skulls hidden (perfect skulls still shown)
  * Unidentified rare boots and necro heads hidden
  * Tradeoff: you will walk past low runes — only consider this filter if you would double back for a WSS

* **10: 3 Minute Mapper** — Everything from level 9, plus:
  * 3-star unidentified uniques and sets hidden (only 4-star shown)
  * Still shows: Ko and up, item level 85+ magic jewels, perfect skulls, unidentified rare circlets

* **11: No Items Out of Town** — Extreme clutter removal. Almost nothing shows outside of town.
  * Only desecrated items, slammed items, and runeword bases visible outside town - in case of miss click
  * Tradeoff: you will miss nearly everything — intended for carry runs, group content, or testing


## Uniques Shown by Filter Level

Cumulative list of unidentified uniques visible at each filter level. Higher (stricter) levels show fewer items; each block below adds **new** items not already listed in the level above. Unidentified uniques only reveal their base, so each unique is listed at its base's tier (source: `builderfilter/data/unique-set-tiers.json`).

### Level 11 — most strict

*None.* All unidentified uniques outside town are hidden.

### Level 10 — 4-star uniques

- Aetherwing (Razor Arrows)
- Alma Negra (Sacred Rondache)
- Andariel's Visage (Demonhead)
- Arachnid Mesh (Spiderweb Sash) — non-ETH
- Arioc's Needle (Hyperion Spear) — ETH
- Astreon's Iron Ward (Caduceus)
- Azurewrath (Phase Blade)
- Basilisk's Quill (Razor Arrows)
- Crown of Ages (Corona)
- Death Cleaver (Berserker Axe) — ETH
- Death's Web (Unearthed Wand)
- Doom's Finger (Razor Arrows)
- Doombringer (Champion Sword) — ETH
- Dracul's Grasp (Vampirebone Gloves)
- Earth Shifter (Thunder Maul) — ETH
- Ephemeral (Sacred Targe)
- Ghostflame (Legend Spike) — non-ETH
- Giant Skull (Bone Visage)
- Gore Rider (War Boots)
- Griffon's Eye (Diadem)
- Herald of Zakarum (Gilded Shield)
- Lacerator (Winged Axe) — ETH
- Lava Gout (Battle Gauntlets) — non-ETH
- Lightsabre (Phase Blade)
- Mang Song's Lesson (Archon Staff)
- Nightwing's Veil (Spired Helm)
- Occultist (Crusader Gauntlets) — ETH
- Plague Bearer (Rune Sword) — ETH
- Purgatory (Archon Plate) — ETH
- Ravenlore (Sky Spirit) — non-ETH
- Ribcracker (Quarterstaff) — ETH
- Schaefer's Hammer (Legendary Mallet)
- Siggard's Staunch (Colossus Girdle)
- Silks of the Victor (Ancient Armor) — ETH
- Skull Collector (Rune Staff)
- Skyfall (Vortex Orb)
- Skywarden (Vortex Shield)
- Soul Drainer (Vambraces)
- Spirit Keeper (Earth Spirit)
- Steel Carapace (Shadow Plate)
- Steelrend (Ogre Gauntlets) — non-ETH
- Stone Crusher (Legendary Mallet)
- Stoneraven (Matriarchal Spear) — ETH
- Stormspire (Giant Thresher) — ETH
- Templar's Might (Sacred Armor)
- The Cranium Basher (Thunder Maul) — ETH
- The Grandfather (Colossus Blade) — ETH
- The Reaper's Toll (Thresher) — ETH
- Thunderstroke (Matriarchal Javelin) — ETH
- True Silver (Maiden Javelin) — ETH
- Tyrael's Might (Sacred Armor)
- Vampire Gaze (Grim Helm)
- Veil of Steel (Spired Helm)
- Verdungo's Hearty Cord (Mithril Coil) — ETH
- War Traveler (Battle Boots)
- Warshrike (Winged Knife) — ETH
- Waterwalk (Sharkskin Boots)
- Windforce (Hydra Bow)
- Zerae's Resolve (Matriarchal Pike) — ETH

### Level 9-8 — adds 3-star uniques

- Abyssal Ward (War Bolts) — ETH
- Arachnid Mesh (Spiderweb Sash) — ETH
- Arkaine's Valor (Balrog Skin) — non-ETH
- Athena's Wrath (Battle Scythe) — ETH
- Bannerlord's Call (War Bolts) — ETH
- Brimstone Rain (Shillelagh)
- Darkforce Spawn (Bloodlord Skull) — ETH
- Death's Fathom (Dimensional Shard) — non-ETH
- Demon Machine (Chu-Ko-Nu)
- Denmother (Sun Spirit) — ETH
- Fenris (Alpha Helm) — ETH
- Firelizard's Talons (Feral Claws) — ETH
- Frozen Sorrow (War Bolts) — ETH
- Gerke's Sanctuary (Pavise) — ETH
- Ghostflame (Legend Spike) — ETH
- Goblin Toe (Light Plated Boots)
- Guardian Angel (Templar Coat) — non-ETH
- Halaberd's Reign (Conqueror Crown) — ETH
- Harlequin Crest (Shako) — non-ETH
- Infernostride (Demonhide Boots) — ETH
- Jalal's Mane (Totemic Mask) — ETH
- Kira's Guardian (Tiara) — non-ETH
- Lava Gout (Battle Gauntlets) — ETH
- Lidless Wall (Grim Shield) — ETH
- Magefist (Light Gauntlets)
- Marrowwalk (Boneweave Boots)
- Martyrdom (Overseer Skull) — non-ETH
- Medusa's Gaze (Aegis) — ETH
- Nosferatu's Coil (Vampirefang Belt) — ETH
- Occultist (Crusader Gauntlets) — non-ETH
- Ormus' Robes (Dusk Shroud) — non-ETH
- Pus Spitter (Siege Crossbow)
- Razortail (Sharkskin Belt) — ETH
- Sacred Totem (Hellspawn Skull) — ETH
- Shaftstop (Mesh Armor)
- Silkweave (Mesh Boots)
- Skin of the Vipermagi (Serpentskin Armor) — ETH
- Snowclash (Battle Belt) — non-ETH
- Spectral Plate (Great Hauberk) — non-ETH
- Spirit Ward (Ward)
- Stalker's Cull (Runic Talons) — ETH
- Steel Pillar (War Pike) — ETH
- Steel Shade (Armet) — non-ETH
- Steelrend (Ogre Gauntlets) — ETH
- Stormspire (Giant Thresher) — non-ETH
- String of Ears (Demonhide Sash)
- Thundergod's Vigor (War Belt) — non-ETH
- Thunderstroke (Matriarchal Javelin) — non-ETH
- Tomb Reaver (Cryptic Axe)
- Toothrow (Sharktooth Armor) — non-ETH
- Twilight's Reflection (Hyperion) — ETH
- Valkyrie Wing (Winged Helm)
- Verdungo's Hearty Cord (Mithril Coil) — non-ETH
- Warlord's Trust (Military Axe) — ETH
- Warriv's Warder (Heater) — ETH
- Warshrike (Winged Knife) — non-ETH
- Wraithskin (Diamond Mail)

### Level 7 — adds 2-star uniques

- Anvilguard Strap (Heavy Bolts) — ETH
- Arkaine's Valor (Balrog Skin) — ETH
- Arm of King Leoric (Tomb Wand) — ETH
- Arreat's Face (Slayer Guard)
- Athena's Wrath (Battle Scythe) — non-ETH
- Atma's Wail (Embossed Plate)
- Bartuc's Cut-Throat (Greater Talons) — ETH
- Black Hades (Chaos Armor) — non-ETH
- Blackhand Key (Grave Wand)
- Blade of Ali Baba (Tulwar)
- Blood Raven's Charge (Matriarchal Bow) — ETH
- Bloodtree Stump (War Club) — ETH
- Boneflame (Succubus Skull) — ETH
- Boneshade (Lich Wand) — ETH
- Buriza-Do Kyanon (Ballista) — ETH
- Cerebus' Bite (Blood Spirit) — ETH
- Chance Guards (Chain Gloves) — non-ETH
- Crow Caw (Tigulated Mail) — ETH
- Cyclopean Roar (Jawbone Visor) — ETH
- Darkforce Spawn (Bloodlord Skull) — non-ETH
- Death Cleaver (Berserker Axe) — non-ETH
- Death's Fathom (Dimensional Shard) — ETH
- Demonhorn's Edge (Destroyer Helm) — ETH
- Doombringer (Champion Sword) — non-ETH
- Dragonscale (Zakarum Shield)
- Earth Shifter (Thunder Maul) — non-ETH
- Ebonbane (Grand Matron Bow)
- Embersworn (Demon Heart) — ETH
- Eschuta's Temper (Eldritch Orb) — ETH
- Executioner's Justice (Glorious Axe) — non-ETH
- Firelizard's Talons (Feral Claws) — non-ETH
- Flamebellow (Balrog Blade) — ETH
- Gargoyle's Bite (Winged Harpoon) — ETH
- Gerke's Sanctuary (Pavise) — non-ETH
- Ghoulhide (Heavy Bracers) — ETH
- Goldwrap (Heavy Belt) — ETH
- Gravepalm (Sharkskin Gloves) — ETH
- Grim's Burning Dead (Grim Scythe)
- Gut Siphon (Demon Crossbow)
- Halaberd's Reign (Conqueror Crown) — non-ETH
- Head Hunter's Glory (Troll Nest)
- Heart Carver (Rondel)
- Heavenly Garb (Light Plate) — ETH
- Hellmouth (War Gauntlets) — ETH
- Hellslayer (Decapitator) — ETH
- Horizon's Tornado (Scourge)
- Infernostride (Demonhide Boots) — non-ETH
- Kira's Guardian (Tiara) — ETH
- Leviathan (Kraken Shell) — ETH
- Lidless Wall (Grim Shield) — non-ETH
- Martyrdom (Overseer Skull) — ETH
- Merman's Sprocket (Wyrmhide Boots) — ETH
- Nosferatu's Coil (Vampirefang Belt) — non-ETH
- Ondal's Wisdom (Elder Staff) — non-ETH
- Ormus' Robes (Dusk Shroud) — ETH
- Peasant Crown (War Hat) — ETH
- Plague Bearer (Rune Sword) — non-ETH
- Que-Hegan's Wisdom (Mage Plate) — ETH
- Raekor's Virtue (Guardian Crown)
- Ravenlore (Sky Spirit) — ETH
- Razortail (Sharkskin Belt) — non-ETH
- Sacred Totem (Hellspawn Skull) — non-ETH
- Sage's Defiance (Giant Conch) — ETH
- Sandstorm Trek (Scarabshell Boots)
- Shadow Dancer (Myrmidon Greaves)
- Shatterhead (Heavy Bolts) — ETH
- Silks of the Victor (Ancient Armor) — non-ETH
- Skin of the Vipermagi (Serpentskin Armor) — non-ETH
- Skullder's Ire (Russet Armor)
- Spectral Plate (Great Hauberk) — ETH
- Spike Thorn (Blade Barrier) — ETH
- Stalker's Cull (Runic Talons) — non-ETH
- Steel Pillar (War Pike) — non-ETH
- Steel Shade (Armet) — ETH
- Steelclash (Kite Shield)
- Stoneraven (Matriarchal Spear) — non-ETH
- Stormlash (Scourge)
- Stormshield (Monarch)
- Suicide Branch (Burnt Wand)
- Swiftwind Needle (Sharp Arrows) — ETH
- The Cranium Basher (Thunder Maul) — non-ETH
- The Gavel of Pain (Martel de Fer) — ETH
- The Gladiator's Bane (Wire Fleece)
- The Grandfather (Colossus Blade) — non-ETH
- The Oculus (Swirling Crystal) — ETH
- The Patriarch (Great Sword) — ETH
- The Reaper's Toll (Thresher) — non-ETH
- Titan's Grip (Bramble Mitts) — ETH
- Titan's Revenge (Ceremonial Javelin) — ETH
- Tombsong (Sharp Arrows) — ETH
- Treads of Cthon (Chain Boots)
- Venom Grip (Demonhide Gloves) — ETH
- Warriv's Warder (Heater) — non-ETH
- Whispering Mirage (War Fist)
- Widowmaker (Ward Bow) — ETH
- Wildspeaker (Lion Helm)
- Zerae's Resolve (Matriarchal Pike) — non-ETH

### Level 6 — adds 1-star uniques

- Abyssal Ward (War Bolts) — non-ETH
- Anvilguard Strap (Heavy Bolts) — non-ETH
- Arioc's Needle (Hyperion Spear) — non-ETH
- Arm of King Leoric (Tomb Wand) — non-ETH
- Bannerlord's Call (War Bolts) — non-ETH
- Bartuc's Cut-Throat (Greater Talons) — non-ETH
- Biggin's Bonnet (Cap)
- Black Hades (Chaos Armor) — ETH
- Blackoak Shield (Luna) — non-ETH
- Blood Raven's Charge (Matriarchal Bow) — non-ETH
- Bloodfist (Heavy Gloves)
- Bloodtree Stump (War Club) — non-ETH
- Boneflame (Succubus Skull) — non-ETH
- Boneshade (Lich Wand) — non-ETH
- Buriza-Do Kyanon (Ballista) — non-ETH
- Cerebus' Bite (Blood Spirit) — non-ETH
- Chance Guards (Chain Gloves) — ETH
- Chromatic Ire (Cedar Staff) — ETH
- Corpsemourn (Ornate Plate)
- Crow Caw (Tigulated Mail) — non-ETH
- Crown of Thieves (Grand Crown)
- Cyclopean Roar (Jawbone Visor) — non-ETH
- Demonhorn's Edge (Destroyer Helm) — non-ETH
- Denmother (Sun Spirit) — non-ETH
- Duskdeep (Full Helm)
- Eaglehorn (Crusader Bow)
- Embersworn (Demon Heart) — non-ETH
- Eschuta's Temper (Eldritch Orb) — non-ETH
- Executioner's Justice (Glorious Axe) — ETH
- Fenris (Alpha Helm) — non-ETH
- Frostburn (Gauntlets)
- Frostwind (Cryptic Sword) — ETH
- Frozen Sorrow (War Bolts) — non-ETH
- Gargoyle's Bite (Winged Harpoon) — non-ETH
- Ghoulhide (Heavy Bracers) — non-ETH
- Goldwrap (Heavy Belt) — non-ETH
- Gravepalm (Sharkskin Gloves) — non-ETH
- Guardian Angel (Templar Coat) — ETH
- Harlequin Crest (Shako) — ETH
- Hellslayer (Decapitator) — non-ETH
- Homunculus (Hierophant Trophy)
- Humongous (Giant Axe) — ETH
- Jade Talon (Wrist Sword)
- Jalal's Mane (Totemic Mask) — non-ETH
- Leviathan (Kraken Shell) — non-ETH
- Medusa's Gaze (Aegis) — non-ETH
- Merman's Sprocket (Wyrmhide Boots) — non-ETH
- Nethercrux (Ghost Wand) — ETH
- Ondal's Wisdom (Elder Staff) — ETH
- Que-Hegan's Wisdom (Mage Plate) — non-ETH
- Ribcracker (Quarterstaff) — non-ETH
- Rockstopper (Sallet)
- Rune Master (Ettin Axe)
- Sage's Defiance (Giant Conch) — non-ETH
- Shatterblade (Mithril Point) — ETH
- Shatterhead (Heavy Bolts) — non-ETH
- Snowclash (Battle Belt) — ETH
- Spike Thorn (Blade Barrier) — non-ETH
- Spirit Shroud (Ghost Armor) — ETH
- Swiftwind Needle (Sharp Arrows) — non-ETH
- Swordguard (Executioner Sword) — ETH
- The Oculus (Swirling Crystal) — non-ETH
- The Spirit Shroud (Ghost Armor) — ETH
- Thundergod's Vigor (War Belt) — ETH
- Titan's Grip (Bramble Mitts) — non-ETH
- Tombsong (Sharp Arrows) — non-ETH
- Toothrow (Sharktooth Armor) — ETH
- Twilight's Reflection (Hyperion) — non-ETH
- Ursa's Nightmare (Dream Spirit) — ETH
- Venom Grip (Demonhide Gloves) — non-ETH
- Venom Ward (Breast Plate)
- Viperfork (Mancatcher) — ETH
- Widowmaker (Ward Bow) — non-ETH
- Witchwild String (Short Siege Bow) — ETH
- Wizardspike (Bone Knife) — ETH
- Wolfhowl (Fury Visor) — non-ETH

### Level 5 — adds 0-star uniques

- Blackbog's Sharp (Cinquedeas)
- Endlesshail (Double Bow)
- Flamebellow (Balrog Blade) — non-ETH
- Frostwind (Cryptic Sword) — non-ETH
- Giant Maimer (Colossus Voulge) — ETH
- Gorefoot (Heavy Boots)
- Odium (Colossus Sword)
- Radament's Sphere (Ancient Shield)
- Shatterblade (Mithril Point) — non-ETH
- Spirit Shroud (Ghost Armor) — non-ETH
- The Jade Tan Do (Kris) — ETH
- The Spirit Shroud (Ghost Armor) — non-ETH
- Titan's Revenge (Ceremonial Javelin) — non-ETH
- Ursa's Nightmare (Dream Spirit) — non-ETH
- Windhammer (Ogre Maul) — ETH
- Witchwild String (Short Siege Bow) — non-ETH
- Wizendraw (Long Battle Bow)
- Wolfhowl (Fury Visor) — ETH

### Level 4 — adds NO-star uniques

- Baezil's Vortex (Knout)
- Blackoak Shield (Luna) — ETH
- Chromatic Ire (Cedar Staff) — non-ETH
- Cloudcrack (Gothic Sword)
- Djinn Slayer (Ataghan)
- Giant Maimer (Colossus Voulge) — non-ETH
- Gimmershred (Flying Axe)
- Gull (Dagger)
- Heavenly Garb (Light Plate) — non-ETH
- Hellmouth (War Gauntlets) — non-ETH
- Humongous (Giant Axe) — non-ETH
- Kuko Shakaku (Cedar Bow)
- Lacerator (Winged Axe) — non-ETH
- Magewrath (Rune Bow)
- Nethercrux (Ghost Wand) — non-ETH
- Peasant Crown (War Hat) — non-ETH
- Purgatory (Archon Plate) — non-ETH
- Swordguard (Executioner Sword) — non-ETH
- The Gavel of Pain (Martel de Fer) — non-ETH
- The Hand of Broc (Leather Gloves)
- The Impaler (War Spear)
- The Jade Tan Do (Kris) — non-ETH
- The Patriarch (Great Sword) — non-ETH
- Viperfork (Mancatcher) — non-ETH
- Warlord's Trust (Military Axe) — non-ETH
- Windhammer (Ogre Maul) — non-ETH
- Wizardspike (Bone Knife) — non-ETH

### Level 1-3 — most permissive

*All uniques are shown.*

