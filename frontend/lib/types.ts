// Type definitions matching Python backend schemas

export type ResearchDomain =
  | 'general'
  | 'technology'
  | 'science'
  | 'business'
  | 'health'
  | 'sports'
  | 'entertainment'

export interface ResearchResponse {
  query: string
  domain: ResearchDomain
  answer: string
  confidence: number
  sources: string[]
  model_name: string
  tokens_used: number
  timestamp: string
}

export interface ComparisonResult {
  query: string
  domain: ResearchDomain
  responses: Record<string, ResearchResponse>
  total_agents: number
  successful_agents: number
  failed_agents: string[]
  consensus_points: string[]
  disagreement_points: string[]
  confidence_range: string | null
  synthesized_answer: string | null
  timestamp: string
  total_tokens: number | null
  total_cost: number | null
}

export interface ResearchRequest {
  query: string
  domain: ResearchDomain
  max_tokens?: number
}

export interface AgentStatus {
  model_name: string
  status: 'idle' | 'running' | 'completed' | 'failed'
  progress?: number
  error?: string
}

export interface RecentResearch {
  id: string
  query: string
  domain: ResearchDomain
  timestamp: string
  successful_agents: number
  total_agents: number
}
