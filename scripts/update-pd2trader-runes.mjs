// Updates rune economy aliases in builderfilter/02-alias/04-alias-economy-values[ALL].filter
// using median prices from the PD2 Trader API. Ported with permission from Roofoo's filter
// (https://github.com/RoofooEvazan/Roofoo-s-PD2-Loot-Filter), trimmed to runes only and
// to a single latest-prices window.

import { readFile, writeFile } from 'node:fs/promises';

const API_URL = 'https://pd2trader.com/item-prices/average/batch';
const ALIAS_FILE = 'builderfilter/02-alias/04-alias-economy-values[ALL].filter';

const isLadder = process.env.PD2TRADER_LADDER !== 'false';
const isHardcore = process.env.PD2TRADER_HARDCORE === 'true';
const windowHours = Number(process.env.PD2TRADER_WINDOW_HOURS) || 24;
const minSampleCount = Number(process.env.PD2TRADER_MIN_SAMPLES) || 2;

const runes = [
  { code: 'r27', name: 'Ohm',  alias: 'OHM' },
  { code: 'r28', name: 'Lo',   alias: 'LO' },
  { code: 'r29', name: 'Sur',  alias: 'SUR' },
  { code: 'r30', name: 'Ber',  alias: 'BER' },
  { code: 'r31', name: 'Jah',  alias: 'JAH' },
  { code: 'r32', name: 'Cham', alias: 'CHAM' },
  { code: 'r33', name: 'Zod',  alias: 'ZOD' },
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

function formatHr(value) {
  if (!Number.isFinite(value)) return '0';
  return value.toFixed(2).replace(/\.?0+$/, '');
}

async function fetchPrices() {
  const body = {
    baseCodes: runes.map((r) => r.code),
    isLadder,
    isHardcore,
    hours: windowHours,
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
  const pricesByCode = await fetchPrices();
  const original = await readFile(ALIAS_FILE, 'utf8');
  let text = original;
  const updates = [];

  for (const rune of runes) {
    const price = pricesByCode.get(rune.code);
    const hrValue = roundToFiveHundredths(valueFromPrice(price));

    if (!Number.isFinite(hrValue) || hrValue <= 0) {
      console.log(`${rune.name} (${rune.code}): no usable price data, skipping`);
      continue;
    }

    const wssValue = Math.round(hrValue * 100);
    const hrStr = formatHr(hrValue);
    const wssStr = String(wssValue);

    text = replaceAlias(text, `${rune.alias}_RUNE_VALUE`, hrStr);
    text = replaceAlias(text, `${rune.alias}_WSS_VALUE`, wssStr);
    text = replaceAlias(text, `${rune.alias}_STACK_HR`, `(QTY*${hrStr})`);
    text = replaceAlias(text, `${rune.alias}_STACK_WSS`, `(QTY*${wssStr})`);
    updates.push(`${rune.name}=${hrStr}HR/${wssStr}WSS`);
  }

  if (text === original) {
    console.log('No rune value changes needed.');
    return;
  }

  text = text.replace(/^Alias\[CURRENCY_TIMESTAMP\]:.*$/m, timestampLine());
  await writeFile(ALIAS_FILE, text, 'utf8');
  console.log(`Updated rune values: ${updates.join(', ')}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
