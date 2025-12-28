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

// Phase 2: Jury Layer Types
export interface JuryValidation {
  claim_id: string
  evidence_status: 'verified' | 'unverifiable' | 'contradicted'
  issues: string[]
  source_quality_score: number // 0-1
}

export interface EvidenceValidation {
  role: 'evidence_validator'
  model: string
  validations: JuryValidation[]
  overall_source_quality: number // 0-1
  citation_hallucinations_detected: boolean
  critical_issues: string[]
  tokens_used: number
}

export interface LogicContradiction {
  claim_ids: string[]
  conflict: string
  severity: 'critical' | 'major' | 'minor'
}

export interface LogicAnalysis {
  role: 'logic_auditor'
  model: string
  contradictions: LogicContradiction[]
  reasoning_gaps: string[]
  circular_reasoning_detected: boolean
  consistency_score: number // 0-1
  critical_issues: string[]
  tokens_used: number
}

export interface EdgeCase {
  scenario: string
  impact: string
}

export interface BiasDetection {
  type: string
  description: string
}

export interface AssumptionCritique {
  role: 'assumption_critic'
  model: string
  hidden_assumptions: string[]
  edge_cases: EdgeCase[]
  bias_detected?: BiasDetection
  fragile_claims: string[]
  robustness_score: number // 0-1
  recommendations: string[]
  tokens_used: number
}

export interface JuryResult {
  evidence_validation: EvidenceValidation | null
  logic_analysis: LogicAnalysis | null
  assumption_critique: AssumptionCritique | null
  overall_quality_score: number // 0-1
  critical_issues: string[]
  recommendations: string[]
  jury_verdict: 'approved' | 'needs_revision' | 'rejected'
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

  // Phase A: Master Synthesizer fields
  reasoning_trace?: string | null
  knowledge_gaps?: string[]
  verification_needed?: string[]
  confidence_reasoning?: string | null

  // Phase 1: Adaptive Routing fields
  disagreement_score?: number | null
  routing_decision?: string | null
  latency_breakdown?: {
    council_phase_ms?: number
    disagreement_analysis_ms?: number
    judge_phase_ms?: number
    total_ms?: number
  } | null

  // Phase 2: Jury Layer Results (DEEP path only)
  jury_result?: JuryResult | null
}

export interface ResearchRequest {
  query: string
  domain: ResearchDomain
  max_tokens?: number
  depth_mode?: 'auto' | 'fast' | 'medium' | 'deep'
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
