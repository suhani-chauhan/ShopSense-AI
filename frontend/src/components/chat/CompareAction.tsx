import { useState } from 'react'
import { Scale } from 'lucide-react'
import { chatCompare } from '../../api/endpoints'
import type { CompareResponse } from '../../api/types'
import { Spinner } from '../common/Spinner'
import { ErrorBanner } from '../common/ErrorBanner'
import { ProductCarousel } from '../products/ProductCarousel'
import { PriceComparisonTable } from '../products/PriceComparisonTable'
import { AIAdvicePanel } from '../products/AIAdvicePanel'
import { SaveButton } from '../products/SaveButton'

interface CompareActionProps {
  conversationId: number
  userQuery: string
  initialResult?: CompareResponse
}

export function CompareAction({ conversationId, userQuery, initialResult }: CompareActionProps) {
  const [result, setResult] = useState<CompareResponse | null>(initialResult ?? null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleCompare = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await chatCompare(userQuery, conversationId)
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  if (!result) {
    return (
      <div className="mt-2">
        <button
          type="button"
          onClick={handleCompare}
          disabled={loading}
          className="flex items-center gap-1.5 rounded-full border border-zinc-200 px-3 py-1.5 text-xs font-medium text-zinc-600 transition hover:border-violet-300 hover:text-violet-700 disabled:opacity-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:border-violet-700 dark:hover:text-violet-300"
        >
          {loading ? <Spinner className="h-3.5 w-3.5" /> : <Scale className="h-3.5 w-3.5" />}
          {loading ? 'Comparing prices…' : 'Compare prices'}
        </button>
        {error && (
          <div className="mt-2">
            <ErrorBanner message={error} />
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="mt-3 space-y-3">
      <div className="flex items-center justify-between gap-2">
        <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">{result.product.name}</h3>
        <SaveButton product={result.product} />
      </div>
      <ProductCarousel listings={result.listings} />
      {result.listings.length > 0 && <PriceComparisonTable listings={result.listings} />}
      <AIAdvicePanel answer={result.answer} />
    </div>
  )
}
