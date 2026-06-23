# -*- coding: utf-8 -*-
"""End-to-end scenario tests for the collectibles-valuation harness.

Each scenario mirrors the spec in tests/test-scenarios.md and asserts that
framework selection, scoring, and roadmap behavior match expectations.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from collectibles_valuation import ValuationHarness
from collectibles_valuation.schema import Category, Dimension, ValuationPurpose


class HarnessScenarioTests(unittest.TestCase):
    def setUp(self):
        self.harness = ValuationHarness()

    def _run(self, raw):
        return self.harness.run_to_json(raw)

    def test_scenario_1_1916_d_mercury_dime(self):
        raw = {
            "category": "coin",
            "item_name": "1916-D Mercury dime",
            "description": "Worn 1916-D Mercury dime with a readable date and partial wing details",
            "purpose": "sale",
            "condition_description": "worn",
            "year_or_date": "1916",
            "mint_mark_if_any": "D",
            "photos_available": False,
            "rarity_signals": ["1916-D Mercury dime", "key date"],
            "market_signals": ["high demand"],
            "authentication": ["none"],
            "provenance": {"notes": "acquired from estate collection"},
            "red_flags": [],
            "metadata": {"base_value": 1200},
        }
        report = self._run(raw)
        self.assertEqual(report["status"], "complete")
        self.assertIn("Sheldon", report["framework"]["justification"])
        self.assertEqual(report["framework"]["category"], "coin")

        dimensions = {d["dimension"]: d for d in report["scorecard"]["dimensions"]}
        self.assertEqual(set(dimensions.keys()), {d.value for d in Dimension})
        self.assertLess(dimensions["condition"]["score"], 40)
        self.assertGreater(dimensions["rarity"]["score"], 80)
        self.assertTrue(all(dimensions[d]["citations"] for d in dimensions))

        actions = [a["action"] for a in report["roadmap"]]
        self.assertTrue(any("grading" in a.lower() for a in actions))
        self.assertTrue(any("authentication" in a.lower() for a in actions))
        self.assertTrue(report["quality_gate_checklist"]["all_gates_pass"])

    def test_scenario_2_sealed_vintage_pokemon_card(self):
        raw = {
            "category": "trading_card",
            "item_name": "Base Set Charizard",
            "description": "Raw Base Set Charizard, corner wear, slight surface holo scratching",
            "purpose": "sale",
            "condition_description": "raw with light wear",
            "set_name": "Base Set",
            "year_released": "1999",
            "photos_available": True,
            "rarity_signals": ["Base Set Charizard", "1st Edition"],
            "market_signals": ["liquid", "high demand"],
            "authentication": ["none"],
            "provenance": {"notes": "pulled from pack as a child"},
            "red_flags": [],
            "metadata": {"base_value": 10000},
        }
        report = self._run(raw)
        self.assertEqual(report["status"], "complete")
        self.assertIn("PSA", report["framework"]["justification"])
        dimensions = {d["dimension"]: d for d in report["scorecard"]["dimensions"]}
        self.assertEqual(report["framework"]["primary_scale"], "psa_10")
        self.assertGreater(dimensions["demand"]["score"], 70)
        actions = [a["action"] for a in report["roadmap"]]
        self.assertTrue(any("PSA" in a or "BGS" in a or "CGC" in a for a in actions))
        self.assertTrue(report["quality_gate_checklist"]["all_gates_pass"])

    def test_scenario_3_inherited_pocket_watch_unknown_maker(self):
        raw = {
            "category": "watch",
            "item_name": "Inherited pocket watch",
            "description": "Pocket watch from estate; limited photos; maker unknown",
            "purpose": "appraisal",
            "condition_description": "unknown",
            "photos_available": False,
            "rarity_signals": [],
            "market_signals": [],
            "authentication": [],
            "provenance": {},
            "red_flags": [],
        }
        report = self._run(raw)
        self.assertEqual(report["status"], "incomplete")
        missing = report.get("next_questions", [])
        self.assertTrue(any("serial" in m.lower() or "hallmark" in m.lower() for m in missing))
        self.assertTrue(any("maker" in m.lower() for m in missing))
        self.assertIn("NAWCC", report["framework"]["justification"])
        self.assertFalse(report["quality_gate_checklist"]["all_gates_pass"])

    def test_scenario_4_antique_vase_insurance(self):
        raw = {
            "category": "antique",
            "item_name": "Chinese porcelain vase",
            "description": "Blue-and-white porcelain vase, 12 inches, no visible maker mark",
            "purpose": "insurance",
            "condition_description": "good",
            "dimensions_or_material": "porcelain, 12 inches",
            "maker_marks": "none visible",
            "photos_available": True,
            "rarity_signals": ["antique porcelain"],
            "market_signals": ["stable demand"],
            "authentication": ["none"],
            "provenance": {"receipts": ["estate inventory 2019"]},
            "red_flags": [],
            "metadata": {"base_value": 5000},
        }
        report = self._run(raw)
        self.assertEqual(report["status"], "complete")
        self.assertIn("ISA", report["framework"]["justification"])
        self.assertIn("USPAP", report["framework"]["justification"])
        self.assertIn("cost", report["framework"]["justification"].lower())
        actions = [a["action"] for a in report["roadmap"]]
        self.assertTrue(any("insurance" in a.lower() or "replacement-cost" in a.lower() for a in actions))
        self.assertTrue(report["quality_gate_checklist"]["all_gates_pass"])

    def test_scenario_5_suspected_forgery_stamp(self):
        raw = {
            "category": "stamp",
            "item_name": "Rare 19th-century stamp",
            "description": "Stamp offered far below market, seller cannot provide provenance",
            "purpose": "authentication",
            "condition_description": "fine",
            "country": "Unknown",
            "issue_year": "unknown",
            "photos_available": False,
            "rarity_signals": ["rare 19th-century stamp"],
            "market_signals": ["suspicious price"],
            "authentication": ["none"],
            "provenance": {"notes": "seller unable to provide any history"},
            "red_flags": ["too good to be true", "no provenance"],
        }
        report = self._run(raw)
        self.assertEqual(report["status"], "complete")
        dimensions = {d["dimension"]: d for d in report["scorecard"]["dimensions"]}
        self.assertLess(dimensions["authenticity"]["score"], 40)
        actions = [a["action"] for a in report["roadmap"]]
        self.assertTrue(any("Halt" in a or "forensic" in a.lower() for a in actions))
        # The fraud-caution action should be top priority.
        self.assertIn(report["roadmap"][0]["impact"], ["critical"])
        self.assertTrue(report["quality_gate_checklist"]["all_gates_pass"])

    def test_report_has_sources_for_every_citation(self):
        raw = {
            "category": "coin",
            "item_name": "Test coin",
            "description": "Test",
            "purpose": "sale",
            "condition_description": "fine",
            "year_or_date": "1900",
            "mint_mark_if_any": "none",
            "photos_available": True,
            "rarity_signals": ["common"],
            "market_signals": [],
            "authentication": ["PCGS MS-65"],
            "provenance": {"receipts": ["dealer receipt"]},
            "red_flags": [],
        }
        report = self._run(raw)
        self.assertTrue(report["sources"])
        self.assertTrue(report["assumptions"])
        self.assertTrue(report["limitations"])


if __name__ == "__main__":
    unittest.main()
