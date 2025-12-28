# Backend API Phase 2 Update - Jury Results Integration

## Overview

The backend API has been updated to expose Phase 2 jury deliberation results. When queries are routed to the DEEP path (high disagreement > 0.7), the API now returns comprehensive jury analysis alongside the standard research results.

## ✅ Changes Summary

### 1. Schema Updates

**File:** `src/models/schemas.py`

Added `jury_result` field to `ComparisonResult`:

```python
jury_result: Optional[Dict] = Field(
    default=None,
    description=(
        "Jury deliberation results from DEEP path. Contains evidence_validation, "
        "logic_analysis, assumption_critique, overall_quality_score, critical_issues, "
        "recommendations, and jury_verdict (approved/needs_revision/rejected)"
    )
)
```

### 2. Orchestrator Updates

**File:** `src/council/orchestrator.py`

- Updated `research()` method to include `jury_result` in return dictionary
- Added jury_result to docstring documentation
- Automatically passes jury results from adaptive router when DEEP path is taken

### 3. Backend API Updates

**File:** `backend/main.py`

- Updated API version: `1.0.0` → `2.0.0`
- Enhanced API description to highlight Phase 2 features:
  - Council models (GPT-5, Gemini 3 Pro, Gemini 2.5 Pro)
  - Judge model (o3-pro)
  - Jury specialists (o3, Gemini 2.5 Pro, o4-mini)
  - Adaptive routing (FAST/MEDIUM/DEEP)

## 📊 API Response Structure

### Standard Response (FAST/MEDIUM path)

```json
{
  "success": true,
  "message": "Research completed successfully",
  "data": {
    "query": "What is 2+2?",
    "domain": "general",
    "responses": {...},
    "disagreement_score": 0.15,
    "routing_decision": "fast",
    "synthesized_answer": "2+2 equals 4",
    "consensus_points": [...],
    "disagreement_points": [],
    "jury_result": null  // No jury on FAST path
  }
}
```

### Enhanced Response (DEEP path with Jury)

```json
{
  "success": true,
  "message": "Research completed successfully",
  "data": {
    "query": "Is consciousness purely physical?",
    "domain": "general",
    "responses": {...},
    "disagreement_score": 0.85,
    "routing_decision": "deep",
    "synthesized_answer": "...",
    "consensus_points": [...],
    "disagreement_points": [...],
    "jury_result": {
      // Evidence Validator Results
      "evidence_validation": {
        "role": "evidence_validator",
        "model": "o3",
        "validations": [
          {
            "claim_id": "c1",
            "evidence_status": "verified",
            "issues": [],
            "source_quality_score": 0.85
          }
        ],
        "overall_source_quality": 0.85,
        "citation_hallucinations_detected": false,
        "critical_issues": [],
        "tokens_used": 1234
      },

      // Logic Auditor Results
      "logic_analysis": {
        "role": "logic_auditor",
        "model": "gemini-2.5-pro",
        "contradictions": [
          {
            "claim_ids": ["c1", "c5"],
            "conflict": "Claims appear contradictory",
            "severity": "major"
          }
        ],
        "reasoning_gaps": [],
        "circular_reasoning_detected": false,
        "consistency_score": 0.75,
        "critical_issues": [],
        "tokens_used": 1500
      },

      // Assumption Critic Results
      "assumption_critique": {
        "role": "assumption_critic",
        "model": "o4-mini",
        "hidden_assumptions": [
          "Assumes materialist framework",
          "Presumes current scientific understanding"
        ],
        "edge_cases": [
          {
            "scenario": "What if quantum effects matter?",
            "impact": "Claim may not hold"
          }
        ],
        "bias_detected": {
          "type": "confirmation_bias",
          "description": "May favor physicalist view"
        },
        "fragile_claims": [],
        "robustness_score": 0.65,
        "recommendations": ["Consider non-physicalist perspectives"],
        "tokens_used": 980
      },

      // Combined Jury Verdict
      "overall_quality_score": 0.75,
      "critical_issues": ["1 major contradiction found"],
      "recommendations": ["Consider non-physicalist perspectives"],
      "jury_verdict": "needs_revision"
    }
  }
}
```

## 🎯 Jury Result Structure

### Evidence Validation

```typescript
interface EvidenceValidation {
  role: "evidence_validator"
  model: "o3"
  validations: Array<{
    claim_id: string
    evidence_status: "verified" | "unverifiable" | "contradicted"
    issues: string[]
    source_quality_score: number  // 0.0-1.0
  }>
  overall_source_quality: number  // 0.0-1.0
  citation_hallucinations_detected: boolean
  critical_issues: string[]
  tokens_used: number
}
```

### Logic Analysis

```typescript
interface LogicAnalysis {
  role: "logic_auditor"
  model: "gemini-2.5-pro"
  contradictions: Array<{
    claim_ids: string[]
    conflict: string
    severity: "critical" | "major" | "minor"
  }>
  reasoning_gaps: string[]
  circular_reasoning_detected: boolean
  consistency_score: number  // 0.0-1.0
  critical_issues: string[]
  tokens_used: number
}
```

### Assumption Critique

```typescript
interface AssumptionCritique {
  role: "assumption_critic"
  model: "o4-mini"
  hidden_assumptions: string[]
  edge_cases: Array<{
    scenario: string
    impact: string
  }>
  bias_detected?: {
    type: string
    description: string
  }
  fragile_claims: string[]
  robustness_score: number  // 0.0-1.0
  recommendations: string[]
  tokens_used: number
}
```

### Jury Verdict

```typescript
interface JuryResult {
  evidence_validation: EvidenceValidation | null
  logic_analysis: LogicAnalysis | null
  assumption_critique: AssumptionCritique | null
  overall_quality_score: number  // 0.0-1.0 (average of three scores)
  critical_issues: string[]      // Aggregated from all specialists
  recommendations: string[]      // Aggregated from all specialists
  jury_verdict: "approved" | "needs_revision" | "rejected"
}
```

