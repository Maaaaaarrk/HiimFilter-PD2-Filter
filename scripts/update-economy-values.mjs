// Updates rune and uber-material economy aliases in
// builderfilter/02-alias/04-alias-economy-values[ALL].filter from live listings on the
// official Project Diablo 2 market. The listings are asks: each seller counts once (their
// lowest asking price), outliers are dropped (withoutOutliers), the value is the 25th
// percentile of the rest and their min and max become the item's *_MARKET_RANGE alias. The
// primary window is 3 days; when it would lower the current alias, the 7-day window is used
// instead to smooth short-term dips. Also updates DClone / Rathma / Lucion boss mats and PD2
// utility items (WSS, Tainted WSS, Puzzlebox/Piece, Demonic Cube, Catalyst Shard).

import { readFile, writeFile } from 'node:fs/promises';
import { fetchListings, currencyPriceHR, dedupeBySeller, percentile, withoutOutliers } from './lib/market.mjs';

const ALIAS_FILE = 'builderfilter/02-alias/04-alias-economy-values[ALL].filter';

const isLadder = process.env.MARKET_LADDER !== 'false';
const isHardcore = process.env.MARKET_HARDCORE === 'true';
const windowHours = Number(process.env.MARKET_WINDOW_HOURS) || 72;
const decreaseWindowHours = Number(process.env.MARKET_DECREASE_WINDOW_HOURS) || 168;
const minSampleCount = Number(process.env.MARKET_MIN_SELLERS) || 5;
// Open listings are asks, which sit above where trades close, so the value is the price the
// cheapest quarter of sellers ask (25th percentile), not the middle ask.
const ASK_PERCENTILE = Number(process.env.MARKET_ASK_PERCENTILE) || 0.25;

// Low runes (Lem through Gul) use the mats' finer rounding, since a 0.05 HR step is a large
// share of their value.
const runes = [
  { code: 'r20', name: 'Lem',  alias: 'LEM',  round: roundMatValue },
  { code: 'r21', name: 'Pul',  alias: 'PUL',  round: roundMatValue },
  { code: 'r22', name: 'Um',   alias: 'UM',   round: roundMatValue },
  { code: 'r23', name: 'Mal',  alias: 'MAL',  round: roundMatValue },
  { code: 'r24', name: 'Ist',  alias: 'IST',  round: roundMatValue },
  { code: 'r25', name: 'Gul',  alias: 'GUL',  round: roundMatValue },
  { code: 'r27', name: 'Ohm',  alias: 'OHM' },
  { code: 'r28', name: 'Lo',   alias: 'LO',   cap: 1 },   // manual cap: market-driven but never above 1 HR
  { code: 'r29', name: 'Sur',  alias: 'SUR',  floor: 1.5 },
  { code: 'r30', name: 'Ber',  alias: 'BER',  floor: 3 },
  { code: 'r31', name: 'Jah',  alias: 'JAH' },
  { code: 'r32', name: 'Cham', alias: 'CHAM' },  // floor set at runtime to 1/2 Zod
  { code: 'r33', name: 'Zod',  alias: 'ZOD' },
];

