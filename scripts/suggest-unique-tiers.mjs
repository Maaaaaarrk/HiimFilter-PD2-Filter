// Suggests unique-item tier reclassifications by pulling live listings from the
// Project Diablo 2 market API and comparing computed medians against our
// existing tier aliases in builderfilter/02-alias/05-unid-unique-set-stars[ALL].filter.
//
// Output:
//   temp/unique-tier-report.txt  — sorted human-readable report (every base, every variant)
//   temp/unique-tier-diff.json   — machine-readable list of suggested moves
//
// Usage:
//   node scripts/suggest-unique-tiers.mjs
//   node scripts/suggest-unique-tiers.mjs --window-hours=72 --min-samples=5
//   node scripts/suggest-unique-tiers.mjs --hardcore=true --ladder=false
//
// Threshold calibration: thresholds are derived at runtime from the median price
// of each tier's current members (geometric mean of adjacent tier medians).
// Acknowledged-circular: if a tier is currently misconfigured, its threshold
// will reflect that — but it surfaces the relative ordering, which is enough
// to spot outliers.

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';

const ALIAS_FILE = 'builderfilter/02-alias/05-unid-unique-set-stars[ALL].filter';
const REPORT_FILE = 'temp/unique-tier-report.txt';
const DIFF_FILE = 'temp/unique-tier-diff.json';
const MOVES_FILE = 'temp/unique-tier-moves.txt';
const MARKET_URL = 'https://api.projectdiablo2.com/market/listing';

// Tiers in *display priority* order: highest to lowest.
// We only calibrate against the simple value tiers (NO_STAR..4_STAR_UNIQUE).
// The eth-conditional tiers are evaluated separately for ETH/non-ETH variants.
const VALUE_TIERS = [
  '4_STAR_UNIQUE',
  '3_STAR_UNIQUE',
  '2_STAR_UNIQUE',
  '1_STAR_UNIQUE',
  '0_STAR_UNIQUE',
  'NO_STAR_UNIQUE',
];
const ETH_CONDITIONAL_TIERS = [
  '4_STAR_ETH_UNIQUE',     // +ETH copies → 4-star
  '4_STAR_NO_ETH_UNIQUE',  // non-ETH → 4-star, ETH → 3-star
  '3_STAR_NO_ETH_UNIQUE',  // non-ETH → 3-star, ETH → 2-star
];
const ALL_TIERS = [...VALUE_TIERS, ...ETH_CONDITIONAL_TIERS];

