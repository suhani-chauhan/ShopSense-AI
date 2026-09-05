import { useState } from 'react'
import type { Product } from '../../api/types'
import { ProductResultCard } from './ProductResultCard'

const INITIAL_VISIBLE = 4

function groupByCategory(products: Product[]): Map<string, Product[]> {
  const groups = new Map<string, Product[]>()
  for (const product of products) {
    const key = product.category || 'Other'
    const existing = groups.get(key)
    if (existing) {
      existing.push(product)
    } else {
      groups.set(key, [product])
    }
  }
  return groups
}

export function ProductResultsGrid({ products }: { products: Product[] }) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  if (products.length === 0) return null

  const groups = groupByCategory(products)

  const toggle = (category: string) => {
    setExpanded((prev) => {
      const next = new Set(prev)
      if (next.has(category)) {
        next.delete(category)
      } else {
        next.add(category)
      }
      return next
    })
  }

  return (
    <div className="mt-3 space-y-4">
      {Array.from(groups.entries()).map(([category, items]) => {
        const isExpanded = expanded.has(category)
        const visibleItems = isExpanded ? items : items.slice(0, INITIAL_VISIBLE)

        return (
          <div key={category}>
            <h4 className="mb-2 text-xs font-semibold tracking-wide text-zinc-400 uppercase">
              {category}
            </h4>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
              {visibleItems.map((product) => (
                <ProductResultCard key={product.id} product={product} />
              ))}
            </div>
            {items.length > INITIAL_VISIBLE && (
              <button
                type="button"
                onClick={() => toggle(category)}
                className="mt-2 text-xs font-medium text-violet-600 hover:underline dark:text-violet-400"
              >
                {isExpanded ? 'Show less' : `Show all ${items.length} in ${category}`}
              </button>
            )}
          </div>
        )
      })}
    </div>
  )
}
