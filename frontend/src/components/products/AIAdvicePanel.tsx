import { Sparkles } from 'lucide-react'
import { MarkdownContent } from '../chat/MarkdownContent'

export function AIAdvicePanel({ answer }: { answer: string }) {
  return (
    <div className="rounded-2xl border border-violet-100 bg-violet-50 p-4 dark:border-violet-900 dark:bg-violet-950/40">
      <div className="mb-1.5 flex items-center gap-1.5 text-sm font-semibold text-violet-700 dark:text-violet-300">
        <Sparkles className="h-4 w-4" />
        AI Advice
      </div>
      <MarkdownContent content={answer} />
    </div>
  )
}
