export interface Product {
  id: number
  name: string
  brand: string
  gender: string
  category: string
  subcategory: string
  price: number
  price_range: string
  description: string
  image_url: string
  product_url: string
  distance: number
}

// Listing.price/old_price are raw SerpAPI strings (e.g. "₹1,299"), not numbers.
export interface Listing {
  store: string | null
  title: string | null
  price: string | null
  old_price: string | null
  rating: number | null
  review_count: number | null
  url: string | null
  image_url: string | null
  delivery: string | null
}

export interface ChatResponse {
  answer: string
  sources: string[]
}

export interface CompareResponse {
  product: Product
  listings: Listing[]
  answer: string
}

export interface ChatImageResponse {
  caption: string
  answer: string
  sources: string[]
}

// Shape varies by which endpoint produced the message: {sources} from /chat,
// {product, listings} from /chat/compare, {caption, sources} from /chat/image.
export interface MessageExtra {
  sources?: string[]
  caption?: string
  product?: Product
  listings?: Listing[]
}

export interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
  extra: MessageExtra | null
}

export interface ConversationSummary {
  id: number
  title: string
  updated_at: string
}

export interface ConversationCreated {
  id: number
  title: string
  created_at: string
}

export interface ConversationDetail extends ConversationSummary {
  created_at: string
  messages: Message[]
}

export interface SavedProduct {
  id: number
  product_id: number
  name: string
  brand: string | null
  price: number | null
  image_url: string | null
  product_url: string | null
  saved_at: string
}

export interface SaveProductRequest {
  product_id: number
  name: string
  brand?: string | null
  price?: number | null
  image_url?: string | null
  product_url?: string | null
}

export interface HealthResponse {
  status: string
  products_loaded: number
}
