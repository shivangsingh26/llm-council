import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { StatsCards } from '@/components/dashboard/stats-cards'
import { RecentActivity } from '@/components/dashboard/recent-activity'
import { Plus } from 'lucide-react'
import { sdkClient } from '@/lib/sdk-client'

// Fetch real data from backend API
async function getStats() {
  try {
    return await sdkClient.getStats()
  } catch (error) {
    console.error('Failed to fetch stats:', error)
    return {
      total_research: 0,
      total_queries: 0,
      total_tokens: 0,
      total_cost: 0,
      active_agents: 3,
    }
  }
}

async function getRecentResearch() {
  try {
    return await sdkClient.getHistory(5)
  } catch (error) {
    console.error('Failed to fetch recent research:', error)
    return []
  }
}

export default async function DashboardPage() {
  const stats = await getStats()
  const recentResearch = await getRecentResearch()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to LLM Council - Your multi-model research platform
          </p>
        </div>
        <Button asChild size="lg">
          <Link href="/research">
            <Plus className="mr-2 h-4 w-4" />
            New Research
          </Link>
        </Button>
      </div>

      <StatsCards stats={stats} />

      <div className="grid gap-6 lg:grid-cols-2">
        <RecentActivity recentResearch={recentResearch} />

        <div className="space-y-4">
          <div className="rounded-lg border bg-card p-6">
            <h3 className="font-semibold mb-3">Quick Start</h3>
            <div className="space-y-2 text-sm text-muted-foreground">
              <p>1. Click "New Research" to start a query</p>
              <p>2. Select your research domain</p>
              <p>3. Enter your question</p>
              <p>4. Get insights from 3 AI models</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
