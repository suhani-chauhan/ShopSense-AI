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
// `url` is a Google Shopping results page, not the merchant — page_token
// lets the frontend resolve the real merchant link on demand (on click).
export interface Listing {
  store: string | null
  title: string | null
  price: string | null
  old_price: string | null
  rating: number | null
  review_count: number | null
  url: string | null
  page_token: string | null
  image_url: string | null
  delivery: string | null
}

// A real narrow-down chip computed from the returned result set. `count` is
// an exact count of `products`; `filter` is applied server-side on a
// follow-up turn (e.g. { subcategory: "Knitwear" }).
export interface Facet {
  label: string
  count: number
  filter: Record<string, string>
}

export interface ChatResponse {
  answer: string
  sources: string[]
  products: Product[]
  facets?: Facet[]
  clarifying?: boolean
  // The query that actually produced this answer — may be the raw query
  // combined with an earlier turn if this resolved a clarifying question.
  // Use this (not the previous message's raw content) when re-issuing the
  // same search for a "Compare prices" click.
  effective_query?: string
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
  products: Product[]
  facets?: Facet[]
  clarifying?: boolean
  effective_query?: string
}

// Shape varies by which endpoint produced the message: {sources, products}
// from /chat, {product, listings} from /chat/compare, {caption, sources,
// products} from /chat/image.
export interface MessageExtra {
  sources?: string[]
  caption?: string
  products?: Product[]
  product?: Product
  listings?: Listing[]
  facets?: Facet[]
  clarifying?: boolean
  effective_query?: string
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
