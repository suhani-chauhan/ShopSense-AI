import { useCallback, useState, type MouseEvent } from 'react'
import { Link, NavLink, useNavigate, useParams } from 'react-router-dom'
import {
  Bookmark,
  Info,
  MessageSquarePlus,
  Settings,
  ShoppingBag,
  Sparkles,
  Trash2,
  type LucideIcon,
} from 'lucide-react'
import clsx from 'clsx'
import { useConversations } from '../../context/ConversationsContext'
import { createConversation, deleteConversation } from '../../api/endpoints'
import { relativeTime } from '../../utils/relativeTime'

function SidebarNavLink({ to, icon: Icon, label }: { to: string; icon: LucideIcon; label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        clsx(
          'flex items-center gap-2.5 rounded-xl px-3 py-2 text-sm transition',
          isActive
            ? 'bg-violet-50 text-violet-700 dark:bg-violet-950/40 dark:text-violet-300'
            : 'text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800',
        )
      }
    >
      <Icon className="h-4 w-4" />
      {label}
    </NavLink>
  )
}

export function Sidebar() {
  const { conversations, refresh } = useConversations()
  const navigate = useNavigate()
  const { conversationId } = useParams()
  const activeId = conversationId ? Number(conversationId) : null
  const [deletingId, setDeletingId] = useState<number | null>(null)

  const handleNewChat = useCallback(async () => {
    const created = await createConversation()
    await refresh()
    navigate(`/c/${created.id}`)
  }, [navigate, refresh])

  const handleDelete = useCallback(
    async (e: MouseEvent, id: number) => {
      e.preventDefault()
      e.stopPropagation()
      setDeletingId(id)
      try {
        await deleteConversation(id)
        await refresh()
        if (activeId === id) navigate('/')
      } finally {
        setDeletingId(null)
      }
    },
    [activeId, navigate, refresh],
  )

  return (
    <aside className="flex w-72 shrink-0 flex-col border-r border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center gap-2 px-4 py-4">
        <ShoppingBag className="h-6 w-6 text-violet-600" />
        <span className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">ShopAssist AI</span>
      </div>

      <div className="px-4">
        <button
          type="button"
          onClick={handleNewChat}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-violet-700"
        >
          <MessageSquarePlus className="h-4 w-4" />
          New Chat
        </button>
      </div>

      <div className="mt-6 min-h-0 flex-1 overflow-y-auto px-4">
        <h2 className="mb-2 px-1 text-xs font-semibold tracking-wide text-zinc-400 uppercase">
          Recent Chats
        </h2>
        <ul className="space-y-1">
          {conversations.map((c) => (
            <li key={c.id}>
              <Link
                to={`/c/${c.id}`}
                className={clsx(
                  'group flex items-center justify-between gap-2 rounded-xl px-3 py-2 text-sm transition',
                  c.id === activeId
                    ? 'bg-violet-50 text-violet-700 dark:bg-violet-950/40 dark:text-violet-300'
                    : 'text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800',
                )}
              >
                <span className="min-w-0 flex-1">
                  <span className="block truncate">{c.title}</span>
                  <span className="block truncate text-xs text-zinc-400">{relativeTime(c.updated_at)}</span>
                </span>
                <button
                  type="button"
                  onClick={(e) => handleDelete(e, c.id)}
                  disabled={deletingId === c.id}
                  className="shrink-0 rounded-lg p-1 text-zinc-400 opacity-0 transition hover:bg-zinc-200 hover:text-zinc-700 group-hover:opacity-100 dark:hover:bg-zinc-700 dark:hover:text-zinc-200"
                  aria-label={`Delete ${c.title}`}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </Link>
            </li>
          ))}
          {conversations.length === 0 && (
            <li className="px-3 py-2 text-sm text-zinc-400">No chats yet</li>
          )}
        </ul>
      </div>

      <div className="mx-4 mb-4 rounded-xl border border-violet-100 bg-violet-50 p-3 dark:border-violet-900 dark:bg-violet-950/40">
        <div className="mb-1 flex items-center gap-1.5 text-sm font-medium text-violet-700 dark:text-violet-300">
          <Sparkles className="h-4 w-4" />
          AI Shopping, Smarter Choices
        </div>
        <p className="text-xs text-violet-600/80 dark:text-violet-300/70">
          Get product recommendations, compare prices, read reviews, and get AI advice.
        </p>
      </div>

      <nav className="space-y-1 border-t border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <SidebarNavLink to="/settings" icon={Settings} label="Settings" />
        <SidebarNavLink to="/saved" icon={Bookmark} label="Saved Products" />
        <SidebarNavLink to="/about" icon={Info} label="About" />
      </nav>
    </aside>
  )
}
