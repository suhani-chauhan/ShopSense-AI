import { Star } from 'lucide-react'
import type { Listing } from '../../api/types'

export function ProductCard({ listing }: { listing: Listing }) {
  const card = (
    <div className="flex h-full w-48 shrink-0 flex-col rounded-2xl border border-zinc-200 bg-white p-3 shadow-sm transition hover:border-violet-300 hover:shadow-md dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-violet-700">
      {listing.image_url ? (
        <img
          src={listing.image_url}
          alt={listing.title ?? ''}
          className="mb-2 aspect-square w-full rounded-xl bg-zinc-100 object-cover dark:bg-zinc-800"
          onError={(e) => {
            e.currentTarget.style.visibility = 'hidden'
          }}
        />
      ) : (
        <div className="mb-2 aspect-square w-full rounded-xl bg-zinc-100 dark:bg-zinc-800" />
      )}

      <p className="line-clamp-2 min-h-[2.5em] text-xs text-zinc-700 dark:text-zinc-300">
        {listing.title ?? 'Untitled listing'}
      </p>

      <div className="mt-1.5 flex items-baseline gap-1.5">
        <span className="text-sm font-bold text-zinc-900 dark:text-zinc-50">{listing.price ?? 'N/A'}</span>
        {listing.old_price && (
          <span className="text-xs text-zinc-400 line-through">{listing.old_price}</span>
        )}
      </div>

      <span className="mt-0.5 truncate text-xs text-zinc-500 dark:text-zinc-400">
        {listing.store ?? 'Unknown store'}
      </span>

      {listing.rating != null && (
        <span className="mt-0.5 flex items-center gap-1 text-xs text-amber-600 dark:text-amber-400">
          <Star className="h-3 w-3 fill-current" />
          {listing.rating.toFixed(1)}
          {listing.review_count != null && <span className="text-zinc-400">({listing.review_count})</span>}
        </span>
      )}

      {listing.delivery && (
        <span className="mt-0.5 truncate text-[11px] text-zinc-400">{listing.delivery}</span>
      )}
    </div>
  )

  if (!listing.url) return card

  return (
    <a href={listing.url} target="_blank" rel="noopener noreferrer" className="block">
      {card}
    </a>
  )
}
