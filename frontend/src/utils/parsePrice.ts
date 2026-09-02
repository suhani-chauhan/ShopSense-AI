// Listing.price is a raw SerpAPI string like "₹2,450" — never guaranteed clean
// (occasionally a range like "₹999 - ₹1,499", or null). Falls back to null
// rather than coercing garbage to 0, so it's excluded from "best price" math
// but still shown as raw text.
export function parsePrice(raw: string | null): number | null {
  if (!raw) return null
  const match = raw.match(/[\d,]+(\.\d+)?/)
  if (!match) return null
  const numeric = Number(match[0].replace(/,/g, ''))
  return Number.isFinite(numeric) ? numeric : null
}
