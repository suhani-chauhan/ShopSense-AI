import { useCallback, useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { Mic, Paperclip, Send } from 'lucide-react'

interface ChatInputProps {
  onSend: (text: string) => void
  onSendImage: (file: File) => void
  disabled?: boolean
}

export function ChatInput({ onSend, onSendImage, disabled }: ChatInputProps) {
  const [value, setValue] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault()
      const trimmed = value.trim()
      if (!trimmed || disabled) return
      onSend(trimmed)
      setValue('')
    },
    [value, disabled, onSend],
  )

  const handleFileChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) onSendImage(file)
      e.target.value = ''
    },
    [onSendImage],
  )

  return (
    <div className="border-t border-zinc-200 bg-white px-6 py-4 dark:border-zinc-800 dark:bg-zinc-900">
      <form
        onSubmit={handleSubmit}
        className="mx-auto flex max-w-3xl items-center gap-2 rounded-full border border-zinc-200 bg-white px-3 py-2 shadow-sm dark:border-zinc-800 dark:bg-zinc-950"
      >
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className="shrink-0 rounded-full p-2 text-zinc-400 transition hover:bg-zinc-100 hover:text-zinc-700 disabled:opacity-50 dark:hover:bg-zinc-800 dark:hover:text-zinc-200"
          aria-label="Attach an image"
        >
          <Paperclip className="h-4 w-4" />
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png"
          className="hidden"
          onChange={handleFileChange}
        />

        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Ask me anything... (e.g., best running shoes under $200)"
          disabled={disabled}
          className="min-w-0 flex-1 bg-transparent text-sm text-zinc-900 focus:outline-none dark:text-zinc-50"
        />

        <button
          type="button"
          disabled
          title="Voice input isn't available yet"
          className="shrink-0 cursor-not-allowed rounded-full p-2 text-zinc-300 dark:text-zinc-600"
          aria-label="Voice input (not available)"
        >
          <Mic className="h-4 w-4" />
        </button>

        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="flex shrink-0 items-center justify-center rounded-full bg-violet-600 p-2 text-white transition hover:bg-violet-700 disabled:opacity-40"
          aria-label="Send"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
      <p className="mt-2 px-2 text-center text-xs text-zinc-400">
        Prices and availability are subject to change. Please check the store for the latest updates.
      </p>
    </div>
  )
}
