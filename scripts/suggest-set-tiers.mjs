// Suggests set-item tier reclassifications by pulling live listings from the
// Project Diablo 2 market API and comparing computed medians against our
// existing tier aliases in builderfilter/02-alias/05-unid-unique-set-stars[ALL].filter.
//
// Mirrors suggest-unique-tiers.mjs but for set items. Differences:
//   - item.quality.name = Set
//   - tiers: 4_STAR_SET .. 0_STAR_SET (no ETH-conditional variants)
//   - eth + non-eth listings are aggregated per base (no split rows)
//
// Output:
//   temp/set-tier-report.txt   — sorted human-readable report (every base)
//   temp/set-tier-diff.json    — machine-readable list of suggested moves
//   temp/set-tier-moves.txt    — moves-only text file, split upgrade/downgrade
//
// Usage:
//   node scripts/suggest-set-tiers.mjs
//   node scripts/suggest-set-tiers.mjs --window-hours=72 --min-samples=5
//   node scripts/suggest-set-tiers.mjs --change-multiplier=2

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';

const ALIAS_FILE = 'builderfilter/02-alias/05-unid-unique-set-stars[ALL].filter';
const REPORT_FILE = 'temp/set-tier-report.txt';
const DIFF_FILE = 'temp/set-tier-diff.json';
const MOVES_FILE = 'temp/set-tier-moves.txt';
const MARKET_URL = 'https://api.projectdiablo2.com/market/listing';

const VALUE_TIERS = [
  '4_STAR_SET',
  '3_STAR_SET',
  '2_STAR_SET',
  '1_STAR_SET',
  '0_STAR_SET',
];

const args = parseArgs(process.argv.slice(2));
const isLadder = args.ladder !== 'false';
const isHardcore = args.hardcore === 'true';
const minSamples = Number(args['min-samples']) || 5;
const windowHours = Number(args['window-hours']) || 168;
const throttleMs = Number(args['throttle-ms']) || 200;
// Manual tier cutoffs in HR (top-down, first match wins). Override via CLI:
//   --cutoff-4=2.0 --cutoff-3=1.0 --cutoff-2=0.5 --cutoff-1=0.25 --cutoff-0=0.10
const CUTOFFS_HR = [
  { tier: '4_STAR_SET', cutoffHR: Number(args['cutoff-4'] ?? 2.0) },
  { tier: '3_STAR_SET', cutoffHR: Number(args['cutoff-3'] ?? 1.0) },
  { tier: '2_STAR_SET', cutoffHR: Number(args['cutoff-2'] ?? 0.5) },
  { tier: '1_STAR_SET', cutoffHR: Number(args['cutoff-1'] ?? 0.25) },
  { tier: '0_STAR_SET', cutoffHR: Number(args['cutoff-0'] ?? 0.10) },
];
const topPercentile = Number(args['top-percentile']) || 0.25;
const excludeCorrupted = args['exclude-corrupted'] === 'true';
// changeMultiplier: hysteresis. A tier change (upgrade or downgrade) is only
// suggested if the data clears the cutoff by this multiplier — i.e. promotions
// must hit M × cutoff(new tier), and demotions must fail to clear cutoff(current) / M.
// Default 1.0 = no hysteresis. Pass --change-multiplier=2 to require 2x clearance.
const changeMultiplier = Number(args['change-multiplier']) || 1.0;
const pageSize = 200;
const maxPagesPerBase = 5;
const maxConcurrent = 4;

function parseArgs(argv) {
  const out = {};
  for (const arg of argv) {
    const m = arg.match(/^--([^=]+)=(.*)$/);
    if (m) out[m[1]] = m[2];
  }
  return out;
}

function parseAliases(text) {
  const tiersByBase = new Map();
  for (const tier of VALUE_TIERS) {
    const re = new RegExp(`^Alias\\[${tier}\\]:\\s*\\(([^)]+)\\)`, 'm');
    const m = text.match(re);
    if (!m) {
      console.warn(`alias ${tier} not found in source file`);
      continue;
    }
    const codes = m[1]
      .split(/\s+OR\s+/i)
      .map((s) => s.trim())
      .filter((s) => s && /^[a-z0-9]+$/i.test(s));
    for (const code of codes) {
      if (!tiersByBase.has(code)) tiersByBase.set(code, new Set());
      tiersByBase.get(code).add(tier);
    }
  }
  return tiersByBase;
}

