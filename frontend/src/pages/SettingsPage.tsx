import { useTheme } from '../context/ThemeContext'

// Intentionally minimal — no backend-driven settings exist yet.
export function SettingsPage() {
  const { theme, toggle } = useTheme()

  return (
    <div className="h-full overflow-y-auto px-6 py-6">
      <div className="mx-auto max-w-xl space-y-4">
        <div className="rounded-2xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
          <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Appearance</h2>
          <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Currently using {theme} mode.</p>
          <button
            type="button"
            onClick={toggle}
            className="mt-3 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-violet-700"
          >
            Switch to {theme === 'dark' ? 'light' : 'dark'} mode
          </button>
        </div>
        <p className="text-center text-xs text-zinc-400">
          More settings are on the way — this page is intentionally minimal for now.
        </p>
      </div>
    </div>
  )
}
