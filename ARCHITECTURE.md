# LLM-Council: Multi-LLM Research & Reasoning Platform
## Principal Architect's Implementation Plan

---

## ✅ VERIFIED MODEL AVAILABILITY (OpenAI + Gemini Only)

**Good news! Most of your suggested models exist.** Here's the verified model pool based on official documentation:

**Available OpenAI Models (Jan 2025):**
- GPT-5 series: GPT-5, GPT-5.1, GPT-5.2, GPT-5 mini, GPT-5 nano, GPT-5 Pro
- o-series reasoning: o3, o3-pro, o3-mini, o4-mini, o1, o1-pro
- GPT-4.1 series: GPT-4.1, GPT-4.1 mini, GPT-4.1 nano
- GPT-4o series: GPT-4o, GPT-4o mini

**Available Gemini Models (Jan 2025):**
- Gemini 3 Pro (newest, state-of-the-art reasoning, multimodal)
- Gemini 3 Flash (speed-focused, frontier intelligence)
- Gemini 2.5 Pro (specialized thinking model for complex reasoning in code, math, STEM)
- Gemini 2.5 Flash, 2.5 Flash-Lite (large-scale processing)
- Gemini 2.0 Flash, 2.0 Flash-Lite (stable alternatives)

**Recommended Model Pool (OpenAI + Gemini):**

```
COUNCIL (diverse base models):
├─ OpenAI GPT-5           ← Latest GPT model, strong general reasoning
├─ Gemini 3 Pro           ← Newest Google model, state-of-the-art multimodal
└─ Gemini 2.5 Pro         ← Specialized thinking model (code, math, STEM)

Alternative council configurations:
- Budget-conscious: GPT-4.1, Gemini 3 Flash, Gemini 2.5 Flash
- Maximum diversity: GPT-5.2, Gemini 3 Pro, GPT-4.1
- Speed-focused: GPT-4.1 mini, Gemini 3 Flash, Gemini 2.5 Flash

JURY (deep reasoning models):
├─ OpenAI o3              ← Advanced reasoning model
├─ OpenAI o4-mini         ← Fast, cost-efficient reasoning
└─ Gemini 2.5 Pro         ← Gemini's best reasoning model

JUDGE (single authoritative synthesizer):
└─ OpenAI o3-pro          ← Most intelligent reasoning model with extended compute
   Alternative: GPT-5 Pro ← If cost/latency is concern
```

**Recommendation:** Start with 3 council models (GPT-5, Gemini 3 Pro, Gemini 2.5 Pro) to maximize diversity between OpenAI and Google architectures.

---

## 1. END-TO-END SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP SERVER INTERFACE                      │
│  Exposes: llm_council_query(query, context, depth_mode)     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                        │
│  - Query preprocessing                                       │
│  - Adaptive routing decisions                                │
│  - Job queue management (async)                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┴─────────────────────┐
        ↓                                           ↓
┌──────────────────┐                    ┌──────────────────────┐
│  FAST PATH       │                    │   DEEP PATH          │
│  (high agreement)│                    │  (disagreement/high  │
│                  │                    │   stakes)            │
│  Council → Judge │                    │  Council → Jury →    │
│  (lightweight)   │                    │  Judge (full)        │
└──────────────────┘                    └──────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    COUNCIL LAYER (parallel)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │  GPT-5   │  │ Gemini   │  │ Gemini   │                  │
│  │          │  │  3 Pro   │  │ 2.5 Pro  │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│       ↓              ↓              ↓                        │
│  [Structured Response Schema]                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              DISAGREEMENT ANALYZER                           │
│  - Claim overlap matrix                                      │
│  - Evidence conflict detection                               │
│  - Confidence variance                                       │
│  → Routing decision: Fast path vs Deep path                 │
└─────────────────────────────────────────────────────────────┘
                              ↓ (if Deep path)