function effectiveTier(tiers) {
  // First-match-wins, top-down (mirrors 06-unidfiltering/20-Unid_UniquesSet_Tiers).
  for (const t of VALUE_TIERS) if (tiers.has(t)) return t;
  return null;
}

async function fetchListingsForBase(baseCode) {
  const updatedAfter = new Date(Date.now() - windowHours * 3600 * 1000).toISOString();
  const all = [];
  for (let page = 0; page < maxPagesPerBase; page++) {
    const baseParams = {
      type: 'item',
      $limit: String(pageSize),
      $skip: String(page * pageSize),
      accepted_offer_id: 'null',
      'updated_at[$gte]': updatedAfter,
      is_hardcore: String(isHardcore),
      is_ladder: String(isLadder),
      'item.base_code': baseCode,
      'item.quality.name': 'Set',
    };
    if (excludeCorrupted) baseParams['item.corrupted'] = 'false';
    const params = new URLSearchParams(baseParams);
    const res = await fetch(`${MARKET_URL}?${params}`);
    if (!res.ok) throw new Error(`market API ${res.status} for ${baseCode}`);
    const payload = await res.json();
    const rows = Array.isArray(payload?.data) ? payload.data : [];
    all.push(...rows);
    if (rows.length < pageSize) break;
    await sleep(throttleMs);
  }
  return all;
}

function priceToHR(listing) {
  const hr = listing?.hr_price;
  if (Number.isFinite(hr) && hr > 0) return hr;
  const parsed = parsePriceString(listing?.price);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : undefined;
}

function parsePriceString(s) {
  if (typeof s !== 'string') return undefined;
  const lower = s.trim().toLowerCase();
  const wss = lower.match(/^(\d+(?:\.\d+)?)\s*wss/);
  if (wss) return Number(wss[1]) * 0.01;
  const hr = lower.match(/^(\d+(?:\.\d+)?)\s*hr/);
  if (hr) return Number(hr[1]);
  const num = lower.match(/^(\d+(?:\.\d+)?)/);
  if (num) return Number(num[1]);
  return undefined;
}

function aggregateListings(listings) {
  const byName = new Map();
  for (const l of listings) {
    const name = l?.item?.name;
    const hr = priceToHR(l);
    if (!name || !Number.isFinite(hr)) continue;
    if (!byName.has(name)) byName.set(name, []);
    byName.get(name).push(hr);
  }
  const medians = [];
  for (const [name, prices] of byName) {
    if (prices.length < minSamples) continue;
    const sortedDesc = [...prices].sort((a, b) => b - a);
    const topCount = Math.max(minSamples, Math.ceil(sortedDesc.length * topPercentile));
    const top = sortedDesc.slice(0, topCount);
    const sortedAsc = [...top].sort((a, b) => a - b);
    const median = sortedAsc[Math.floor(sortedAsc.length / 2)];
    medians.push({ name, median, count: prices.length, topCount, sortedDesc });
  }
  medians.sort((a, b) => b.median - a.median);
  const top = medians[0];
  return {
    medians,
    maxMedian: top?.median,
    maxName: top?.name,
    maxNameTopCount: top?.topCount,
    maxNameCount: top?.count,
    maxNamePrices: top?.sortedDesc,
    totalListings: listings.length,
    distinctNames: byName.size,
  };
}

function countAtOrAbove(sortedDescPrices, threshold) {
  if (!Array.isArray(sortedDescPrices) || !Number.isFinite(threshold)) return 0;
  let n = 0;
  for (const p of sortedDescPrices) {
    if (p >= threshold) n++;
    else break;
  }
  return n;
}

