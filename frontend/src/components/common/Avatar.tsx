import { User } from 'lucide-react'

// No auth system exists yet — this is a static placeholder, not a real identity.
export function Avatar() {
  return (
    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-violet-100 text-violet-600 dark:bg-violet-950 dark:text-violet-300">
      <User className="h-4 w-4" />
    </div>
  )
}
