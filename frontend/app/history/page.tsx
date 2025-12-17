'use client'

import { useState, useMemo, useEffect } from 'react'
import { HistoryFilters } from '@/components/history/history-filters'
import { HistoryList } from '@/components/history/history-list'
import { Pagination } from '@/components/history/pagination'
import { sdkClient } from '@/lib/sdk-client'
import { useToast } from '@/hooks/use-toast'
import type { RecentResearch } from '@/lib/types'

const ITEMS_PER_PAGE = 10

export default function HistoryPage() {
  const [allResearch, setAllResearch] = useState<RecentResearch[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDomain, setSelectedDomain] = useState('all')
  const [currentPage, setCurrentPage] = useState(1)
  const { toast } = useToast()

  // Fetch history from backend on mount
  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    setIsLoading(true)
    try {
      const history = await sdkClient.getHistory(100) // Fetch up to 100 items
      setAllResearch(history)
    } catch (error) {
      console.error('Failed to load history:', error)
      toast({
        variant: 'destructive',
        title: 'Failed to load history',
        description: error instanceof Error ? error.message : 'An unexpected error occurred',
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Filter research based on search and domain
  const filteredResearch = useMemo(() => {
    return allResearch.filter((item) => {
      const matchesSearch = item.query
        .toLowerCase()
        .includes(searchQuery.toLowerCase())
      const matchesDomain =
        selectedDomain === 'all' || item.domain === selectedDomain
      return matchesSearch && matchesDomain
    })
  }, [allResearch, searchQuery, selectedDomain])

  // Pagination
  const totalPages = Math.ceil(filteredResearch.length / ITEMS_PER_PAGE)
  const paginatedResearch = filteredResearch.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  )

  // Reset to page 1 when filters change
  const handleSearchChange = (query: string) => {
    setSearchQuery(query)
    setCurrentPage(1)
  }

  const handleDomainChange = (domain: string) => {
    setSelectedDomain(domain)
    setCurrentPage(1)
  }

  const handleDelete = async (id: string) => {
    try {
      await sdkClient.deleteResearch(id)

      // Remove from local state
      setAllResearch((prev) => prev.filter((item) => item.id !== id))

      toast({
        title: 'Research deleted',
        description: 'The research session has been deleted successfully',
      })
    } catch (error) {
      console.error('Failed to delete research:', error)
      toast({
        variant: 'destructive',
        title: 'Failed to delete',
        description: error instanceof Error ? error.message : 'An unexpected error occurred',
      })
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">History</h1>
        <p className="text-muted-foreground">
          View all your past research sessions
        </p>
      </div>

      <HistoryFilters
        onSearchChange={handleSearchChange}
        onDomainChange={handleDomainChange}
      />

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-sm text-muted-foreground">Loading history...</p>
          </div>
        </div>
      ) : filteredResearch.length === 0 ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <p className="text-muted-foreground">
              {searchQuery || selectedDomain !== 'all'
                ? 'No research sessions match your filters'
                : 'No research sessions yet. Start a new research to see it here!'}
            </p>
          </div>
        </div>
      ) : (
        <>
          <HistoryList research={paginatedResearch} onDelete={handleDelete} />

          {totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
            />
          )}
        </>
      )}
    </div>
  )
}
