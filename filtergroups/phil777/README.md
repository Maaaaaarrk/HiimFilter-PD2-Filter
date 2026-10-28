# phil777
## Last updated October 28th Season 14 - build 114
## [Compare the Hiim styles side by side](../HIIM_STYLES.md)

## Filters
* philanthropy777: Standard filter with a philanthropy777 visual theme. [Kassahi_Phil777.filter]
* Mystery: Mystery filter with a philanthropy777 visual theme. [Kassahi_Mystery_Phil777.filter]
* Crafting: Crafting filter (good crafting bases stay visible at higher filter levels) with the philanthropy777 visual theme. [Kassahi_Phil777_Crafting.filter]
* Mystery — Crafting: Mystery crafting filter (good crafting bases stay visible at higher filter levels) with the philanthropy777 visual theme. [Kassahi_Mystery_Phil777_Crafting.filter]
* Class — Amazon: Class filter tuned for Amazon with the philanthropy777 visual theme. [Kassahi_Phil777_Crafting_Amazon_Focused.filter]
* Class — Assassin: Class filter tuned for Assassin with the philanthropy777 visual theme. [Kassahi_Phil777_Crafting_Assassin_Focused.filter]
* Class — Barbarian: Class filter tuned for Barbarian with the philanthropy777 visual theme. [Kassahi_Phil777_Crafting_Barbarian_Focused.filter]
* Class — Druid: Class filter tuned for Druid with the philanthropy777 visual theme. [Kassahi_Phil777_Crafting_Druid_Focused.filter]
* Class — Necromancer: Class filter tuned for Necromancer with the philanthropy777 visual theme. [Kassahi_Phil777_Crafting_Necromancer_Focused.filter]
* Class — Paladin: Class filter tuned for Paladin with the philanthropy777 visual theme. [Kassahi_Phil777_Crafting_Paladin_Focused.filter]
* Class — Sorceress: Class filter tuned for Sorceress with the philanthropy777 visual theme. [Kassahi_Phil777_Crafting_Sorceress_Focused.filter]
* Mystery — Class — Amazon: Mystery class filter tuned for Amazon with the philanthropy777 visual theme. [Kassahi_Mystery_Phil777_Crafting_Amazon_Focused.filter]
* Mystery — Class — Assassin: Mystery class filter tuned for Assassin with the philanthropy777 visual theme. [Kassahi_Mystery_Phil777_Crafting_Assassin_Focused.filter]
* Mystery — Class — Barbarian: Mystery class filter tuned for Barbarian with the philanthropy777 visual theme. [Kassahi_Mystery_Phil777_Crafting_Barbarian_Focused.filter]
* Mystery — Class — Druid: Mystery class filter tuned for Druid with the philanthropy777 visual theme. [Kassahi_Mystery_Phil777_Crafting_Druid_Focused.filter]
* Mystery — Class — Necromancer: Mystery class filter tuned for Necromancer with the philanthropy777 visual theme. [Kassahi_Mystery_Phil777_Crafting_Necromancer_Focused.filter]
* Mystery — Class — Paladin: Mystery class filter tuned for Paladin with the philanthropy777 visual theme. [Kassahi_Mystery_Phil777_Crafting_Paladin_Focused.filter]
* Mystery — Class — Sorceress: Mystery class filter tuned for Sorceress with the philanthropy777 visual theme. [Kassahi_Mystery_Phil777_Crafting_Sorceress_Focused.filter]

