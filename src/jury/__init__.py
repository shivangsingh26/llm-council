"""
Jury Layer: Specialist agents for deep analysis and validation.

The jury consists of three specialized roles:
1. Evidence Validator: Verifies sources and citations
2. Logic Auditor: Checks reasoning consistency
3. Assumption Critic: Challenges assumptions and finds edge cases

Invoked on DEEP path when disagreement > 0.7.
"""

from src.jury.base_juror import BaseJuror, JuryRole
from src.jury.evidence_validator import EvidenceValidator
from src.jury.logic_auditor import LogicAuditor
from src.jury.assumption_critic import AssumptionCritic
from src.jury.orchestrator import JuryOrchestrator

__all__ = [
    "BaseJuror",
    "JuryRole",
    "EvidenceValidator",
    "LogicAuditor",
    "AssumptionCritic",
    "JuryOrchestrator",
]
