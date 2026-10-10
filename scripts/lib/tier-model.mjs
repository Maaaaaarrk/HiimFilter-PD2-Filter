// Shared model of the unique / set star tiers.
//
// Source of truth: builderfilter/data/unique-set-tiers.json (one entry per unique or set
// item: code, name, base, current, floor, optional eth {current, floor}, lld, locked).
// builderfilter/tier_aliases.py generates the 05-unid-unique-set-stars alias file from it
// on every build — the scripts only read and write the JSON.
//
// Unidentified items only reveal their base, so a base code's tier is the best tier of
// any entry on it, per variant (ETH / non-ETH). Keep uniqueAliasesFor() in sync with
// unique_aliases_for() in builderfilter/tier_aliases.py.

import { readFile, writeFile } from 'node:fs/promises';

export const TIERS_FILE = 'builderfilter/data/unique-set-tiers.json';

// Best -> worst. "no-star" is still a shown tier; null means "not starred".
export const UNIQUE_SCALE = ['4', '3', '2', '1', '0', 'no-star'];
export const SET_SCALE = ['4', '3', '2', '1', '0'];

// Alias-style tier names (used by the suggest scripts' reports and diff files).
export const UNIQUE_ALIAS = {
  4: '4_STAR_UNIQUE', 3: '3_STAR_UNIQUE', 2: '2_STAR_UNIQUE', 1: '1_STAR_UNIQUE', 0: '0_STAR_UNIQUE', 'no-star': 'NO_STAR_UNIQUE',
};
export const UNIQUE_ETH_ALIAS = Object.fromEntries(
  Object.entries(UNIQUE_ALIAS).map(([t, a]) => [t, a.replace('_UNIQUE', '_ETH_UNIQUE')]),
);
export const SET_ALIAS = { 4: '4_STAR_SET', 3: '3_STAR_SET', 2: '2_STAR_SET', 1: '1_STAR_SET', 0: '0_STAR_SET' };
export const UNIQUE_VALUE_TIERS = UNIQUE_SCALE.map((t) => UNIQUE_ALIAS[t]);
export const SET_TIERS = SET_SCALE.map((t) => SET_ALIAS[t]);
const FROM_ALIAS = Object.fromEntries([
  ...Object.entries(UNIQUE_ALIAS).map(([t, a]) => [a, t]),
  ...Object.entries(UNIQUE_ETH_ALIAS).map(([t, a]) => [a, t]),
  ...Object.entries(SET_ALIAS).map(([t, a]) => [a, t]),
]);
export const tierFromAlias = (alias) => (alias == null ? null : FROM_ALIAS[alias] ?? null);

// Rank on a scale: higher is better; null (not starred) is below everything.
export const rankOn = (scale, tier) => (tier == null ? -1 : scale.length - scale.indexOf(tier));
export const bestOf = (scale, tiers) =>
  tiers.filter((t) => t != null).reduce((best, t) => (rankOn(scale, t) > rankOn(scale, best) ? t : best), null);

// Alias-name rank (kept for callers that work with alias names).
export const rank = (alias) => {
  const t = tierFromAlias(alias);
  if (t == null) return -1;
  return alias.endsWith('_SET') ? rankOn(SET_SCALE, t) : rankOn(UNIQUE_SCALE, t);
};
export const stars = (aliasOrTier) => {
  if (aliasOrTier == null) return '—';
  const t = tierFromAlias(aliasOrTier) ?? aliasOrTier;
  return t === 'no-star' ? 'no' : `${t}★`;
};

// ---- JSON I/O ----------------------------------------------------------------------

export async function loadTiers(path = TIERS_FILE) {
  return JSON.parse(await readFile(path, 'utf8'));
}

// Compact JSON with ", " / ": " separators (matches Python's json.dumps default).
const spaced = (v) => (v && typeof v === 'object'
  ? `{${Object.entries(v).map(([k, x]) => `${JSON.stringify(k)}: ${spaced(x)}`).join(', ')}}`
  : JSON.stringify(v));

