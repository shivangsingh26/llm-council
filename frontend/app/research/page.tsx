'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ResearchForm } from '@/components/research/research-form'
import { AgentStatusPanel } from '@/components/research/agent-status-panel'
import { ResultsDisplay } from '@/components/research/results-display'
import { sdkClient } from '@/lib/sdk-client'
import { useToast } from '@/hooks/use-toast'
import type { ResearchRequest, AgentStatus, ComparisonResult } from '@/lib/types'

export default function ResearchPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [agents, setAgents] = useState<AgentStatus[]>([
    { model_name: 'gpt-4o', status: 'idle' },
    { model_name: 'gemini-2.5-flash', status: 'idle' },
    { model_name: 'deepseek-r1:14b', status: 'idle' },
  ])
  const [result, setResult] = useState<ComparisonResult | null>(null)
  const { toast } = useToast()
  const router = useRouter()

  const handleSubmit = async (data: ResearchRequest) => {
    setIsLoading(true)
    setResult(null)

    // Update all agents to running status
    setAgents((prev) =>
      prev.map((agent) => ({ ...agent, status: 'running' as const }))
    )

    try {
      // Call real backend API
      const researchResult = await sdkClient.executeResearch(data)

      // Update agent statuses based on result
      setAgents((prev) =>
        prev.map((agent) => {
          const modelName = agent.model_name
          const failed = researchResult.failed_agents?.includes(modelName)
          const hasResponse = researchResult.responses?.[modelName]

          if (failed || (hasResponse && hasResponse.error)) {
            return { ...agent, status: 'failed' as const }
          } else if (hasResponse) {
            return { ...agent, status: 'completed' as const }
          } else {
            return { ...agent, status: 'idle' as const }
          }
        })
      )

      setResult(researchResult)

      toast({
        title: 'Research completed',
        description: `Successfully analyzed with ${researchResult.successful_agents} agent(s)`,
      })

      // Refresh dashboard data by triggering a router refresh
      router.refresh()

    } catch (error) {
      console.error('Research failed:', error)

      // Mark all agents as failed
      setAgents((prev) =>
        prev.map((agent) => ({ ...agent, status: 'failed' as const }))
      )

      toast({
        variant: 'destructive',
        title: 'Research failed',
        description: error instanceof Error ? error.message : 'An unexpected error occurred',
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Research</h1>
        <p className="text-muted-foreground">
          Start a new research session with the LLM Council
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <ResearchForm onSubmit={handleSubmit} isLoading={isLoading} />
          {result && <ResultsDisplay result={result} />}
        </div>

        <div>
          <AgentStatusPanel agents={agents} />
        </div>
      </div>
    </div>
  )
}
