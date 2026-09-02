import { del, getJSON, postForm, postJSON } from './client'
import type {
  ChatImageResponse,
  ChatResponse,
  CompareResponse,
  ConversationCreated,
  ConversationDetail,
  ConversationSummary,
  HealthResponse,
  Product,
  SaveProductRequest,
  SavedProduct,
} from './types'

export function getHealth() {
  return getJSON<HealthResponse>('/health')
}

export function searchText(query: string, topK = 3) {
  return postJSON<Product[]>('/search/text', { query, top_k: topK })
}

export function chat(query: string, conversationId: number | null) {
  return postJSON<ChatResponse>('/chat', { query, conversation_id: conversationId })
}

export function chatCompare(query: string, conversationId: number | null) {
  return postJSON<CompareResponse>('/chat/compare', { query, conversation_id: conversationId })
}

export function chatImage(file: File, conversationId: number | null) {
  const formData = new FormData()
  formData.append('file', file)
  if (conversationId != null) {
    formData.append('conversation_id', String(conversationId))
  }
  return postForm<ChatImageResponse>('/chat/image', formData)
}

export function createConversation() {
  return postJSON<ConversationCreated>('/conversations', {})
}

export function listConversations() {
  return getJSON<ConversationSummary[]>('/conversations')
}

export function getConversation(id: number) {
  return getJSON<ConversationDetail>(`/conversations/${id}`)
}

export function deleteConversation(id: number) {
  return del<{ deleted: true }>(`/conversations/${id}`)
}

export function saveProduct(payload: SaveProductRequest) {
  return postJSON<SavedProduct>('/saved-products', payload)
}

export function listSavedProducts() {
  return getJSON<SavedProduct[]>('/saved-products')
}

export function deleteSavedProduct(id: number) {
  return del<{ deleted: true }>(`/saved-products/${id}`)
}
