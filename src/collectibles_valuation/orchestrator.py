# -*- coding: utf-8 -*-
"""End-to-end valuation harness.

Wires intake → framework selection → scoring → roadmap → devil's advocate
into a single deterministic, reproducible report.  The same harness is
described in the skill instructions so human/AI runtimes stay aligned.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .devils_advocate import run_quality_gate
from .frameworks import select_frameworks
from .intake import build_intake
from .roadmap import build_roadmap
from .schema import (
    FrameworkSelection,
    IntakeProfile,
    RoadmapAction,
    Scorecard,
    ValuationPurpose,
    ValuationReport,
    serialize,
)
from .scoring import build_scorecard


class ValuationHarness:
    """Production harness for collectibles valuation."""

    def run(self, raw_input: Dict[str, Any]) -> ValuationReport:
        """Execute the full harness on a raw intake payload."""
        profile = build_intake(raw_input)

        if profile.missing_fields:
            framework = self._placeholder_framework(profile)
            return self._incomplete_report(profile, framework)

        framework = self._select_framework(profile)
        scorecard = build_scorecard(profile, framework)
        roadmap = build_roadmap(profile, scorecard)
        checks, notes = run_quality_gate(profile, framework, scorecard, roadmap)

        sources = self._collect_sources(framework, scorecard, roadmap)

        return ValuationReport(
            status="complete" if checks.get("all_gates_pass") else "complete_with_gate_warnings",
            subject=profile.item_name,
            purpose=profile.purpose,
            framework=framework,
            scorecard=scorecard,
            roadmap=roadmap,
            quality_gate_checklist=checks,
            devil_advocate_notes=notes,
            sources=sources,
            assumptions=scorecard.assumptions,
            limitations=scorecard.limitations,
            next_questions=[],
        )

    def run_to_json(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """Run the harness and return a JSON-serializable report."""
        return serialize(self.run(raw_input))

    @staticmethod
    def _select_framework(profile: IntakeProfile) -> FrameworkSelection:
        frameworks, approaches, scale, justification = select_frameworks(profile.category, profile.purpose)
        return FrameworkSelection(
            category=profile.category,
            frameworks=frameworks,
            primary_scale=scale,
            valuation_approaches=approaches,
            justification=justification,
        )

    @staticmethod
    def _placeholder_framework(profile: IntakeProfile) -> FrameworkSelection:
        frameworks, approaches, scale, justification = select_frameworks(
            profile.category, profile.purpose or ValuationPurpose.APPRAISAL
        )
        return FrameworkSelection(
            category=profile.category,
            frameworks=frameworks,
            primary_scale=scale,
            valuation_approaches=approaches,
            justification=justification,
        )

    @staticmethod
    def _incomplete_report(profile: IntakeProfile, framework: FrameworkSelection) -> ValuationReport:
        from .schema import Scorecard

        empty_scorecard = Scorecard(
            dimensions=[],
            composite=0.0,
            confidence=None,  # type: ignore[arg-type]
            value_index=0.0,
            currency=profile.requested_currency,
            assumptions=["Intake incomplete; assumptions cannot be finalized."],
            limitations=["Cannot score until required fields are provided."],
        )
        return ValuationReport(
            status="incomplete",
            subject=profile.item_name or "unknown subject",
            purpose=profile.purpose or ValuationPurpose.APPRAISAL,
            framework=framework,
            scorecard=empty_scorecard,
            roadmap=[],
            quality_gate_checklist={
                "framework_selection_justified": True,
                "scores_have_citations": False,
                "roadmap_has_effort_and_impact": False,
                "assumptions_stated": True,
                "limitations_stated": True,
                "devils_advocate_completed": False,
                "all_gates_pass": False,
            },
            devil_advocate_notes=["Intake incomplete: devil's advocate pass deferred until full data is supplied."],
            sources=[framework.frameworks[0].value],
            assumptions=empty_scorecard.assumptions,
            limitations=empty_scorecard.limitations,
            next_questions=profile.missing_fields,
        )

    @staticmethod
    def _collect_sources(
        framework: FrameworkSelection, scorecard: Scorecard, roadmap: List[RoadmapAction]
    ) -> List[str]:
        sources = [f.value for f in framework.frameworks]
        for d in scorecard.dimensions:
            sources.extend(d.citations)
        for a in roadmap:
            if "heritage" in a.action.lower():
                sources.append("Heritage Auctions realized prices")
            if "sotheby" in a.action.lower():
                sources.append("Sotheby's realized prices")
            if "ebay" in a.action.lower():
                sources.append("eBay sold listings (market evidence)")
        return sorted(set(sources))

