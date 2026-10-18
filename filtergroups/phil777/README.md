# phil777
## Last updated October 18th Season 14 - build 76
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
  * Magic rings and amulets hidden
  * Most unidentified rares hidden (CLVL 86+)
  * Rune number labels removed from display
  * Still shows: all uniques/sets, high value rares, runes, jewels, charms

* **4: Semi-Strict** — Everything from level 3, plus:
  * Unrated unidentified uniques and sets (no star tier) hidden (CLVL 85+)

* **5: Strict** — For players comfortable with the game who want a cleaner screen during fast farming.
  * NO-star unidentified uniques hidden
  * Class-specific rare item decorations end at higher filter levels
  * Eth magic crafting bases reduced
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
  * ETH rare armor (chests) hidden; non-ETH rare gloves, boots, and belts hidden; Chests (ALVL<85) hidden
  * Class-specific items hidden: sorc orbs, druid pelts, paladin shields, magic necro heads (barb helms already hidden since level 5; rare necro heads not hidden until level 9)
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
- Arkaine's Valor (Balrog Skin) — non-ETH
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
- Ghostflame (Legend Spike)
- Giant Skull (Bone Visage)
- Gore Rider (War Boots)
- Griffon's Eye (Diadem)
- Guardian Angel (Templar Coat) — ETH
- Herald of Zakarum (Gilded Shield)
- Kira's Guardian (Tiara) — non-ETH
- Lacerator (Winged Axe) — ETH
- Lightsabre (Phase Blade)
- Mang Song's Lesson (Archon Staff)
- Nightwing's Veil (Spired Helm)
- Occultist (Crusader Gauntlets)
- Plague Bearer (Rune Sword)
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
- Spectral Plate (Great Hauberk)
- Spirit Keeper (Earth Spirit)
- Spirit Ward (Ward) — non-ETH
- Steel Carapace (Shadow Plate)
- Steel Shade (Armet) — non-ETH
- Stone Crusher (Legendary Mallet)
- Stoneraven (Matriarchal Spear)
- Stormspire (Giant Thresher) — ETH
- Templar's Might (Sacred Armor)
- The Cranium Basher (Thunder Maul) — ETH
- The Grandfather (Colossus Blade) — ETH
- The Reaper's Toll (Thresher) — ETH
- Thunderstroke (Matriarchal Javelin)
- Tomb Reaver (Cryptic Axe)
- True Silver (Maiden Javelin) — ETH
- Tyrael's Might (Sacred Armor)
- Vampire Gaze (Grim Helm)
- Veil of Steel (Spired Helm)
- Verdungo's Hearty Cord (Mithril Coil)
- War Traveler (Battle Boots)
- Waterwalk (Sharkskin Boots)
- Windforce (Hydra Bow)
- Zerae's Resolve (Matriarchal Pike) — ETH

### Level 9-8 — adds 3-star uniques

