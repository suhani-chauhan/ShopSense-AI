export function AboutPage() {
  return (
    <div className="h-full overflow-y-auto px-6 py-6">
      <div className="mx-auto max-w-xl space-y-4 text-sm text-zinc-600 dark:text-zinc-300">
        <h2 className="text-base font-semibold text-zinc-900 dark:text-zinc-50">About ShopAssist AI</h2>
        <p>
          ShopAssist AI is an AI shopping assistant that searches a fashion catalog by text or image,
          answers questions with a Groq-powered LLM, and compares live prices across marketplaces via
          SerpAPI.
        </p>
        <p>
          Comparing prices uses a limited external quota — please use the "Compare prices" action
          thoughtfully rather than repeatedly.
        </p>
        <ul className="list-disc space-y-1 pl-5">
          <li>FAISS for semantic product search</li>
          <li>BLIP for image captioning</li>
          <li>Groq LLM for conversational answers</li>
          <li>SerpAPI for live multi-store price comparison</li>
        </ul>
      </div>
    </div>
  )
}
