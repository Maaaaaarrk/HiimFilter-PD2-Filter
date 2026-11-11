// Shared helpers for reading the official Project Diablo 2 market
// (https://api.projectdiablo2.com/market/listing): paged listing fetches, de-duping, and
// turning free-text currency prices ("300 wss", "2 vex", "3.5") into HR.

export const MARKET_URL = 'https://api.projectdiablo2.com/market/listing';

const PAGE_SIZE = 200;

export async function fetchListings(filters, { hours, maxPages = 10, throttleMs = 200 } = {}) {
  const updatedAfter = new Date(Date.now() - hours * 3600 * 1000).toISOString();
  const all = [];
  for (let page = 0; page < maxPages; page++) {
    const params = new URLSearchParams({
      $limit: String(PAGE_SIZE),
      $skip: String(page * PAGE_SIZE),
      accepted_offer_id: 'null',
      'updated_at[$gte]': updatedAfter,
      ...filters,
    });
    const res = await fetch(`${MARKET_URL}?${params}`);
    if (!res.ok) throw new Error(`market API ${res.status} for ${JSON.stringify(filters)}`);
    const payload = await res.json();
    const rows = Array.isArray(payload?.data) ? payload.data : [];
    all.push(...rows);
    if (rows.length < PAGE_SIZE) break;
    await new Promise((resolve) => setTimeout(resolve, throttleMs));
  }
  return all;
}

// A seller's listings are the same item when every roll matches (name, quality, ethereal,
// corruption, sockets and each modifier's values) or when they share an item id. Relists
// then count once, at their lowest price. Different sellers' copies always count, since
// low-variance items (Rainbow Facets, Shako) often roll identically.
export function rollKey(item) {
  if (!item) return '';
  const modifiers = (item.modifiers ?? [])
    .map((m) => `${m?.name}:${JSON.stringify(m?.values ?? [])}`)
    .sort();
  return [
    item.base_code,
    item.name,
    item.quality?.name,
    Boolean(item.is_ethereal),
    Boolean(item.corrupted),
    item.socket_count ?? 0,
    modifiers.join('|'),
  ].join('#');
}

export function dedupeIdenticalRolls(listings, priceOf) {
  const sameItem = keepCheapest(listings, (l) => l?.user_id && l?.item?.id && `${l.user_id}@${l.item.id}`, priceOf);
  return keepCheapest(sameItem, (l) => l?.user_id && l?.item && `${l.user_id}@${rollKey(l.item)}`, priceOf);
}

export function dedupeBySeller(entries, priceOf) {
  return keepCheapest(entries, (e) => e.seller, priceOf);
}

function keepCheapest(rows, keyOf, priceOf) {
  const best = new Map();
  const unpriced = [];
  for (const row of rows) {
    const key = keyOf(row);
    if (!key) { unpriced.push(row); continue; }
    const kept = best.get(key);
    if (!kept) { best.set(key, row); continue; }
    const price = priceOf(row);
    const keptPrice = priceOf(kept);
    if (Number.isFinite(price) && (!Number.isFinite(keptPrice) || price < keptPrice)) best.set(key, row);
  }
  return [...best.values(), ...unpriced];
}

// Tukey's fences: drops prices below Q1 - 1.5 IQR or above Q3 + 1.5 IQR. Currency prices
// cluster on round numbers, so the IQR is held to at least 10% of the median; otherwise a
// tight cluster (most Ohms at exactly 1 HR) would throw out ordinary neighbours like 0.95.
export function withoutOutliers(values) {
  if (values.length < 4) return [...values];
  const sorted = [...values].sort((a, b) => a - b);
  const quartile = (q) => {
    const pos = (sorted.length - 1) * q;
    const low = Math.floor(pos);
    return sorted[low] + (sorted[Math.ceil(pos)] - sorted[low]) * (pos - low);
  };
  const q1 = quartile(0.25);
  const q3 = quartile(0.75);
  const spread = Math.max(q3 - q1, 0.1 * median(sorted));
  return sorted.filter((v) => v >= q1 - 1.5 * spread && v <= q3 + 1.5 * spread);
}