const args = parseArgs(process.argv.slice(2));
const isLadder = args.ladder !== 'false';
const isHardcore = args.hardcore === 'true';
const minSamples = Number(args['min-samples']) || 5;
const windowHours = Number(args['window-hours']) || 168;
const throttleMs = Number(args['throttle-ms']) || 200;
// Manual tier cutoffs in HR (top-down, first match wins). Override via CLI:
//   --cutoff-4=2.0 --cutoff-3=1.0 --cutoff-2=0.5 --cutoff-1=0.25 --cutoff-0=0.15 --cutoff-no=0.1
// Note: 100 WSS = 1 HR. Item-name medians are converted to HR before comparison.
const CUTOFFS_HR = [
  { tier: '4_STAR_UNIQUE',  cutoffHR: Number(args['cutoff-4']  ?? 2.0) },
  { tier: '3_STAR_UNIQUE',  cutoffHR: Number(args['cutoff-3']  ?? 1.0) },
  { tier: '2_STAR_UNIQUE',  cutoffHR: Number(args['cutoff-2']  ?? 0.5) },
  { tier: '1_STAR_UNIQUE',  cutoffHR: Number(args['cutoff-1']  ?? 0.25) },
  { tier: '0_STAR_UNIQUE',  cutoffHR: Number(args['cutoff-0']  ?? 0.15) },
  { tier: 'NO_STAR_UNIQUE', cutoffHR: Number(args['cutoff-no'] ?? 0.10) },
];
// top-percentile: per-name, only the top X% of listings by price contribute to the
// per-name median. Default 0.25 = "median of the top 25% priced listings". Captures
// the upside of finding a good (often corrupted) copy rather than the typical drop.
const topPercentile = Number(args['top-percentile']) || 0.25;
// excludeCorrupted: by default we include corrupted listings (top-priced copies are
// typically corrupted, and the filter highlights upside potential). Pass
// --exclude-corrupted=true to revert to clean-only listings.
const excludeCorrupted = args['exclude-corrupted'] === 'true';
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
  for (const tier of ALL_TIERS) {
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

function effectiveTier(tiers, isEth) {
  // Map a base's tier-set + eth flag into a single effective value tier.
  // Mirrors the rule precedence in 06-unidfiltering/20-Unid_UniquesSet_Tiers[ALL].filter
  // (first matching ItemDisplay rule wins, top-down).
  if (isEth && tiers.has('4_STAR_ETH_UNIQUE')) return '4_STAR_UNIQUE';
  if (!isEth && tiers.has('4_STAR_NO_ETH_UNIQUE')) return '4_STAR_UNIQUE';
  if (isEth && tiers.has('4_STAR_NO_ETH_UNIQUE')) return '3_STAR_UNIQUE';
  if (tiers.has('4_STAR_UNIQUE')) return '4_STAR_UNIQUE';
  if (!isEth && tiers.has('3_STAR_NO_ETH_UNIQUE')) return '3_STAR_UNIQUE';
  if (isEth && tiers.has('3_STAR_NO_ETH_UNIQUE')) return '2_STAR_UNIQUE';
  if (tiers.has('3_STAR_UNIQUE')) return '3_STAR_UNIQUE';
  if (tiers.has('2_STAR_UNIQUE')) return '2_STAR_UNIQUE';
  if (tiers.has('1_STAR_UNIQUE')) return '1_STAR_UNIQUE';
  if (tiers.has('0_STAR_UNIQUE')) return '0_STAR_UNIQUE';
  if (tiers.has('NO_STAR_UNIQUE')) return 'NO_STAR_UNIQUE';
  return null;
}

async function fetchListingsForBase(baseCode, isEth) {
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
      'item.quality.name': 'Unique',
      'item.is_ethereal': String(isEth),
    };
    if (excludeCorrupted) baseParams['item.corrupted'] = 'false';
    const params = new URLSearchParams(baseParams);
    const res = await fetch(`${MARKET_URL}?${params}`);
    if (!res.ok) {
      throw new Error(`market API ${res.status} for ${baseCode} eth=${isEth}`);
    }
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
    // Top X% of listings by price (descending), floored at minSamples so we never
    // collapse to a single outlier when a name has few listings.
    const sortedDesc = [...prices].sort((a, b) => b - a);
    const topCount = Math.max(minSamples, Math.ceil(sortedDesc.length * topPercentile));
    const top = sortedDesc.slice(0, topCount);
    const sortedAsc = [...top].sort((a, b) => a - b);
    const median = sortedAsc[Math.floor(sortedAsc.length / 2)];
    medians.push({ name, median, count: prices.length, topCount });
  }
  medians.sort((a, b) => b.median - a.median);
  return {
    medians,
    maxMedian: medians[0]?.median,
    maxName: medians[0]?.name,
    totalListings: listings.length,
    distinctNames: byName.size,
  };
}

function median(values) {
  return percentile(values, 0.5);
}

function percentile(values, p) {
  const filtered = values.filter((v) => Number.isFinite(v));
  if (filtered.length === 0) return undefined;
  const sorted = [...filtered].sort((a, b) => a - b);
  const idx = Math.min(sorted.length - 1, Math.floor(sorted.length * p));
  return sorted[idx];
}