// Uber materials and PD2 utility items.
//   set:'single' updates only `${alias}${valueSuffix}` (boss mats — no WSS/STACK siblings)
//   set:'full'   updates four aliases: `${alias}${valueSuffix}`, `${alias}_WSS_VALUE`,
//                `${alias}_STACK_HR`, `${alias}_STACK_WSS` (PD2 items)
// valueSuffix defaults to '_VALUE'; WSS_ITEM uses '_HR_VALUE' instead.
const ubermats = [
  // DClone mats
  { code: 'dcho', name: 'Black Soulstone',           alias: 'BLACK_SOULSTONE',           set: 'single' },
  { code: 'dcso', name: 'Prime Evil Soul',           alias: 'PRIME_EVIL_SOUL',           set: 'single' },
  { code: 'dcbl', name: 'Pure Demonic Essence',      alias: 'PURE_DEMONIC_ESSENCE',      set: 'single' },
  // Rathma mats
  { code: 'cm2f', name: 'Hellfire Ashes',            alias: 'HELLFIRE_ASHES',            set: 'single' },
  { code: 'rtmv', name: 'Splinter of the Void',      alias: 'SPLINTER_OF_THE_VOID',      set: 'single' },
  { code: 'rtmo', name: "Trang-Oul's Jawbone",       alias: 'TRANG_OUL_JAWBONE',         set: 'single' },
  // Lucion mats
  { code: 'lucb', name: 'Demonic Insignia',          alias: 'DEMONIC_INSIGNIA',          set: 'single' },
  { code: 'lucc', name: 'Talisman of Transgression', alias: 'TALISMAN_OF_TRANSGRESSION', set: 'single' },
  { code: 'lucd', name: 'Flesh of Malic',            alias: 'FLESH_OF_MALIC',            set: 'single' },
  // Token of Absolution essences
  { code: 'fed',  name: 'Festering Essence',         alias: 'FESTERING_ESS',             set: 'single' },
  { code: 'bet',  name: 'Burning Essence',           alias: 'BURNING_ESS',               set: 'single' },
  { code: 'ceh',  name: 'Charged Essence',           alias: 'CHARGED_ESS',               set: 'single' },
  { code: 'tes',  name: 'Twisted Essence',           alias: 'TWISTED_ESS',               set: 'single' },
  // PD2 utility items (full alias set: VALUE / WSS_VALUE / STACK_HR / STACK_WSS)
  { code: 'wss',  name: 'Worldstone Shard',          alias: 'WSS_ITEM',                  set: 'full', valueSuffix: '_HR_VALUE', range: false },
  { code: 'cwss', name: 'Tainted Worldstone Shard',  alias: 'TAINTED_WORLDSTONE_SHARD',  set: 'full' },
  { code: 'iwss', name: 'Catalyst Shard',            alias: 'CATALYST_SHARD',            set: 'full' },
  { code: 'lbox', name: 'Larzuk Puzzlebox',          alias: 'LARZUK_PUZZLEBOX',          set: 'full' },
  { code: 'lpp',  name: 'Larzuk Puzzlepiece',        alias: 'LARZUK_PUZZLEPIECE',        set: 'full' },
  { code: 'imrn', name: 'Demonic Cube',              alias: 'DEMONIC_CUBE',              set: 'full' },
];

function valueFromPrice(price) {
  if (!price || price.sellers < minSampleCount) return undefined;
  return price.value;
}

function roundToFiveHundredths(value) {
  if (!Number.isFinite(value)) return value;
  const rounded = Math.round(value * 20) / 20;
  return value > 0 && rounded === 0 ? 0.05 : rounded;
}

// Mats span a wider price range than runes — under 0.25 HR a 0.05 step rounds away most
// of the signal, so use 0.01 steps there and switch to 0.05 once it's worth at least 0.25.
function roundMatValue(value) {
  if (!Number.isFinite(value)) return value;
  if (value < 0.25) {
    const rounded = Math.round(value * 100) / 100;
    return value > 0 && rounded === 0 ? 0.01 : rounded;
  }
  return Math.round(value * 20) / 20;
}

function formatHr(value) {
  if (!Number.isFinite(value)) return '0';
  return value.toFixed(2).replace(/\.?0+$/, '');
}

function currentRuneValues(text) {
  const values = {};
  for (const match of text.matchAll(/^Alias\[([A-Z]+)_RUNE_VALUE\]:\s*([\d.]+)\s*$/gm)) {
    values[match[1]] = Number(match[2]);
  }
  return values;
}

function referenceValue(text, item) {
  const alias = runes.includes(item) ? `${item.alias}_RUNE_VALUE` : `${item.alias}${item.valueSuffix ?? '_VALUE'}`;
  return getCurrentAliasNumber(text, alias);
}

function priceSummary(listings, referenceHR, runeHR) {
  const priced = listings
    .map((l) => ({ seller: l.user_id, hr: currencyPriceHR(l, { referenceHR, runeHR }) }))
    .filter((e) => e.seller && Number.isFinite(e.hr) && e.hr > 0);
  const perSeller = dedupeBySeller(priced, (e) => e.hr);
  const kept = withoutOutliers(perSeller.map((e) => e.hr));
  return {
    value: percentile(kept, ASK_PERCENTILE),
    min: Math.min(...kept),
    max: Math.max(...kept),
    sellers: perSeller.length,
    outliers: perSeller.length - kept.length,
    listings: listings.length,
  };
}