- Abyssal Ward (War Bolts)
- Arachnid Mesh (Spiderweb Sash) — ETH
- Athena's Wrath (Battle Scythe) — ETH
- Bannerlord's Call (War Bolts)
- Brimstone Rain (Shillelagh)
- Darkforce Spawn (Bloodlord Skull)
- Demon Machine (Chu-Ko-Nu)
- Denmother (Sun Spirit)
- Doombringer (Champion Sword) — non-ETH
- Earth Shifter (Thunder Maul) — non-ETH
- Fenris (Alpha Helm)
- Firelizard's Talons (Feral Claws)
- Frozen Sorrow (War Bolts)
- Gerke's Sanctuary (Pavise)
- Goblin Toe (Light Plated Boots)
- Guardian Angel (Templar Coat) — non-ETH
- Halaberd's Reign (Conqueror Crown)
- Harlequin Crest (Shako) — non-ETH
- Infernostride (Demonhide Boots)
- Jade Talon (Wrist Sword)
- Jalal's Mane (Totemic Mask)
- Lava Gout (Battle Gauntlets)
- Lidless Wall (Grim Shield)
- Magefist (Light Gauntlets)
- Marrowwalk (Boneweave Boots)
- Martyrdom (Overseer Skull) — non-ETH
- Medusa's Gaze (Aegis)
- Nosferatu's Coil (Vampirefang Belt)
- Ormus' Robes (Dusk Shroud) — non-ETH
- Pus Spitter (Siege Crossbow)
- Razortail (Sharkskin Belt)
- Sacred Totem (Hellspawn Skull)
- Shaftstop (Mesh Armor)
- Silkweave (Mesh Boots)
- Skin of the Vipermagi (Serpentskin Armor)
- Snowclash (Battle Belt) — non-ETH
- Spirit Ward (Ward) — ETH
- Stalker's Cull (Runic Talons)
- Steel Pillar (War Pike) — ETH
- Steelrend (Ogre Gauntlets)
- Stormshield (Monarch) — non-ETH
- Stormspire (Giant Thresher) — non-ETH
- String of Ears (Demonhide Sash)
- The Cranium Basher (Thunder Maul) — non-ETH
- The Gavel of Pain (Martel de Fer) — ETH
- The Grandfather (Colossus Blade) — non-ETH
- The Reaper's Toll (Thresher) — non-ETH
- Thundergod's Vigor (War Belt) — non-ETH
- Twilight's Reflection (Hyperion)
- Valkyrie Wing (Winged Helm)
- Warlord's Trust (Military Axe) — ETH
- Warriv's Warder (Heater)
- Whispering Mirage (War Fist)
- Wraithskin (Diamond Mail)
- Zerae's Resolve (Matriarchal Pike) — non-ETH

### Level 7 — adds 2-star uniques

- Anvilguard Strap (Heavy Bolts)
- Arioc's Needle (Hyperion Spear) — non-ETH
- Arkaine's Valor (Balrog Skin) — ETH
- Arm of King Leoric (Tomb Wand)
- Arreat's Face (Slayer Guard)
- Athena's Wrath (Battle Scythe) — non-ETH
- Atma's Wail (Embossed Plate)
- Bartuc's Cut-Throat (Greater Talons)
- Blackhand Key (Grave Wand)
- Blade of Ali Baba (Tulwar)
- Blood Raven's Charge (Matriarchal Bow)
- Bloodtree Stump (War Club) — ETH
- Boneflame (Succubus Skull)
- Boneshade (Lich Wand)
- Buriza-Do Kyanon (Ballista)
- Cerebus' Bite (Blood Spirit)
- Crow Caw (Tigulated Mail)
- Cyclopean Roar (Jawbone Visor)
- Death Cleaver (Berserker Axe) — non-ETH
- Death's Fathom (Dimensional Shard)
- Demonhorn's Edge (Destroyer Helm)
- Dragonscale (Zakarum Shield)
- Ebonbane (Grand Matron Bow)
- Embersworn (Demon Heart)
- Eschuta's Temper (Eldritch Orb)
- Flamebellow (Balrog Blade)
- Gargoyle's Bite (Winged Harpoon)
- Ghoulhide (Heavy Bracers)
- Goldwrap (Heavy Belt)
- Gravepalm (Sharkskin Gloves)
- Grim's Burning Dead (Grim Scythe)
- Head Hunter's Glory (Troll Nest)
- Heart Carver (Rondel)
- Heavenly Garb (Light Plate)
- Hellmouth (War Gauntlets)
- Hellslayer (Decapitator)
- Horizon's Tornado (Scourge)
- Kira's Guardian (Tiara) — ETH
- Leviathan (Kraken Shell)
- Martyrdom (Overseer Skull) — ETH
- Merman's Sprocket (Wyrmhide Boots)
- Ormus' Robes (Dusk Shroud) — ETH
- Peasant Crown (War Hat)
- Que-Hegan's Wisdom (Mage Plate)
- Raekor's Virtue (Guardian Crown)
- Ravenlore (Sky Spirit) — ETH
- Sage's Defiance (Giant Conch)
- Sandstorm Trek (Scarabshell Boots)
- Shadow Dancer (Myrmidon Greaves)
- Shatterhead (Heavy Bolts)
- Silks of the Victor (Ancient Armor) — non-ETH
- Skullder's Ire (Russet Armor)
- Spike Thorn (Blade Barrier)
- Steel Pillar (War Pike) — non-ETH
- Steel Shade (Armet) — ETH
- Steelclash (Kite Shield)
- Stormlash (Scourge)
- Stormshield (Monarch) — ETH
- Suicide Branch (Burnt Wand)
- Swiftwind Needle (Sharp Arrows)
- The Gladiator's Bane (Wire Fleece)
- The Oculus (Swirling Crystal)
- The Patriarch (Great Sword)
- Titan's Grip (Bramble Mitts)
- Titan's Revenge (Ceremonial Javelin) — ETH
- Tombsong (Sharp Arrows)
- Treads of Cthon (Chain Boots)
- Venom Grip (Demonhide Gloves)
- Widowmaker (Ward Bow)
- Wildspeaker (Lion Helm)
- Windhammer (Ogre Maul)

