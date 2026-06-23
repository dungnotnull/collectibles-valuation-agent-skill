# -*- coding: utf-8 -*-
"""collectibles-valuation: a research-first, framework-grounded collectibles
valuation harness for coins, stamps, watches, trading cards, and antiques.
"""
from .devils_advocate import run_quality_gate
from .frameworks import select_frameworks
from .intake import build_intake
from .orchestrator import ValuationHarness
from .roadmap import build_roadmap
from .scoring import build_scorecard
from .schema import (
    Category,
    ConditionEvidence,
    ConfidenceBand,
    Dimension,
    DimensionScore,
    Effort,
    FrameworkName,
    FrameworkSelection,
    GradingScale,
    IntakeProfile,
    Priority,
    ProvenanceEvidence,
    RoadmapAction,
    Scorecard,
    ValuationApproach,
    ValuationPurpose,
    ValuationReport,
    report_to_json,
    serialize,
)

__version__ = "0.1.0"

__all__ = [
    "Category",
    "ConditionEvidence",
    "ConfidenceBand",
    "Dimension",
    "DimensionScore",
    "Effort",
    "FrameworkName",
    "FrameworkSelection",
    "GradingScale",
    "IntakeProfile",
    "Priority",
    "ProvenanceEvidence",
    "RoadmapAction",
    "Scorecard",
    "ValuationApproach",
    "ValuationHarness",
    "ValuationPurpose",
    "ValuationReport",
    "build_intake",
    "build_roadmap",
    "build_scorecard",
    "report_to_json",
    "run_quality_gate",
    "select_frameworks",
    "serialize",
]
