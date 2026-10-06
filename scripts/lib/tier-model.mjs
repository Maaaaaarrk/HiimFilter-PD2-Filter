// Shared model of the unique/set star-tier aliases in
// builderfilter/02-alias/05-unid-unique-set-stars[ALL].filter.
//
// uniqueTier() / setTier() mirror the first-match-wins rule order of
// builderfilter/06-unidfiltering/20-Unid_UniquesSet_Tiers*. Keep them in sync:
// the unique order is NOT monotonic (an ETH copy in 4_STAR_NO_ETH_UNIQUE hits the
// 3★ rule before the 4_STAR_ETH_UNIQUE rule is reached), so anything that edits
// the aliases must re-evaluate with this model rather than assume.

export const ALIAS_FILE = 'builderfilter/02-alias/05-unid-unique-set-stars[ALL].filter';

export const UNIQUE_VALUE_TIERS = [
  '4_STAR_UNIQUE',
  '3_STAR_UNIQUE',
  '2_STAR_UNIQUE',
  '1_STAR_UNIQUE',
  '0_STAR_UNIQUE',
  'NO_STAR_UNIQUE',
];
export const UNIQUE_ETH_TIERS = ['4_STAR_ETH_UNIQUE', '4_STAR_NO_ETH_UNIQUE', '3_STAR_NO_ETH_UNIQUE'];
export const UNIQUE_TIERS = [...UNIQUE_VALUE_TIERS, ...UNIQUE_ETH_TIERS];
export const SET_TIERS = ['4_STAR_SET', '3_STAR_SET', '2_STAR_SET', '1_STAR_SET', '0_STAR_SET'];

// Rank of a value tier: higher is better. NO_STAR = 0, unlisted = -1.
const RANK = {
  '4_STAR_UNIQUE': 5, '3_STAR_UNIQUE': 4, '2_STAR_UNIQUE': 3, '1_STAR_UNIQUE': 2, '0_STAR_UNIQUE': 1, NO_STAR_UNIQUE: 0,
  '4_STAR_SET': 4, '3_STAR_SET': 3, '2_STAR_SET': 2, '1_STAR_SET': 1, '0_STAR_SET': 0,
};
export const rank = (tier) => (tier in RANK ? RANK[tier] : -1);
export const stars = (tier) => (tier ? (tier.startsWith('NO_') ? 'no' : `${tier[0]}★`) : '—');

// Effective value tier of a unique base for an ETH / non-ETH copy.
// `has(alias)` answers whether the base code is listed in that alias.
export function uniqueTier(has, isEth) {
  if (has('4_STAR_UNIQUE')) return '4_STAR_UNIQUE';
  if (has('4_STAR_NO_ETH_UNIQUE')) return isEth ? '3_STAR_UNIQUE' : '4_STAR_UNIQUE';
  if (isEth && has('4_STAR_ETH_UNIQUE')) return '4_STAR_UNIQUE';
  if (has('3_STAR_UNIQUE')) return '3_STAR_UNIQUE';
  if (has('3_STAR_NO_ETH_UNIQUE')) return isEth ? '2_STAR_UNIQUE' : '3_STAR_UNIQUE';
  for (const t of ['2_STAR_UNIQUE', '1_STAR_UNIQUE', '0_STAR_UNIQUE', 'NO_STAR_UNIQUE']) if (has(t)) return t;
  return null;
}

export function setTier(has) {
  for (const t of SET_TIERS) if (has(t)) return t;
  return null;
}

// Parse every `Alias[TIER]: (a OR b OR c)` line into TIER -> [codes] (order kept).
export function parseTierAliases(text, tiers) {
  const lists = new Map();
  for (const tier of tiers) {
    const m = text.match(new RegExp(`^Alias\\[${tier}\\]:\\s*\\(([^)]*)\\)`, 'm'));
    if (!m) throw new Error(`alias ${tier} not found in ${ALIAS_FILE}`);
    lists.set(tier, m[1].split(/\s+OR\s+/i).map((s) => s.trim()).filter(Boolean));
  }
  return lists;
}