┌─────────────────────────────────────────────────────────────┐
│                    JURY LAYER (sequential)                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Role 1: Evidence Validator (o3)                        │ │
│  │ Task: Verify citations, check source quality           │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Role 2: Logic Auditor (Gemini 2.5 Pro)                │ │
│  │ Task: Find contradictions, check reasoning chains      │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Role 3: Assumption Critic (o4-mini)                    │ │
│  │ Task: Surface hidden assumptions, edge cases           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      JUDGE LAYER                             │
│  Model: o3-pro (or GPT-5 Pro)                                │
│  Input: Council responses + Jury analysis (if triggered)    │
│  Output: Synthesized answer + uncertainty score             │
│  Constraints: Evidence-only, must flag unknowns             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    RESPONSE FORMATTER                        │
│  - Strip chain-of-thought artifacts                         │
│  - Structure final JSON                                      │
│  - Add provenance metadata                                   │
└─────────────────────────────────────────────────────────────┘
```

### Synchronous vs Asynchronous

**Synchronous (blocking):**
- MCP tool call returns job ID immediately
- Client polls or waits for completion

**Asynchronous (internal):**
- Council calls are parallelized (3-4 concurrent API calls)
- Jury roles run sequentially (each builds on previous)
- Judge waits for all inputs

**Why not fully async?**
- Jury roles have dependencies (can't validate evidence before claims exist)
- Judge needs complete picture
- Premature optimization is bad; measure first, optimize later

---

## 2. COUNCIL DESIGN

### How Many Models?

**Maximum: 3 council models.**

**Rationale:**
- Diminishing returns after 3 diverse models
- 4th model rarely adds novel information
- Cost/latency scales linearly with count
- Quality improvement is sublinear

**Diversity Enforcement:**

```python
# Conceptual diversity matrix
#                 GPT-5       Gemini 3 Pro    Gemini 2.5 Pro
# Architecture    GPT         Gemini          Gemini
# Training org    OpenAI      Google          Google
# Focus           General     Multimodal      Code/Math/STEM
# Model family    Base LLM    Latest Gen      Thinking model
# Strengths       Balanced    Multimodal      Deep reasoning
# Context window  Large       1M tokens       1M tokens
```

**Bad diversity:** GPT-5 + GPT-5.1 + GPT-5.2 (same lineage, redundant)
**Good diversity:** GPT-5 + Gemini 3 Pro + Gemini 2.5 Pro (different orgs, different specializations)

**Why this works:**
- OpenAI vs Google (different training data, architectures, RLHF approaches)
- General model (GPT-5) vs Multimodal (Gemini 3 Pro) vs Reasoning specialist (Gemini 2.5 Pro)
- Maximizes chance of catching different failure modes

### Council Output Schema

Each council member produces:

```json
{
  "model_id": "gpt-5",
  "timestamp": "2025-12-18T10:30:00Z",
  "response": {
    "claims": [
      {
        "claim_id": "c1",
        "statement": "The capital of France is Paris",
        "confidence": 0.99,
        "evidence": [
          {
            "source": "Encyclopedia Britannica",
            "quote": "Paris, city and capital of France...",
            "source_quality": "high"
          }
        ],
        "assumptions": [
          "Definition of 'capital' refers to administrative capital"
        ],
        "caveats": []
      }
    ],
    "overall_confidence": 0.95,
    "knowledge_gaps": [
      "No information about historical changes in capital status"
    ],
    "reasoning_trace": "<internal, not shown to user>"
  }
}
```

**Schema enforcement:**
- Use structured output APIs (OpenAI JSON mode, Gemini structured outputs)
- Validation layer rejects non-compliant responses
- Fallback: re-prompt with error message (max 1 retry)

**Key design choice:** Claims are atomic units. This allows:
- Granular agreement/disagreement analysis
- Evidence traceability
- Easier jury validation

---

## 3. JURY DESIGN

### Core Philosophy

**Critical insight:** Most jury architectures are redundant. Don't use 5 LLMs to do the same reasoning 5 times.

**Anti-pattern:**
```
Jury member 1: "Evaluate the response"
Jury member 2: "Critique the response"
Jury member 3: "Assess the response"
```
This is wasteful. Instead: **Non-overlapping responsibilities.**

### Jury Roles (3 max)

#### Role 1: Evidence Validator
**Model:** o3 (advanced reasoning for verification)
**Input:** Council claims + evidence citations
**Task:**
- Verify sources exist and are correctly quoted
- Check for citation hallucinations
- Assess source quality (peer-reviewed > blog post)
- Flag missing evidence for strong claims

**Output:**
```json
{
  "role": "evidence_validator",
  "validations": [
    {
      "claim_id": "c1",
      "evidence_status": "verified" | "unverifiable" | "contradicted",
      "issues": ["Source URL 404", "Quote not found in source"],
      "source_quality_score": 0.85
    }
  ]
}
```

#### Role 2: Logic Auditor
**Model:** Gemini 2.5 Pro (specialized thinking model)
**Input:** Council claims + reasoning traces
**Task:**
- Find logical contradictions between claims
- Check internal consistency
- Identify circular reasoning
- Flag non-sequiturs

**Output:**
```json
{
  "role": "logic_auditor",
  "contradictions": [
    {
      "claim_ids": ["c1", "c5"],
      "conflict": "Claim c1 states X, but c5 implies not-X",
      "severity": "high"
    }
  ],
  "reasoning_gaps": ["Conclusion doesn't follow from premises"]
}
```

#### Role 3: Assumption Critic
**Model:** o4-mini (fast, cost-efficient reasoning)
**Input:** Council claims + assumptions lists
**Task:**
- Surface hidden assumptions
- Test edge cases
- Find scenarios where claims fail
- Identify bias in framing

**Output:**
```json
{
  "role": "assumption_critic",
  "hidden_assumptions": [
    "Assumes Western legal framework",
    "Presumes current geopolitical status"
  ],
  "edge_cases": [
    "What if the user meant Paris, Texas?"
  ],
  "robustness_score": 0.75
}
```

### When to Trigger Jury

**Trigger conditions (ANY of):**
1. Council disagreement score > 0.4 (on 0-1 scale)
2. Query flagged as "high stakes" by user (e.g., medical, legal)
3. Any council member confidence < 0.6
4. Explicit user request for deep mode

**Skip conditions (ALL of):**
1. Council agreement > 0.9
2. All confidence scores > 0.85
3. Simple factual query (not analysis/reasoning)

**Jury run mode:**
- Sequential (not parallel): Logic auditor needs evidence validation results
- If Role 1 finds critical issues, short-circuit (don't waste tokens on Roles 2-3)

---

## 4. JUDGE DESIGN

### Model Selection

**Use o3-pro** (most intelligent reasoning model with extended compute).

**Alternative:** GPT-5 Pro (if latency/cost is a concern)

**Why o3-pro?**
- Strongest reasoning capability for conflict resolution
- Extended thinking time = better synthesis quality
- Budget constraints suggest: diverse council + strong judge > all-strong council
- Can detect subtle logical flaws missed by base models

### Judge Responsibilities

1. **Synthesize** council responses + jury analysis into coherent answer
2. **Resolve conflicts** using explicit rules (see below)
3. **Calibrate confidence** based on agreement, evidence quality, jury feedback
4. **Reject unsupported claims** (allowed to say "unknown")
5. **Strip reasoning artifacts** from final output

### Conflict Resolution Strategy

**Priority hierarchy:**
1. **Evidence quality**: Claims with better sources win
2. **Model consensus**: 2-of-3 agreement > 1 outlier
3. **Jury validation**: Jury-verified claim > unverified
4. **Explicit uncertainty**: If tie, output both views + uncertainty flag

**Example:**
```
Council says:
- GPT-5: "Paris" (confidence 0.99, strong evidence)
- Gemini 3 Pro: "Paris" (confidence 0.95, strong evidence)
- Gemini 2.5 Pro: "Lyon" (confidence 0.60, weak evidence)

