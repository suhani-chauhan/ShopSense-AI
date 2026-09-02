import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { listConversations } from '../api/endpoints'
import type { ConversationSummary } from '../api/types'

interface ConversationsContextValue {
  conversations: ConversationSummary[]
  loading: boolean
  refresh: () => Promise<void>
}

const ConversationsContext = createContext<ConversationsContextValue | null>(null)

export function ConversationsProvider({ children }: { children: ReactNode }) {
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    try {
      const data = await listConversations()
      setConversations(data)
    } catch {
      // Backend may not be reachable yet — sidebar just stays empty until the next refresh.
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  return (
    <ConversationsContext.Provider value={{ conversations, loading, refresh }}>
      {children}
    </ConversationsContext.Provider>
  )
}

export function useConversations(): ConversationsContextValue {
  const ctx = useContext(ConversationsContext)
  if (!ctx) throw new Error('useConversations must be used within a ConversationsProvider')
  return ctx
}
