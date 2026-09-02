import { ExternalLink, Trash2 } from 'lucide-react'
import { useSavedProducts } from '../hooks/useSavedProducts'
import { Spinner } from '../components/common/Spinner'

export function SavedProductsPage() {
  const { products, loading, remove } = useSavedProducts()

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center text-zinc-400">
        <Spinner className="h-6 w-6" />
      </div>
    )
  }

  if (products.length === 0) {
    return (
      <div className="flex h-full items-center justify-center px-6 text-center text-sm text-zinc-400">
        Nothing saved yet — save a product from a price comparison to see it here.
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto px-6 py-6">
      <div className="mx-auto grid max-w-5xl grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
        {products.map((product) => (
          <div
            key={product.id}
            className="flex flex-col rounded-2xl border border-zinc-200 bg-white p-3 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
          >
            {product.image_url ? (
              <img
                src={product.image_url}
                alt={product.name}
                className="mb-2 aspect-square w-full rounded-xl bg-zinc-100 object-cover dark:bg-zinc-800"
              />
            ) : (
              <div className="mb-2 aspect-square w-full rounded-xl bg-zinc-100 dark:bg-zinc-800" />
            )}
            <p className="line-clamp-2 text-sm text-zinc-800 dark:text-zinc-200">{product.name}</p>
            {product.brand && <p className="text-xs text-zinc-400">{product.brand}</p>}
            {product.price != null && (
              <p className="mt-1 text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                ${product.price.toFixed(2)}
              </p>
            )}
            <div className="mt-2 flex items-center justify-between">
              {product.product_url ? (
                <a
                  href={product.product_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-xs text-violet-600 hover:underline dark:text-violet-400"
                >
                  View <ExternalLink className="h-3 w-3" />
                </a>
              ) : (
                <span />
              )}
              <button
                type="button"
                onClick={() => remove(product.id)}
                className="rounded-lg p-1.5 text-zinc-400 transition hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950/40 dark:hover:text-red-400"
                aria-label={`Remove ${product.name}`}
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
