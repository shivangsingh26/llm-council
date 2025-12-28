# Phase 2: Research Depth Enhancements + Model Upgrades
## Implementation Checklist (Weeks 4-6)

---

## 🎯 PHASE 2 GOALS

**Primary Objectives:**
1. Upgrade council models to latest GPT-5/Gemini 3 generation
2. Implement 3-role Jury layer for deep analysis
3. Enhance 3-tier adaptive routing (FAST/MEDIUM/DEEP)
4. Improve research depth with validation & reasoning
5. Maintain Phase 1 performance targets

**Success Criteria:**
- ✅ Citation quality score > 0.8
- ✅ Edge case identification in ≥60% of complex queries
- ✅ No degradation in FAST path latency (< 8s)
- ✅ DEEP path latency < 30s (with full jury)
- ✅ Accuracy improvement ≥5% on complex queries

---

## 📋 WEEK 1: MODEL UPGRADES

### Task 1.1: Upgrade Council Models

**Current Models:**
- ✗ GPT-4o (older generation)
- ✗ Gemini 2.5 Flash (lightweight)
- ✗ DeepSeek-R1:14b (local)

**Target Models (from ARCHITECTURE.md):**
- ✓ GPT-5 (latest GPT model, strong general reasoning)
- ✓ Gemini 3 Pro (newest Google model, state-of-the-art multimodal)
- ✓ Gemini 2.5 Pro (specialized thinking model for code/math/STEM)

**Rationale:**
- Maximum diversity (OpenAI vs Google)
- Different specializations (general vs multimodal vs reasoning)
- Better performance on complex queries

**Implementation Steps:**
- [ ] 1.1.1 Create new agent classes
  - [ ] `src/agents/gpt5_agent.py` (OpenAI GPT-5)
  - [ ] `src/agents/gemini3_pro_agent.py` (Gemini 3 Pro)
  - [ ] `src/agents/gemini25_pro_agent.py` (Gemini 2.5 Pro)

- [ ] 1.1.2 Update model configurations
  - [ ] Add API endpoints for new models
  - [ ] Configure token limits and pricing
  - [ ] Set up structured output formats

- [ ] 1.1.3 Update ResearchService
  - [ ] Replace old agents with new ones
  - [ ] Update agent initialization logic
  - [ ] Maintain backward compatibility (keep old agents as fallback)

- [ ] 1.1.4 Test new agents
  - [ ] Unit tests for each agent
  - [ ] Integration test with council
  - [ ] Compare performance vs old models

**Deliverables:**
- ✓ 3 new agent classes
- ✓ Updated research service
- ✓ Test suite for new agents
- ✓ Performance comparison report

---

### Task 1.2: Upgrade Judge Model

**Current Judge:**
- ✗ o1-mini (in Master Synthesizer)

**Target Judge:**
- ✓ o3-pro (most intelligent reasoning model)
- ✓ Alternative: GPT-5 Pro (if cost/latency concern)

**Implementation Steps:**
- [ ] 1.2.1 Update MasterSynthesizer
  - [ ] Add o3-pro model support
  - [ ] Add GPT-5 Pro as fallback
  - [ ] Implement model selection logic

- [ ] 1.2.2 Enhanced conflict resolution
  - [ ] Priority hierarchy (evidence > consensus > jury validation)
  - [ ] Confidence calibration algorithm
  - [ ] Hallucination detection and penalties

- [ ] 1.2.3 Update prompts
  - [ ] Judge system prompt with jury integration
  - [ ] Conflict resolution rules
  - [ ] Uncertainty flagging instructions

**Deliverables:**
- ✓ o3-pro integration in synthesizer
- ✓ Enhanced conflict resolution
- ✓ Updated judge prompts

---

## 📋 WEEK 2: JURY LAYER IMPLEMENTATION

### Task 2.1: Core Jury Infrastructure

**Implementation Steps:**
- [ ] 2.1.1 Create jury base classes
  - [ ] `src/jury/__init__.py`
  - [ ] `src/jury/base_juror.py` (abstract base class)
  - [ ] Define JuryRole enum (EVIDENCE_VALIDATOR, LOGIC_AUDITOR, ASSUMPTION_CRITIC)

- [ ] 2.1.2 Define jury schemas
  - [ ] Update `src/models/schemas.py`:
    - [ ] `JuryValidation` (evidence validator output)
    - [ ] `JuryLogicAnalysis` (logic auditor output)
    - [ ] `JuryAssumptionCritique` (assumption critic output)
    - [ ] `JuryResult` (combined jury output)

