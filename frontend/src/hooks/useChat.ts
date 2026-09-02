import { useCallback, useEffect, useRef, useState } from 'react'
import { chat, chatImage, createConversation, getConversation } from '../api/endpoints'
import type { Message } from '../api/types'

export interface ChatMessage extends Omit<Message, 'id'> {
  id: number | string
  pending?: boolean
  error?: string
}

interface UseChatResult {
  messages: ChatMessage[]
  loadingHistory: boolean
  sending: boolean
  send: (query: string) => Promise<void>
  sendImage: (file: File) => Promise<void>
}

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : 'Something went wrong. Please try again.'
}

export function useChat(
  conversationId: number | null,
  onConversationCreated: (id: number) => void,
  onExchangeComplete: () => void,
): UseChatResult {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [sending, setSending] = useState(false)

  // Guards against re-fetching history for a conversation we just created
  // ourselves mid-send — the optimistic local state already reflects it.
  const justCreatedIdRef = useRef<number | null>(null)

  useEffect(() => {
    if (conversationId != null && justCreatedIdRef.current === conversationId) {
      justCreatedIdRef.current = null
      return
    }

    if (conversationId == null) {
      setMessages([])
      return
    }

    let cancelled = false
    setLoadingHistory(true)
    getConversation(conversationId)
      .then((detail) => {
        if (!cancelled) setMessages(detail.messages)
      })
      .catch(() => {
        if (!cancelled) setMessages([])
      })
      .finally(() => {
        if (!cancelled) setLoadingHistory(false)
      })

    return () => {
      cancelled = true
    }
  }, [conversationId])

  const ensureConversation = useCallback(async (): Promise<number> => {
    if (conversationId != null) return conversationId
    const created = await createConversation()
    justCreatedIdRef.current = created.id
    onConversationCreated(created.id)
    return created.id
  }, [conversationId, onConversationCreated])

  const runExchange = useCallback(
    async (userContent: string, call: (id: number) => Promise<Pick<ChatMessage, 'content' | 'extra'>>) => {
      const userMessage: ChatMessage = {
        id: `local-user-${Date.now()}`,
        role: 'user',
        content: userContent,
        created_at: new Date().toISOString(),
        extra: null,
      }
      const pendingId = `local-assistant-${Date.now()}`
      const pendingMessage: ChatMessage = {
        id: pendingId,
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
        extra: null,
        pending: true,
      }

      setMessages((prev) => [...prev, userMessage, pendingMessage])
      setSending(true)

      try {
        const id = await ensureConversation()
        const result = await call(id)
        setMessages((prev) =>
          prev.map((m) =>
            m.id === pendingId ? { ...m, ...result, pending: false } : m,
          ),
        )
        onExchangeComplete()
      } catch (err) {
        setMessages((prev) =>
          prev.map((m) => (m.id === pendingId ? { ...m, pending: false, error: errorMessage(err) } : m)),
        )
      } finally {
        setSending(false)
      }
    },
    [ensureConversation, onExchangeComplete],
  )

  const send = useCallback(
    async (query: string) => {
      const trimmed = query.trim()
      if (!trimmed) return
      await runExchange(trimmed, async (id) => {
        const result = await chat(trimmed, id)
        return { content: result.answer, extra: { sources: result.sources } }
      })
    },
    [runExchange],
  )

  const sendImage = useCallback(
    async (file: File) => {
      await runExchange(`[Image] ${file.name}`, async (id) => {
        const result = await chatImage(file, id)
        return {
          content: result.answer,
          extra: { caption: result.caption, sources: result.sources },
        }
      })
    },
    [runExchange],
  )

  return { messages, loadingHistory, sending, send, sendImage }
}