// One fetch per item over the longer window; the primary window is the recent slice of it.
async function fetchPrices(text) {
  const runeHR = currentRuneValues(text);
  const cutoff = Date.now() - windowHours * 3600 * 1000;
  const primary = new Map();
  const decrease = new Map();
  for (const item of [...runes, ...ubermats]) {
    const listings = await fetchListings(
      { is_ladder: String(isLadder), is_hardcore: String(isHardcore), 'item.base_code': item.code },
      { hours: decreaseWindowHours },
    );
    const referenceHR = referenceValue(text, item);
    const recent = listings.filter((l) => Date.parse(l.updated_at) >= cutoff);
    primary.set(item.code, priceSummary(recent, referenceHR, runeHR));
    decrease.set(item.code, priceSummary(listings, referenceHR, runeHR));
  }
  return [primary, decrease];
}

function getCurrentAliasNumber(text, aliasName) {
  const re = new RegExp(`^Alias\\[${aliasName}\\]:\\s*(.+)$`, 'm');
  const match = text.match(re);
  if (!match) return undefined;
  const v = Number(match[1].trim());
  return Number.isFinite(v) ? v : undefined;
}

function currentRuneValue(text, rune) {
  return getCurrentAliasNumber(text, `${rune.alias}_RUNE_VALUE`);
}

function computeHrValue(price, floor, cap, round, finish = (v) => v) {
  let hrValue = round(valueFromPrice(price));
  if (!Number.isFinite(hrValue) || hrValue <= 0) return undefined;
  if (floor !== undefined && hrValue < floor) hrValue = floor;   // manual minimum
  if (cap !== undefined && hrValue > cap) hrValue = cap;         // manual maximum
  return finish(hrValue);
}

// Runes worth more than 2 HR always round down to the nearest 0.25 HR.
function floorHighRune(value) {
  return value > 2 ? Math.floor(value * 4 + 1e-9) / 4 : value;
}

function runeRound(rune) {
  return rune.round ?? roundToFiveHundredths;
}

function marketRange(price, round, finish = (v) => v) {
  if (!price || price.sellers < minSampleCount || !Number.isFinite(price.min)) return undefined;
  return `${formatHr(finish(round(price.min)))} - ${formatHr(finish(round(price.max)))} HR`;
}

// Final HR value a rune will be written at: primary window, falling back to the longer
// decrease window when the primary would lower the current alias. Quiet (no logging) — used
// to derive Cham's dynamic floor before the main loop recomputes and logs the same value.
function resolveRuneValue(rune, pricesPrimary, pricesDecrease, text) {
  let hrValue = computeHrValue(pricesPrimary.get(rune.code), rune.floor, rune.cap, runeRound(rune), floorHighRune);
  if (hrValue === undefined) return undefined;
  const current = currentRuneValue(text, rune);
  if (Number.isFinite(current) && hrValue < current) {
    const altValue = computeHrValue(pricesDecrease.get(rune.code), rune.floor, rune.cap, runeRound(rune), floorHighRune);
    if (altValue !== undefined) hrValue = altValue;
  }
  return hrValue;
}

function replaceAlias(text, aliasName, newValue) {
  const re = new RegExp(`^(Alias\\[${aliasName}\\]:\\s*).+$`, 'm');
  if (!re.test(text)) {
    console.warn(`Alias ${aliasName} not found — skipping`);
    return text;
  }
  return text.replace(re, `$1${newValue}`);
}

function timestampLine() {
  const now = new Date();
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const month = months[now.getUTCMonth()];
  const day = now.getUTCDate();
  const year = now.getUTCFullYear();
  return `Alias[CURRENCY_TIMESTAMP]: %WHITE%HR Values Last updated ${month} ${day} ${year}`;
}

