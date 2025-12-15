'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { CheckCircle, Loader2, XCircle, Circle } from 'lucide-react'
import type { AgentStatus } from '@/lib/types'

interface AgentStatusPanelProps {
  agents: AgentStatus[]
}

export function AgentStatusPanel({ agents }: AgentStatusPanelProps) {
  const getStatusIcon = (status: AgentStatus['status']) => {
    switch (status) {
      case 'idle':
        return <Circle className="h-4 w-4 text-muted-foreground" />
      case 'running':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
    }
  }

  const getStatusColor = (status: AgentStatus['status']) => {
    switch (status) {
      case 'idle':
        return 'secondary'
      case 'running':
        return 'default'
      case 'completed':
        return 'default'
      case 'failed':
        return 'destructive'
      default:
        return 'secondary'
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Agent Status</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {agents.map((agent) => (
          <div
            key={agent.model_name}
            className="flex items-center justify-between p-3 rounded-lg border bg-card/50"
          >
            <div className="flex items-center gap-3">
              {getStatusIcon(agent.status)}
              <div>
                <p className="font-medium">{agent.model_name}</p>
                {agent.error && (
                  <p className="text-xs text-destructive">{agent.error}</p>
                )}
              </div>
            </div>
            <Badge variant={getStatusColor(agent.status)}>
              {agent.status}
            </Badge>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
