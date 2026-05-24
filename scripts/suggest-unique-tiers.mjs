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
//   --cutoff-4=4.0 --cutoff-3=2.0 --cutoff-2=0.5 --cutoff-1=0.25 --cutoff-0=0.15 --cutoff-no=0.1
// Note: 100 WSS = 1 HR. Item-name medians are converted to HR before comparison.
// Early ladder, 4,3, 1, .5, .25, .15
const CUTOFFS_HR = [
  { tier: '4_STAR_UNIQUE',  cutoffHR: Number(args['cutoff-4']  ?? 7.0) },
  { tier: '3_STAR_UNIQUE',  cutoffHR: Number(args['cutoff-3']  ?? 4.0) },
  { tier: '2_STAR_UNIQUE',  cutoffHR: Number(args['cutoff-2']  ?? 2) },
  { tier: '1_STAR_UNIQUE',  cutoffHR: Number(args['cutoff-1']  ?? 1) },
  { tier: '0_STAR_UNIQUE',  cutoffHR: Number(args['cutoff-0']  ?? 0.5) },
  { tier: 'NO_STAR_UNIQUE', cutoffHR: Number(args['cutoff-no'] ?? 0.25) },
];

// Items to skip when emitting move suggestions. Matched case-insensitively against
// the item's display name (substring match). Optional fields:
//   variant   — single row variant to match: 'eth' | 'noneth' | 'both'
//   variants  — array of row variants to match (use instead of variant when more than one)
//   direction — 'upgrade' or 'downgrade'; omit to match either
// Omit all of the above to ignore every move for the matched name.
const IGNORE_MOVES = [
  { name: 'Silks of the Victor' }, // eth-only unique; market data isn't useful for tiering
  // Eth-protected: ignore demotions when the eth version is part of the move.
  // The eth-rolled copy of these weapons holds its tier even if non-eth softens.
  // Non-eth-only demotions (variant === 'noneth') are still allowed through.
  { name: 'Stoneraven',         variants: ['eth'], direction: 'downgrade' },
  { name: 'The Cranium Basher', variants: ['eth'], direction: 'downgrade' },
  { name: 'Bloodtree Stump',    variants: ['eth'], direction: 'downgrade' },
  { name: 'Steel Pillar',       variants: ['eth'], direction: 'downgrade' },
  { name: 'The Grandfather',    variants: ['eth'], direction: 'downgrade' },
  { name: 'Death Cleaver',      variants: ['eth'], direction: 'downgrade' },
  { name: 'Lacerator',          variants: ['eth'], direction: 'downgrade' },
  { name: "Titan's Revenge",    variants: ['eth'], direction: 'downgrade' },
  { name: 'Purgatory',          variants: ['eth'], direction: 'downgrade' },
  { name: 'The Gavel of Pain',  variants: ['eth'], direction: 'downgrade' },
  { name: "Warlord's Trust",    variants: ['eth'], direction: 'downgrade' },
  { name: 'Ribcracker',         variants: ['eth'], direction: 'downgrade' },
  { name: "Zerae's Resolve",    variants: ['eth'], direction: 'downgrade' },
];

function isMoveIgnored(name, variant, direction) {
  const n = (name || '').toLowerCase();
  return IGNORE_MOVES.some((rule) => {
    if (rule.name && !n.includes(rule.name.toLowerCase())) return false;
    if (rule.variant && rule.variant !== variant) return false;
    if (rule.variants && !rule.variants.includes(variant)) return false;
    if (rule.direction && rule.direction !== direction) return false;
    return true;
  });
}

// True when the item has an eth-downgrade-protection rule in IGNORE_MOVES.
// Used to force a split row (eth + noneth) instead of collapsing into 'both',
// so the eth side gets pinned by its existing alias and only the non-eth side
// is re-tiered via the generic value alias.
function isEthProtected(name) {
  const n = (name || '').toLowerCase();
  return IGNORE_MOVES.some((rule) => {
    if (!rule.name || !n.includes(rule.name.toLowerCase())) return false;
    const matchesEth = rule.variant === 'eth' || rule.variants?.includes('eth');
    const matchesDowngrade = !rule.direction || rule.direction === 'downgrade';
    return matchesEth && matchesDowngrade;
  });
}
// top-percentile: per-name, only the top X% of listings by price contribute to the
// per-name median. Default 0.25 = "median of the top 25% priced listings". Captures
// the upside of finding a good (often corrupted) copy rather than the typical drop.
const topPercentile = Number(args['top-percentile']) || 0.25;
// excludeCorrupted: by default we include corrupted listings (top-priced copies are
// typically corrupted, and the filter highlights upside potential). Pass
// --exclude-corrupted=true to revert to clean-only listings.
const excludeCorrupted = args['exclude-corrupted'] === 'true';
// changeMultiplier: hysteresis. A tier change (upgrade or downgrade) is only
// suggested if the data clears the cutoff by this multiplier — i.e. promotions
// must hit M × cutoff(new tier), and demotions must fail to clear cutoff(current) / M.
// Default 1.0 = no hysteresis (current behavior). Pass --change-multiplier=2 to
// require 2x clearance, leaving borderline items in their current tier.
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

