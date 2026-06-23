# -*- coding: utf-8 -*-
"""Improvement-roadmap generator.

Produces a prioritized list of concrete next actions ranked by value uplift
versus cost.  Each action names an owner, a dimension, and the expected
effect on the valuation.
"""
from __future__ import annotations

from typing import List

from .schema import Category, Dimension, Effort, IntakeProfile, Priority, RoadmapAction, Scorecard


EFFORT_COST = {Effort.LOW: 0.5, Effort.MEDIUM: 1.5, Effort.HIGH: 2.5}
IMPACT_WEIGHT = {Priority.CRITICAL: 4.0, Priority.HIGH: 3.0, Priority.MEDIUM: 2.0, Priority.LOW: 1.0}

GRADING_SERVICE = {
    Category.COIN: "PCGS or NGC",
    Category.CARD: "PSA, BGS, or CGC",
    Category.STAMP: "APS or Philatelic Foundation expertizing",
    Category.WATCH: "NAWCC-accredited watchmaker/auction specialist",
    Category.ANTIQUE: "ISA/AAA-accredited appraiser",
}

AUTHORITY = {
    Category.COIN: "PCGS/NGC or a reputable numismatist",
    Category.CARD: "PSA/BGS/CGC or a trading-card expert",
    Category.STAMP: "APS expertization service",
    Category.WATCH: "NAWCC specialist or brand service center",
    Category.ANTIQUE: "ISA-accredited appraiser or specialty dealer",
}


def build_roadmap(profile: IntakeProfile, scorecard: Scorecard) -> List[RoadmapAction]:
    """Create a prioritized improvement roadmap based on scorecard gaps."""
    actions: List[RoadmapAction] = []
    dim_scores = {d.dimension: d.score for d in scorecard.dimensions}

    # Condition / grading
    if dim_scores[Dimension.CONDITION] < 70 or profile.condition.raw_grade_value is None:
        actions.append(_action(
            profile,
            f"Submit to {GRADING_SERVICE[profile.category]} for professional grading/condition documentation",
            f"Current condition score {dim_scores[Dimension.CONDITION]:.0f} is below the threshold for confident pricing; "
            f"{GRADING_SERVICE[profile.category]} provides a market-recognized grade.",
            Effort.MEDIUM,
            Priority.HIGH,
            "Improves condition-score precision and narrows value range.",
            Dimension.CONDITION,
        ))

    # Authenticity
    if dim_scores[Dimension.AUTHENTICITY] < 70 or profile.red_flags:
        priority = Priority.CRITICAL if profile.red_flags else Priority.HIGH
        actions.append(_action(
            profile,
            f"Obtain authentication/certification from {AUTHORITY[profile.category]}",
            f"Authenticity confidence is {dim_scores[Dimension.AUTHENTICITY]:.0f}/100; "
            f"third-party authentication resolves the largest risk to value.",
            Effort.MEDIUM,
            priority,
            "Removes authenticity risk; often required for high-value transactions.",
            Dimension.AUTHENTICITY,
        ))

    # Provenance
    if dim_scores[Dimension.PROVENANCE] < 60:
        actions.append(_action(
            profile,
            "Compile chain-of-custody documentation (receipts, prior auction records, certificates)",
            f"Provenance score {dim_scores[Dimension.PROVENANCE]:.0f} is weak; documented ownership history supports both value and authenticity.",
            Effort.LOW,
            Priority.MEDIUM,
            "Increases provenance score and supports insurance/estate claims.",
            Dimension.PROVENANCE,
        ))

    # Demand / comparables
    if dim_scores[Dimension.DEMAND] < 60 or not profile.market_signals:
        actions.append(_action(
            profile,
            "Research comparable sales (Heritage Auctions, Sotheby's, eBay sold listings, catalogue records)",
            "Market evidence is required for a defensible value range.",
            Effort.LOW,
            Priority.HIGH,
            "Supplies demand/liquidity score and enables monetary value estimate.",
            Dimension.DEMAND,
        ))

    # Purpose-specific actions
    if profile.purpose.value == "insurance":
        actions.append(_action(
            profile,
            "Obtain a formal replacement-cost appraisal documented to USPAP/ISA standards",
            "Insurance scheduling requires replacement-value documentation and photographs.",
            Effort.MEDIUM,
            Priority.CRITICAL,
            "Provides carrier-accepted documentation for scheduled coverage.",
            Dimension.PROVENANCE,
        ))
    elif profile.purpose.value == "sale":
        actions.append(_action(
            profile,
            "Select optimal sale channel (specialty auction, dealer consignment, or marketplace)",
            "Channel choice materially affects realized price and liquidity.",
            Effort.LOW,
            Priority.HIGH,
            "Maximizes net proceeds given demand signals and item rarity.",
            Dimension.DEMAND,
        ))

    # Fraud / red-flag override
    if profile.red_flags:
        actions.insert(
            0,
            _action(
                profile,
                "Halt transaction and engage a forensic expert or law enforcement if fraud is suspected",
                f"Red flags present: {', '.join(profile.red_flags)}.  Proceeding without verification risks financial loss.",
                Effort.LOW,
                Priority.CRITICAL,
                "Prevents loss; preserves evidence for investigation.",
                Dimension.AUTHENTICITY,
            ),
        )

    return sorted(actions, key=lambda a: a.priority_score, reverse=True)


def _action(
    profile: IntakeProfile,
    action: str,
    rationale: str,
    effort: Effort,
    impact: Priority,
    expected_effect: str,
    dimension: Dimension,
) -> RoadmapAction:
    urgency = 2.0 if impact == Priority.CRITICAL else 0.0
    score = IMPACT_WEIGHT[impact] - EFFORT_COST[effort] + urgency
    owner = "Owner/Collector"
    if "grading" in action.lower() or "authentication" in action.lower():
        owner = "Professional third-party service"
    elif "auction" in action.lower() or "dealer" in action.lower():
        owner = "Owner with auction-house/dealer support"
    elif "insurance" in action.lower() or "appraisal" in action.lower():
        owner = "ISA/AAA-accredited appraiser"
    elif "forensic" in action.lower():
        owner = "Forensic expert / law enforcement"

    return RoadmapAction(
        action=action,
        rationale=rationale,
        effort=effort,
        impact=impact,
        expected_effect=expected_effect,
        owner=owner,
        dimension=dimension,
        priority_score=round(score, 2),
    )
