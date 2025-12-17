'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  CheckCircle,
  XCircle,
  Eye,
  Trash2,
  AlertCircle,
} from 'lucide-react'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { toast } from 'sonner'
import type { RecentResearch } from '@/lib/types'

interface HistoryListProps {
  research: RecentResearch[]
  onDelete: (id: string) => void
}

export function HistoryList({ research, onDelete }: HistoryListProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const handleDelete = async (id: string) => {
    setDeletingId(id)
    try {
      // TODO: Replace with actual API call in Phase 4
      await new Promise((resolve) => setTimeout(resolve, 500))
      onDelete(id)
      toast.success('Research deleted successfully')
    } catch (error) {
      toast.error('Failed to delete research')
    } finally {
      setDeletingId(null)
    }
  }

  if (research.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-lg font-medium mb-2">No research found</p>
          <p className="text-sm text-muted-foreground mb-4">
            Try adjusting your filters or start a new research
          </p>
          <Button asChild>
            <Link href="/research">Start Research</Link>
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {research.map((item) => (
        <Card key={item.id} className="hover:bg-accent/50 transition-colors">
          <CardContent className="p-6">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-lg mb-2 truncate">
                  {item.query}
                </h3>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant="outline">{item.domain}</Badge>
                  <span className="text-xs text-muted-foreground">
                    {new Date(item.timestamp).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                  <div className="flex items-center gap-1">
                    {item.successful_agents === item.total_agents ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <XCircle className="h-4 w-4 text-yellow-500" />
                    )}
                    <span className="text-xs text-muted-foreground">
                      {item.successful_agents}/{item.total_agents} agents
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" asChild>
                  <Link href={`/history/${item.id}`}>
                    <Eye className="h-4 w-4 mr-2" />
                    View
                  </Link>
                </Button>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={deletingId === item.id}
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Delete Research</AlertDialogTitle>
                      <AlertDialogDescription>
                        Are you sure you want to delete this research? This
                        action cannot be undone.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction
                        onClick={() => handleDelete(item.id)}
                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                      >
                        Delete
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
