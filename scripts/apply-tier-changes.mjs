// Applies the moves suggested by suggest-unique-tiers.mjs and suggest-set-tiers.mjs to
// builderfilter/data/unique-set-tiers.json (the build regenerates the alias file from it).
//
// Upgrades are always applied: the entry for the market's top item on that base is raised
// (a new entry is added if the JSON doesn't list that item yet).
// Downgrades are applied only with --downgrades=true: every entry on the base is lowered to
// the suggested tier, but never below its own floor. Locked entries are never touched, and
// a change is skipped if the base's ETH / non-ETH combination can't be expressed by the
// tier aliases. In upgrade-only mode a final check aborts if any base would end up lower.
//
// Input:  temp/unique-tier-diff.json, temp/set-tier-diff.json (either may be missing)
// Output: builderfilter/data/unique-set-tiers.json (only if something changed)
//         temp/tier-changes-applied.md — summary used as the bot PR body
//
// Usage:
//   node scripts/suggest-unique-tiers.mjs && node scripts/suggest-set-tiers.mjs
//   node scripts/apply-tier-changes.mjs [--downgrades=true] [--dry-run=true]

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import {
  loadTiers, saveTiers, uniqueBaseTiers, setBaseTiers, isExpressible,
  UNIQUE_SCALE, SET_SCALE, rankOn, tierFromAlias, stars, sameName, entryTier, entryFloor,
} from './lib/tier-model.mjs';

const UNIQUE_DIFF = 'temp/unique-tier-diff.json';
const SET_DIFF = 'temp/set-tier-diff.json';
const SUMMARY_FILE = 'temp/tier-changes-applied.md';

const dryRun = process.argv.includes('--dry-run=true');
const allowDowngrades = process.argv.includes('--downgrades=true');

async function readDiff(path) {
  try {
    return JSON.parse(await readFile(path, 'utf8'));
  } catch (err) {
    if (err.code === 'ENOENT') return null;
    throw err;
  }
}

const clone = (x) => JSON.parse(JSON.stringify(x));
const higher = (scale, a, b) => (rankOn(scale, a) >= rankOn(scale, b) ? a : b);

// Set one variant of an entry ('noneth' | 'eth'), keeping the other variant as it was.
// Set items have no ETH variant: only 'current' is used.
function setVariant(e, variant, tier, isUnique = true) {
  if (!isUnique) { e.current = tier; return; }
  if (variant === 'eth') {
    if (!e.eth) e.eth = { current: e.current ?? null, floor: e.floor ?? null };
    e.eth.current = tier;
  } else {
    if (!e.eth && 'current' in e) e.eth = { current: e.current ?? null, floor: e.floor ?? null };
    e.current = tier;
  }
}

// Drop an eth block that says the same thing as the entry itself.
function tidyEth(e) {
  if (e.eth && (e.eth.current ?? null) === (e.current ?? null) && (e.eth.floor ?? null) === (e.floor ?? null)) delete e.eth;
}

// "Name 2★ → 3★", or per variant when ETH and non-ETH moved differently.
function describe(e, moved, isUnique) {
  if (!moved.length) return [];
  const same = moved.length > 1 && moved.every((x) => x.cur === moved[0].cur && x.next === moved[0].next);
  const label = (x) => `${stars(x.cur)} → ${stars(x.next)}${x.floored ? ' (floor)' : ''}`;
  if (!isUnique || same || moved.length === 1 && !e.eth) return [`${e.name} ${label(moved[0])}`];
  return moved.map((x) => `${e.name} (${x.v === 'eth' ? 'ETH' : 'non-ETH'}) ${label(x)}`);
}

const VARIANTS = { both: ['noneth', 'eth'], noneth: ['noneth'], eth: ['eth'] };

