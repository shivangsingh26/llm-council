'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  CommandDialog,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
} from '@/components/ui/command'
import {
  LayoutDashboard,
  Search,
  History,
  Settings,
  Clock,
} from 'lucide-react'

interface RecentSearch {
  id: string
  query: string
  timestamp: string
}

export function CommandPalette() {
  const [open, setOpen] = useState(false)
  const [recentSearches, setRecentSearches] = useState<RecentSearch[]>([])
  const router = useRouter()

  // Load recent searches from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('recent_searches')
    if (stored) {
      setRecentSearches(JSON.parse(stored))
    }
  }, [])

  // Handle Cmd+K / Ctrl+K
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }

    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [])

  const navigateTo = (path: string) => {
    router.push(path)
    setOpen(false)
  }

  const viewRecentSearch = (searchId: string) => {
    router.push(`/history/${searchId}`)
    setOpen(false)
  }

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

        <CommandGroup heading="Pages">
          <CommandItem onSelect={() => navigateTo('/')}>
            <LayoutDashboard className="mr-2 h-4 w-4" />
            <span>Dashboard</span>
          </CommandItem>
          <CommandItem onSelect={() => navigateTo('/research')}>
            <Search className="mr-2 h-4 w-4" />
            <span>New Research</span>
          </CommandItem>
          <CommandItem onSelect={() => navigateTo('/history')}>
            <History className="mr-2 h-4 w-4" />
            <span>History</span>
          </CommandItem>
          <CommandItem onSelect={() => navigateTo('/settings')}>
            <Settings className="mr-2 h-4 w-4" />
            <span>Settings</span>
          </CommandItem>
        </CommandGroup>

        {recentSearches.length > 0 && (
          <CommandGroup heading="Recent Searches">
            {recentSearches.slice(0, 5).map((search) => (
              <CommandItem
                key={search.id}
                onSelect={() => viewRecentSearch(search.id)}
              >
                <Clock className="mr-2 h-4 w-4" />
                <span>{search.query}</span>
              </CommandItem>
            ))}
          </CommandGroup>
        )}
      </CommandList>
    </CommandDialog>
  )
}