## 🔄 Routing Logic

| Disagreement Score | Path | Jury Triggered | Response Time |
|-------------------|------|----------------|---------------|
| < 0.3 | FAST | ❌ No | < 12s |
| 0.3 - 0.7 | MEDIUM | ❌ No | < 15s |
| > 0.7 | DEEP | ✅ Yes | < 30s |

## 📡 API Endpoints

### POST /api/research

Execute new research with adaptive routing.

**Request:**
```json
{
  "query": "Your research question",
  "domain": "general",
  "max_tokens": 500,
  "depth_mode": "auto"  // or "fast", "medium", "deep"
}
```

**Response:** `ResearchResponse` with complete `ComparisonResult` including `jury_result` (if DEEP path)

### GET /api/research/{id}

Retrieve research result by ID.

**Response:** Same structure as POST response, loaded from saved JSON file.

## 🎨 Frontend Integration Guide

### Detecting Jury Results

```typescript
// Check if jury was triggered
if (response.data.jury_result) {
  // DEEP path - show jury analysis
  const verdict = response.data.jury_result.jury_verdict
  const quality = response.data.jury_result.overall_quality_score
  const issues = response.data.jury_result.critical_issues

  // Display verdict badge
  <Badge variant={verdict === "approved" ? "success" : "warning"}>
    {verdict}
  </Badge>

  // Show quality score
  <QualityMeter score={quality} />

  // List critical issues
  {issues.map(issue => <Alert>{issue}</Alert>)}
}
```

### Displaying Jury Specialists

```typescript
const juryResult = response.data.jury_result

if (juryResult) {
  // Evidence Validation
  if (juryResult.evidence_validation) {
    const ev = juryResult.evidence_validation
    <Card>
      <h3>📋 Evidence Validator (o3)</h3>
      <p>Source Quality: {ev.overall_source_quality.toFixed(2)}</p>
      <p>Hallucinations: {ev.citation_hallucinations_detected ? "⚠️ Detected" : "✅ None"}</p>
    </Card>
  }

  // Logic Analysis
  if (juryResult.logic_analysis) {
    const la = juryResult.logic_analysis
    <Card>
      <h3>🔍 Logic Auditor (Gemini 2.5 Pro)</h3>
      <p>Consistency: {la.consistency_score.toFixed(2)}</p>
      <p>Contradictions: {la.contradictions.length}</p>
    </Card>
  }

  // Assumption Critique
  if (juryResult.assumption_critique) {
    const ac = juryResult.assumption_critique
    <Card>
      <h3>🤔 Assumption Critic (o4-mini)</h3>
      <p>Robustness: {ac.robustness_score.toFixed(2)}</p>
      <p>Hidden Assumptions: {ac.hidden_assumptions.length}</p>
      <p>Edge Cases: {ac.edge_cases.length}</p>
    </Card>
  }
}
```

## 🔍 Example Queries

### High Disagreement (Triggers DEEP + Jury)

- "Is free will real or is everything determined?"
- "Should we colonize Mars or fix Earth first?"
- "Is consciousness purely physical?"
- "Will AI be beneficial or harmful to humanity?"

### Low Disagreement (FAST path, no jury)

- "What is 2+2?"
- "Who is the current US president?"
- "What is the capital of France?"

## ⚙️ Configuration

### Enable/Disable Jury

Jury is enabled by default in the orchestrator:

```python
from src.council.orchestrator import CouncilOrchestrator

# Jury enabled (default)
orchestrator = CouncilOrchestrator(
    openai_api_key="...",
    gemini_api_key="...",
    enable_jury=True
)

# Jury disabled
orchestrator = CouncilOrchestrator(
    openai_api_key="...",
    gemini_api_key="...",
    enable_jury=False
)
```

### Override Routing

Force a specific path via `depth_mode`:

```json
{
  "query": "Your question",
  "domain": "general",
  "depth_mode": "deep"  // Force DEEP path with jury
}
```

## 📈 Performance Metrics

The API now tracks:
- Council phase latency
- Disagreement analysis time
- Judge phase latency (includes jury if DEEP)
- Total request time

```json
"latency_breakdown": {
  "council_phase_ms": 5234,
  "disagreement_analysis_ms": 123,
  "judge_phase_ms": 8945,  // Includes jury on DEEP path
  "total_ms": 14302
}
```

## 🚀 Testing

### Test DEEP Path

```bash
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Is consciousness purely physical or does it require something beyond physics?",
    "domain": "general",
    "max_tokens": 500,
    "depth_mode": "deep"
  }'
```

### Test FAST Path

```bash
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is 2+2?",
    "domain": "general",
    "max_tokens": 500
  }'
```

## 🔧 Troubleshooting

### Jury Not Appearing

1. Check disagreement score: `response.data.disagreement_score`
   - Must be > 0.7 for DEEP path (auto mode)
2. Check routing decision: `response.data.routing_decision`
   - Should be "deep" for jury
3. Check API keys are set for both OpenAI and Gemini
4. Check logs for jury initialization errors

### Partial Jury Results

If some jury specialists fail:
- System continues with available specialists
- Failed specialists return null
- Critical issues will note errors
- Verdict still provided based on available data

## 📚 Additional Resources

- **Full API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Alternative Documentation:** http://localhost:8000/redoc (ReDoc)
- **ARCHITECTURE.md:** System design and model specifications
- **PHASE2_SUMMARY.md:** Complete Phase 2 implementation details

---

**API Version:** 2.0.0
**Phase:** 2 (Jury Layer Complete)
**Last Updated:** 2025-12-29
