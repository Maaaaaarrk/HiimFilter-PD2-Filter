// Refresh builderfilter/data/class-builds/<Class>.json from Hiim's tier lists on hiimpd2.com.
//
// For each class, every build linked from the current season's tier lists (solo, group-*,
// boss, starter) is fetched from the public planner API, and the uniques and set items the
// character wears are collected with their base codes. Mercenary gear is left out, and so
// are rings and amulets (unidentified unique jewelry already shows through level 10). The class
// filters use the list as a safety net: those items stay visible at the stricter filter
// levels (see builderfilter/class_build_aliases.py).
//
// Usage: node scripts/update-class-build-items.mjs [--season=14]

import { mkdir, readFile, writeFile } from 'node:fs/promises';

const API = 'https://hiimpd2.com/api';
const LISTS = ['solo', 'group-generalist', 'group-physical', 'group-elemental', 'boss', 'starter'];
const OUT_DIR = 'builderfilter/data/class-builds';
const CLASSES = ['Amazon', 'Assassin', 'Barbarian', 'Druid', 'Necromancer', 'Paladin', 'Sorceress'];
const JEWELRY_SLOTS = new Set(['ring', 'amulet']);

const args = Object.fromEntries(
  process.argv.slice(2).map((a) => a.replace(/^--/, '').split('=')).map(([k, v]) => [k, v ?? 'true']),
);

async function getJson(url) {
  for (let attempt = 1; ; attempt++) {
    const res = await fetch(url);
    if (res.ok) return res.json();
    if (attempt >= 3 || res.status < 500) throw new Error(`${url}: HTTP ${res.status}`);
    await new Promise((r) => setTimeout(r, 1000 * attempt));
  }
}

async function main() {
  // Tier lists: build ids and their names per class
  const first = await getJson(`${API}/tiers?list=${LISTS[0]}${args.season ? `&season=${args.season}` : ''}`);
  const season = first.season;
  const builds = new Map(); // buildId -> { className, names: Set }
  for (const list of LISTS) {
    const data = list === LISTS[0] ? first : await getJson(`${API}/tiers?list=${list}&season=${season}`);
    for (const e of data.entries) {
      if (!e.buildId || e.hidden) continue;
      if (!builds.has(e.buildId)) builds.set(e.buildId, { className: e.className, names: new Set() });
      builds.get(e.buildId).names.add(e.buildName);
    }
  }

  const { items } = await getJson(`https://hiimpd2.com/data/s${season}/planner/items.json`);
  const byId = new Map(items.map((i) => [i.id, i]));

  // class -> item id -> build names
  const usage = Object.fromEntries(CLASSES.map((c) => [c, new Map()]));
  let fetched = 0;
  const ids = [...builds.keys()];
  for (let i = 0; i < ids.length; i += 8) {
    await Promise.all(ids.slice(i, i + 8).map(async (id) => {
      let build;
      try {
        ({ build } = await getJson(`${API}/builds/${id}`));
      } catch (err) {
        // private or deleted builds are not readable; the rest still count
        console.warn(`skipped build ${id} (${[...builds.get(id).names].join(', ')}): ${err.message}`);
        return;
      }
      fetched++;
      const info = builds.get(id);
      const cls = usage[info.className];
      if (!cls) return;
      // the character's own gear only (not the merc's), without rings and amulets
      for (const g of Object.values(build.build?.gear || {})) {
        if (!g || (g.kind !== 'unique' && g.kind !== 'set') || !byId.has(g.id)) continue;
        if (JEWELRY_SLOTS.has(byId.get(g.id).slot)) continue;
        if (!cls.has(g.id)) cls.set(g.id, new Set());
        for (const n of info.names) cls.get(g.id).add(n);
      }
    }));
  }

  const classes = {};
  for (const c of CLASSES) {
    const out = { uniques: [], sets: [] };
    for (const [id, names] of usage[c]) {
      const it = byId.get(id);
      const entry = { name: it.name, code: it.base ?? it.code ?? ({ ring: 'rin', amulet: 'amu' })[it.slot] ?? null, base: it.baseName ?? null, builds: [...names].sort() };
      (it.kind === 'unique' ? out.uniques : out.sets).push(entry);
    }
    for (const k of ['uniques', 'sets']) {
      out[k].sort((a, b) => b.builds.length - a.builds.length || a.name.localeCompare(b.name));
    }
    classes[c] = out;
  }

  console.log(`season ${season}: ${builds.size} tier-list builds (${fetched} fetched)`);
  await mkdir(OUT_DIR, { recursive: true });
  for (const c of CLASSES) {
    const path = `${OUT_DIR}/${c}.json`;
    // Hand edits survive a refresh: "manual" entries are kept and "exclude" names stay out.
    let old = {};
    try { old = JSON.parse(await readFile(path, 'utf8')); } catch { /* new file */ }
    const exclude = old.exclude ?? [];
    const merged = {};
    for (const k of ['uniques', 'sets']) {
      const planner = classes[c][k].filter((e) => !exclude.includes(e.name));
      const manual = (old[k] ?? []).filter((e) => e.manual && !planner.some((p) => p.name === e.name));
      merged[k] = [...planner, ...manual];
    }
    await writeFile(path, formatClass(c, season, exclude, merged), 'utf8');
    console.log(`  ${c.padEnd(12)} ${merged.uniques.length} uniques, ${merged.sets.length} set items -> ${path}`);
  }
}

const README = [
  'Uniques and set items the character wears (not merc gear, rings or amulets) in this class\'s builds on Hiim\'s',
  'tier lists (hiimpd2.com). builderfilter/class_build_aliases.py builds CLASS_BUILD_UNIQUE /',
  'CLASS_BUILD_SET for this class filter from it on every build; those items stay visible through',
  'filter level 10. Refresh from the planners: node scripts/update-class-build-items.mjs',
  'Editing: add {"name": "<unique or set item>", "manual": true} to keep an item the planners',
  'don\'t list (add "code" for items not in unique-set-tiers.json, e.g. rings / amulets), and',
  'put names in "exclude" to drop a planner item. Both survive a refresh.',
];

// One item per line so edits and refreshes diff cleanly.
function formatClass(cls, season, exclude, items) {
  const list = (arr) => (arr.length ? `[\n${arr.map((e) => `    ${JSON.stringify(e)}`).join(',\n')}\n  ]` : '[]');
  return [
    '{',
    `  "_readme": [\n${README.map((s) => `    ${JSON.stringify(s)}`).join(',\n')}\n  ],`,
    `  "class": ${JSON.stringify(cls)},`,
    `  "season": ${season},`,
    `  "exclude": ${JSON.stringify(exclude)},`,
    `  "uniques": ${list(items.uniques)},`,
    `  "sets": ${list(items.sets)}`,
    '}',
  ].join('\n') + '\n';
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
