import { Bot } from 'lucide-react'
import type { ChatMessage } from '../../hooks/useChat'
import type { Facet } from '../../api/types'
import { MarkdownContent } from './MarkdownContent'
import { CompareAction } from './CompareAction'
import { Spinner } from '../common/Spinner'
import { ErrorBanner } from '../common/ErrorBanner'
import { ProductResultsGrid } from '../products/ProductResultsGrid'

interface MessageBubbleProps {
  message: ChatMessage
  conversationId: number | null
  userQuery: string | null
  onFacetClick?: (facet: Facet) => void
}

export function MessageBubble({ message, conversationId, userQuery, onFacetClick }: MessageBubbleProps) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-lg rounded-2xl rounded-br-sm bg-violet-600 px-4 py-2.5 text-sm text-white">
          {message.content}
        </div>
      </div>
    )
  }

  // Prefer the backend-recorded query that actually produced this answer —
  // it may be combined with an earlier turn if this resolved a clarifying
  // question, so it's not always the same as the previous message's raw
  // content. `userQuery` (the previous message's content) is only a
  // fallback for messages persisted before this field existed.
  const compareQuery = message.extra?.effective_query ?? message.extra?.caption ?? userQuery
  const hasPrecomputedCompare = Boolean(message.extra?.product && message.extra?.listings)
  const isClarifying = Boolean(message.extra?.clarifying)
  const facets = message.extra?.facets ?? []

  return (
    <div className="flex items-start gap-2.5">
      <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-violet-100 text-violet-600 dark:bg-violet-950 dark:text-violet-300">
        <Bot className="h-4 w-4" />
      </div>
      <div className="max-w-3xl min-w-0 flex-1 rounded-2xl rounded-bl-sm border border-zinc-200 bg-white px-4 py-3 dark:border-zinc-800 dark:bg-zinc-900">
        {message.pending ? (
          <div className="flex items-center gap-2 text-sm text-zinc-400">
            <Spinner />
            Thinking…
          </div>
        ) : message.error ? (
          <ErrorBanner message={message.error} />
        ) : (
          <>
            {message.extra?.caption && (
              <p className="mb-1.5 text-xs text-zinc-400">I see: {message.extra.caption}</p>
            )}
            <MarkdownContent content={message.content} />
            {facets.length > 0 && onFacetClick && (
              <div className="mt-3 flex flex-wrap gap-1.5">
                {facets.map((facet) => (
                  <button
                    key={facet.label}
                    type="button"
                    onClick={() => onFacetClick(facet)}
                    className="rounded-full border border-zinc-300 bg-zinc-50 px-2.5 py-1 text-xs font-medium text-zinc-700 transition hover:border-violet-400 hover:bg-violet-50 hover:text-violet-700 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:border-violet-600 dark:hover:bg-violet-950 dark:hover:text-violet-300"
                  >
                    {facet.label} <span className="text-zinc-400">({facet.count})</span>
                  </button>
                ))}
              </div>
            )}
            {!isClarifying && (
              <>
                {message.extra?.products && message.extra.products.length > 0 ? (
                  <ProductResultsGrid products={message.extra.products} />
                ) : (
                  message.extra?.sources &&
                  message.extra.sources.length > 0 &&
                  !hasPrecomputedCompare && (
                    <p className="mt-2 text-xs text-zinc-400">Sources: {message.extra.sources.join(', ')}</p>
                  )
                )}
                {hasPrecomputedCompare ? (
                  <CompareAction
                    conversationId={conversationId ?? -1}
                    userQuery={compareQuery ?? ''}
                    initialResult={{
                      product: message.extra!.product!,
                      listings: message.extra!.listings!,
                      answer: message.content,
                    }}
                  />
                ) : (
                  conversationId != null &&
                  compareQuery && <CompareAction conversationId={conversationId} userQuery={compareQuery} />
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  )
}