function tierStatsFromRows(itemRows) {
  // Diagnostic-only: per-tier price distribution from current memberships.
  // Cutoffs themselves are manual (CUTOFFS_HR), independent of these stats.
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

function suggestTier(maxMedianHR) {
  if (!Number.isFinite(maxMedianHR)) return null;
  for (const c of CUTOFFS_HR) {
    if (maxMedianHR >= c.cutoffHR) return c.tier;
  }
  return null; // below the lowest cutoff — too cheap to even register
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
  if (!Number.isFinite(v)) return '   ?  ';
  if (v >= 100) return v.toFixed(0).padStart(4) + ' HR';
  if (v >= 10) return v.toFixed(1).padStart(4) + ' HR';
  if (v >= 1) return v.toFixed(2).padStart(4) + ' HR';
  return (v * 100).toFixed(1).padStart(4) + ' WS';
}

const tierShort = {
  '4_STAR_UNIQUE': '4*',
  '3_STAR_UNIQUE': '3*',
  '2_STAR_UNIQUE': '2*',
  '1_STAR_UNIQUE': '1*',
  '0_STAR_UNIQUE': '0*',
  NO_STAR_UNIQUE: '--',
};

async function main() {
  console.error(`fetching uniques from PD2 market API`);
  console.error(
    `  window: ${windowHours}h, min-samples: ${minSamples}, top-pct: ${topPercentile}, ladder=${isLadder} hardcore=${isHardcore}, corrupted=${excludeCorrupted ? 'excluded' : 'included'}`,
  );

  const aliasText = await readFile(ALIAS_FILE, 'utf8');
  const tiersByBase = parseAliases(aliasText);
  const baseCodes = [...tiersByBase.keys()].sort();
  console.error(`  ${baseCodes.length} unique base codes across ${ALL_TIERS.length} tiers`);

  const jobs = [];
  for (const base of baseCodes) {
    for (const isEth of [false, true]) {
      jobs.push(async () => {
        const listings = await fetchListingsForBase(base, isEth);
        const agg = aggregateListings(listings);
        return { base, isEth, ...agg };
      });
    }
  }

  console.error(`  ${jobs.length} fetches (eth + non-eth per base) at ${maxConcurrent} concurrent`);
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
    const eff = effectiveTier(tiers, r.isEth);
    if (!eff) continue;
    itemRows.push({
      base: r.base,
      isEth: r.isEth,
      currentTier: eff,
      sourceTiers: [...tiers],
      maxMedian: r.maxMedian,
      maxName: r.maxName,
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
    row.suggestedTier = suggestTier(row.maxMedian);
    row.delta =
      row.suggestedTier && row.currentTier
        ? VALUE_TIERS.indexOf(row.currentTier) - VALUE_TIERS.indexOf(row.suggestedTier)
        : null;
  }

  itemRows.sort((a, b) => (b.maxMedian ?? -1) - (a.maxMedian ?? -1));

  // Report
  const lines = [];
  lines.push(`Unique tier suggestions — generated ${new Date().toISOString()}`);
  lines.push(`Window ${windowHours}h, min ${minSamples} samples, ladder=${isLadder} hardcore=${isHardcore}`);
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
  lines.push('Item                                Var    Cur   Median     Sug   Δ   Listings  Top name');
  lines.push('-'.repeat(110));
  for (const r of itemRows) {
    const cur = tierShort[r.currentTier] ?? r.currentTier ?? '-';
    const sug = tierShort[r.suggestedTier] ?? r.suggestedTier ?? '-';
    const delta = r.delta ?? 0;
    const deltaStr = delta === 0 ? '  ' : delta > 0 ? `+${delta}` : `${delta}`;
    const variant = r.isEth ? 'ETH ' : 'norm';
    const med = fmtHR(r.maxMedian);
    const top = r.maxName ? `${r.maxName} (${r.medians[0]?.count ?? 0})` : '';
    lines.push(
      `${r.base.padEnd(8)} ${(r.sourceTiers.join(',') || '').padEnd(28)} ${variant}  ${cur.padEnd(3)} ${med}  ${sug.padEnd(3)} ${deltaStr.padStart(3)}  ${String(r.totalListings).padStart(5)}  ${top}`,
    );
  }

  await mkdir(dirname(REPORT_FILE), { recursive: true });
  await writeFile(REPORT_FILE, lines.join('\n') + '\n', 'utf8');
  console.error(`wrote ${REPORT_FILE} (${itemRows.length} rows)`);

  // Diff JSON: only items where suggested differs from current
  const moves = itemRows
    .filter((r) => r.suggestedTier && r.currentTier && r.suggestedTier !== r.currentTier)
    .map((r) => ({
      base: r.base,
      variant: r.isEth ? 'eth' : 'noneth',
      sourceTiers: r.sourceTiers,
      currentEffectiveTier: r.currentTier,
      suggestedTier: r.suggestedTier,
      delta: r.delta,
      maxMedianHR: r.maxMedian,
      topName: r.maxName,
      sampleCount: r.medians[0]?.count ?? 0,
      totalListings: r.totalListings,
    }));

  const diff = {
    generatedAt: new Date().toISOString(),
    params: { windowHours, minSamples, isLadder, isHardcore, topPercentile, excludeCorrupted },
    cutoffs: CUTOFFS_HR,
    tierStats: Object.fromEntries(tierStats),
    moves,
  };
  await writeFile(DIFF_FILE, JSON.stringify(diff, null, 2), 'utf8');
  console.error(`wrote ${DIFF_FILE} (${moves.length} suggested moves)`);

  // Moves-only text file split by direction (upgrades vs downgrades)
  const upgrades = moves
    .filter((m) => (m.delta ?? 0) > 0)
    .sort((a, b) => (b.delta ?? 0) - (a.delta ?? 0) || (b.maxMedianHR ?? 0) - (a.maxMedianHR ?? 0));
  const downgrades = moves
    .filter((m) => (m.delta ?? 0) < 0)
    .sort((a, b) => (a.delta ?? 0) - (b.delta ?? 0) || (b.maxMedianHR ?? 0) - (a.maxMedianHR ?? 0));

  const movesLines = [];
  movesLines.push(`Unique tier suggested moves — ${diff.generatedAt}`);
  movesLines.push(
    `Window ${windowHours}h, min ${minSamples} samples, top-pct ${topPercentile}, ladder=${isLadder} hardcore=${isHardcore}, corrupted=${excludeCorrupted ? 'excluded' : 'included'}`,
  );
  movesLines.push('');
  movesLines.push(`Total: ${upgrades.length} upgrade(s), ${downgrades.length} downgrade(s)`);
  movesLines.push('');
  const header = 'base    var   cur → sug   Δ    median       listings  top name (samples)';
  const sep = '-'.repeat(90);

  movesLines.push(`UPGRADES (${upgrades.length}) — promote to a higher tier, sorted by Δ desc`);
  movesLines.push(sep);
  movesLines.push(header);
  movesLines.push(sep);
  for (const m of upgrades) movesLines.push(formatMoveLine(m));

  movesLines.push('');
  movesLines.push(`DOWNGRADES (${downgrades.length}) — demote to a lower tier, sorted by Δ asc`);
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
  const cur = tierShort[m.currentEffectiveTier] || '?';
  const sug = tierShort[m.suggestedTier] || '?';
  const v = m.variant === 'eth' ? 'ETH ' : 'norm';
  const d = (m.delta ?? 0) > 0 ? `+${m.delta}` : `${m.delta}`;
  const med = fmtHR(m.maxMedianHR).padStart(8);
  return `${m.base.padEnd(6)} ${v}  ${cur} → ${sug}   ${d.padStart(3)}  ${med}    ${String(m.totalListings).padStart(5)}  ${m.topName || ''} (${m.sampleCount})`;
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
