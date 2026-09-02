import { useLocation } from 'react-router-dom'
import { ThemeToggle } from '../common/ThemeToggle'
import { Avatar } from '../common/Avatar'

const PAGE_TITLES: Record<string, string> = {
  '/saved': 'Saved Products',
  '/settings': 'Settings',
  '/about': 'About',
}

export function TopBar() {
  const location = useLocation()
  const title = PAGE_TITLES[location.pathname] ?? 'ShopAssist AI'

  return (
    <header className="flex items-center justify-between border-b border-zinc-200 bg-white px-6 py-3 dark:border-zinc-800 dark:bg-zinc-900">
      <h1 className="text-base font-semibold text-zinc-900 dark:text-zinc-50">{title}</h1>
      <div className="flex items-center gap-3">
        <ThemeToggle />
        <Avatar />
      </div>
    </header>
  )
}
