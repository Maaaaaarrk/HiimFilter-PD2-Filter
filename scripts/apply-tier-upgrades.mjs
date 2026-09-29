// Applies the UPGRADE moves suggested by suggest-unique-tiers.mjs and
// suggest-set-tiers.mjs to builderfilter/02-alias/05-unid-unique-set-stars[ALL].filter.
//
// Upgrade-only by design (used by the scheduled pipeline): downgrades are never
// applied, and every edit is re-evaluated with the filter's real rule order
// (scripts/lib/tier-model.mjs). A move is applied only if its target variant
// reaches the suggested tier and neither the ETH nor the non-ETH copy of any base
// ends up lower than before. A final whole-file check aborts without writing if
// anything would drop. Downgrades stay a manual, local decision.
//
// Input:  temp/unique-tier-diff.json, temp/set-tier-diff.json (either may be missing)
// Output: the alias file (only if something was applied)
//         temp/tier-upgrades-applied.md — summary used as the bot PR body
//
// Usage:
//   node scripts/suggest-unique-tiers.mjs && node scripts/suggest-set-tiers.mjs
//   node scripts/apply-tier-upgrades.mjs [--dry-run=true]

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import {
  ALIAS_FILE, UNIQUE_TIERS, UNIQUE_VALUE_TIERS, SET_TIERS,
  uniqueTier, setTier, parseTierAliases, rank, stars,
} from './lib/tier-model.mjs';

const UNIQUE_DIFF = 'temp/unique-tier-diff.json';
const SET_DIFF = 'temp/set-tier-diff.json';
const SUMMARY_FILE = 'temp/tier-upgrades-applied.md';

const dryRun = process.argv.includes('--dry-run=true');

async function readDiff(path) {
  try {
    return JSON.parse(await readFile(path, 'utf8'));
  } catch (err) {
    if (err.code === 'ENOENT') return null;
    throw err;
  }
}

// ---- alias state -----------------------------------------------------------------

function makeState(lists) {
  const state = new Map([...lists].map(([k, v]) => [k, [...v]]));
  return {
    lists: state,
    has: (code) => (tier) => state.get(tier)?.includes(code) ?? false,
    add(code, tier) { if (!state.get(tier).includes(code)) state.get(tier).push(code); },
    remove(code, tier) { state.set(tier, state.get(tier).filter((c) => c !== code)); },
    clone() { return makeState(state); },
  };
}

const uniqueEval = (st, code) => ({
  eth: uniqueTier(st.has(code), true),
  noneth: uniqueTier(st.has(code), false),
});
const setEval = (st, code) => ({ both: setTier(st.has(code)) });

// Every variant is at least as good as before.
const noDrop = (before, after) => Object.keys(before).every((k) => rank(after[k]) >= rank(before[k]));

// ---- candidate edits per move ---------------------------------------------------

// Each candidate is { desc, edit(state) }. They are tried in order; the first one
// that reaches the target without lowering anything wins.
function uniqueCandidates(code, variant, target, st) {
  const plain = { desc: `add to ${target}`, edit: (s) => s.add(code, target) };
  if (variant === 'both') return [plain];
  if (variant === 'noneth') {
    const cond = target === '4_STAR_UNIQUE' ? '4_STAR_NO_ETH_UNIQUE'
      : target === '3_STAR_UNIQUE' ? '3_STAR_NO_ETH_UNIQUE' : null;
    return [...(cond ? [{ desc: `add to ${cond}`, edit: (s) => s.add(code, cond) }] : []), plain];
  }
  // eth
  const out = [];
  if (target === '4_STAR_UNIQUE') {
    out.push({ desc: 'add to 4_STAR_ETH_UNIQUE', edit: (s) => s.add(code, '4_STAR_ETH_UNIQUE') });
    // 4_STAR_NO_ETH_UNIQUE pins ETH copies to 3★ before the ETH rule is reached;
    // if non-ETH is already 4★ the base can simply become a plain 4★.
    if (st.has(code)('4_STAR_NO_ETH_UNIQUE')) {
      out.push({
        desc: 'move 4_STAR_NO_ETH_UNIQUE -> 4_STAR_UNIQUE',
        edit: (s) => { s.remove(code, '4_STAR_NO_ETH_UNIQUE'); s.add(code, '4_STAR_UNIQUE'); },
      });
    }
  }
  out.push(plain);
  return out;
}

// Drop memberships in lower plain value tiers that no longer affect any variant.
function tidy(st, code, plainTiers, evalFn) {
  const want = evalFn(st, code);
  const dropped = [];
  for (const t of plainTiers) {
    if (!st.has(code)(t)) continue;
    const trial = st.clone();
    trial.remove(code, t);
    const got = evalFn(trial, code);
    if (Object.keys(want).every((k) => got[k] === want[k])) {
      st.remove(code, t);
      dropped.push(t);
    }
  }
  return dropped;
}

