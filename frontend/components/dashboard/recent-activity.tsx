import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ArrowRight, CheckCircle, XCircle } from 'lucide-react'
import type { RecentResearch } from '@/lib/types'

interface RecentActivityProps {
  recentResearch: RecentResearch[]
}

export function RecentActivity({ recentResearch }: RecentActivityProps) {
  if (recentResearch.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <p className="text-sm text-muted-foreground mb-4">
              No research sessions yet
            </p>
            <Button asChild>
              <Link href="/research">Start Your First Research</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Recent Activity</CardTitle>
        <Button variant="ghost" size="sm" asChild>
          <Link href="/history">
            View All <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {recentResearch.map((research) => (
            <Link
              key={research.id}
              href={`/history/${research.id}`}
              className="flex items-start justify-between p-3 rounded-lg border bg-card/50 hover:bg-accent transition-colors"
            >
              <div className="flex-1">
                <p className="font-medium line-clamp-1">{research.query}</p>
                <div className="flex items-center gap-2 mt-1">
                  <Badge variant="outline" className="text-xs">
                    {research.domain}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {new Date(research.timestamp).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2 ml-4">
                {research.successful_agents === research.total_agents ? (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                ) : (
                  <XCircle className="h-4 w-4 text-yellow-500" />
                )}
                <span className="text-xs text-muted-foreground">
                  {research.successful_agents}/{research.total_agents}
                </span>
              </div>
            </Link>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