- [ ] 2.1.3 Create JuryOrchestrator
  - [ ] `src/jury/orchestrator.py`
  - [ ] Sequential execution (Role 1 → Role 2 → Role 3)
  - [ ] Short-circuit logic (skip if critical issues found)
  - [ ] Error handling and fallbacks

**Deliverables:**
- ✓ Jury base infrastructure
- ✓ Jury schemas
- ✓ JuryOrchestrator

---

### Task 2.2: Role 1 - Evidence Validator

**Model:** o3 (advanced reasoning for verification)

**Responsibilities:**
- Verify sources exist and are correctly quoted
- Check for citation hallucinations
- Assess source quality (peer-reviewed > blog post)
- Flag missing evidence for strong claims

**Implementation Steps:**
- [ ] 2.2.1 Create EvidenceValidator class
  - [ ] `src/jury/evidence_validator.py`
  - [ ] Implements BaseJuror interface
  - [ ] Uses o3 model

- [ ] 2.2.2 Implement validation logic
  - [ ] Extract claims and evidence from council responses
  - [ ] Generate validation prompts
  - [ ] Parse validation results
  - [ ] Score source quality (0-1 scale)

- [ ] 2.2.3 Output schema
  ```python
  {
    "role": "evidence_validator",
    "validations": [
      {
        "claim_id": "c1",
        "evidence_status": "verified" | "unverifiable" | "contradicted",
        "issues": ["Source URL 404", "Quote not found"],
        "source_quality_score": 0.85
      }
    ]
  }
  ```

**Deliverables:**
- ✓ EvidenceValidator class
- ✓ Validation prompts
- ✓ Unit tests

---

### Task 2.3: Role 2 - Logic Auditor

**Model:** Gemini 2.5 Pro (specialized thinking model)

**Responsibilities:**
- Find logical contradictions between claims
- Check internal consistency
- Identify circular reasoning
- Flag non-sequiturs

**Implementation Steps:**
- [ ] 2.3.1 Create LogicAuditor class
  - [ ] `src/jury/logic_auditor.py`
  - [ ] Uses Gemini 2.5 Pro

- [ ] 2.3.2 Implement logic checking
  - [ ] Contradiction detection
  - [ ] Consistency verification
  - [ ] Reasoning chain validation

- [ ] 2.3.3 Output schema
  ```python
  {
    "role": "logic_auditor",
    "contradictions": [
      {
        "claim_ids": ["c1", "c5"],
        "conflict": "Claim c1 states X, but c5 implies not-X",
        "severity": "high" | "medium" | "low"
      }
    ],
    "reasoning_gaps": ["Conclusion doesn't follow from premises"]
  }
  ```

**Deliverables:**
- ✓ LogicAuditor class
- ✓ Logic checking algorithms
- ✓ Unit tests

---

### Task 2.4: Role 3 - Assumption Critic

**Model:** o4-mini (fast, cost-efficient reasoning)

**Responsibilities:**
- Surface hidden assumptions
- Test edge cases
- Find scenarios where claims fail
- Identify bias in framing

**Implementation Steps:**
- [ ] 2.4.1 Create AssumptionCritic class
  - [ ] `src/jury/assumption_critic.py`
  - [ ] Uses o4-mini

- [ ] 2.4.2 Implement assumption analysis
  - [ ] Extract explicit and hidden assumptions
  - [ ] Generate edge case scenarios
  - [ ] Bias detection
  - [ ] Robustness scoring

- [ ] 2.4.3 Output schema
  ```python
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

**Deliverables:**
- ✓ AssumptionCritic class
- ✓ Assumption extraction logic
- ✓ Unit tests

---

## 📋 WEEK 3: ENHANCED ROUTING & INTEGRATION

### Task 3.1: 3-Tier Adaptive Routing

**Current:** 2-tier (FAST vs DEEP)
**Target:** 3-tier (FAST/MEDIUM/DEEP)

**Routing Logic:**
```python
if disagreement_score < 0.3:
    path = "FAST"     # Council → Judge (no jury)
elif disagreement_score < 0.7:
    path = "MEDIUM"   # Council → Jury (2 roles) → Judge
else:
    path = "DEEP"     # Council → Jury (all 3 roles) → Judge
