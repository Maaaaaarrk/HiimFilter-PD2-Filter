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
// cutoff-percentile: lower = more conservative tier promotion (item must clear higher
// portion of target tier). 0.5 = median (loose), 0.25 = p25 (strict).
const cutoffPercentile = Number(args['cutoff-percentile']) || 0.33;
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
    const params = new URLSearchParams({
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
      'item.corrupted': 'false',
    });
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
    const sorted = [...prices].sort((a, b) => a - b);
    const median = sorted[Math.floor(sorted.length / 2)];
    medians.push({ name, median, count: prices.length });
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

function calibrateThresholds(itemRows, cutoffPercentile) {
  // For each VALUE_TIER, gather the maxMedian of every (base, eth) row whose
  // currentTier resolves to that value tier. Tier stats = distribution of those.
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
  // Cutoff for entering tier_high = cutoffPercentile of tier_high prices.
  // Default 0.5 = median, more conservative values (e.g. 0.33) require items
  // to be in the upper portion of the tier's distribution to qualify.
  const ordered = VALUE_TIERS.filter((t) => Number.isFinite(tierStats.get(t)?.p50));
  const cutoffs = [];
  for (const tier of ordered) {
    const prices = pricesByTier.get(tier);
    cutoffs.push({ tier, cutoffHR: percentile(prices, cutoffPercentile) });
  }
  return { tierStats, cutoffs, ordered };
}

function suggestTier(maxMedianHR, calibration) {
  if (!Number.isFinite(maxMedianHR)) return null;
  for (const c of calibration.cutoffs) {
    if (maxMedianHR >= c.cutoffHR) return c.tier;
  }
  return calibration.ordered[calibration.ordered.length - 1] || null;
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
  console.error(`  window: ${windowHours}h, min-samples: ${minSamples}, ladder=${isLadder} hardcore=${isHardcore}`);

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

  const calibration = calibrateThresholds(itemRows, cutoffPercentile);
  console.error(`tier price distribution (n / p10 / p50 / p90, HR):`);
  for (const t of calibration.ordered) {
    const s = calibration.tierStats.get(t);
    console.error(
      `  ${t.padEnd(20)} n=${String(s.count).padStart(3)}  p10=${(s.p10 ?? 0).toFixed(3)}  p50=${(s.p50 ?? 0).toFixed(3)}  p90=${(s.p90 ?? 0).toFixed(3)}`,
    );
  }
  console.error(`cutoffs (≥ X HR → tier, percentile=${cutoffPercentile}):`);
  for (const c of calibration.cutoffs) {
    console.error(`  ≥ ${c.cutoffHR.toFixed(3)} HR → ${c.tier}`);
  }

  for (const row of itemRows) {
    row.suggestedTier = suggestTier(row.maxMedian, calibration);
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
  lines.push('Tier price distribution (n / p10 / p50 / p90, HR):');
  for (const t of calibration.ordered) {
    const s = calibration.tierStats.get(t);
    lines.push(
      `  ${t.padEnd(20)} n=${String(s.count).padStart(3)}  p10=${(s.p10 ?? 0).toFixed(3).padStart(7)}  p50=${(s.p50 ?? 0).toFixed(3).padStart(7)}  p90=${(s.p90 ?? 0).toFixed(3).padStart(7)}`,
    );
  }
  lines.push('');
  lines.push(`Cutoffs (≥ X HR → tier, cutoff-percentile=${cutoffPercentile}):`);
  for (const c of calibration.cutoffs) {
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
    params: { windowHours, minSamples, isLadder, isHardcore, cutoffPercentile },
    calibration: {
      tierStats: Object.fromEntries(calibration.tierStats),
      cutoffs: calibration.cutoffs,
    },
    moves,
  };
  await writeFile(DIFF_FILE, JSON.stringify(diff, null, 2), 'utf8');
  console.error(`wrote ${DIFF_FILE} (${moves.length} suggested moves)`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