async function main() {
  const original = await readFile(ALIAS_FILE, 'utf8');
  const [pricesPrimary, pricesDecrease] = await fetchPrices(original);
  let text = original;
  const updates = [];

  // Cham tracks Zod: never list Cham below half of Zod's resolved value.
  const chamRune = runes.find((r) => r.alias === 'CHAM');
  const zodRune = runes.find((r) => r.alias === 'ZOD');
  if (chamRune && zodRune) {
    const zodValue = resolveRuneValue(zodRune, pricesPrimary, pricesDecrease, text);
    if (zodValue !== undefined) {
      chamRune.floor = roundToFiveHundredths(zodValue / 2);
      console.log(`Cham floor set to ${chamRune.floor}HR (1/2 of Zod ${zodValue}HR)`);
    }
  }

  for (const rune of runes) {
    let hrValue = computeHrValue(pricesPrimary.get(rune.code), rune.floor, rune.cap, runeRound(rune), floorHighRune);

    if (hrValue === undefined) {
      console.log(`${rune.name} (${rune.code}): no usable price data, skipping`);
      continue;
    }

    const currentAlias = `${rune.alias}_RUNE_VALUE`;
    const current = currentRuneValue(text, rune);
    let used = pricesPrimary.get(rune.code);
    if (Number.isFinite(current) && hrValue < current) {
      const altValue = computeHrValue(pricesDecrease.get(rune.code), rune.floor, rune.cap, runeRound(rune), floorHighRune);
      if (altValue !== undefined) {
        console.log(`${rune.name} (${rune.code}): ${windowHours}h ${hrValue}HR below current ${current}HR, using ${decreaseWindowHours}h window ${altValue}HR`);
        hrValue = altValue;
        used = pricesDecrease.get(rune.code);
      }
    }
    const range = marketRange(used, runeRound(rune), floorHighRune);
    if (range) text = replaceAlias(text, `${rune.alias}_MARKET_RANGE`, range);

    const wssValue = Math.round(hrValue * 100);
    const hrStr = formatHr(hrValue);
    const wssStr = String(wssValue);

    text = replaceAlias(text, currentAlias, hrStr);
    text = replaceAlias(text, `${rune.alias}_WSS_VALUE`, wssStr);
    text = replaceAlias(text, `${rune.alias}_STACK_HR`, `(QTY*${hrStr})`);
    text = replaceAlias(text, `${rune.alias}_STACK_WSS`, `(QTY*${wssStr})`);
    updates.push(`${rune.name}=${hrStr}HR/${wssStr}WSS`);
  }

  for (const mat of ubermats) {
    let hrValue = computeHrValue(pricesPrimary.get(mat.code), mat.floor, mat.cap, roundMatValue);

    if (hrValue === undefined) {
      console.log(`${mat.name} (${mat.code}): no usable price data, skipping`);
      continue;
    }

    const valueSuffix = mat.valueSuffix ?? '_VALUE';
    const valueAlias = `${mat.alias}${valueSuffix}`;
    const current = getCurrentAliasNumber(text, valueAlias);
    let used = pricesPrimary.get(mat.code);
    if (Number.isFinite(current) && hrValue < current) {
      const altValue = computeHrValue(pricesDecrease.get(mat.code), mat.floor, mat.cap, roundMatValue);
      if (altValue !== undefined) {
        console.log(`${mat.name} (${mat.code}): ${windowHours}h ${hrValue}HR below current ${current}HR, using ${decreaseWindowHours}h window ${altValue}HR`);
        hrValue = altValue;
        used = pricesDecrease.get(mat.code);
      }
    }
    if (mat.set === 'full' && mat.range !== false) {
      const range = marketRange(used, roundMatValue);
      if (range) text = replaceAlias(text, `${mat.alias}_MARKET_RANGE`, range);
    }

    const wssValue = Math.round(hrValue * 100);
    const hrStr = formatHr(hrValue);
    const wssStr = String(wssValue);

    text = replaceAlias(text, valueAlias, hrStr);
    if (mat.set === 'full') {
      text = replaceAlias(text, `${mat.alias}_WSS_VALUE`, wssStr);
      text = replaceAlias(text, `${mat.alias}_STACK_HR`, `(QTY*${hrStr})`);
      text = replaceAlias(text, `${mat.alias}_STACK_WSS`, `(QTY*${wssStr})`);
    }
    updates.push(`${mat.name}=${hrStr}HR/${wssStr}WSS`);
  }

  if (text === original) {
    console.log('No economy value changes needed.');
    return;
  }

  text = text.replace(/^Alias\[CURRENCY_TIMESTAMP\]:.*$/m, timestampLine());
  await writeFile(ALIAS_FILE, text, 'utf8');
  console.log(`Updated economy values: ${updates.join(', ')}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