function applyMoves(moves, initial, kind) {
  let st = initial;
  const applied = [];
  const skipped = [];
  const evalFn = kind === 'unique' ? uniqueEval : setEval;
  const plainTiers = kind === 'unique' ? UNIQUE_VALUE_TIERS : SET_TIERS;

  for (const m of moves) {
    const variant = kind === 'unique' ? m.variant : 'both';
    const target = m.suggestedTier;
    if (!(m.delta > 0)) continue; // never downgrade (callers pre-filter too)
    const before = evalFn(st, m.base);
    const targetKeys = kind === 'set' ? ['both'] : variant === 'both' ? ['eth', 'noneth'] : [variant];
    if (targetKeys.every((k) => rank(before[k]) >= rank(target))) {
      skipped.push({ m, reason: `already ${stars(target)} or better` });
      continue;
    }
    const candidates = kind === 'unique'
      ? uniqueCandidates(m.base, variant, target, st)
      : [{ desc: `add to ${target}`, edit: (s) => s.add(m.base, target) }];

    let done = null;
    for (const c of candidates) {
      const trial = st.clone();
      c.edit(trial);
      const after = evalFn(trial, m.base);
      const reached = targetKeys.every((k) => rank(after[k]) >= rank(target));
      if (reached && noDrop(before, after)) { done = { c, trial }; break; }
    }
    if (!done) {
      skipped.push({ m, reason: 'no alias edit reaches the target without lowering the other variant' });
      continue;
    }
    st = done.trial;
    const dropped = tidy(st, m.base, plainTiers, evalFn);
    applied.push({ m, variant, before, after: evalFn(st, m.base), edit: done.c.desc, dropped });
  }
  return { applied, skipped, state: st };
}

// ---- rewriting the alias file ---------------------------------------------------

const norm = (s) => s.toLowerCase().replace(/\([^)]*\)/g, '').replace(/[^a-z0-9]/g, '');

// Comment lines between the previous Alias[...] line and Alias[tier].
function blockRange(lines, tier) {
  const aliasIdx = lines.findIndex((l) => l.startsWith(`Alias[${tier}]:`));
  let start = aliasIdx - 1;
  while (start >= 0 && !lines[start].startsWith('Alias[')) start--;
  return { start: start + 1, aliasIdx };
}

function findItemComment(lines, tier, name) {
  const { start, aliasIdx } = blockRange(lines, tier);
  const want = norm(name);
  for (let i = start; i < aliasIdx; i++) {
    const l = lines[i];
    if (!l.startsWith('// ') || l.startsWith('//--')) continue;
    // "Unique - Base"; the market's top name can be either side (e.g. "Harlequin Crest")
    const names = l.slice(3).split(' - ').flatMap((p) => p.split(/\s+or\s+/i)).map(norm);
    if (names.includes(want)) return i;
  }
  return -1;
}

function insertComment(lines, tier, text) {
  const { start, aliasIdx } = blockRange(lines, tier);
  let at = aliasIdx;
  for (let i = aliasIdx - 1; i >= start; i--) {
    if (lines[i].startsWith('// ')) { at = i + 1; break; }
    if (lines[i].trim() !== '') break;
  }
  lines.splice(at, 0, text);
}

function rewrite(text, before, after, applied) {
  const eol = text.includes('\r\n') ? '\r\n' : '\n';
  const lines = text.split(/\r?\n/);
  // 1. alias code lists
  for (const [tier, codes] of after) {
    if (codes.join(' ') === before.get(tier).join(' ')) continue;
    const i = lines.findIndex((l) => l.startsWith(`Alias[${tier}]:`));
    lines[i] = lines[i].replace(/\(([^)]*)\)/, `(${codes.join(' OR ')})`);
  }
  // 2. comment blocks: move the item's line (or add one) under its new tier
  for (const a of applied) {
    const name = a.m.topName || a.m.base;
    const addedTo = a.edit.match(/(\w+_(?:UNIQUE|SET))$/)?.[1];
    const fromTier = a.m.currentEffectiveTier;
    const note = a.variant === 'eth' ? 'ETH; ' : a.variant === 'noneth' ? 'non-ETH; ' : '';
    let label = `${name}`;
    for (const t of a.dropped) {
      const idx = findItemComment(lines, t, name);
      if (idx >= 0) { label = lines[idx].slice(3).replace(/\s*\((?:promoted|demoted)[^)]*\)\s*$/, ''); lines.splice(idx, 1); break; }
    }
    if (addedTo && findItemComment(lines, addedTo, name) < 0) {
      insertComment(lines, addedTo, `// ${label} (${note}promoted from ${stars(fromTier)}, auto)`);
    }
  }
  return lines.join(eol);
}

// ---- main ------------------------------------------------------------------------

function fmtHR(v) {
  if (!Number.isFinite(v)) return '?';
  return v >= 1 ? `${v.toFixed(2)} HR` : `${(v * 100).toFixed(1)} WSS`;
}

