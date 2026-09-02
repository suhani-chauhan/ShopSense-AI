import { Bot } from 'lucide-react'
import type { ChatMessage } from '../../hooks/useChat'
import { MarkdownContent } from './MarkdownContent'
import { CompareAction } from './CompareAction'
import { Spinner } from '../common/Spinner'
import { ErrorBanner } from '../common/ErrorBanner'

interface MessageBubbleProps {
  message: ChatMessage
  conversationId: number | null
  userQuery: string | null
}

export function MessageBubble({ message, conversationId, userQuery }: MessageBubbleProps) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-lg rounded-2xl rounded-br-sm bg-violet-600 px-4 py-2.5 text-sm text-white">
          {message.content}
        </div>
      </div>
    )
  }

  // For image-search-derived messages, the raw user message is just a
  // filename placeholder — the BLIP caption is the real semantic query.
  const compareQuery = message.extra?.caption ?? userQuery
  const hasPrecomputedCompare = Boolean(message.extra?.product && message.extra?.listings)

  return (
    <div className="flex items-start gap-2.5">
      <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-violet-100 text-violet-600 dark:bg-violet-950 dark:text-violet-300">
        <Bot className="h-4 w-4" />
      </div>
      <div className="max-w-2xl min-w-0 flex-1 rounded-2xl rounded-bl-sm border border-zinc-200 bg-white px-4 py-3 dark:border-zinc-800 dark:bg-zinc-900">
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
            {message.extra?.sources && message.extra.sources.length > 0 && !hasPrecomputedCompare && (
              <p className="mt-2 text-xs text-zinc-400">Sources: {message.extra.sources.join(', ')}</p>
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
      </div>
    </div>
  )
}
