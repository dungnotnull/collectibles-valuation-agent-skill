# -*- coding: utf-8 -*-
"""Multi-dimensional scoring engine.

Translates a validated intake profile and selected framework into five
0-100 dimension scores, a weighted composite, a confidence band, and a
defensible value index / range.  Every score surfaces the framework
criterion or evidence source it rests on.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from .frameworks import (
    authenticity_score,
    demand_score,
    normalize_condition_score,
    provenance_score,
    rarity_score,
)
from .schema import (
    ConfidenceBand,
    Dimension,
    DimensionScore,
    FrameworkSelection,
    IntakeProfile,
    Scorecard,
    ValuationApproach,
    ValuationPurpose,
)


PURPOSE_WEIGHTS: dict[ValuationPurpose, dict[Dimension, float]] = {
    ValuationPurpose.SALE: {
        Dimension.CONDITION: 0.25,
        Dimension.RARITY: 0.15,
        Dimension.AUTHENTICITY: 0.25,
        Dimension.DEMAND: 0.25,
        Dimension.PROVENANCE: 0.10,
    },
    ValuationPurpose.INSURANCE: {
        Dimension.CONDITION: 0.25,
        Dimension.RARITY: 0.10,
        Dimension.AUTHENTICITY: 0.20,
        Dimension.DEMAND: 0.15,
        Dimension.PROVENANCE: 0.30,
    },
    ValuationPurpose.ESTATE: {
        Dimension.CONDITION: 0.20,
        Dimension.RARITY: 0.20,
        Dimension.AUTHENTICITY: 0.20,
        Dimension.DEMAND: 0.20,
        Dimension.PROVENANCE: 0.20,
    },
    ValuationPurpose.APPRAISAL: {
        Dimension.CONDITION: 0.22,
        Dimension.RARITY: 0.18,
        Dimension.AUTHENTICITY: 0.20,
        Dimension.DEMAND: 0.20,
        Dimension.PROVENANCE: 0.20,
    },
    ValuationPurpose.AUTHENTICATION: {
        Dimension.AUTHENTICITY: 0.50,
        Dimension.PROVENANCE: 0.20,
        Dimension.CONDITION: 0.15,
        Dimension.RARITY: 0.10,
        Dimension.DEMAND: 0.05,
    },
}

VOLATILITY_BY_CONFIDENCE = {
    ConfidenceBand.HIGH: 0.15,
    ConfidenceBand.MEDIUM: 0.30,
    ConfidenceBand.LOW: 0.55,
}


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def build_scorecard(profile: IntakeProfile, framework: FrameworkSelection) -> Scorecard:
    """Create a defensible scorecard for the subject."""
    weights = PURPOSE_WEIGHTS.get(profile.purpose, PURPOSE_WEIGHTS[ValuationPurpose.APPRAISAL])

    condition, condition_reason, condition_citations = normalize_condition_score(
        profile.condition, profile.category
    )
    rarity, rarity_reason, rarity_citations = rarity_score(
        profile.category, profile.rarity_signals, {"item_name": profile.item_name, **profile.metadata}
    )
    auth, auth_reason, auth_citations = authenticity_score(
        profile.category,
        profile.authentication,
        serialize_provenance(profile.provenance),
        profile.red_flags,
        profile.condition.photos_available,
        profile.metadata,
    )
    demand, demand_reason, demand_citations = demand_score(
        profile.category, profile.market_signals, profile.metadata
    )
    prov, prov_reason, prov_citations = provenance_score(
        serialize_provenance(profile.provenance), profile.metadata
    )

    dimensions = [
        DimensionScore(
            dimension=Dimension.CONDITION,
            score=_clamp(condition),
            weight=weights[Dimension.CONDITION],
            justification=condition_reason,
            citations=condition_citations,
        ),
        DimensionScore(
            dimension=Dimension.RARITY,
            score=_clamp(rarity),
            weight=weights[Dimension.RARITY],
            justification=rarity_reason,
            citations=rarity_citations,
        ),
        DimensionScore(
            dimension=Dimension.AUTHENTICITY,
            score=_clamp(auth),
            weight=weights[Dimension.AUTHENTICITY],
            justification=auth_reason,
            citations=auth_citations,
        ),
        DimensionScore(
            dimension=Dimension.DEMAND,
            score=_clamp(demand),
            weight=weights[Dimension.DEMAND],
            justification=demand_reason,
            citations=demand_citations,
        ),
        DimensionScore(
            dimension=Dimension.PROVENANCE,
            score=_clamp(prov),
            weight=weights[Dimension.PROVENANCE],
            justification=prov_reason,
            citations=prov_citations,
        ),
    ]

    composite = sum(d.score * d.weight for d in dimensions)
    confidence = _determine_confidence(profile, framework, dimensions)
    value_index = _clamp(composite)
    value_low, value_high = _value_range(profile, value_index, confidence)

    assumptions = _build_assumptions(profile, framework)
    limitations = _build_limitations(profile, framework, dimensions)

    return Scorecard(
        dimensions=dimensions,
        composite=round(composite, 2),
        confidence=confidence,
        value_index=round(value_index, 2),
        value_range_low=value_low,
        value_range_high=value_high,
        currency=profile.requested_currency,
        assumptions=assumptions,
        limitations=limitations,
    )


def _determine_confidence(
    profile: IntakeProfile, framework: FrameworkSelection, dimensions: List[DimensionScore]
) -> ConfidenceBand:
    """Set confidence band based on missing data, photos, and score volatility."""
    if profile.missing_fields:
        return ConfidenceBand.LOW
    if not profile.condition.photos_available:
        return ConfidenceBand.LOW
    if any(d.score < 30 for d in dimensions):
        return ConfidenceBand.LOW
    if any(d.citations and "fallback" in " ".join(d.citations).lower() for d in dimensions):
        return ConfidenceBand.MEDIUM
    if any(d.score < 50 for d in dimensions):
        return ConfidenceBand.MEDIUM
    return ConfidenceBand.HIGH


def _value_range(profile: IntakeProfile, value_index: float, confidence: ConfidenceBand) -> Tuple[Optional[float], Optional[float]]:
    """Translate the synthetic value index into a monetary range if a base value
    is supplied, otherwise leave it for live comparables to fill.
    """
    base = profile.metadata.get("base_value")
    if base is None:
        return None, None
    factor = VOLATILITY_BY_CONFIDENCE[confidence]
    midpoint = float(base) * (value_index / 100.0)
    return round(midpoint * (1.0 - factor), 2), round(midpoint * (1.0 + factor), 2)


def _build_assumptions(profile: IntakeProfile, framework: FrameworkSelection) -> List[str]:
    assumptions = [
        f"Framework: {framework.frameworks[0].value}",
        f"Valuation purpose: {profile.purpose.value}",
        f"Currency: {profile.requested_currency}",
    ]
    if not profile.condition.photos_available:
        assumptions.append("Visual assessment is based on the provided description only; photos not reviewed.")
    if framework.valuation_approaches and framework.valuation_approaches[0] == ValuationApproach.COST:
        assumptions.append("Value is oriented toward replacement cost / fair-market replacement rather than speculative resale.")
    return assumptions


def _build_limitations(
    profile: IntakeProfile, framework: FrameworkSelection, dimensions: List[DimensionScore]
) -> List[str]:
    limitations = []
    if framework.category.value in ("coin", "card", "stamp", "watch"):
        limitations.append("No in-hand inspection; grading is an estimate pending professional submission.")
    if any(d.score < 40 for d in dimensions):
        limitations.append("One or more dimensions score below 40, widening the uncertainty band.")
    if not profile.metadata.get("base_value"):
        limitations.append("No base market value supplied; monetary range requires comparable-sales research.")
    return limitations


def serialize_provenance(provenance) -> dict:
    """Convert a ProvenanceEvidence dataclass or dict into a plain dict."""
    if hasattr(provenance, "__dataclass_fields__"):
        from dataclasses import asdict
        return asdict(provenance)
    return dict(provenance)