async function main() {
  const text = await readFile(ALIAS_FILE, 'utf8');
  const uniqueDiff = await readDiff(UNIQUE_DIFF);
  const setDiff = await readDiff(SET_DIFF);
  if (!uniqueDiff && !setDiff) throw new Error(`neither ${UNIQUE_DIFF} nor ${SET_DIFF} exists — run the suggest scripts first`);

  const upOnly = (d) => (d?.moves ?? []).filter((m) => m.delta > 0);
  const ignoredDowngrades = (uniqueDiff?.moves ?? []).length + (setDiff?.moves ?? []).length
    - upOnly(uniqueDiff).length - upOnly(setDiff).length;

  const uBefore = parseTierAliases(text, UNIQUE_TIERS);
  const sBefore = parseTierAliases(text, SET_TIERS);
  const u = applyMoves(upOnly(uniqueDiff), makeState(uBefore), 'unique');
  const s = applyMoves(upOnly(setDiff), makeState(sBefore), 'set');
  const uState = u.state;
  const sState = s.state;

  // Hard guarantee: nothing anywhere in the file got worse.
  const drops = [];
  const uCodes = new Set([...uBefore.values()].flat());
  const uB = makeState(uBefore);
  for (const c of uCodes) {
    const b = uniqueEval(uB, c), a = uniqueEval(uState, c);
    if (!noDrop(b, a)) drops.push(`unique ${c}: ${JSON.stringify(b)} -> ${JSON.stringify(a)}`);
  }
  const sB = makeState(sBefore);
  for (const c of new Set([...sBefore.values()].flat())) {
    const b = setEval(sB, c), a = setEval(sState, c);
    if (!noDrop(b, a)) drops.push(`set ${c}: ${b.both} -> ${a.both}`);
  }
  if (drops.length) {
    console.error('ABORT: an edit would lower a tier — nothing written:\n  ' + drops.join('\n  '));
    process.exit(1);
  }

  const applied = [...u.applied.map((a) => ({ ...a, kind: 'Unique' })), ...s.applied.map((a) => ({ ...a, kind: 'Set' }))];
  const skipped = [...u.skipped.map((x) => ({ ...x, kind: 'Unique' })), ...s.skipped.map((x) => ({ ...x, kind: 'Set' }))];

  // Summary (PR body)
  const tierOf = (a) => (a.variant === 'eth' ? a.after.eth : a.variant === 'noneth' ? a.after.noneth : (a.after.both ?? a.after.noneth));
  const md = [];
  md.push(`Automated **upgrade-only** star-tier update from the PD2 market (\`suggest-unique-tiers\` + \`suggest-set-tiers\`, then \`apply-tier-upgrades\`).`);
  md.push('');
  md.push(`Downgrades are never applied by this pipeline (${ignoredDowngrades} suggested downgrade(s) ignored — run the suggest scripts locally to review them).`);
  md.push('');
  md.push(`### Applied (${applied.length})`);
  if (applied.length) {
    md.push('| Type | Base | Item | Variant | Move | Est. value | Qualifying listings | Alias edit |');
    md.push('|---|---|---|---|---|---|---|---|');
    for (const a of applied) {
      md.push(`| ${a.kind} | \`${a.m.base}\` | ${a.m.topName ?? ''} | ${a.variant} | ${stars(a.m.currentEffectiveTier)} → ${stars(tierOf(a))} | ${fmtHR(a.m.maxMedianHR)} | ${a.m.cutoffCount ?? '?'} | ${a.edit}${a.dropped.length ? `, removed from ${a.dropped.join(', ')}` : ''} |`);
    }
  }
  if (skipped.length) {
    md.push('');
    md.push(`### Skipped upgrades (${skipped.length})`);
    for (const x of skipped) md.push(`- ${x.kind} \`${x.m.base}\` ${x.m.topName ?? ''} (${x.m.variant ?? 'both'}) → ${stars(x.m.suggestedTier)}: ${x.reason}`);
  }
  const params = uniqueDiff?.params ?? setDiff?.params;
  if (params) {
    md.push('');
    md.push(`<sub>Window ${params.windowHours}h, min ${params.minSamples} samples, ladder=${params.isLadder}, hardcore=${params.isHardcore}, change-multiplier=${params.changeMultiplier}</sub>`);
  }
  await mkdir('temp', { recursive: true });
  await writeFile(SUMMARY_FILE, md.join('\n') + '\n', 'utf8');

  for (const a of applied) console.error(`  applied  ${a.kind.padEnd(6)} ${a.m.base.padEnd(5)} ${a.variant.padEnd(6)} ${stars(a.m.currentEffectiveTier)} -> ${stars(tierOf(a))}  ${a.m.topName ?? ''}  [${a.edit}]`);
  for (const x of skipped) console.error(`  skipped  ${x.kind.padEnd(6)} ${x.m.base.padEnd(5)} ${x.reason}`);
  console.error(`${applied.length} upgrade(s) applied, ${skipped.length} skipped, ${ignoredDowngrades} downgrade(s) ignored`);

  if (!applied.length || dryRun) return;
  const after = new Map([...uState.lists, ...sState.lists]);
  const before = new Map([...uBefore, ...sBefore]);
  await writeFile(ALIAS_FILE, rewrite(text, before, after, applied), 'utf8');
  console.error(`wrote ${ALIAS_FILE}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