### Level 6 — adds 1-star uniques

- Biggin's Bonnet (Cap)
- Black Hades (Chaos Armor)
- Bloodfist (Heavy Gloves)
- Chance Guards (Chain Gloves)
- Chromatic Ire (Cedar Staff)
- Corpsemourn (Ornate Plate)
- Crown of Thieves (Grand Crown)
- Duskdeep (Full Helm)
- Eaglehorn (Crusader Bow)
- Executioner's Justice (Glorious Axe)
- Frostburn (Gauntlets)
- Frostwind (Cryptic Sword)
- Giant Maimer (Colossus Voulge)
- Gimmershred (Flying Axe)
- Harlequin Crest (Shako) — ETH
- Homunculus (Hierophant Trophy)
- Humongous (Giant Axe)
- Nethercrux (Ghost Wand)
- Ondal's Wisdom (Elder Staff)
- Purgatory (Archon Plate) — non-ETH
- Ribcracker (Quarterstaff) — non-ETH
- Rockstopper (Sallet)
- Rune Master (Ettin Axe)
- Shatterblade (Mithril Point)
- Snowclash (Battle Belt) — ETH
- Spirit Shroud (Ghost Armor)
- Swordguard (Executioner Sword)
- The Gavel of Pain (Martel de Fer) — non-ETH
- Thundergod's Vigor (War Belt) — ETH
- Titan's Revenge (Ceremonial Javelin) — non-ETH
- Toothrow (Sharktooth Armor)
- Ursa's Nightmare (Dream Spirit)
- Venom Ward (Breast Plate)
- Viperfork (Mancatcher)
- Witchwild String (Short Siege Bow)
- Wizardspike (Bone Knife)

### Level 5 — adds 0-star uniques

- Blackbog's Sharp (Cinquedeas)
- Bloodtree Stump (War Club) — non-ETH
- Endlesshail (Double Bow)
- Gorefoot (Heavy Boots)
- Lacerator (Winged Axe) — non-ETH
- Odium (Colossus Sword)
- Radament's Sphere (Ancient Shield)
- The Jade Tan Do (Kris)
- Wizendraw (Long Battle Bow)
- Wolfhowl (Fury Visor)

### Level 4 — adds NO-star uniques

- Baezil's Vortex (Knout)
- Blackoak Shield (Luna)
- Cloudcrack (Gothic Sword)
- Djinn Slayer (Ataghan)
- Gull (Dagger)
- Kuko Shakaku (Cedar Bow)
- Magewrath (Rune Bow)
- The Hand of Broc (Leather Gloves)
- The Impaler (War Spear)
- Warlord's Trust (Military Axe) — non-ETH

### Level 1-3 — most permissive

*All uniques are shown.*

