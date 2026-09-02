import { Bot } from 'lucide-react'

const EXAMPLES = [
  'warm gloves for men under $600',
  'elegant wool cardigan for women',
  'leather handbag under $1000',
  'affordable accessories',
]

interface EmptyStateProps {
  onExampleClick: (text: string) => void
}

export function EmptyState({ onExampleClick }: EmptyStateProps) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-6 px-6 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-violet-100 text-violet-600 dark:bg-violet-950 dark:text-violet-300">
        <Bot className="h-6 w-6" />
      </div>
      <div>
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          Hi! I'm your AI shopping assistant
        </h2>
        <p className="mt-1 max-w-md text-sm text-zinc-500 dark:text-zinc-400">
          Search for any product by text or image and I'll find the best options, compare prices, and
          give you AI advice.
        </p>
      </div>
      <div className="flex flex-wrap justify-center gap-2">
        {EXAMPLES.map((example) => (
          <button
            key={example}
            type="button"
            onClick={() => onExampleClick(example)}
            className="rounded-full border border-zinc-200 bg-white px-3 py-1.5 text-xs text-zinc-600 transition hover:border-violet-300 hover:text-violet-700 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:border-violet-700 dark:hover:text-violet-300"
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  )
}