Jury says:
- Evidence validator: "Paris claims verified, Lyon claim has no evidence"

Judge decision: "Paris" (consensus + evidence + jury validation)
```

**Counter-example (genuine ambiguity):**
```
Council says:
- GPT-5: "Answer is A" (conf 0.70, medium evidence)
- Gemini 3 Pro: "Answer is B" (conf 0.75, medium evidence)
- Gemini 2.5 Pro: "Answer is A" (conf 0.65, medium evidence)

Jury says:
- Logic auditor: "Both A and B are logically valid under different assumptions"
- Assumption critic: "Depends on interpretation of term X"

Judge decision: "Answer is ambiguous. Under interpretation 1, answer is A. Under interpretation 2, answer is B. Confidence: 0.5"
```

### Confidence Calibration

```python
# Pseudocode
base_confidence = weighted_average(council_confidences)

# Adjustments
if jury_found_evidence_issues:
    base_confidence *= 0.7
if logical_contradictions_found:
    base_confidence *= 0.6
if council_high_agreement:
    base_confidence *= 1.1  # (capped at 1.0)
if assumptions_untested:
    base_confidence *= 0.8

final_confidence = clamp(base_confidence, 0.0, 1.0)

# Uncertainty flags
if final_confidence < 0.5:
    uncertainty_level = "high"
elif final_confidence < 0.75:
    uncertainty_level = "medium"
else:
    uncertainty_level = "low"