function applyMove(data, kind, m) {
  const isUnique = kind === 'unique';
  const scale = isUnique ? UNIQUE_SCALE : SET_SCALE;
  const list = isUnique ? data.uniques : data.sets;
  const variants = isUnique ? VARIANTS[m.variant ?? 'both'] : ['noneth'];
  const target = tierFromAlias(m.suggestedTier);
  const up = m.delta > 0;
  const entries = list.filter((e) => e.code === m.base);
  if (target == null) return { skip: `unknown tier ${m.suggestedTier}` };
  if (entries.some((e) => e.locked)) return { skip: 'locked' };
  if (!up && !allowDowngrades) return { skip: 'downgrades disabled', ignored: true };

  const view = (d) => (isUnique ? uniqueBaseTiers(d) : setBaseTiers(d)).get(m.base);
  const tiersOf = (b) => (isUnique ? { noneth: b?.noneth ?? null, eth: b?.eth ?? null } : { noneth: b?.tier ?? null });
  const before = tiersOf(view(data));
  const trial = clone(data);
  const tList = isUnique ? trial.uniques : trial.sets;
  const changed = [];

  if (up) {
    let e = tList.find((x) => x.code === m.base && sameName(x.name, m.topName));
    if (!e) {
      const like = entries[0];
      e = { code: m.base, name: m.topName || `${like?.base ?? m.base} (${kind})`, base: like?.base ?? m.base, current: null, floor: null };
      tList.push(e);
      changed.push(`added ${e.name}`);
    }
    const moved = [];
    for (const v of variants) {
      const cur = entryTier(e, v);
      if (rankOn(scale, target) > rankOn(scale, cur)) {
        setVariant(e, v, target, isUnique);
        moved.push({ v, cur, next: target });
      }
    }
    tidyEth(e);
    changed.push(...describe(e, moved, isUnique));
  } else {
    for (const e of tList.filter((x) => x.code === m.base)) {
      const moved = [];
      for (const v of variants) {
        const cur = entryTier(e, v);
        if (rankOn(scale, cur) <= rankOn(scale, target)) continue;
        const next = higher(scale, target, entryFloor(e, v));
        if (next === cur) continue;
        setVariant(e, v, next, isUnique);
        moved.push({ v, cur, next, floored: next !== target });
      }
      tidyEth(e);
      changed.push(...describe(e, moved, isUnique));
    }
  }
  if (!changed.length) return { skip: up ? 'already at or above the target' : 'held by floors' };

  const after = tiersOf(view(trial));
  if (isUnique && !isExpressible(after.noneth, after.eth)) {
    return { skip: `non-ETH ${stars(after.noneth)} / ETH ${stars(after.eth)} can't be expressed by the tier aliases` };
  }
  if (up && Object.keys(before).some((k) => rankOn(scale, after[k]) < rankOn(scale, before[k]))) {
    return { skip: 'would lower another variant' };
  }
  return { data: trial, before, after, changed };
}

function fmtHR(v) {
  if (!Number.isFinite(v)) return '?';
  return v >= 1 ? `${v.toFixed(2)} HR` : `${(v * 100).toFixed(1)} WSS`;
}
const fmtTiers = (t) => (t.eth !== undefined && t.eth !== t.noneth ? `${stars(t.noneth)} / ETH ${stars(t.eth)}` : stars(t.noneth));

