import type { Listing } from '../../api/types'
import { parsePrice } from '../../utils/parsePrice'

export function PriceComparisonTable({ listings }: { listings: Listing[] }) {
  if (listings.length === 0) return null

  const parsedPrices = listings.map((l) => parsePrice(l.price))
  const lowestPrice = parsedPrices.reduce<number | null>((min, p) => {
    if (p == null) return min
    if (min == null || p < min) return p
    return min
  }, null)

  return (
    <div className="overflow-x-auto rounded-2xl border border-zinc-200 dark:border-zinc-800">
      <table className="w-full text-left text-sm">
        <thead className="bg-zinc-50 text-xs text-zinc-500 dark:bg-zinc-900 dark:text-zinc-400">
          <tr>
            <th className="px-3 py-2 font-medium">Store</th>
            <th className="px-3 py-2 font-medium">Price</th>
            <th className="px-3 py-2 font-medium">Rating</th>
            <th className="px-3 py-2 font-medium">Delivery</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
          {listings.map((listing, i) => {
            const price = parsedPrices[i]
            const isBest = price != null && lowestPrice != null && price === lowestPrice
            return (
              <tr key={`${listing.store}-${i}`} className={isBest ? 'bg-emerald-50 dark:bg-emerald-950/30' : undefined}>
                <td className="px-3 py-2 text-zinc-700 dark:text-zinc-300">{listing.store ?? 'Unknown'}</td>
                <td
                  className={
                    isBest
                      ? 'px-3 py-2 font-semibold text-emerald-700 dark:text-emerald-400'
                      : 'px-3 py-2 text-zinc-900 dark:text-zinc-50'
                  }
                >
                  {listing.price ?? 'N/A'}
                  {isBest && (
                    <span className="ml-1.5 rounded-full bg-emerald-100 px-1.5 py-0.5 text-[10px] font-medium text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300">
                      Best Price
                    </span>
                  )}
                </td>
                <td className="px-3 py-2 text-zinc-600 dark:text-zinc-400">
                  {listing.rating != null ? `${listing.rating.toFixed(1)}★ (${listing.review_count ?? 0})` : '—'}
                </td>
                <td className="px-3 py-2 text-zinc-500 dark:text-zinc-400">{listing.delivery ?? '—'}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