```

### Hallucination Penalties

**Detection mechanisms:**
1. Jury evidence validator flags non-existent sources
2. Council claims without evidence
3. Contradictions between council members

**Penalty actions:**
1. Downweight or remove hallucinated claims from synthesis
2. Reduce confidence score
3. Add warning to final output: "Some claims could not be verified"
4. Log hallucination for model quality metrics

**Judge system prompt (simplified):**
```
You are the final arbiter in a multi-model research pipeline.

RULES:
1. Only include claims supported by verified evidence
2. If councils disagree and evidence is weak, say "unknown"
3. Surface uncertainty explicitly
4. Never invent information to fill gaps
5. If jury found critical issues, downweight those claims

OUTPUT REQUIREMENTS:
- Structured JSON (no prose)
- Confidence score (0-1)
- Uncertainty flags
- Provenance (which models contributed what)
```

---

## 5. ADAPTIVE ROUTING LOGIC

### Disagreement Measurement

```python
def calculate_disagreement(council_responses):
    """
    Returns disagreement score 0.0 (full agreement) to 1.0 (total disagreement)
    """
    # Extract claim statements from all councils
    all_claims = [claim.statement for r in council_responses for claim in r.claims]

    # Compute pairwise semantic similarity (using embeddings)
    similarities = []
    for i in range(len(council_responses)):
        for j in range(i+1, len(council_responses)):
            sim = semantic_similarity(
                council_responses[i].claims,
                council_responses[j].claims
            )
            similarities.append(sim)

    avg_similarity = mean(similarities)
    disagreement = 1.0 - avg_similarity

    # Also check confidence variance
    confidences = [r.overall_confidence for r in council_responses]
    confidence_variance = variance(confidences)

    # Combined score
    final_score = 0.7 * disagreement + 0.3 * confidence_variance
    return clamp(final_score, 0.0, 1.0)
```

### Decision Thresholds

```python
disagreement_score = calculate_disagreement(council_responses)

if disagreement_score < 0.3:
    path = "FAST"  # Council → Judge (lightweight)
elif disagreement_score < 0.7:
    path = "MEDIUM"  # Council → Jury (2 roles) → Judge
else:
    path = "DEEP"  # Council → Jury (all 3 roles) → Judge
```

### Fallback Strategies

**Failure mode 1: Council member fails**
- Continue with remaining council members (2 minimum)
- If < 2 councils succeed, return error to user
- Log failure for monitoring

**Failure mode 2: Jury member fails**
- Skip that jury role, continue with others
- Judge receives partial jury analysis
- Flag in final output: "Some validation steps incomplete"

**Failure mode 3: Judge fails**
- Retry once with simplified prompt
- If still fails, return best council response + warning
- This is rare with o3-pro but possible

**Failure mode 4: All models timeout**
- Return error: "System unavailable, retry later"
- Don't attempt heroics; fail gracefully

### Short-circuit Optimization

```python
# After council phase
if all_councils_agree() and all_confidence_high() and query_is_simple():
    # Skip jury entirely
    send_to_judge_lightweight_mode()