export function median(values) {
  if (!values.length) return undefined;
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

const RUNE_WORDS = {
  el: 'EL', eld: 'ELD', tir: 'TIR', nef: 'NEF', eth: 'ETH', ith: 'ITH', tal: 'TAL', ral: 'RAL',
  ort: 'ORT', thul: 'THUL', amn: 'AMN', sol: 'SOL', shael: 'SHAEL', dol: 'DOL', hel: 'HEL',
  io: 'IO', lum: 'LUM', ko: 'KO', fal: 'FAL', lem: 'LEM', pul: 'PUL', um: 'UM', mal: 'MAL',
  ist: 'IST', gul: 'GUL', vex: 'VEX', ohm: 'OHM', lo: 'LO', sur: 'SUR', ber: 'BER', jah: 'JAH',
  cham: 'CHAM', zod: 'ZOD',
};
const WSS_WORDS = new Set(['wss', 'wsss', 'ws', 'w', 'shard', 'shards']);
const HR_WORDS = new Set(['hr', 'hrs']);
const EACH_WORDS = new Set(['ea', 'each', 'per', 'pc', 'pcs', 'piece', 'apiece']);
const FILLER_WORDS = new Set([
  'break', 'at', 'firm', 'obo', 'bo', 'bin', 'n', 'nb', 'price', 'now', 'for', 'and', 'x', 'only',
  'fg', 'fixed', 'buyout', 'total', 'stack', 'all', 'the', 'is', 'net', 'rune', 'runes', '+', '&',
]);

// One price clause: the text before the first alternative ("or", "/", ",", "|", ";", " - ")
// and before stock notes ("have 4", "got 2", "stock 5"). Parenthesised notes are dropped first. Returns undefined when any word is not a known
// amount, unit or filler, so ambiguous listings never reach the median.
function parseClause(text, runeHR) {
  const clause = text
    .toLowerCase()
    .replace(/\([^)]*\)|\[[^\]]*\]/g, ' ')
    .replace(/(\d),(\d)/g, '$1.$2')
    .split(/\bor\b|[/,|;]|\s-\s|\b(?:have|got|stock|avail)/)[0]
    .replace(/[!?:"'`*~]|\.(?!\d)/g, ' ')
    .replace(/(\d)\s*x\s*(?=[a-z])/g, '$1 ')
    .replace(/(\d)([a-z])/g, '$1 $2')
    .replace(/([a-z])(\d)/g, '$1 $2')
    .trim();
  if (!clause) return undefined;
  const words = clause.split(/\s+/).filter((word) => !FILLER_WORDS.has(word));
  const unitHR = (word) => {
    if (WSS_WORDS.has(word)) return 0.01;
    if (HR_WORDS.has(word)) return 1;
    const alias = RUNE_WORDS[word];
    return alias ? runeHR[alias] : undefined;
  };

  if (words.length === 1 && unitHR(words[0]) !== undefined) {
    const hr = unitHR(words[0]);
    return Number.isFinite(hr) ? { hr, bare: false, each: false } : undefined;
  }

  let total = 0;
  let bareAmount;
  let each = false;
  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    if (EACH_WORDS.has(word)) { each = true; continue; }
    const amount = Number(word);
    if (!Number.isFinite(amount)) return undefined;
    const next = words[i + 1];
    const unit = next === undefined ? undefined : unitHR(next);
    if (next !== undefined && unit === undefined && RUNE_WORDS[next]) return undefined;
    if (unit !== undefined) {
      if (!Number.isFinite(unit)) return undefined;
      total += amount * unit;
      i++;
    } else {
      if (bareAmount !== undefined || total > 0) return undefined;
      bareAmount = amount;
    }
  }
  if (bareAmount !== undefined) return total > 0 ? undefined : { hr: bareAmount, bare: true, each };
  return total > 0 ? { hr: total, bare: false, each } : undefined;
}

// HR per unit for a currency listing. A bare number may mean HR or WSS, and a stack's
// price may be for one unit or the whole stack: each reading is tried and the one closest
// to the item's current value wins. Without a current value, ambiguous listings are skipped.
export function currencyPriceHR(listing, { referenceHR, runeHR }) {
  const parsed = parseClause(String(listing?.price ?? ''), runeHR);
  if (!parsed) return undefined;
  const quantity = Math.max(1, Number(listing?.item?.quantity) || 1);
  const amounts = parsed.bare ? [parsed.hr, parsed.hr * 0.01] : [parsed.hr];
  const perUnit = parsed.each || quantity === 1
    ? amounts
    : amounts.flatMap((hr) => [hr, hr / quantity]);
  const candidates = perUnit.filter((hr) => Number.isFinite(hr) && hr > 0);
  if (candidates.length === 1) return candidates[0];
  if (!candidates.length || !(referenceHR > 0)) return undefined;
  const distance = (hr) => Math.abs(Math.log(hr / referenceHR));
  return candidates.reduce((best, hr) => (distance(hr) < distance(best) ? hr : best));
}