function avgAtOrAbove(sortedDescPrices, threshold) {
  if (!Array.isArray(sortedDescPrices) || !Number.isFinite(threshold)) return undefined;
  let sum = 0;
  let n = 0;
  for (const p of sortedDescPrices) {
    if (p >= threshold) {
      sum += p;
      n++;
    } else break;
  }
  return n > 0 ? sum / n : undefined;
}

function avgOfTopN(sortedDescPrices, n) {
  if (!Array.isArray(sortedDescPrices) || sortedDescPrices.length === 0) return undefined;
  const k = Math.min(n, sortedDescPrices.length);
  let sum = 0;
  for (let i = 0; i < k; i++) sum += sortedDescPrices[i];
  return sum / k;
}

function relevantCutoffForMove(currentTier, suggestedTier) {
  const curIdx = VALUE_TIERS.indexOf(currentTier);
  const sugIdx = VALUE_TIERS.indexOf(suggestedTier);
  if (curIdx < 0 || sugIdx < 0) return null;
  if (sugIdx < curIdx) {
    return CUTOFFS_HR.find((c) => c.tier === suggestedTier) ?? null;
  }
  const aboveTier = VALUE_TIERS[sugIdx - 1];
  return CUTOFFS_HR.find((c) => c.tier === aboveTier) ?? null;
}

function percentile(values, p) {
  const filtered = values.filter((v) => Number.isFinite(v));
  if (filtered.length === 0) return undefined;
  const sorted = [...filtered].sort((a, b) => a - b);
  const idx = Math.min(sorted.length - 1, Math.floor(sorted.length * p));
  return sorted[idx];
}

function tierStatsFromRows(itemRows) {
  const pricesByTier = new Map();
  for (const tier of VALUE_TIERS) pricesByTier.set(tier, []);
  for (const row of itemRows) {
    if (!row.currentTier || !Number.isFinite(row.maxMedian)) continue;
    if (!pricesByTier.has(row.currentTier)) continue;
    pricesByTier.get(row.currentTier).push(row.maxMedian);
  }
  const tierStats = new Map();
  for (const [tier, prices] of pricesByTier) {
    tierStats.set(tier, {
      count: prices.length,
      p10: percentile(prices, 0.1),
      p50: percentile(prices, 0.5),
      p90: percentile(prices, 0.9),
    });
  }
  return tierStats;
}

const MIN_LISTINGS_FOR_TIER = 5;
function suggestTierFromPrices(sortedDescPrices) {
  if (!Array.isArray(sortedDescPrices) || sortedDescPrices.length === 0) return null;
  for (const c of CUTOFFS_HR) {
    if (countAtOrAbove(sortedDescPrices, c.cutoffHR) >= MIN_LISTINGS_FOR_TIER) return c.tier;
  }
  return null;
}

function tierIdx(tier) {
  const i = VALUE_TIERS.indexOf(tier);
  return i < 0 ? VALUE_TIERS.length : i;
}

function moveClearsMultiplier(sortedDescPrices, currentTier, suggestedTier, multiplier) {
  if (!(multiplier > 1)) return true;
  const curIdx = tierIdx(currentTier);
  const sugIdx = tierIdx(suggestedTier);
  if (sugIdx < curIdx) {
    const c = CUTOFFS_HR.find((x) => x.tier === suggestedTier);
    if (!c) return true;
    return countAtOrAbove(sortedDescPrices, c.cutoffHR * multiplier) >= MIN_LISTINGS_FOR_TIER;
  }
  if (sugIdx > curIdx) {
    const c = CUTOFFS_HR.find((x) => x.tier === currentTier);
    if (!c) return true;
    return countAtOrAbove(sortedDescPrices, c.cutoffHR / multiplier) < MIN_LISTINGS_FOR_TIER;
  }
  return true;
}