```

**Judge lightweight mode:**
- Simpler prompt (no conflict resolution needed)
- Faster response
- 50% token reduction

---

## 6. QUALITY METRICS

### Correctness Measurement

**Ground truth dataset:**
- Curate 100-500 questions with known correct answers
- Include: factual, analytical, edge cases, ambiguous questions
- Sources: MMLU, TruthfulQA, domain-specific benchmarks

**Metrics:**
1. **Accuracy**: % of correct final answers
2. **Hallucination rate**: % of responses with fabricated citations
3. **Calibration**: Correlation between confidence and correctness
   - Plot: Predicted confidence vs actual accuracy
   - Good calibration: 90% confidence = 90% accuracy
4. **False confidence**: % of high-confidence wrong answers (worst case)

### Research Depth Measurement

**Metrics:**
1. **Citation count**: Avg # of sources per response
2. **Source diversity**: Unique domains cited
3. **Assumption coverage**: % of hidden assumptions surfaced
4. **Edge case identification**: # of caveats/limitations mentioned
5. **Nuance score**: Manual eval on 1-5 scale

**Manual evaluation (sample 50 responses/week):**
- "Did the system identify important caveats?"
- "Were counterarguments considered?"
- "Was uncertainty appropriately flagged?"

### Signals to Log (for every query)

```json
{
  "query_id": "uuid",
  "timestamp": "ISO-8601",
  "query_text": "...",
  "query_metadata": {
    "estimated_complexity": "simple|medium|complex",
    "domain": "general|medical|legal|...",
    "user_requested_depth": "fast|deep"
  },
  "council_responses": [...],
  "disagreement_score": 0.45,
  "routing_decision": "DEEP",
  "jury_triggered": true,
  "jury_findings": {...},
  "judge_output": {...},
  "final_confidence": 0.82,
  "latency_breakdown": {
    "council_phase_ms": 3200,
    "jury_phase_ms": 5400,
    "judge_phase_ms": 2100,
    "total_ms": 10700
  },
  "cost_breakdown": {
    "council_tokens": 15000,
    "jury_tokens": 8000,
    "judge_tokens": 3000,
    "total_cost_usd": 0.42
  },
  "errors": [],
  "user_feedback": null  // populated later if provided
}
```

### Dashboarding

**Weekly review:**
- Accuracy trend
- Hallucination rate
- Avg latency by routing path
- Cost per query
- User feedback sentiment (if collected)

**Alerts:**
- Accuracy drops below 85%
- Hallucination rate > 5%
- Any model fails > 10% of calls

---

## 7. PHASED ROADMAP

### Phase 1: Core Correctness (Weeks 1-3)
**Goal:** Prove the council → judge pipeline works better than single model.

**Must-haves:**
- ✅ 3-model council (GPT-5, Gemini 3 Pro, Gemini 2.5 Pro)
- ✅ Structured output schema enforcement
- ✅ Simple judge (o3-pro or GPT-5 Pro) with conflict resolution
- ✅ Basic MCP server wrapper
- ✅ Disagreement analyzer
- ✅ Fast path (skip jury if high agreement)
- ✅ Ground truth eval dataset (100 questions)
- ✅ Logging infrastructure

**Success criteria:**
- Accuracy > single best model by ≥5%
- Hallucination rate < 3%
- End-to-end latency < 15s (fast path < 8s)

**Skip for now:**
- Jury layer (add in Phase 2)
- Async job queue (blocking is fine initially)
- Advanced prompt engineering

### Phase 2: Research Depth Enhancements (Weeks 4-6)
**Goal:** Add jury layer to surface deeper insights.

**Additions:**
- ✅ Evidence validator jury role (o3)
- ✅ Logic auditor jury role (Gemini 2.5 Pro)
- ✅ Assumption critic jury role (o4-mini)
- ✅ Adaptive jury triggering (3-tier routing)
- ✅ Enhanced judge with jury integration
- ✅ Research depth metrics

**Success criteria:**
- Citation quality score > 0.8
- Edge case identification in ≥60% of complex queries
- No degradation in latency for fast path
- Deep path latency < 30s

### Phase 3: Performance Optimization (Weeks 7-9)
**Goal:** Make it production-ready at scale.

**Optimizations:**
- ✅ Async job queue (Redis + Celery or similar)
- ✅ Response caching (semantic similarity cache)
- ✅ Prompt compression (reduce council token usage)
- ✅ Model selection tuning (maybe swap models based on domain)
- ✅ Batch processing support
- ✅ Rate limiting and quota management

**Success criteria:**
- Deep path latency < 20s (33% reduction)
- Cost per query < $0.30 (from ~$0.50)
- Cache hit rate > 15% (for similar queries)
- 99.9% uptime

---

## 8. CRITICAL DESIGN CRITIQUES

### What Could Go Wrong

**1. Latency Explosion**
- Deep path with 3 councils + 3 jury + 1 judge = 7 sequential LLM calls
- Even at 3s per call = 21s+ latency
- **Mitigation:** Parallelize council, make jury roles lightweight, cache aggressively

**2. Cost Spiral**
- $0.50/query × 1000 queries/day = $500/day = $15k/month
- **Mitigation:** Fast path for 70%+ of queries, cheaper models for jury roles where possible

**3. Schema Drift**
- LLMs are stochastic; even with JSON mode, schemas can drift
- **Mitigation:** Strict validation + auto-retry + monitoring

**4. Overfitting to Benchmarks**
- Easy to optimize for your eval set
- **Mitigation:** Holdout test set, add new questions monthly, real user feedback

**5. Complexity Overkill**
- Maybe a single o3-pro or GPT-5 Pro is 90% as good for 20% of the cost
- **Mitigation:** A/B test council vs single model; kill the project if delta is <5%

### Simplifications to Consider

**If latency is unacceptable:**
- Reduce council to 2 models
- Make jury roles optional (user can request)
- Pre-compute answers for common questions

**If cost is unacceptable:**
- Use GPT-4.1 mini / Gemini 2.5 Flash for council
- Skip jury entirely for medium disagreement (only use for high)
- Implement aggressive caching
- Use o4-mini instead of o3 for jury roles

**If complexity is unmanageable:**
- Start with council + judge only
- Add jury only if Phase 1 proves insufficient

---

## 9. MCP INTEGRATION SPECIFICS

### MCP Server Endpoint

```
Tool name: llm_council_query
Description: "Execute multi-LLM research with adaptive depth"