```

**Implementation Steps:**
- [ ] 3.1.1 Update AdaptiveRouter
  - [ ] Add MEDIUM path logic
  - [ ] Implement partial jury execution
  - [ ] Update routing thresholds (keep < 0.3 and > 0.7)

- [ ] 3.1.2 Define jury triggering rules
  - [ ] FAST: Skip jury entirely
  - [ ] MEDIUM: Evidence Validator + Logic Auditor only
  - [ ] DEEP: All 3 jury roles

- [ ] 3.1.3 Update latency targets
  - [ ] FAST: < 8s (no change)
  - [ ] MEDIUM: < 20s (council + 2 jury + judge)
  - [ ] DEEP: < 30s (council + 3 jury + judge)

**Deliverables:**
- ✓ 3-tier routing implementation
- ✓ Updated AdaptiveRouter
- ✓ Jury triggering logic

---

### Task 3.2: Judge Integration with Jury

**Enhanced Judge Capabilities:**
- Synthesize council + jury analysis
- Use jury findings for conflict resolution
- Calibrate confidence based on jury feedback
- Hallucination penalties from evidence validator

**Implementation Steps:**
- [ ] 3.2.1 Update MasterSynthesizer
  - [ ] Accept jury results as input
  - [ ] Integrate jury findings into synthesis prompt
  - [ ] Implement confidence calibration algorithm

- [ ] 3.2.2 Confidence calibration formula
  ```python
  base_confidence = weighted_average(council_confidences)

  # Adjustments from jury
  if jury_found_evidence_issues:
      base_confidence *= 0.7
  if logical_contradictions_found:
      base_confidence *= 0.6
  if council_high_agreement:
      base_confidence *= 1.1  # (capped at 1.0)
  if assumptions_untested:
      base_confidence *= 0.8

  final_confidence = clamp(base_confidence, 0.0, 1.0)
  ```

- [ ] 3.2.3 Conflict resolution with jury
  - [ ] Evidence quality priority (jury-verified > unverified)
  - [ ] Logic validation priority (no contradictions > contradictions)
  - [ ] Assumption robustness (tested > untested)

- [ ] 3.2.4 Hallucination handling
  - [ ] Downweight claims with evidence issues
  - [ ] Add warnings to final output
  - [ ] Log hallucinations for metrics

**Deliverables:**
- ✓ Judge + jury integration
- ✓ Confidence calibration
- ✓ Enhanced conflict resolution

---

### Task 3.3: Update Orchestrator

**Integration Points:**
- Council → Disagreement Analyzer → Router → Jury (if needed) → Judge

**Implementation Steps:**
- [ ] 3.3.1 Update CouncilOrchestrator
  - [ ] Add jury orchestrator integration
  - [ ] Update `research_with_routing` method
  - [ ] Add jury phase to latency breakdown

- [ ] 3.3.2 Execution flow
  ```python
  # 1. Council (parallel)
  council_responses = await council.research_all(...)

  # 2. Disagreement analysis
  disagreement = await analyzer.calculate_disagreement(council_responses)

  # 3. Routing decision
  path = router.determine_path(disagreement.score)

  # 4. Jury (conditional)
  jury_result = None
  if path in ["MEDIUM", "DEEP"]:
      jury_result = await jury_orchestrator.execute(
          council_responses,
          path
      )

  # 5. Judge synthesis
  final_answer = await judge.synthesize(
      council_responses,
      jury_result
  )
  ```

- [ ] 3.3.3 Update response schema
  - [ ] Add jury_triggered field
  - [ ] Add jury_findings field
  - [ ] Add research_depth_metrics

**Deliverables:**
- ✓ Updated orchestrator
- ✓ Jury integration in flow
- ✓ Enhanced response schema

---

## 📋 TESTING & VALIDATION

### Task 4.1: Unit Tests

- [ ] 4.1.1 Jury layer tests
  - [ ] test_evidence_validator.py (10 tests)
  - [ ] test_logic_auditor.py (10 tests)
  - [ ] test_assumption_critic.py (10 tests)
  - [ ] test_jury_orchestrator.py (8 tests)

- [ ] 4.1.2 New agent tests
  - [ ] test_gpt5_agent.py
  - [ ] test_gemini3_pro_agent.py
  - [ ] test_gemini25_pro_agent.py

- [ ] 4.1.3 Integration tests
  - [ ] test_3tier_routing.py
  - [ ] test_jury_integration.py
  - [ ] test_judge_with_jury.py

**Target:** 70+ tests total

---

### Task 4.2: Performance Validation

- [ ] 4.2.1 Latency benchmarks
  - [ ] FAST path: < 8s (maintain Phase 1 performance)
  - [ ] MEDIUM path: < 20s
  - [ ] DEEP path: < 30s

- [ ] 4.2.2 Quality metrics
  - [ ] Citation quality score > 0.8
  - [ ] Edge case identification ≥60%
  - [ ] Accuracy improvement ≥5% on complex queries

- [ ] 4.2.3 Create test dataset
  - [ ] 50 complex queries requiring deep analysis
  - [ ] Queries with known edge cases
  - [ ] Queries requiring evidence validation

---

### Task 4.3: Research Depth Metrics

**Implement tracking for:**
- [ ] 4.3.1 Citation metrics
  - [ ] Citation count per response
  - [ ] Source diversity
  - [ ] Source quality scores

- [ ] 4.3.2 Research depth metrics
  - [ ] Assumption coverage (% surfaced)
  - [ ] Edge case identification count
  - [ ] Nuance score (1-5 scale)

- [ ] 4.3.3 Jury effectiveness
  - [ ] Evidence issues caught
  - [ ] Logic contradictions found
  - [ ] Hidden assumptions surfaced

---

## 📋 BACKEND & FRONTEND UPDATES

### Task 5.1: Backend Integration

- [ ] 5.1.1 Update ResearchService
  - [ ] Integrate new council models
  - [ ] Add jury orchestrator
  - [ ] Update response building

- [ ] 5.1.2 Update API schemas
  - [ ] Add jury_triggered field
  - [ ] Add jury_findings field
  - [ ] Add research_depth_metrics
  - [ ] Update latency_breakdown (add jury_phase_ms)

- [ ] 5.1.3 Update database models
  - [ ] Add jury metadata fields
  - [ ] Add research depth metrics fields

---

### Task 5.2: Frontend Visualization

- [ ] 5.2.1 Update ResultsDisplay component
  - [ ] Add jury analysis section
  - [ ] Show evidence validation status
  - [ ] Display logic contradictions
  - [ ] Show hidden assumptions

- [ ] 5.2.2 Enhanced routing metrics
  - [ ] Update routing badge (now 3 options)
  - [ ] Add MEDIUM path visualization
  - [ ] Show jury phase in latency breakdown

- [ ] 5.2.3 Research depth indicators
  - [ ] Citation quality score
  - [ ] Edge case count
  - [ ] Assumption coverage

---

## 📋 DOCUMENTATION

### Task 6.1: Update Documentation

- [ ] 6.1.1 README updates
  - [ ] Add Phase 2 features
  - [ ] Update model list
  - [ ] Add jury layer explanation
  - [ ] Update architecture diagram

- [ ] 6.1.2 ARCHITECTURE.md
  - [ ] Mark Phase 2 as complete
  - [ ] Add implementation notes
  - [ ] Document lessons learned

- [ ] 6.1.3 Create PHASE_2_RESULTS.md
  - [ ] Performance metrics
  - [ ] Quality improvements
  - [ ] Cost analysis
  - [ ] Next steps

---

## 📊 SUCCESS METRICS

### Must-Haves (Block Phase 3):
- ✅ All 3 jury roles implemented and tested
- ✅ 3-tier routing working correctly
- ✅ FAST path latency maintained (< 8s)
- ✅ DEEP path latency < 30s
- ✅ Citation quality score > 0.8
- ✅ 70+ tests passing
- ✅ No regressions in Phase 1 functionality

### Nice-to-Haves (Can defer):
- ⭐ Edge case identification ≥80% (target: 60%)
- ⭐ DEEP path latency < 25s (target: 30s)
- ⭐ Accuracy improvement ≥7% (target: 5%)

---

## 🚨 RISKS & MITIGATIONS

### Risk 1: Latency Explosion
**Problem:** Jury + enhanced judge could push DEEP path > 30s
**Mitigation:**
- Make jury roles lightweight (max 2s each)
- Parallel where possible
- Aggressive short-circuiting

### Risk 2: Cost Increase
**Problem:** More models = higher cost per query
**Mitigation:**
- FAST path handles 70%+ queries (no jury cost)
- Use o4-mini for assumption critic (cheaper)
- Monitor cost metrics daily

### Risk 3: Complexity
**Problem:** 3 jury roles + enhanced routing = complex system
**Mitigation:**
- Comprehensive testing
- Clear error messages
- Fallback to Phase 1 behavior if jury fails

---

## 📅 TIMELINE

**Week 1 (Days 1-7):**
- Days 1-3: Model upgrades (council + judge)
- Days 4-5: Testing new models
- Days 6-7: Judge enhancement

**Week 2 (Days 8-14):**
- Days 8-9: Jury infrastructure
- Days 10-11: Evidence validator
- Days 12: Logic auditor
- Days 13-14: Assumption critic

**Week 3 (Days 15-21):**
- Days 15-16: 3-tier routing
- Days 17-18: Judge + jury integration
- Days 19-20: Testing & validation
- Day 21: Documentation & deployment

---

## ✅ DEFINITION OF DONE

Phase 2 is complete when:
- [ ] All 70+ tests passing
- [ ] All latency targets met
- [ ] All quality metrics met
- [ ] Documentation updated
- [ ] Demo prepared
- [ ] Code reviewed and merged
- [ ] Production deployment successful

---

**Let's build Phase 2! 🚀**
