import { useCallback } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useChat } from '../hooks/useChat'
import { useConversations } from '../context/ConversationsContext'
import { ChatPanel } from '../components/chat/ChatPanel'
import { ChatInput } from '../components/chat/ChatInput'

export function ChatPage() {
  const { conversationId: conversationIdParam } = useParams()
  const conversationId = conversationIdParam ? Number(conversationIdParam) : null
  const navigate = useNavigate()
  const { refresh } = useConversations()

  const handleConversationCreated = useCallback(
    (id: number) => {
      navigate(`/c/${id}`, { replace: true })
    },
    [navigate],
  )

  const { messages, loadingHistory, sending, send, sendImage } = useChat(
    conversationId,
    handleConversationCreated,
    refresh,
  )

  return (
    <div className="flex h-full flex-col">
      <div className="min-h-0 flex-1">
        <ChatPanel
          messages={messages}
          conversationId={conversationId}
          loadingHistory={loadingHistory}
          onExampleClick={send}
        />
      </div>
      <ChatInput onSend={send} onSendImage={sendImage} disabled={sending} />
    </div>
  )
}