Parameters:
{
  "query": string (required),
  "context": string (optional, additional background),
  "depth_mode": "auto" | "fast" | "deep" (optional, default "auto"),
  "domain": "general" | "medical" | "legal" | ... (optional, for future routing)
}

Returns:
{
  "answer": string (final synthesized response),
  "confidence": float (0-1),
  "uncertainty_level": "low" | "medium" | "high",
  "sources": [list of citations],
  "provenance": {
    "council_models": [...],
    "jury_triggered": bool,
    "routing_path": "FAST" | "MEDIUM" | "DEEP"
  },
  "warnings": [list of caveats],
  "job_id": string (for async polling if needed)
}
```

### Implementation Notes

- MCP server runs as a standalone process
- Orchestrates LLM calls via API clients (OpenAI SDK, Google Generative AI SDK)
- Returns structured JSON (no streaming for v1)
- Optional: Add streaming support in Phase 3 for better UX

---

## 10. FINAL RECOMMENDATIONS

### Do This
1. **Start with Phase 1 only.** Don't build jury layer until you prove council value.
2. **Measure everything.** Log every query, build dashboards week 1.
3. **A/B test against single model.** If council isn't ≥5% better, stop.
4. **Use real model names.** Update your model pool to actually available APIs.
5. **Enforce schemas strictly.** LLMs will drift; validation is non-negotiable.

### Don't Do This
1. **Don't use 5+ council models.** Diminishing returns, latency hell.
2. **Don't make jury roles redundant.** Three LLMs saying "looks good" is waste.
3. **Don't skip fast path.** Most queries don't need deep research.
4. **Don't ignore cost.** $15k/month happens fast; monitor from day 1.
5. **Don't over-engineer prompts.** Simple, clear instructions > clever tricks.

### Open Questions to Resolve
1. **Token budget per query?** Set hard limits or let it run?
2. **Human-in-the-loop?** Should judge ask user for clarification on ambiguous queries?
3. **Model version pinning?** Lock to specific versions or auto-upgrade?
4. **Cache invalidation?** How long do cached responses stay valid?

---

## APPENDIX: ASCII Data Flow

```
USER QUERY
    ↓
┌───────────────────┐
│  MCP SERVER       │
│  (FastAPI/etc)    │
└───────────────────┘
    ↓
┌───────────────────┐
│  ORCHESTRATOR     │
│  - Parse query    │
│  - Estimate depth │
└───────────────────┘
    ↓
┌─────────────────────────────────┐
│  COUNCIL (parallel)             │
│  ┌─────┐ ┌─────┐ ┌─────┐       │
│  │GPT-5│ │Gem3P│ │G2.5P│       │
│  └─────┘ └─────┘ └─────┘       │
│     ↓        ↓        ↓          │
│  [claim] [claim] [claim]        │
└─────────────────────────────────┘
    ↓
┌─────────────────────┐
│ DISAGREEMENT CALC   │
│ score = 0.65        │──→ routing = DEEP
└─────────────────────┘
    ↓
┌─────────────────────────────────┐
│  JURY (sequential)              │
│  ┌──────────────────────┐       │
│  │ Evidence Validator   │       │
│  └──────────────────────┘       │
│           ↓                      │
│  ┌──────────────────────┐       │
│  │ Logic Auditor        │       │
│  └──────────────────────┘       │
│           ↓                      │
│  ┌──────────────────────┐       │
│  │ Assumption Critic    │       │
│  └──────────────────────┘       │
└─────────────────────────────────┘
    ↓
┌─────────────────────┐
│  JUDGE (o3-pro)     │
│  - Synthesize       │
│  - Resolve conflicts│
│  - Calibrate conf.  │
└─────────────────────┘
    ↓
┌─────────────────────┐
│  FINAL RESPONSE     │
│  {answer, conf,...} │
└─────────────────────┘
    ↓
USER
```

---

**This is your implementation blueprint. Start with Phase 1, measure ruthlessly, and only add complexity if metrics justify it.**