async function fetchAllConcurrent(jobs, concurrency, onProgress) {
  const results = new Array(jobs.length);
  let nextIndex = 0;
  let completed = 0;
  const workers = Array.from({ length: concurrency }, async () => {
    while (true) {
      const i = nextIndex++;
      if (i >= jobs.length) return;
      try {
        results[i] = await jobs[i]();
      } catch (err) {
        results[i] = { error: err.message };
      }
      completed++;
      if (onProgress) onProgress(completed, jobs.length);
    }
  });
  await Promise.all(workers);
  return results;
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function fmtHR(v) {
  if (!Number.isFinite(v)) return '       ?';
  if (v >= 100) return `${v.toFixed(0).padStart(5)} HR`;
  if (v >= 10) return `${v.toFixed(1).padStart(5)} HR`;
  if (v >= 1) return `${v.toFixed(2).padStart(5)} HR`;
  return `${(v * 100).toFixed(1).padStart(5)} WS`;
}

const tierShort = {
  '4_STAR_SET': '4*',
  '3_STAR_SET': '3*',
  '2_STAR_SET': '2*',
  '1_STAR_SET': '1*',
  '0_STAR_SET': '0*',
};

async function main() {
  console.error(`fetching sets from PD2 market API`);
  console.error(
    `  window: ${windowHours}h, min-samples: ${minSamples}, top-pct: ${topPercentile}, ladder=${isLadder} hardcore=${isHardcore}, corrupted=${excludeCorrupted ? 'excluded' : 'included'}, change-multiplier=${changeMultiplier}`,
  );

  const aliasText = await readFile(ALIAS_FILE, 'utf8');
  const tiersByBase = parseAliases(aliasText);
  const baseCodes = [...tiersByBase.keys()].sort();
  console.error(`  ${baseCodes.length} set base codes across ${VALUE_TIERS.length} tiers`);

  const jobs = baseCodes.map((base) => async () => {
    const listings = await fetchListingsForBase(base);
    const agg = aggregateListings(listings);
    return { base, ...agg };
  });

  console.error(`  ${jobs.length} fetches at ${maxConcurrent} concurrent`);
  const fetchResults = await fetchAllConcurrent(jobs, maxConcurrent, (done, total) => {
    if (done % 20 === 0 || done === total) {
      process.stderr.write(`\r  progress: ${done}/${total}`);
    }
  });
  process.stderr.write('\n');

  const itemRows = [];
  for (const r of fetchResults) {
    if (!r || r.error) continue;
    const tiers = tiersByBase.get(r.base);
    if (!tiers) continue;
    const eff = effectiveTier(tiers);
    if (!eff) continue;
    itemRows.push({
      base: r.base,
      currentTier: eff,
      sourceTiers: [...tiers],
      maxMedian: r.maxMedian,
      maxName: r.maxName,
      maxNameTopCount: r.maxNameTopCount,
      maxNameCount: r.maxNameCount,
      maxNamePrices: r.maxNamePrices,
      medians: r.medians,
      totalListings: r.totalListings,
      distinctNames: r.distinctNames,
    });
  }

  const tierStats = tierStatsFromRows(itemRows);
  console.error(`tier price distribution (n / p10 / p50 / p90, HR) — diagnostic:`);
  for (const t of VALUE_TIERS) {
    const s = tierStats.get(t);
    if (!s) continue;
    console.error(
      `  ${t.padEnd(20)} n=${String(s.count).padStart(3)}  p10=${(s.p10 ?? 0).toFixed(3)}  p50=${(s.p50 ?? 0).toFixed(3)}  p90=${(s.p90 ?? 0).toFixed(3)}`,
    );
  }
  console.error(`manual cutoffs (≥ X HR → tier):`);
  for (const c of CUTOFFS_HR) {
    console.error(`  ≥ ${c.cutoffHR.toFixed(3)} HR → ${c.tier}`);
  }

  for (const row of itemRows) {
    const rawSug = suggestTierFromPrices(row.maxNamePrices);
    if (
      rawSug &&
      row.currentTier &&
      rawSug !== row.currentTier &&
      !moveClearsMultiplier(row.maxNamePrices, row.currentTier, rawSug, changeMultiplier)
    ) {
      row.suggestedTier = row.currentTier;
    } else {
      row.suggestedTier = rawSug;
    }
  }

  itemRows.sort((a, b) => (b.maxMedian ?? -1) - (a.maxMedian ?? -1));

  // Report
  const lines = [];
  lines.push(`Set tier suggestions — generated ${new Date().toISOString()}`);
  lines.push(`Window ${windowHours}h, min ${minSamples} samples, ladder=${isLadder} hardcore=${isHardcore}, change-multiplier=${changeMultiplier}`);
  lines.push('');
  lines.push('Tier price distribution (n / p10 / p50 / p90, HR) — diagnostic:');
  for (const t of VALUE_TIERS) {
    const s = tierStats.get(t);
    if (!s) continue;
    lines.push(
      `  ${t.padEnd(20)} n=${String(s.count).padStart(3)}  p10=${(s.p10 ?? 0).toFixed(3).padStart(7)}  p50=${(s.p50 ?? 0).toFixed(3).padStart(7)}  p90=${(s.p90 ?? 0).toFixed(3).padStart(7)}`,
    );
  }
  lines.push('');
  lines.push('Manual cutoffs (≥ X HR → tier):');
  for (const c of CUTOFFS_HR) {
    lines.push(`  ≥ ${c.cutoffHR.toFixed(3).padStart(8)} HR → ${c.tier}`);
  }
  lines.push('');
  lines.push('Item                                Cur   Median     Sug   Δ   Listings  Top name');
  lines.push('-'.repeat(110));
  for (const r of itemRows) {
    const cur = tierShort[r.currentTier] ?? r.currentTier ?? '-';
    const sug = tierShort[r.suggestedTier] ?? r.suggestedTier ?? '-';
    const delta = tierIdx(r.currentTier) - tierIdx(r.suggestedTier);
    const deltaStr = delta === 0 ? '  ' : delta > 0 ? `+${delta}` : `${delta}`;
    const med = fmtHR(r.maxMedian);
    const top = r.maxName ? `${r.maxName} (${r.medians[0]?.count ?? 0})` : '';
    lines.push(
      `${r.base.padEnd(8)} ${(r.sourceTiers.join(',') || '').padEnd(28)} ${cur.padEnd(3)} ${med}  ${sug.padEnd(3)} ${deltaStr.padStart(3)}  ${String(r.totalListings).padStart(5)}  ${top}`,
    );
  }

  await mkdir(dirname(REPORT_FILE), { recursive: true });
  await writeFile(REPORT_FILE, lines.join('\n') + '\n', 'utf8');
  console.error(`wrote ${REPORT_FILE} (${itemRows.length} rows)`);

  // Diff JSON
  const moves = itemRows
    .filter((r) => r.suggestedTier && r.currentTier && r.suggestedTier !== r.currentTier)
    .map((r) => {
      const cutoff = relevantCutoffForMove(r.currentTier, r.suggestedTier);
      const cutoffCount = cutoff ? countAtOrAbove(r.maxNamePrices, cutoff.cutoffHR) : 0;
      const delta = tierIdx(r.currentTier) - tierIdx(r.suggestedTier);
      const isUpgrade = delta > 0;
      const sugCutoffHR = CUTOFFS_HR.find((c) => c.tier === r.suggestedTier)?.cutoffHR;
      const estTopValHR = isUpgrade
        ? avgAtOrAbove(r.maxNamePrices, sugCutoffHR)
        : avgOfTopN(r.maxNamePrices, 5);
      return {
        base: r.base,
        sourceTiers: r.sourceTiers,
        currentEffectiveTier: r.currentTier,
        suggestedTier: r.suggestedTier,
        delta,
        maxMedianHR: r.maxMedian,
        estTopValHR,
        topName: r.maxName,
        topUsedForMedian: r.maxNameTopCount ?? 0,
        topNameTotal: r.maxNameCount ?? 0,
        totalListings: r.totalListings,
        cutoffTier: cutoff?.tier ?? null,
        cutoffHR: cutoff?.cutoffHR ?? null,
        cutoffCount,
      };
    });

  const diff = {
    generatedAt: new Date().toISOString(),
    params: { windowHours, minSamples, isLadder, isHardcore, topPercentile, excludeCorrupted, changeMultiplier },
    cutoffs: CUTOFFS_HR,
    tierStats: Object.fromEntries(tierStats),
    moves,
  };
  await writeFile(DIFF_FILE, JSON.stringify(diff, null, 2), 'utf8');
  console.error(`wrote ${DIFF_FILE} (${moves.length} suggested moves)`);

  // Moves-only text file split by direction
  const byTierThenValue = (a, b) =>
    tierIdx(a.suggestedTier) - tierIdx(b.suggestedTier) ||
    (b.maxMedianHR ?? 0) - (a.maxMedianHR ?? 0);
  const upgrades = moves.filter((m) => (m.delta ?? 0) > 0).sort(byTierThenValue);
  const downgrades = moves.filter((m) => (m.delta ?? 0) < 0).sort(byTierThenValue);

  const movesLines = [];
  movesLines.push(`Set tier suggested moves — ${diff.generatedAt}`);
  movesLines.push(
    `Window ${windowHours}h, min ${minSamples} samples, top-pct ${topPercentile}, ladder=${isLadder} hardcore=${isHardcore}, corrupted=${excludeCorrupted ? 'excluded' : 'included'}, change-multiplier=${changeMultiplier}`,
  );
  movesLines.push('');
  movesLines.push('est val   = median of the top X% (or top 5, whichever is more) of listings, per item-name.');
  movesLines.push('est top   = average price of selected high-end listings:');
  movesLines.push('  - upgrades:   average of listings that clear the suggested tier cutoff.');
  movesLines.push('  - downgrades: average of the top 5 listings (peak being demoted away from).');
  movesLines.push('qualify(n)= count of listings that clear the named tier:');
  movesLines.push('  - upgrades:   ≥(suggested tier) — validates the promotion (must be ≥5 for the move).');
  movesLines.push('  - downgrades: ≥(tier just above the demotion target).');
  movesLines.push('');
  movesLines.push(`Total: ${upgrades.length} upgrade(s), ${downgrades.length} downgrade(s)`);
  movesLines.push('');
  const header = `${'base'.padEnd(5)}     ${'move   '.padEnd(7)}   ${'est val '.padEnd(8)}   ${'est top '.padEnd(8)}   ${'qualify(n)'.padEnd(11)}  total  top name (top of total)`;
  const sep = '-'.repeat(125);

  movesLines.push(`UPGRADES (${upgrades.length}) — promote to a higher tier`);
  movesLines.push(sep);
  movesLines.push(header);
  movesLines.push(sep);
  for (const m of upgrades) movesLines.push(formatMoveLine(m));

  movesLines.push('');
  movesLines.push(`DOWNGRADES (${downgrades.length}) — demote to a lower tier`);
  movesLines.push(sep);
  movesLines.push(header);
  movesLines.push(sep);
  for (const m of downgrades) movesLines.push(formatMoveLine(m));

  await writeFile(MOVES_FILE, movesLines.join('\n') + '\n', 'utf8');
  console.error(
    `wrote ${MOVES_FILE} (${upgrades.length} upgrade(s), ${downgrades.length} downgrade(s))`,
  );
}

function formatMoveLine(m) {
  const base = m.base.padEnd(5);
  const cur = (tierShort[m.currentEffectiveTier] || '? ').padStart(2);
  const sug = (tierShort[m.suggestedTier] || '? ').padEnd(2);
  const move = `${cur} → ${sug}`;
  const med = fmtHR(m.maxMedianHR);
  const topVal = fmtHR(m.estTopValHR);
  const qualifyStr = m.cutoffTier ? `≥${tierShort[m.cutoffTier]} (${m.cutoffCount})` : '';
  const qualifyPadded = qualifyStr.padEnd(11);
  const total = String(m.totalListings).padStart(5);
  const topStr = `${m.topName || ''} (top ${m.topUsedForMedian} of ${m.topNameTotal})`;
  return `${base}    ${move}   ${med}   ${topVal}   ${qualifyPadded}  ${total}  ${topStr}`;
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
