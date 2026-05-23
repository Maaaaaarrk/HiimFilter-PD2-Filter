// Updates rune and uber-material economy aliases in
// builderfilter/02-alias/04-alias-economy-values[ALL].filter using median prices from the
// PD2 Trader API. Ported with permission from Roofoo's filter
// (https://github.com/RoofooEvazan/Roofoo-s-PD2-Loot-Filter). Primary window is 24h, but
// when a scraped value would lower the current alias the longer 3-day window is used
// instead to smooth short-term dips. Filename kept for CI compatibility — also updates
// DClone / Rathma / Lucion boss mats and PD2 utility items (WSS, Tainted WSS,
// Puzzlebox/Piece, Demonic Cube, Catalyst Shard).

import { readFile, writeFile } from 'node:fs/promises';

const API_URL = 'https://pd2trader.com/item-prices/average/batch';
const ALIAS_FILE = 'builderfilter/02-alias/04-alias-economy-values[ALL].filter';

const isLadder = process.env.PD2TRADER_LADDER !== 'false';
const isHardcore = process.env.PD2TRADER_HARDCORE === 'true';
const windowHours = Number(process.env.PD2TRADER_WINDOW_HOURS) || 24;
const decreaseWindowHours = Number(process.env.PD2TRADER_DECREASE_WINDOW_HOURS) || 72;
const minSampleCount = Number(process.env.PD2TRADER_MIN_SAMPLES) || 5;

const runes = [
  { code: 'r27', name: 'Ohm',  alias: 'OHM' },
  { code: 'r28', name: 'Lo',   alias: 'LO',   cap: 1 },   // manual cap: market-driven but never above 1 HR
  { code: 'r29', name: 'Sur',  alias: 'SUR',  floor: 1.5 },
  { code: 'r30', name: 'Ber',  alias: 'BER',  floor: 3 },
  { code: 'r31', name: 'Jah',  alias: 'JAH' },
  { code: 'r32', name: 'Cham', alias: 'CHAM' },
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
  // PD2 utility items (full alias set: VALUE / WSS_VALUE / STACK_HR / STACK_WSS)
  { code: 'wss',  name: 'Worldstone Shard',          alias: 'WSS_ITEM',                  set: 'full', valueSuffix: '_HR_VALUE' },
  { code: 'cwss', name: 'Tainted Worldstone Shard',  alias: 'TAINTED_WORLDSTONE_SHARD',  set: 'full' },
  { code: 'iwss', name: 'Catalyst Shard',            alias: 'CATALYST_SHARD',            set: 'full' },
  { code: 'lbox', name: 'Larzuk Puzzlebox',          alias: 'LARZUK_PUZZLEBOX',          set: 'full' },
  { code: 'lpp',  name: 'Larzuk Puzzlepiece',        alias: 'LARZUK_PUZZLEPIECE',        set: 'full' },
  { code: 'imrn', name: 'Demonic Cube',              alias: 'DEMONIC_CUBE',              set: 'full' },
];

function normalizePriceValue(value) {
  if (typeof value === 'number') return value;
  if (typeof value !== 'string') return undefined;
  const normalized = value.trim().toLowerCase();
  const wssMatch = normalized.match(/^(\d+(?:\.\d+)?)\s*wss$/);
  if (wssMatch) return Number(wssMatch[1]) * 0.01;
  const hrMatch = normalized.match(/^(\d+(?:\.\d+)?)\s*hr$/);
  if (hrMatch) return Number(hrMatch[1]);
  const numericValue = Number(normalized);
  return Number.isFinite(numericValue) ? numericValue : undefined;
}

function valueFromPrice(price) {
  if (!price) return undefined;
  if ((price.sampleCount ?? 0) < minSampleCount) return undefined;
  for (const key of ['medianPrice', 'averagePrice', 'movingAverage7Days']) {
    const v = normalizePriceValue(price[key]);
    if (Number.isFinite(v) && v > 0) return v;
  }
  return undefined;
}

function roundToFiveHundredths(value) {
  if (!Number.isFinite(value)) return value;
  const rounded = Math.round(value * 20) / 20;
  return value > 0 && rounded === 0 ? 0.05 : rounded;
}

// Mats span a wider price range than runes — under 0.1 HR a 0.05 step rounds away most
// of the signal, so use 0.01 steps there and switch to 0.05 once it's worth at least 0.1.
function roundMatValue(value) {
  if (!Number.isFinite(value)) return value;
  if (value < 0.1) {
    const rounded = Math.round(value * 100) / 100;
    return value > 0 && rounded === 0 ? 0.01 : rounded;
  }
  return Math.round(value * 20) / 20;
}

function formatHr(value) {
  if (!Number.isFinite(value)) return '0';
  return value.toFixed(2).replace(/\.?0+$/, '');
}

async function fetchPrices(hours) {
  const body = {
    baseCodes: [...runes.map((r) => r.code), ...ubermats.map((m) => m.code)],
    isLadder,
    isHardcore,
    hours,
  };

  const response = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`PD2 Trader API returned ${response.status} ${response.statusText}`);
  }

  const payload = await response.json();

  if (!payload || !Array.isArray(payload.data)) {
    throw new Error('PD2 Trader API response did not include a data array');
  }

  return new Map(payload.data.map((p) => [p.baseCode, p]));
}

function getCurrentAliasNumber(text, aliasName) {
  const re = new RegExp(`^Alias\\[${aliasName}\\]:\\s*(.+)$`, 'm');
  const match = text.match(re);
  if (!match) return undefined;
  const v = Number(match[1].trim());
  return Number.isFinite(v) ? v : undefined;
}

function computeHrValue(price, floor, cap, round) {
  let hrValue = round(valueFromPrice(price));
  if (!Number.isFinite(hrValue) || hrValue <= 0) return undefined;
  if (floor !== undefined && hrValue < floor) hrValue = floor;   // manual minimum
  if (cap !== undefined && hrValue > cap) hrValue = cap;         // manual maximum
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
  const [pricesPrimary, pricesDecrease] = await Promise.all([
    fetchPrices(windowHours),
    fetchPrices(decreaseWindowHours),
  ]);
  const original = await readFile(ALIAS_FILE, 'utf8');
  let text = original;
  const updates = [];

  for (const rune of runes) {
    let hrValue = computeHrValue(pricesPrimary.get(rune.code), rune.floor, rune.cap, roundToFiveHundredths);

    if (hrValue === undefined) {
      console.log(`${rune.name} (${rune.code}): no usable price data, skipping`);
      continue;
    }

    const currentAlias = `${rune.alias}_RUNE_VALUE`;
    const current = getCurrentAliasNumber(text, currentAlias);
    if (Number.isFinite(current) && hrValue < current) {
      const altValue = computeHrValue(pricesDecrease.get(rune.code), rune.floor, rune.cap, roundToFiveHundredths);
      if (altValue !== undefined) {
        console.log(`${rune.name} (${rune.code}): ${windowHours}h ${hrValue}HR below current ${current}HR, using ${decreaseWindowHours}h window ${altValue}HR`);
        hrValue = altValue;
      }
    }

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
    if (Number.isFinite(current) && hrValue < current) {
      const altValue = computeHrValue(pricesDecrease.get(mat.code), mat.floor, mat.cap, roundMatValue);
      if (altValue !== undefined) {
        console.log(`${mat.name} (${mat.code}): ${windowHours}h ${hrValue}HR below current ${current}HR, using ${decreaseWindowHours}h window ${altValue}HR`);
        hrValue = altValue;
      }
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
