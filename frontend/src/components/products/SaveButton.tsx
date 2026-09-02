import { useState } from 'react'
import { Bookmark, BookmarkCheck } from 'lucide-react'
import { saveProduct } from '../../api/endpoints'
import type { Product } from '../../api/types'

export function SaveButton({ product }: { product: Product }) {
  const [saved, setSaved] = useState(false)
  const [busy, setBusy] = useState(false)

  const handleClick = async () => {
    if (saved || busy) return
    setBusy(true)
    try {
      await saveProduct({
        product_id: product.id,
        name: product.name,
        brand: product.brand,
        price: product.price,
        image_url: product.image_url,
        product_url: product.product_url,
      })
      setSaved(true)
    } finally {
      setBusy(false)
    }
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={busy}
      className={
        saved
          ? 'flex shrink-0 items-center gap-1.5 rounded-full bg-violet-100 px-3 py-1.5 text-xs font-medium text-violet-700 dark:bg-violet-950 dark:text-violet-300'
          : 'flex shrink-0 items-center gap-1.5 rounded-full border border-zinc-200 px-3 py-1.5 text-xs font-medium text-zinc-600 transition hover:border-violet-300 hover:text-violet-700 disabled:opacity-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:border-violet-700 dark:hover:text-violet-300'
      }
    >
      {saved ? <BookmarkCheck className="h-3.5 w-3.5" /> : <Bookmark className="h-3.5 w-3.5" />}
      {saved ? 'Saved' : 'Save'}
    </button>
  )
}
