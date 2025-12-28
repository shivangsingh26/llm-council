'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import type { ComparisonResult } from '@/lib/types'

interface ResultsDisplayProps {
  result: ComparisonResult
}

export function ResultsDisplay({ result }: ResultsDisplayProps) {
  // Helper to get routing badge variant
  const getRoutingBadgeVariant = (routing: string) => {
    switch (routing) {
      case 'fast':
        return 'default' // green-ish
      case 'medium':
        return 'secondary' // yellow-ish
      case 'deep':
        return 'destructive' // red-ish
      default:
        return 'outline'
    }
  }

  // Helper to get disagreement color
  const getDisagreementColor = (score: number) => {
    if (score < 0.3) return 'text-green-500'
    if (score < 0.7) return 'text-yellow-500'
    return 'text-red-500'
  }

  return (
    <div className="space-y-6">
      {/* Synthesized Answer */}
      {result.synthesized_answer && (
        <Card>
          <CardHeader>
            <CardTitle>Synthesized Answer</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-foreground leading-relaxed">
              {result.synthesized_answer}
            </p>
            <div className="flex items-center gap-2 mt-4">
              <Badge variant="outline">
                {result.successful_agents}/{result.total_agents} agents
              </Badge>
              {result.confidence_range && (
                <Badge variant="outline">{result.confidence_range}</Badge>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Phase 1: Adaptive Routing Metrics */}
      {(result.disagreement_score !== undefined || result.routing_decision || result.latency_breakdown) && (
        <Card className="border-2 border-primary/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              🎯 Adaptive Routing Metrics
              <Badge variant="outline" className="ml-auto">Phase 1</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Disagreement Score */}
            {result.disagreement_score !== undefined && (
              <div>
                <h4 className="font-semibold mb-2 text-sm">Disagreement Score</h4>
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="h-2 bg-secondary rounded-full overflow-hidden">
                      <div
                        className={`h-full ${
                          result.disagreement_score < 0.3
                            ? 'bg-green-500'
                            : result.disagreement_score < 0.7
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${result.disagreement_score * 100}%` }}
                      />
                    </div>
                  </div>
                  <span className={`font-mono font-bold ${getDisagreementColor(result.disagreement_score)}`}>
                    {result.disagreement_score.toFixed(3)}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {result.disagreement_score < 0.3
                    ? 'High agreement - models are aligned'
                    : result.disagreement_score < 0.7
                    ? 'Moderate disagreement - some differences'
                    : 'High disagreement - significant differences'}
                </p>
              </div>
            )}

            {/* Routing Decision */}
            {result.routing_decision && (
              <div>
                <h4 className="font-semibold mb-2 text-sm">Routing Path</h4>
                <div className="flex items-center gap-2">
                  <Badge
                    variant={getRoutingBadgeVariant(result.routing_decision)}
                    className="text-lg py-1 px-4"
                  >
                    {result.routing_decision.toUpperCase()}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {result.routing_decision === 'fast'
                      ? '⚡ Lightweight processing'
                      : result.routing_decision === 'medium'
                      ? '⚙️ Standard processing'
                      : '🔍 Deep processing'}
                  </span>
                </div>
              </div>
            )}

            {/* Latency Breakdown */}
            {result.latency_breakdown && (
              <div>
                <h4 className="font-semibold mb-2 text-sm">Latency Breakdown</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {result.latency_breakdown.council_phase_ms !== undefined && (
                    <div className="rounded-lg border bg-card/50 p-3">
                      <div className="text-xs text-muted-foreground mb-1">Council</div>
                      <div className="font-mono font-bold">
                        {result.latency_breakdown.council_phase_ms}ms
                      </div>
                    </div>
                  )}
                  {result.latency_breakdown.disagreement_analysis_ms !== undefined && (
                    <div className="rounded-lg border bg-card/50 p-3">
                      <div className="text-xs text-muted-foreground mb-1">Analysis</div>
                      <div className="font-mono font-bold">
                        {result.latency_breakdown.disagreement_analysis_ms}ms
                      </div>
                    </div>
                  )}
                  {result.latency_breakdown.judge_phase_ms !== undefined && (
                    <div className="rounded-lg border bg-card/50 p-3">
                      <div className="text-xs text-muted-foreground mb-1">Judge</div>
                      <div className="font-mono font-bold">
                        {result.latency_breakdown.judge_phase_ms}ms
                      </div>
                    </div>
                  )}
                  {result.latency_breakdown.total_ms !== undefined && (
                    <div className="rounded-lg border bg-primary/10 p-3">
                      <div className="text-xs text-muted-foreground mb-1">Total</div>
                      <div className="font-mono font-bold text-primary">
                        {result.latency_breakdown.total_ms}ms
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Phase 2: Jury Deliberation Results (DEEP path only) */}
      {result.jury_result && (
        <Card className="border-2 border-purple-500/30 bg-gradient-to-br from-purple-500/5 to-transparent">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              ⚖️ Jury Deliberation
              <Badge variant="outline" className="ml-auto">Phase 2</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Verdict and Quality Score */}
            <div className="flex items-center justify-between p-4 rounded-lg border bg-card">
              <div>
                <h4 className="font-semibold mb-2 text-sm text-muted-foreground">Jury Verdict</h4>
                <Badge
                  variant={
                    result.jury_result.jury_verdict === 'approved'
                      ? 'default'
                      : result.jury_result.jury_verdict === 'needs_revision'
                      ? 'secondary'
                      : 'destructive'
                  }
                  className="text-lg py-1.5 px-4"
                >
                  {result.jury_result.jury_verdict === 'approved' && '✓ '}
                  {result.jury_result.jury_verdict === 'needs_revision' && '⚠ '}
                  {result.jury_result.jury_verdict === 'rejected' && '✗ '}
                  {result.jury_result.jury_verdict.toUpperCase().replace('_', ' ')}
                </Badge>
              </div>
              <div className="text-right">
                <h4 className="font-semibold mb-2 text-sm text-muted-foreground">Overall Quality</h4>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-secondary rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        result.jury_result.overall_quality_score >= 0.8
                          ? 'bg-green-500'
                          : result.jury_result.overall_quality_score >= 0.6
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${result.jury_result.overall_quality_score * 100}%` }}
                    />
                  </div>
                  <span className="font-mono font-bold text-lg">
                    {(result.jury_result.overall_quality_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Critical Issues */}
            {result.jury_result.critical_issues.length > 0 && (
              <div className="p-4 rounded-lg border border-destructive/30 bg-destructive/5">
                <h4 className="font-semibold mb-2 text-destructive">Critical Issues</h4>
                <ul className="space-y-1">
                  {result.jury_result.critical_issues.map((issue, idx) => (
                    <li key={idx} className="text-sm text-muted-foreground pl-4 border-l-2 border-destructive">
                      {issue}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommendations */}
            {result.jury_result.recommendations.length > 0 && (
              <div className="p-4 rounded-lg border border-blue-500/30 bg-blue-500/5">
                <h4 className="font-semibold mb-2 text-blue-500">Recommendations</h4>
                <ul className="space-y-1">
                  {result.jury_result.recommendations.map((rec, idx) => (
                    <li key={idx} className="text-sm text-muted-foreground pl-4 border-l-2 border-blue-500">
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Jury Specialists */}
            <div className="grid md:grid-cols-3 gap-4">
              {/* Evidence Validator */}
              {result.jury_result.evidence_validation && (
                <Card className="border-green-500/30">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      📋 Evidence Validator
                      <Badge variant="outline" className="text-xs ml-auto">
                        {result.jury_result.evidence_validation.model}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3 text-sm">
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Source Quality</div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-secondary rounded-full overflow-hidden">
                          <div
                            className="h-full bg-green-500"
                            style={{
                              width: `${result.jury_result.evidence_validation.overall_source_quality * 100}%`,
                            }}
                          />
                        </div>
                        <span className="font-mono text-xs font-bold">
                          {(result.jury_result.evidence_validation.overall_source_quality * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Hallucinations</div>
                      <Badge
                        variant={
                          result.jury_result.evidence_validation.citation_hallucinations_detected
                            ? 'destructive'
                            : 'default'
                        }
                      >
                        {result.jury_result.evidence_validation.citation_hallucinations_detected
                          ? '⚠️ Detected'
                          : '✓ None'}
                      </Badge>
                    </div>
                    {result.jury_result.evidence_validation.validations.length > 0 && (
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">Validations</div>
                        <div className="text-xs font-mono">
                          {result.jury_result.evidence_validation.validations.length} claim(s) checked
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Logic Auditor */}
              {result.jury_result.logic_analysis && (
                <Card className="border-blue-500/30">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      🔍 Logic Auditor
                      <Badge variant="outline" className="text-xs ml-auto">
                        {result.jury_result.logic_analysis.model}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3 text-sm">
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Consistency Score</div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-secondary rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500"
                            style={{
                              width: `${result.jury_result.logic_analysis.consistency_score * 100}%`,
                            }}
                          />
                        </div>
                        <span className="font-mono text-xs font-bold">
                          {(result.jury_result.logic_analysis.consistency_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Contradictions</div>
                      <Badge variant={result.jury_result.logic_analysis.contradictions.length > 0 ? 'destructive' : 'default'}>
                        {result.jury_result.logic_analysis.contradictions.length} found
                      </Badge>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Circular Reasoning</div>
                      <Badge
                        variant={result.jury_result.logic_analysis.circular_reasoning_detected ? 'destructive' : 'default'}
                      >
                        {result.jury_result.logic_analysis.circular_reasoning_detected ? '⚠️ Detected' : '✓ None'}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Assumption Critic */}
              {result.jury_result.assumption_critique && (
                <Card className="border-purple-500/30">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      🤔 Assumption Critic
                      <Badge variant="outline" className="text-xs ml-auto">
                        {result.jury_result.assumption_critique.model}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3 text-sm">
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Robustness Score</div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-secondary rounded-full overflow-hidden">
                          <div
                            className="h-full bg-purple-500"
                            style={{
                              width: `${result.jury_result.assumption_critique.robustness_score * 100}%`,
                            }}
                          />
                        </div>
                        <span className="font-mono text-xs font-bold">
                          {(result.jury_result.assumption_critique.robustness_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Hidden Assumptions</div>
                      <div className="text-xs font-mono">
                        {result.jury_result.assumption_critique.hidden_assumptions.length} identified
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Edge Cases</div>
                      <div className="text-xs font-mono">
                        {result.jury_result.assumption_critique.edge_cases.length} found
                      </div>
                    </div>
                    {result.jury_result.assumption_critique.bias_detected && (
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">Bias Detected</div>
                        <Badge variant="destructive">
                          {result.jury_result.assumption_critique.bias_detected.type}
                        </Badge>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {result.consensus_points.length > 0 && (
            <div>
              <h4 className="font-semibold mb-2 text-green-500">
                Consensus Points
              </h4>
              <ul className="space-y-2">
                {result.consensus_points.map((point, idx) => (
                  <li key={idx} className="text-sm text-muted-foreground pl-4 border-l-2 border-green-500">
                    {point}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.disagreement_points.length > 0 && (
            <>
              <Separator />
              <div>
                <h4 className="font-semibold mb-2 text-yellow-500">
                  Disagreement Points
                </h4>
                <ul className="space-y-2">
                  {result.disagreement_points.map((point, idx) => (
                    <li key={idx} className="text-sm text-muted-foreground pl-4 border-l-2 border-yellow-500">
                      {point}
                    </li>
                  ))}
                </ul>
              </div>
            </>
          )}

          {result.knowledge_gaps && result.knowledge_gaps.length > 0 && (
            <>
              <Separator />
              <div>
                <h4 className="font-semibold mb-2 text-blue-500">
                  Knowledge Gaps
                </h4>
                <ul className="space-y-2">
                  {result.knowledge_gaps.map((gap, idx) => (
                    <li key={idx} className="text-sm text-muted-foreground pl-4 border-l-2 border-blue-500">
                      {gap}
                    </li>
                  ))}
                </ul>
              </div>
            </>
          )}

          {result.verification_needed && result.verification_needed.length > 0 && (
            <>
              <Separator />
              <div>
                <h4 className="font-semibold mb-2 text-purple-500">
                  Verification Needed
                </h4>
                <ul className="space-y-2">
                  {result.verification_needed.map((claim, idx) => (
                    <li key={idx} className="text-sm text-muted-foreground pl-4 border-l-2 border-purple-500">
                      {claim}
                    </li>
                  ))}
                </ul>
              </div>
            </>
          )}

          {result.failed_agents.length > 0 && (
            <>
              <Separator />
              <div>
                <h4 className="font-semibold mb-2 text-destructive">
                  Failed Agents
                </h4>
                <div className="flex gap-2">
                  {result.failed_agents.map((agent) => (
                    <Badge key={agent} variant="destructive">
                      {agent}
                    </Badge>
                  ))}
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Reasoning Trace (Phase A: Master Synthesizer) */}
      {result.reasoning_trace && (
        <Card>
          <CardHeader>
            <CardTitle>🧠 Reasoning Trace (Master Synthesizer)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg border bg-card/50 p-4">
              <p className="text-sm leading-relaxed whitespace-pre-wrap">
                {result.reasoning_trace}
              </p>
            </div>
            {result.confidence_reasoning && (
              <>
                <Separator className="my-4" />
                <div>
                  <h4 className="font-semibold mb-2">Confidence Reasoning</h4>
                  <p className="text-sm text-muted-foreground">
                    {result.confidence_reasoning}
                  </p>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      )}

      {/* Individual Agent Responses */}
      <Card>
        <CardHeader>
          <CardTitle>Individual Responses</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue={Object.keys(result.responses)[0]}>
            <TabsList className="grid w-full grid-cols-3">
              {Object.keys(result.responses).map((modelName) => (
                <TabsTrigger key={modelName} value={modelName}>
                  {modelName}
                </TabsTrigger>
              ))}
            </TabsList>
            {Object.entries(result.responses).map(([modelName, response]) => (
              <TabsContent key={modelName} value={modelName} className="space-y-4 mt-4">
                <div className="rounded-lg border bg-card/50 p-4">
                  <p className="text-sm leading-relaxed">{response.answer}</p>
                </div>
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span>Confidence: {response.confidence}</span>
                  <Separator orientation="vertical" className="h-4" />
                  <span>Tokens: {response.tokens_used}</span>
                  {response.sources && response.sources.length > 0 && (
                    <>
                      <Separator orientation="vertical" className="h-4" />
                      <span>Sources: {response.sources.length}</span>
                    </>
                  )}
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>

      {/* Metadata */}
      <Card>
        <CardHeader>
          <CardTitle>Metadata</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Query:</span>
              <span className="font-medium">{result.query}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Domain:</span>
              <Badge variant="outline">{result.domain}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Timestamp:</span>
              <span className="font-mono text-xs">
                {new Date(result.timestamp).toLocaleString()}
              </span>
            </div>
            {result.total_tokens && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Total Tokens:</span>
                <span className="font-medium">{result.total_tokens.toLocaleString()}</span>
              </div>
            )}
            {result.total_cost && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Total Cost:</span>
                <span className="font-medium">${result.total_cost.toFixed(4)}</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
