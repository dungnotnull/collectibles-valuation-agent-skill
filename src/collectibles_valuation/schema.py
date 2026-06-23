# -*- coding: utf-8 -*-
"""Canonical schemas for the collectibles-valuation harness.

All data structures are plain dataclasses so the core engine has zero
third-party runtime dependencies.  They serialize to JSON-compatible
dictionaries via :func:`serialize` for interop with skill runtimes,
web front ends, and regression tests.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class Category(Enum):
    COIN = "coin"
    STAMP = "stamp"
    WATCH = "watch"
    CARD = "trading_card"
    ANTIQUE = "antique"


class ValuationPurpose(Enum):
    SALE = "sale"
    INSURANCE = "insurance"
    ESTATE = "estate"
    APPRAISAL = "appraisal"
    AUTHENTICATION = "authentication"


class GradingScale(Enum):
    SHELDON_70 = "sheldon_70"
    PSA_10 = "psa_10"
    BGS_10 = "bgs_10"
    CGC_10 = "cgc_10"
    APS_STAMP = "aps_stamp"
    NAWCC_WATCH = "nawcc_watch"
    ISA_QUALITATIVE = "isa_qualitative"


class FrameworkName(Enum):
    SHELDON_PCGS_NGC = "Sheldon Coin Grading Scale / PCGS-NGC"
    PSA_BGS_CGC = "PSA/BGS/CGC card grading"
    APS_SCOTT = "APS philatelic grading & Scott catalogue"
    NAWCC = "NAWCC watch condition grading"
    ISA_USPAP = "ISA/USPAP appraisal principles"
    COMPARABLE_SALES = "Comparable-sales market approach"


class ValuationApproach(Enum):
    MARKET = "market"
    COST = "cost"
    INCOME = "income"


class ConfidenceBand(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Dimension(Enum):
    RARITY = "rarity"
    CONDITION = "condition"
    AUTHENTICITY = "authenticity"
    DEMAND = "demand"
    PROVENANCE = "provenance"


class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Effort(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ConditionEvidence:
    raw_grade_value: Optional[float] = None
    scale: Optional[GradingScale] = None
    textual_description: Optional[str] = None
    defects: List[str] = field(default_factory=list)
    photos_available: bool = False


@dataclass
class ProvenanceEvidence:
    chain_of_custody: List[str] = field(default_factory=list)
    receipts: List[str] = field(default_factory=list)
    certificates: List[str] = field(default_factory=list)
    exhibition_history: List[str] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class IntakeProfile:
    category: Category
    item_name: str
    description: str
    purpose: ValuationPurpose
    condition: ConditionEvidence
    provenance: ProvenanceEvidence
    acquisition_history: Optional[str] = None
    authentication: List[str] = field(default_factory=list)
    market_signals: List[str] = field(default_factory=list)
    rarity_signals: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    requested_currency: str = "USD"
    missing_fields: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FrameworkSelection:
    category: Category
    frameworks: List[FrameworkName]
    primary_scale: GradingScale
    valuation_approaches: List[ValuationApproach]
    justification: str


@dataclass
class DimensionScore:
    dimension: Dimension
    score: float
    weight: float
    justification: str
    citations: List[str] = field(default_factory=list)


@dataclass
class Scorecard:
    dimensions: List[DimensionScore]
    composite: float
    confidence: ConfidenceBand
    value_index: float
    value_range_low: Optional[float] = None
    value_range_high: Optional[float] = None
    currency: str = "USD"
    assumptions: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)


@dataclass
class RoadmapAction:
    action: str
    rationale: str
    effort: Effort
    impact: Priority
    expected_effect: str
    owner: str
    dimension: Optional[Dimension] = None
    priority_score: float = 0.0


@dataclass
class ValuationReport:
    status: str
    subject: str
    purpose: ValuationPurpose
    framework: FrameworkSelection
    scorecard: Scorecard
    roadmap: List[RoadmapAction]
    quality_gate_checklist: Dict[str, bool]
    devil_advocate_notes: List[str]
    sources: List[str]
    assumptions: List[str]
    limitations: List[str]
    next_questions: List[str] = field(default_factory=list)


def _serialize(obj: Any) -> Any:
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, list):
        return [_serialize(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _serialize(v) for k, v in asdict(obj).items()}
    return obj


def serialize(obj: Any) -> Any:
    """Convert any dataclass / enum / nested structure into JSON-safe primitives."""
    return _serialize(obj)


def report_to_json(report: ValuationReport) -> Dict[str, Any]:
    """Serialize a full valuation report to a JSON-compatible dict."""
    return serialize(report)