async function main() {
  const uniqueDiff = await readDiff(UNIQUE_DIFF);
  const setDiff = await readDiff(SET_DIFF);
  if (!uniqueDiff && !setDiff) throw new Error(`neither ${UNIQUE_DIFF} nor ${SET_DIFF} exists — run the suggest scripts first`);

  const original = await loadTiers();
  let data = clone(original);
  const applied = [];
  const skipped = [];
  let ignoredDowngrades = 0;
  const jobs = [
    ...(uniqueDiff?.moves ?? []).map((m) => ['unique', m]),
    ...(setDiff?.moves ?? []).map((m) => ['set', m]),
  ];
  for (const [kind, m] of jobs) {
    const r = applyMove(data, kind, m);
    if (r.ignored) { ignoredDowngrades++; continue; }
    if (r.skip) { skipped.push({ kind, m, reason: r.skip }); continue; }
    data = r.data;
    applied.push({ kind, m, before: r.before, after: r.after, changed: r.changed });
  }

  // Upgrade-only safety net: no base anywhere ends up lower.
  if (!allowDowngrades) {
    const drops = [];
    const check = (fn, scale, keys) => {
      const b = fn(original), a = fn(data);
      for (const [code, x] of b) for (const k of keys) {
        if (rankOn(scale, a.get(code)?.[k] ?? null) < rankOn(scale, x[k])) drops.push(`${code} ${k}: ${x[k]} -> ${a.get(code)?.[k]}`);
      }
    };
    check(uniqueBaseTiers, UNIQUE_SCALE, ['noneth', 'eth']);
    check(setBaseTiers, SET_SCALE, ['tier']);
    if (drops.length) {
      console.error('ABORT: an upgrade would lower a tier — nothing written:\n  ' + drops.join('\n  '));
      process.exit(1);
    }
  }

  const ups = applied.filter((a) => a.m.delta > 0);
  const downs = applied.filter((a) => a.m.delta < 0);
  const md = [];
  md.push(`Automated star-tier update from the PD2 market (\`suggest-unique-tiers\` + \`suggest-set-tiers\`, then \`apply-tier-changes\`${allowDowngrades ? ' --downgrades=true' : ''}).`);
  md.push('');
  md.push(allowDowngrades
    ? 'Downgrades are **on**: entries are lowered to the market tier but never below their `floor` in `builderfilter/data/unique-set-tiers.json`; `locked` entries are never changed.'
    : `Downgrades are **off** (${ignoredDowngrades} suggested downgrade(s) not applied). Set the repo variable \`TIER_AUTO_DOWNGRADES\` to \`true\` to apply them (floors still hold).`);
  const table = (rows) => {
    md.push('| Type | Base | Top item | Variant | Base tier | Est. value | Qualifying listings | JSON change |');
    md.push('|---|---|---|---|---|---|---|---|');
    for (const a of rows) {
      md.push(`| ${a.kind === 'unique' ? 'Unique' : 'Set'} | \`${a.m.base}\` | ${a.m.topName ?? ''} | ${a.m.variant ?? 'both'} | ${fmtTiers(a.before)} → ${fmtTiers(a.after)} | ${fmtHR(a.m.maxMedianHR)} | ${a.m.cutoffCount ?? '?'} | ${a.changed.join('; ')} |`);
    }
  };
  md.push('', `### Upgrades (${ups.length})`);
  if (ups.length) table(ups);
  if (allowDowngrades) {
    md.push('', `### Downgrades (${downs.length})`);
    if (downs.length) table(downs);
  }
  if (skipped.length) {
    md.push('', `### Skipped (${skipped.length})`);
    for (const x of skipped) md.push(`- ${x.kind === 'unique' ? 'Unique' : 'Set'} \`${x.m.base}\` ${x.m.topName ?? ''} (${x.m.variant ?? 'both'}) → ${stars(x.m.suggestedTier)}: ${x.reason}`);
  }
  const params = uniqueDiff?.params ?? setDiff?.params;
  if (params) {
    md.push('', `<sub>Window ${params.windowHours}h, min ${params.minSamples} samples, ladder=${params.isLadder}, hardcore=${params.isHardcore}, change-multiplier=${params.changeMultiplier}</sub>`);
  }
  await mkdir('temp', { recursive: true });
  await writeFile(SUMMARY_FILE, md.join('\n') + '\n', 'utf8');

  for (const a of applied) console.error(`  applied  ${a.kind.padEnd(6)} ${a.m.base.padEnd(5)} ${(a.m.variant ?? 'both').padEnd(6)} ${fmtTiers(a.before)} -> ${fmtTiers(a.after)}  ${a.changed.join('; ')}`);
  for (const x of skipped) console.error(`  skipped  ${x.kind.padEnd(6)} ${x.m.base.padEnd(5)} ${x.reason}`);
  console.error(`${ups.length} upgrade(s), ${downs.length} downgrade(s) applied, ${skipped.length} skipped, ${ignoredDowngrades} downgrade(s) not applied (disabled)`);

  if (!applied.length || dryRun) return;
  await saveTiers(data);
  console.error('wrote builderfilter/data/unique-set-tiers.json');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
