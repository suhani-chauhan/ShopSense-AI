import type { ComponentPropsWithoutRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

// Wide markdown tables (common in the LLM's product comparisons) would
// otherwise overflow the chat bubble's fixed width — scope the scroll to
// just the table itself, never the page.
function Table(props: ComponentPropsWithoutRef<'table'>) {
  return (
    <div className="overflow-x-auto">
      <table {...props} />
    </div>
  )
}

export function MarkdownContent({ content }: { content: string }) {
  return (
    <div className="prose prose-sm dark:prose-invert prose-p:my-1.5 prose-headings:my-2 prose-table:my-2 prose-a:text-violet-600 dark:prose-a:text-violet-400 max-w-none">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={{ table: Table }}>
        {content}
      </ReactMarkdown>
    </div>
  )
}