## Filter Preview — Kassahi & Philanthropy777
**[See Kassahi & Philanthropy777 at every filter level on FilterForge](https://maaaaaarrk.github.io/FilterForge/compare.html?only=philanthropy777@2,philanthropy777@4,philanthropy777@6,philanthropy777@7,philanthropy777@8,philanthropy777@10)** — the same drops as the filter shows them in game, one column per filter level (2, 4, 6, 7, 8, 10). Compare all Hiim styles side by side: [Hiim styles](../HIIM_STYLES.md)

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
- Azurewrath (Phase Blade) — ETH
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
- Giant Skull (Bone Visage) — ETH
- Gore Rider (War Boots)
- Griffon's Eye (Diadem)
- Guardian Angel (Templar Coat) — ETH
- Harlequin Crest (Shako) — non-ETH
- Herald of Zakarum (Gilded Shield)
- Lacerator (Winged Axe) — ETH
- Lightsabre (Phase Blade) — ETH
- Mang Song's Lesson (Archon Staff)
- Nightwing's Veil (Spired Helm)
- Occultist (Crusader Gauntlets) — ETH
- Ormus' Robes (Dusk Shroud) — non-ETH
- Plague Bearer (Rune Sword) — ETH
- Purgatory (Archon Plate) — ETH
- Ravenlore (Sky Spirit) — non-ETH
- Ribcracker (Quarterstaff) — ETH
- Schaefer's Hammer (Legendary Mallet)
- Siggard's Staunch (Colossus Girdle)
- Silks of the Victor (Ancient Armor) — ETH
- Skull Collector (Rune Staff)
- Skyfall (Vortex Orb)
- Skywarden (Vortex Shield) — ETH
- Soul Drainer (Vambraces)
- Spectral Plate (Great Hauberk)
- Spirit Keeper (Earth Spirit)
- Steel Carapace (Shadow Plate)
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
- Veil of Steel (Spired Helm)
- War Traveler (Battle Boots) — ETH
- Waterwalk (Sharkskin Boots) — ETH
- Windforce (Hydra Bow) — ETH
- Zerae's Resolve (Matriarchal Pike) — ETH

### Level 9-8 — adds 3-star uniques

- Abyssal Ward (War Bolts) — ETH
- Arachnid Mesh (Spiderweb Sash) — ETH
- Arkaine's Valor (Balrog Skin) — non-ETH
- Athena's Wrath (Battle Scythe) — ETH
- Azurewrath (Phase Blade) — non-ETH
- Bannerlord's Call (War Bolts) — ETH
- Brimstone Rain (Shillelagh)
- Darkforce Spawn (Bloodlord Skull) — ETH
- Demon Machine (Chu-Ko-Nu)
- Denmother (Sun Spirit) — ETH
- Fenris (Alpha Helm) — ETH
- Firelizard's Talons (Feral Claws) — ETH
- Frozen Sorrow (War Bolts) — ETH
- Gerke's Sanctuary (Pavise) — ETH
- Ghostflame (Legend Spike) — ETH
- Giant Skull (Bone Visage) — non-ETH
- Goblin Toe (Light Plated Boots)
- Guardian Angel (Templar Coat) — non-ETH
- Halaberd's Reign (Conqueror Crown) — ETH
- Infernostride (Demonhide Boots) — ETH
- Jade Talon (Wrist Sword) — ETH
- Jalal's Mane (Totemic Mask) — ETH
- Kira's Guardian (Tiara) — non-ETH
- Lava Gout (Battle Gauntlets) — ETH
- Lidless Wall (Grim Shield) — ETH
- Lightsabre (Phase Blade) — non-ETH
- Magefist (Light Gauntlets)
- Marrowwalk (Boneweave Boots)
- Martyrdom (Overseer Skull) — non-ETH
- Medusa's Gaze (Aegis) — ETH
- Nosferatu's Coil (Vampirefang Belt) — ETH
- Occultist (Crusader Gauntlets) — non-ETH
- Pus Spitter (Siege Crossbow)
- Razortail (Sharkskin Belt) — ETH
- Sacred Totem (Hellspawn Skull) — ETH
- Shaftstop (Mesh Armor)
- Silkweave (Mesh Boots) — ETH
- Skin of the Vipermagi (Serpentskin Armor) — ETH
- Skywarden (Vortex Shield) — non-ETH
- Spirit Ward (Ward)
- Stalker's Cull (Runic Talons)
- Steel Pillar (War Pike) — ETH
- Steel Shade (Armet) — non-ETH
- Steelrend (Ogre Gauntlets) — ETH
- Stormspire (Giant Thresher) — non-ETH
- String of Ears (Demonhide Sash)
- The Gavel of Pain (Martel de Fer) — ETH
- Thundergod's Vigor (War Belt) — non-ETH
- Thunderstroke (Matriarchal Javelin) — non-ETH
- Tomb Reaver (Cryptic Axe)
- Twilight's Reflection (Hyperion) — ETH
- Valkyrie Wing (Winged Helm) — ETH
- Vampire Gaze (Grim Helm)
- Verdungo's Hearty Cord (Mithril Coil)
- War Traveler (Battle Boots) — non-ETH
- Warlord's Trust (Military Axe) — ETH
- Warriv's Warder (Heater)
- Waterwalk (Sharkskin Boots) — non-ETH
- Windforce (Hydra Bow) — non-ETH
- Wraithskin (Diamond Mail) — ETH

### Level 7 — adds 2-star uniques

- Anvilguard Strap (Heavy Bolts) — ETH
- Arkaine's Valor (Balrog Skin) — ETH
- Arm of King Leoric (Tomb Wand)
- Arreat's Face (Slayer Guard) — ETH
- Athena's Wrath (Battle Scythe) — non-ETH
- Atma's Wail (Embossed Plate)
- Bartuc's Cut-Throat (Greater Talons) — ETH
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
- Death's Fathom (Dimensional Shard) — non-ETH
- Demonhorn's Edge (Destroyer Helm) — ETH
- Doombringer (Champion Sword) — non-ETH
- Dragonscale (Zakarum Shield) — ETH
- Earth Shifter (Thunder Maul) — non-ETH
- Ebonbane (Grand Matron Bow)
- Embersworn (Demon Heart) — ETH
- Eschuta's Temper (Eldritch Orb) — ETH
- Firelizard's Talons (Feral Claws) — non-ETH
- Flamebellow (Balrog Blade) — ETH
- Frostburn (Gauntlets) — non-ETH
- Gargoyle's Bite (Winged Harpoon)
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
- Horizon's Tornado (Scourge)
- Infernostride (Demonhide Boots) — non-ETH
- Kira's Guardian (Tiara) — ETH
- Lava Gout (Battle Gauntlets) — non-ETH
- Leviathan (Kraken Shell) — ETH
- Lidless Wall (Grim Shield) — non-ETH
- Martyrdom (Overseer Skull) — ETH
- Medusa's Gaze (Aegis) — non-ETH
- Merman's Sprocket (Wyrmhide Boots) — ETH
- Nosferatu's Coil (Vampirefang Belt) — non-ETH
- Ormus' Robes (Dusk Shroud) — ETH
- Peasant Crown (War Hat)
- Plague Bearer (Rune Sword) — non-ETH
- Que-Hegan's Wisdom (Mage Plate) — ETH
- Raekor's Virtue (Guardian Crown) — ETH
- Ravenlore (Sky Spirit) — ETH
- Razortail (Sharkskin Belt) — non-ETH
- Sacred Totem (Hellspawn Skull) — non-ETH
- Sage's Defiance (Giant Conch) — ETH
- Sandstorm Trek (Scarabshell Boots)
- Shadow Dancer (Myrmidon Greaves)
- Shatterhead (Heavy Bolts) — ETH
- Silks of the Victor (Ancient Armor) — non-ETH
- Skin of the Vipermagi (Serpentskin Armor) — non-ETH
- Skullder's Ire (Russet Armor) — ETH
- Snowclash (Battle Belt) — non-ETH
- Spike Thorn (Blade Barrier) — ETH
- Steel Shade (Armet) — ETH
- Steelclash (Kite Shield)
- Steelrend (Ogre Gauntlets) — non-ETH
- Stoneraven (Matriarchal Spear) — non-ETH
- Stormlash (Scourge)
- Stormshield (Monarch)
- Suicide Branch (Burnt Wand)
- Swiftwind Needle (Sharp Arrows)
- The Cranium Basher (Thunder Maul) — non-ETH
- The Gladiator's Bane (Wire Fleece)
- The Grandfather (Colossus Blade) — non-ETH
- The Oculus (Swirling Crystal) — ETH
- The Patriarch (Great Sword) — ETH
- The Reaper's Toll (Thresher) — non-ETH
- Titan's Grip (Bramble Mitts) — ETH
- Titan's Revenge (Ceremonial Javelin) — ETH
- Tombsong (Sharp Arrows)
- Treads of Cthon (Chain Boots)
- Valkyrie Wing (Winged Helm) — non-ETH
- Venom Grip (Demonhide Gloves) — ETH
- Warshrike (Winged Knife)
- Whispering Mirage (War Fist)
- Widowmaker (Ward Bow) — ETH
- Wildspeaker (Lion Helm)
- Wraithskin (Diamond Mail) — non-ETH
- Zerae's Resolve (Matriarchal Pike) — non-ETH

### Level 6 — adds 1-star uniques

- Arioc's Needle (Hyperion Spear) — non-ETH
- Arreat's Face (Slayer Guard) — non-ETH
- Biggin's Bonnet (Cap)
- Black Hades (Chaos Armor)
- Bloodfist (Heavy Gloves)
- Boneflame (Succubus Skull) — non-ETH
- Boneshade (Lich Wand) — non-ETH
- Buriza-Do Kyanon (Ballista) — non-ETH
- Cerebus' Bite (Blood Spirit) — non-ETH
- Chance Guards (Chain Gloves) — ETH
- Chromatic Ire (Cedar Staff)
- Corpsemourn (Ornate Plate) — ETH
- Crow Caw (Tigulated Mail) — non-ETH
- Crown of Thieves (Grand Crown)
- Cyclopean Roar (Jawbone Visor) — non-ETH
- Denmother (Sun Spirit) — non-ETH
- Dragonscale (Zakarum Shield) — non-ETH
- Duskdeep (Full Helm)
- Eaglehorn (Crusader Bow)
- Executioner's Justice (Glorious Axe) — ETH
- Fenris (Alpha Helm) — non-ETH
- Frostburn (Gauntlets) — ETH
- Frostwind (Cryptic Sword)
- Giant Maimer (Colossus Voulge) — ETH
- Gimmershred (Flying Axe)
- Gravepalm (Sharkskin Gloves) — non-ETH
- Harlequin Crest (Shako) — ETH
- Hellslayer (Decapitator)
- Homunculus (Hierophant Trophy) — ETH
- Humongous (Giant Axe)
- Jade Talon (Wrist Sword) — non-ETH
- Jalal's Mane (Totemic Mask) — non-ETH
- Leviathan (Kraken Shell) — non-ETH
- Merman's Sprocket (Wyrmhide Boots) — non-ETH
- Nethercrux (Ghost Wand) — ETH
- Ondal's Wisdom (Elder Staff)
- Purgatory (Archon Plate) — non-ETH
- Radament's Sphere (Ancient Shield) — non-ETH
- Raekor's Virtue (Guardian Crown) — non-ETH
- Ribcracker (Quarterstaff) — non-ETH
- Rockstopper (Sallet)
- Rune Master (Ettin Axe)
- Sage's Defiance (Giant Conch) — non-ETH
- Shatterblade (Mithril Point)
- Silkweave (Mesh Boots) — non-ETH
- Skullder's Ire (Russet Armor) — non-ETH
- Snowclash (Battle Belt) — ETH
- Spike Thorn (Blade Barrier) — non-ETH
- Spirit Shroud (Ghost Armor) — ETH
- Steel Pillar (War Pike) — non-ETH
- Swordguard (Executioner Sword) — non-ETH
- The Spirit Shroud (Ghost Armor) — ETH
- Thundergod's Vigor (War Belt) — ETH
- Toothrow (Sharktooth Armor)
- Twilight's Reflection (Hyperion) — non-ETH
- Ursa's Nightmare (Dream Spirit) — ETH
- Venom Grip (Demonhide Gloves) — non-ETH
- Venom Ward (Breast Plate)
- Viperfork (Mancatcher)
- Windhammer (Ogre Maul) — non-ETH
- Witchwild String (Short Siege Bow) — ETH
- Wizardspike (Bone Knife)

### Level 5 — adds 0-star uniques

- Abyssal Ward (War Bolts) — non-ETH
- Anvilguard Strap (Heavy Bolts) — non-ETH
- Bannerlord's Call (War Bolts) — non-ETH
- Bartuc's Cut-Throat (Greater Talons) — non-ETH
- Blackbog's Sharp (Cinquedeas)
- Blood Raven's Charge (Matriarchal Bow) — non-ETH
- Bloodtree Stump (War Club) — non-ETH
- Death Cleaver (Berserker Axe) — non-ETH
- Death's Fathom (Dimensional Shard) — ETH
- Embersworn (Demon Heart) — non-ETH
- Endlesshail (Double Bow)
- Eschuta's Temper (Eldritch Orb) — non-ETH
- Frozen Sorrow (War Bolts) — non-ETH
- Gorefoot (Heavy Boots)
- Homunculus (Hierophant Trophy) — non-ETH
- Odium (Colossus Sword) — ETH
- Que-Hegan's Wisdom (Mage Plate) — non-ETH
- Radament's Sphere (Ancient Shield) — ETH
- Shatterhead (Heavy Bolts) — non-ETH
- The Gavel of Pain (Martel de Fer) — non-ETH
- The Jade Tan Do (Kris)
- The Oculus (Swirling Crystal) — non-ETH
- The Patriarch (Great Sword) — non-ETH
- Titan's Revenge (Ceremonial Javelin) — non-ETH
- Ursa's Nightmare (Dream Spirit) — non-ETH
- Widowmaker (Ward Bow) — non-ETH
- Wizendraw (Long Battle Bow)
- Wolfhowl (Fury Visor) — ETH

### Level 4 — adds NO-star uniques

- Baezil's Vortex (Knout)
- Blackoak Shield (Luna)
- Cloudcrack (Gothic Sword)
- Corpsemourn (Ornate Plate) — non-ETH
- Demonhorn's Edge (Destroyer Helm) — non-ETH
- Djinn Slayer (Ataghan)
- Executioner's Justice (Glorious Axe) — non-ETH
- Flamebellow (Balrog Blade) — non-ETH
- Ghoulhide (Heavy Bracers) — non-ETH
- Giant Maimer (Colossus Voulge) — non-ETH
- Goldwrap (Heavy Belt) — non-ETH
- Gull (Dagger)
- Heavenly Garb (Light Plate) — non-ETH
- Hellmouth (War Gauntlets) — non-ETH
- Kuko Shakaku (Cedar Bow)
- Lacerator (Winged Axe) — non-ETH
- Magewrath (Rune Bow)
- Nethercrux (Ghost Wand) — non-ETH
- Odium (Colossus Sword) — non-ETH
- Spirit Shroud (Ghost Armor) — non-ETH
- Swordguard (Executioner Sword) — ETH
- The Hand of Broc (Leather Gloves)
- The Impaler (War Spear)
- The Spirit Shroud (Ghost Armor) — non-ETH
- Titan's Grip (Bramble Mitts) — non-ETH
- Warlord's Trust (Military Axe) — non-ETH
- Windhammer (Ogre Maul) — ETH
- Witchwild String (Short Siege Bow) — non-ETH
- Wolfhowl (Fury Visor) — non-ETH

### Level 1-3 — most permissive

*All uniques are shown.*

