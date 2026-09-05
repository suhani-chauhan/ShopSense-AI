import type { Product } from '../../api/types'

// Links directly to the catalog's own product_url — a real merchant page,
// not a Google Shopping intermediate (unlike the live SerpAPI listings).
export function ProductResultCard({ product }: { product: Product }) {
  return (
    <a
      href={product.product_url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex flex-col rounded-xl border border-zinc-200 bg-white p-2 transition hover:border-violet-300 hover:shadow-sm dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-violet-700"
    >
      {product.image_url ? (
        <img
          src={product.image_url}
          alt={product.name}
          className="mb-1.5 aspect-square w-full rounded-lg bg-zinc-100 object-cover dark:bg-zinc-800"
          onError={(e) => {
            e.currentTarget.style.visibility = 'hidden'
          }}
        />
      ) : (
        <div className="mb-1.5 aspect-square w-full rounded-lg bg-zinc-100 dark:bg-zinc-800" />
      )}
      <p className="line-clamp-2 text-xs text-zinc-700 dark:text-zinc-300">{product.name}</p>
      <span className="mt-1 text-sm font-bold text-zinc-900 dark:text-zinc-50">
        ${product.price.toFixed(2)}
      </span>
      <span className="truncate text-[11px] text-zinc-400">{product.brand}</span>
    </a>
  )
}
