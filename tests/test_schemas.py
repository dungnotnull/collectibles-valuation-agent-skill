# -*- coding: utf-8 -*-
"""Schema serialization and validation tests."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from collectibles_valuation import (
    Category,
    ConditionEvidence,
    Dimension,
    FrameworkSelection,
    IntakeProfile,
    Priority,
    ProvenanceEvidence,
    RoadmapAction,
    Scorecard,
    ValuationPurpose,
    ValuationReport,
    report_to_json,
    serialize,
)
from collectibles_valuation.frameworks import select_frameworks


class SchemaTests(unittest.TestCase):
    def test_enum_serialization(self):
        self.assertEqual(serialize(Category.COIN), "coin")
        self.assertEqual(serialize(ValuationPurpose.INSURANCE), "insurance")

    def test_intake_round_trip(self):
        profile = IntakeProfile(
            category=Category.CARD,
            item_name="Base Set Charizard",
            description="Raw vintage Pokemon card",
            purpose=ValuationPurpose.SALE,
            condition=ConditionEvidence(textual_description="raw", photos_available=True),
            provenance=ProvenanceEvidence(notes="acquired from collector"),
        )
        data = serialize(profile)
        self.assertEqual(data["category"], "trading_card")
        self.assertEqual(data["purpose"], "sale")
        self.assertIn("condition", data)

    def test_report_to_json_is_json_dumpable(self):
        framework = FrameworkSelection(
            category=Category.COIN,
            frameworks=[],
            primary_scale=None,  # type: ignore[arg-type]
            valuation_approaches=[],
            justification="test",
        )
        report = ValuationReport(
            status="complete",
            subject="test",
            purpose=ValuationPurpose.SALE,
            framework=framework,
            scorecard=Scorecard(
                dimensions=[],
                composite=50.0,
                confidence=None,  # type: ignore[arg-type]
                value_index=50.0,
            ),
            roadmap=[
                RoadmapAction(
                    action="Get grading",
                    rationale="needed",
                    effort=None,  # type: ignore[arg-type]
                    impact=Priority.HIGH,
                    expected_effect="better value",
                    owner="owner",
                )
            ],
            quality_gate_checklist={"ok": True},
            devil_advocate_notes=["note"],
            sources=["source"],
            assumptions=[],
            limitations=[],
        )
        js = report_to_json(report)
        dumped = json.dumps(js)
        self.assertIsInstance(dumped, str)

    def test_select_frameworks_maps_coin(self):
        frameworks, approaches, scale, justification = select_frameworks(Category.COIN, ValuationPurpose.SALE)
        self.assertIn("Sheldon", justification)
        self.assertEqual(scale.value, "sheldon_70")
        self.assertEqual(approaches[0].value, "market")


if __name__ == "__main__":
    unittest.main()