// Sockets filled with runes or jewels inflate the listed price (the filler itself
// has independent value). Gems are cheap and pass through. Filter at listing level
// so per-name medians reflect the item, not the filler.
function hasRuneOrJewelSocketed(listing) {
  const arr = listing?.item?.socketed;
  if (!Array.isArray(arr) || arr.length === 0) return false;
  return arr.some((s) => {
    const tc = s?.base?.type_code || s?.type_code;
    return tc === 'rune' || tc === 'jewel';
  });
}

function aggregateListings(listings) {
  const byName = new Map();
  for (const l of listings) {
    const name = l?.item?.name;
    const hr = priceToHR(l);
    if (!name || !Number.isFinite(hr)) continue;
    if (hasRuneOrJewelSocketed(l)) continue;
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
    maxNamePrices: top?.sortedDesc, // descending
    totalListings: listings.length,
    distinctNames: byName.size,
  };
}

function countAtOrAbove(sortedDescPrices, threshold) {
  if (!Array.isArray(sortedDescPrices) || !Number.isFinite(threshold)) return 0;
  let n = 0;
  for (const p of sortedDescPrices) {
    if (p >= threshold) n++;
    else break; // sorted desc — we can stop
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
  // Upgrade (sugIdx < curIdx): how many listings clear the cutoff for the new tier?
  if (sugIdx < curIdx) {
    return CUTOFFS_HR.find((c) => c.tier === suggestedTier) ?? null;
  }
  // Downgrade (sugIdx > curIdx): how many listings clear the cutoff for the tier
  // immediately above the demotion target? (i.e. how much "value" is being left
  // on the table by demoting?)
  const aboveTier = VALUE_TIERS[sugIdx - 1];
  return CUTOFFS_HR.find((c) => c.tier === aboveTier) ?? null;
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

// Walks down VALUE_TIERS top-first; returns the first tier where at least
// MIN_LISTINGS_FOR_TIER prices clear the cutoff. Replaces the old median-based
// classification — now an item is in a tier only if there's real liquidity at
// that price, not just one outlier dragging the median up.
const MIN_LISTINGS_FOR_TIER = 5;
function suggestTierFromPrices(sortedDescPrices) {
  if (!Array.isArray(sortedDescPrices) || sortedDescPrices.length === 0) return null;
  for (const c of CUTOFFS_HR) {
    if (countAtOrAbove(sortedDescPrices, c.cutoffHR) >= MIN_LISTINGS_FOR_TIER) return c.tier;
  }
  return null; // doesn't clear even NO★ with the required listing count
}

function tierIdx(tier) {
  const i = VALUE_TIERS.indexOf(tier);
  return i < 0 ? VALUE_TIERS.length : i;
}

// Hysteresis check: does the data clear the cutoff by `multiplier` for the move
// to actually be worth making? Upgrades need M × cutoff(new); downgrades need
// the item to fail to clear cutoff(current) / M (i.e. price has dropped well
// below where it would have held the current tier).
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
  // Always returns exactly 8 chars (right-aligned number + " HR" or " WS")
  if (!Number.isFinite(v)) return '       ?';
  if (v >= 100) return `${v.toFixed(0).padStart(5)} HR`;
  if (v >= 10) return `${v.toFixed(1).padStart(5)} HR`;
  if (v >= 1) return `${v.toFixed(2).padStart(5)} HR`;
  return `${(v * 100).toFixed(1).padStart(5)} WS`;
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
    `  window: ${windowHours}h, min-samples: ${minSamples}, top-pct: ${topPercentile}, ladder=${isLadder} hardcore=${isHardcore}, corrupted=${excludeCorrupted ? 'excluded' : 'included'}, change-multiplier=${changeMultiplier}`,
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

  // Group by base, decide per-base whether to combine ETH and non-ETH into a
  // single suggestion row or keep them split. Rules:
  //  - If both variants suggest the same tier: combine.
  //  - If the higher of the two suggestions is below 3★ (i.e., 2★ or lower):
  //    don't differentiate — force both to the higher tier, single combined row.
  //  - Else: keep split (eth row + non-eth row).
  const THREE_STAR_IDX = VALUE_TIERS.indexOf('3_STAR_UNIQUE');
  const baseGroups = new Map();
  for (const row of itemRows) {
    if (!baseGroups.has(row.base)) baseGroups.set(row.base, {});
    baseGroups.get(row.base)[row.isEth ? 'eth' : 'noneth'] = row;
  }
  const moveCandidates = [];
  for (const [base, group] of baseGroups) {
    const ethRow = group.eth;
    const nonethRow = group.noneth;
    const ethSug = ethRow?.suggestedTier ?? null;
    const nonethSug = nonethRow?.suggestedTier ?? null;
    const higherSugIdx = Math.min(tierIdx(ethSug), tierIdx(nonethSug));
    const lowerSugIdx = Math.max(tierIdx(ethSug), tierIdx(nonethSug));
    // Differentiate eth vs non-eth only when BOTH variants suggest 3★ or higher
    // (our alias system only has *_NO_ETH_UNIQUE / *_ETH_UNIQUE at 3★/4★).
    // If either variant is below 3★, collapse to a combined row at the higher tier.
    const eitherBelowThreeStar = lowerSugIdx > THREE_STAR_IDX;
    // Eth-protected items: force split so the eth row is filtered by IGNORE_MOVES
    // and only the non-eth row reaches the moves output. Without this the
    // collapse-to-'both' shadowed the variants:['eth'] rule.
    const topName = ethRow?.maxName || nonethRow?.maxName;
    const ethProtected = isEthProtected(topName);

    if (!ethProtected && (ethSug === nonethSug || eitherBelowThreeStar)) {
      // Combined row using the higher of the two as the suggestion
      const combinedSug = VALUE_TIERS[higherSugIdx] ?? null;
      // Pick whichever variant has more listings to drive the displayed data
      const dataRow =
        (ethRow?.totalListings ?? 0) >= (nonethRow?.totalListings ?? 0) ? ethRow : nonethRow;
      if (!dataRow) continue;
      // For "current", use the higher of the two effective tiers (most-aggressive
      // current classification — if base sits in eth-conditional alias, that wins).
      const ethCurIdx = tierIdx(ethRow?.currentTier);
      const nonethCurIdx = tierIdx(nonethRow?.currentTier);
      const combinedCurIdx = Math.min(ethCurIdx, nonethCurIdx);
      const combinedCur = VALUE_TIERS[combinedCurIdx] ?? null;
      moveCandidates.push({
        ...dataRow,
        variantLabel: 'both',
        currentTier: combinedCur,
        suggestedTier: combinedSug,
      });
    } else {
      // Split: emit per-variant
      if (ethRow) {
        moveCandidates.push({ ...ethRow, variantLabel: 'eth', suggestedTier: ethSug });
      }
      if (nonethRow) {
        moveCandidates.push({ ...nonethRow, variantLabel: 'noneth', suggestedTier: nonethSug });
      }
    }
  }

  // Sort by max median desc for stable display
  moveCandidates.sort((a, b) => (b.maxMedian ?? -1) - (a.maxMedian ?? -1));
  // Re-bind itemRows for downstream report generation (full table needs all rows)
  itemRows.sort((a, b) => (b.maxMedian ?? -1) - (a.maxMedian ?? -1));

  // Report
  const lines = [];
  lines.push(`Unique tier suggestions — generated ${new Date().toISOString()}`);
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

  // Diff JSON: only items where suggested differs from current. Skip rows
  // where the suggestion is null (no qualifying tier with ≥5 listings); those
  // are typically thin-data items that we don't want to act on.
  const moves = moveCandidates
    .filter((r) => r.suggestedTier && r.currentTier && r.suggestedTier !== r.currentTier)
    .filter((r) => {
      const direction = tierIdx(r.currentTier) > tierIdx(r.suggestedTier) ? 'upgrade' : 'downgrade';
      return !isMoveIgnored(r.maxName, r.variantLabel, direction);
    })
    .map((r) => {
      const cutoff = relevantCutoffForMove(r.currentTier, r.suggestedTier);
      const cutoffCount = cutoff ? countAtOrAbove(r.maxNamePrices, cutoff.cutoffHR) : 0;
      const delta = tierIdx(r.currentTier) - tierIdx(r.suggestedTier);
      const isUpgrade = delta > 0;
      // est top val:
      //   - upgrades: average price of listings ≥ suggested tier's cutoff
      //               (i.e. average price among the listings that justify the new tier)
      //   - downgrades: average of the top 5 listings (peak value being demoted away from)
      const sugCutoffHR = CUTOFFS_HR.find((c) => c.tier === r.suggestedTier)?.cutoffHR;
      const estTopValHR = isUpgrade
        ? avgAtOrAbove(r.maxNamePrices, sugCutoffHR)
        : avgOfTopN(r.maxNamePrices, 5);
      return {
        base: r.base,
        variant: r.variantLabel,
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

  // Moves-only text file split by direction (upgrades vs downgrades).
  // Within each section, sort by NEW (suggested) tier — highest first — then by
  // estimated value desc so the most valuable items per tier surface first.
  const byTierThenValue = (a, b) =>
    tierIdx(a.suggestedTier) - tierIdx(b.suggestedTier) ||
    (b.maxMedianHR ?? 0) - (a.maxMedianHR ?? 0);
  const upgrades = moves.filter((m) => (m.delta ?? 0) > 0).sort(byTierThenValue);
  const downgrades = moves.filter((m) => (m.delta ?? 0) < 0).sort(byTierThenValue);

  const movesLines = [];
  movesLines.push(`Unique tier suggested moves — ${diff.generatedAt}`);
  movesLines.push(
    `Window ${windowHours}h, min ${minSamples} samples, top-pct ${topPercentile}, ladder=${isLadder} hardcore=${isHardcore}, corrupted=${excludeCorrupted ? 'excluded' : 'included'}, change-multiplier=${changeMultiplier}`,
  );
  movesLines.push('');
  movesLines.push('est val   = median of the top X% (or top 5, whichever is more) of listings, per item-name.');
  movesLines.push('est top   = average price of selected high-end listings:');
  movesLines.push('  - upgrades:   average of listings that clear the suggested tier cutoff');
  movesLines.push('                (the typical price *among* the listings justifying the new tier).');
  movesLines.push('  - downgrades: average of the top 5 listings (the peak being demoted away from).');
  movesLines.push('qualify(n)= count of listings that clear the named tier:');
  movesLines.push('  - upgrades:   ≥(suggested tier) — validates the promotion (must be ≥5 for the move).');
  movesLines.push('  - downgrades: ≥(tier just above the demotion target) — listings that still merit');
  movesLines.push('                a tier above where we are demoting to.');
  movesLines.push('');
  movesLines.push(`Total: ${upgrades.length} upgrade(s), ${downgrades.length} downgrade(s)`);
  movesLines.push('');
  // Column widths: base(5) | var(4) | cur(2)+arrow+sug(2)=7 | est val(8) | est top(8) | qualify(11) | total(5) | top
  const header = `${'base'.padEnd(5)}  ${'var '.padEnd(4)}   ${'move   '.padEnd(7)}   ${'est val '.padEnd(8)}   ${'est top '.padEnd(8)}   ${'qualify(n)'.padEnd(11)}  total  top name (top of total)`;
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
  const v =
    m.variant === 'eth' ? 'ETH '   :
    m.variant === 'both' ? 'both' :
    'norm';
  const cur = (tierShort[m.currentEffectiveTier] || '? ').padStart(2);
  const sug = (tierShort[m.suggestedTier] || '? ').padEnd(2);
  const move = `${cur} → ${sug}`; // 7 chars
  const med = fmtHR(m.maxMedianHR); // 8 chars
  const topVal = fmtHR(m.estTopValHR); // 8 chars
  const qualifyStr = m.cutoffTier ? `≥${tierShort[m.cutoffTier]} (${m.cutoffCount})` : '';
  const qualifyPadded = qualifyStr.padEnd(11);
  const total = String(m.totalListings).padStart(5);
  let topStr = `${m.topName || ''} (top ${m.topUsedForMedian} of ${m.topNameTotal})`;
  // Eth-protected non-eth-only move: annotate that the eth side stays pinned
  // by its existing eth-conditional alias; only the generic value alias is moved.
  if (m.variant === 'noneth' && isEthProtected(m.topName)) {
    const ethPinTier =
      m.sourceTiers?.includes('4_STAR_ETH_UNIQUE') ? '4★' :
      m.sourceTiers?.includes('4_STAR_NO_ETH_UNIQUE') ? '3★' :
      null;
    if (ethPinTier) topStr += ` — eth pinned ${ethPinTier}`;
  }
  return `${base}  ${v}   ${move}   ${med}   ${topVal}   ${qualifyPadded}  ${total}  ${topStr}`;
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
