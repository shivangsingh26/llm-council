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