// One entry per line, same layout as the committed file, so diffs stay one line per change.
export function formatTiers(data) {
  const line = (e) => `    ${spaced(e)}`;
  const out = ['{', '  "_readme": [', data._readme.map((s) => `    ${JSON.stringify(s)}`).join(',\n'), '  ],'];
  for (const kind of ['uniques', 'sets']) {
    const sorted = [...data[kind]].sort((a, b) => (a.code < b.code ? -1 : a.code > b.code ? 1 : a.name < b.name ? -1 : a.name > b.name ? 1 : 0));
    out.push(`  "${kind}": [`, sorted.map(line).join(',\n'), `  ]${kind === 'uniques' ? ',' : ''}`);
  }
  out.push('}');
  return out.join('\n') + '\n';
}

export async function saveTiers(data, path = TIERS_FILE) {
  let text = formatTiers(data);
  try {
    if ((await readFile(path, 'utf8')).includes('\r\n')) text = text.replace(/\n/g, '\r\n'); // keep the checkout's EOL
  } catch { /* new file */ }
  await writeFile(path, text, 'utf8');
}

// ---- per-entry / per-base views ----------------------------------------------------

export const entryTier = (e, variant) => (variant === 'eth' && e.eth ? e.eth.current : e.current) ?? null;
export const entryFloor = (e, variant) => (variant === 'eth' && e.eth ? e.eth.floor : e.floor) ?? null;

// code -> { noneth, eth, lld, entries }  (tiers on UNIQUE_SCALE)
export function uniqueBaseTiers(data) {
  const out = new Map();
  for (const e of data.uniques) {
    if (!out.has(e.code)) out.set(e.code, { entries: [] });
    out.get(e.code).entries.push(e);
  }
  for (const b of out.values()) {
    b.noneth = bestOf(UNIQUE_SCALE, b.entries.map((e) => entryTier(e, 'noneth')));
    b.eth = bestOf(UNIQUE_SCALE, b.entries.map((e) => entryTier(e, 'eth')));
    b.lld = b.entries.some((e) => e.lld);
  }
  return out;
}

// code -> { tier, lld, entries }  (tiers on SET_SCALE)
export function setBaseTiers(data) {
  const out = new Map();
  for (const e of data.sets) {
    if (!out.has(e.code)) out.set(e.code, { entries: [] });
    out.get(e.code).entries.push(e);
  }
  for (const b of out.values()) {
    b.tier = bestOf(SET_SCALE, b.entries.map((e) => entryTier(e, 'noneth')));
    b.lld = b.entries.some((e) => e.lld);
  }
  return out;
}

// Highest floor among a base's entries for a variant ('noneth' | 'eth').
export const baseFloor = (scale, entries, variant) => bestOf(scale, entries.map((e) => entryFloor(e, variant)));
export const baseLocked = (entries) => entries.some((e) => e.locked);
// ETH copies held higher than non-ETH ones (old "eth-protected" IGNORE_MOVES rule).
export const ethFloored = (entries) =>
  entries.some((e) => e.eth && e.eth.floor != null && rankOn(UNIQUE_SCALE, e.eth.floor) > rankOn(UNIQUE_SCALE, e.floor));

// Alias names a base is listed in for non-ETH tier n / ETH tier e. Non-ETH and ETH tiers
// have separate alias lists, so every combination works.
// Mirror of unique_aliases_for() in builderfilter/tier_aliases.py.
export function uniqueAliasesFor(n, e) {
  return [...(n != null ? [UNIQUE_ALIAS[n]] : []), ...(e != null ? [UNIQUE_ETH_ALIAS[e]] : [])];
}

const norm = (s) => (s || '').toLowerCase().replace(/[^a-z0-9]/g, '');
export const sameName = (a, b) => norm(a) === norm(b);
