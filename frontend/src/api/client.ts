const DEFAULT_BASE_URL = 'http://127.0.0.1:8000'
const REQUEST_TIMEOUT_MS = 60_000

export const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) || DEFAULT_BASE_URL

export const BACKEND_DOWN_MESSAGE =
  'Backend not running — start it with: uvicorn backend.main:app --reload'

export class ApiRequestError extends Error {
  status: number
  detail: string

  constructor(status: number, detail: string) {
    super(detail)
    this.name = 'ApiRequestError'
    this.status = status
    this.detail = detail
  }
}

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...init, signal: controller.signal })
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new Error('Request timed out — the server took too long to respond.')
    }
    throw new Error(BACKEND_DOWN_MESSAGE)
  } finally {
    clearTimeout(timeoutId)
  }

  if (!response.ok) {
    let detail = response.statusText
    try {
      const body = (await response.json()) as { detail?: string }
      if (body?.detail) detail = body.detail
    } catch {
      // Response body wasn't JSON — fall back to statusText.
    }
    throw new ApiRequestError(response.status, detail)
  }

  return response.json() as Promise<T>
}

export function getJSON<T>(path: string): Promise<T> {
  return request<T>(path, { method: 'GET' })
}

export function postJSON<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body ?? {}),
  })
}

export function postForm<T>(path: string, formData: FormData): Promise<T> {
  return request<T>(path, { method: 'POST', body: formData })
}

export function del<T>(path: string): Promise<T> {
  return request<T>(path, { method: 'DELETE' })
}
