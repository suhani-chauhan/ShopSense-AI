import { useEffect, useRef } from 'react'
import type { ChatMessage } from '../../hooks/useChat'
import { MessageBubble } from './MessageBubble'
import { EmptyState } from './EmptyState'
import { Spinner } from '../common/Spinner'

interface ChatPanelProps {
  messages: ChatMessage[]
  conversationId: number | null
  loadingHistory: boolean
  onExampleClick: (text: string) => void
}

export function ChatPanel({ messages, conversationId, loadingHistory, onExampleClick }: ChatPanelProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length])

  if (loadingHistory) {
    return (
      <div className="flex h-full items-center justify-center text-zinc-400">
        <Spinner className="h-6 w-6" />
      </div>
    )
  }

  if (messages.length === 0) {
    return <EmptyState onExampleClick={onExampleClick} />
  }

  return (
    <div className="h-full overflow-y-auto px-6 py-6">
      <div className="mx-auto max-w-3xl space-y-4">
        {messages.map((message, i) => {
          const userQuery = message.role === 'assistant' ? (messages[i - 1]?.content ?? null) : null
          return (
            <MessageBubble
              key={message.id}
              message={message}
              conversationId={conversationId}
              userQuery={userQuery}
            />
          )
        })}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
