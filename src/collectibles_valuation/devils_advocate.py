# -*- coding: utf-8 -*-
"""Devil's advocate quality gate.

Before any valuation is emitted, this module challenges the framework
choice, every dimension score, and every roadmap action.  It returns a
pass/fail checklist and concrete revisions for the report.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from .schema import Dimension, FrameworkSelection, IntakeProfile, RoadmapAction, Scorecard, ValuationReport


def run_quality_gate(
    profile: IntakeProfile, framework: FrameworkSelection, scorecard: Scorecard, roadmap: List[RoadmapAction]
) -> Tuple[Dict[str, bool], List[str]]:
    """Run the quality gate and return a checklist plus devil's-advocate notes."""
    checks: Dict[str, bool] = {}
    notes: List[str] = []

    checks["framework_selection_justified"] = bool(framework.justification)
    if not framework.justification:
        notes.append("FAIL: framework selection lacks a written justification.")

    checks["scores_have_citations"] = all(bool(d.citations) for d in scorecard.dimensions)
    if not checks["scores_have_citations"]:
        missing = [d.dimension.value for d in scorecard.dimensions if not d.citations]
        notes.append(f"FAIL: dimensions without citations: {', '.join(missing)}")

    checks["roadmap_has_effort_and_impact"] = all(
        a.effort is not None and a.impact is not None and a.rationale for a in roadmap
    )
    if not checks["roadmap_has_effort_and_impact"]:
        notes.append("FAIL: one or more roadmap actions missing effort/impact/rationale.")

    checks["assumptions_stated"] = bool(scorecard.assumptions)
    checks["limitations_stated"] = bool(scorecard.limitations)
    if not checks["assumptions_stated"]:
        notes.append("FAIL: assumptions not stated.")
    if not checks["limitations_stated"]:
        notes.append("FAIL: limitations not stated.")

    checks["devils_advocate_completed"] = True
    notes.extend(_challenge_scores(scorecard))
    notes.extend(_challenge_roadmap(roadmap))
    notes.extend(_challenge_framework(profile, framework))

    # Composite pass rule: all hard gates must be true.
    checks["all_gates_pass"] = all(
        checks[k]
        for k in [
            "framework_selection_justified",
            "scores_have_citations",
            "roadmap_has_effort_and_impact",
            "assumptions_stated",
            "limitations_stated",
            "devils_advocate_completed",
        ]
    )

    return checks, notes


def _challenge_scores(scorecard: Scorecard) -> List[str]:
    notes = ["DEVIL'S ADVOCATE — scores:"]
    for d in scorecard.dimensions:
        notes.append(
            f"- {d.dimension.value}: score={d.score:.1f}, weight={d.weight:.2f}. "
            f"Could the opposite interpretation of the evidence lower this by 20 points?"
        )
        if d.score > 85 and any("fallback" in c.lower() for c in d.citations):
            notes.append(
                f"  WARNING: {d.dimension.value} is high but rests partly on a fallback assumption; "
                f"revise or disclose lower-confidence band."
            )
        if d.score < 30:
            notes.append(
                f"  FLAG: {d.dimension.value} is critically low; value range must reflect wide uncertainty."
            )
    return notes


def _challenge_roadmap(roadmap: List[RoadmapAction]) -> List[str]:
    notes = ["DEVIL'S ADVOCATE — roadmap:"]
    if not roadmap:
        notes.append("- WARNING: roadmap is empty; is there genuinely nothing to improve?")
        return notes
    for a in roadmap:
        notes.append(
            f"- '{a.action}' (impact={a.impact.value}, effort={a.effort.value}). "
            f"What if cost exceeds expected uplift? What evidence supports the effect?"
        )
    return notes


def _challenge_framework(profile: IntakeProfile, framework: FrameworkSelection) -> List[str]:
    notes = ["DEVIL'S ADVOCATE — framework:"]
    notes.append(
        f"- Selected {framework.frameworks[0].value} for {profile.category.value}. "
        f"Could a hybrid approach (e.g., adding {framework.frameworks[-1].value}) better capture value?"
    )
    if profile.purpose.value == "insurance":
        notes.append(
            "- Insurance valuation: confirm that replacement cost, not fair-market speculation, is used."
        )
    if profile.purpose.value == "sale":
        notes.append(
            "- Sale valuation: confirm that the selected comparables are recent, matched, and arms-length."
        )
    return notes
