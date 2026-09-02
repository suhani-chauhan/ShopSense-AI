import type { Listing } from '../../api/types'
import { ProductCard } from './ProductCard'

export function ProductCarousel({ listings }: { listings: Listing[] }) {
  if (listings.length === 0) return null

  return (
    <div className="scrollbar-thin flex gap-3 overflow-x-auto pb-2">
      {listings.map((listing, i) => (
        <ProductCard key={`${listing.store}-${i}`} listing={listing} />
      ))}
    </div>
  )
}
