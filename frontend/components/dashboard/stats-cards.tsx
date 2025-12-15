import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity, Zap, DollarSign, Users } from 'lucide-react'

interface StatsCardsProps {
  stats: {
    total_research: number
    total_queries: number
    total_tokens: number
    total_cost: number
    active_agents: number
  }
}

export function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            Total Research Sessions
          </CardTitle>
          <Activity className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.total_research}</div>
          <p className="text-xs text-muted-foreground">
            All-time research queries
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.active_agents}</div>
          <p className="text-xs text-muted-foreground">
            GPT-4o, Gemini, DeepSeek
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Tokens</CardTitle>
          <Zap className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {stats.total_tokens?.toLocaleString() || 0}
          </div>
          <p className="text-xs text-muted-foreground">Across all queries</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            ${stats.total_cost?.toFixed(2) || '0.00'}
          </div>
          <p className="text-xs text-muted-foreground">API usage cost</p>
        </CardContent>
      </Card>
    </div>
  )
}
