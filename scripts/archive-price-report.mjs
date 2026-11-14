// One-off check of the economy values against the PD2 market archive (sold and expired
// listings). The archive needs a logged-in account: get a short-lived token from the "Market
// archive access" card on hiimpd2.com/admin and run
//   PD2_MARKET_ACCESS_TOKEN=<token> node scripts/archive-price-report.mjs
// It changes nothing; it prints, per item, the current filter value, the open asks the bot
// prices from, and the archived listings split into sold (accepted offer) and expired, and
// writes the same table to temp/archive-price-report.md.

import { mkdir, readFile, writeFile } from 'node:fs/promises';
import {
  ARCHIVE_URL, currencyPriceHR, dedupeBySeller, fetchListings, median, percentile, withoutOutliers,
} from './lib/market.mjs';

const ALIAS_FILE = 'builderfilter/02-alias/04-alias-economy-values[ALL].filter';
const OUT_FILE = 'temp/archive-price-report.md';
const token = process.env.PD2_MARKET_ACCESS_TOKEN?.trim();
const hours = Number(process.env.MARKET_WINDOW_HOURS) || 168;
const ladder = { is_ladder: String(process.env.MARKET_LADDER !== 'false'), is_hardcore: String(process.env.MARKET_HARDCORE === 'true') };

const ITEMS = [
  ['r20', 'Lem', 'LEM_RUNE_VALUE'], ['r21', 'Pul', 'PUL_RUNE_VALUE'], ['r22', 'Um', 'UM_RUNE_VALUE'],
  ['r23', 'Mal', 'MAL_RUNE_VALUE'], ['r24', 'Ist', 'IST_RUNE_VALUE'], ['r25', 'Gul', 'GUL_RUNE_VALUE'],
  ['r26', 'Vex', 'VEX_RUNE_VALUE'], ['r27', 'Ohm', 'OHM_RUNE_VALUE'], ['r28', 'Lo', 'LO_RUNE_VALUE'],
  ['r29', 'Sur', 'SUR_RUNE_VALUE'], ['r30', 'Ber', 'BER_RUNE_VALUE'], ['r31', 'Jah', 'JAH_RUNE_VALUE'],
  ['r32', 'Cham', 'CHAM_RUNE_VALUE'], ['r33', 'Zod', 'ZOD_RUNE_VALUE'],
  ['cwss', 'Tainted WSS', 'TAINTED_WORLDSTONE_SHARD_VALUE'], ['lbox', 'Larzuk Puzzlebox', 'LARZUK_PUZZLEBOX_VALUE'],
  ['lpp', 'Larzuk Puzzlepiece', 'LARZUK_PUZZLEPIECE_VALUE'], ['imrn', 'Demonic Cube', 'DEMONIC_CUBE_VALUE'],
];

function aliasValue(text, name) {
  const match = text.match(new RegExp(`^Alias\\[${name}\\]:\\s*([\\d.]+)`, 'm'));
  return match ? Number(match[1]) : undefined;
}

function prices(listings, referenceHR, runeHR) {
  const priced = listings
    .map((l) => ({ seller: l.user_id, hr: currencyPriceHR(l, { referenceHR, runeHR }) }))
    .filter((e) => e.seller && e.hr > 0);
  return withoutOutliers(dedupeBySeller(priced, (e) => e.hr).map((e) => e.hr));
}

const fmt = (v) => (Number.isFinite(v) ? v.toFixed(2) : '–');
const stats = (values) => `${values.length} | ${fmt(percentile(values, 0.25))} | ${fmt(median(values))}`;

async function main() {
  if (!token) {
    console.error('Set PD2_MARKET_ACCESS_TOKEN (from the Market archive access card on hiimpd2.com/admin).');
    process.exit(1);
  }
  const text = await readFile(ALIAS_FILE, 'utf8');
  const runeHR = {};
  for (const m of text.matchAll(/^Alias\[([A-Z]+)_RUNE_VALUE\]:\s*([\d.]+)/gm)) runeHR[m[1]] = Number(m[2]);

  const lines = [
    `Window ${hours}h, ${ladder.is_ladder === 'true' ? 'ladder' : 'non-ladder'} ${ladder.is_hardcore === 'true' ? 'hardcore' : 'softcore'}. One price per seller, outliers dropped. Columns: sellers | 25th percentile | median (HR).`,
    '',
    '| Item | Filter value | Open asks | Archive sold | Archive not sold |',
    '|---|---|---|---|---|',
  ];
  for (const [code, name, alias] of ITEMS) {
    const filters = { ...ladder, 'item.base_code': code };
    const referenceHR = aliasValue(text, alias);
    const open = await fetchListings(filters, { hours });
    const archive = await fetchListings(filters, { hours, url: ARCHIVE_URL, token, openOnly: false });
    const sold = archive.filter((l) => l.accepted_offer_id);
    const unsold = archive.filter((l) => !l.accepted_offer_id);
    const row = `| ${name} | ${fmt(referenceHR)} | ${stats(prices(open, referenceHR, runeHR))} | ${stats(prices(sold, referenceHR, runeHR))} | ${stats(prices(unsold, referenceHR, runeHR))} |`;
    lines.push(row);
    console.log(row);
  }
  await mkdir('temp', { recursive: true });
  await writeFile(OUT_FILE, `${lines.join('\n')}\n`, 'utf8');
  console.log(`\nWrote ${OUT_FILE}`);
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
