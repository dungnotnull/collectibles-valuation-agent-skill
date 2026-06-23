# -*- coding: utf-8 -*-
"""Tests for the SECOND-KNOWLEDGE-BRAIN updater.

These tests avoid live network calls by exercising the static seed provider,
dedup logic, scoring, and append path against temporary files.
"""
import asyncio
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from tools.knowledge_updater import (
    KnowledgeEntry,
    StaticSeedProvider,
    _hash,
    append_entries,
    load_config,
    load_existing_hashes,
    score_entry,
)


class KnowledgeUpdaterTests(unittest.TestCase):
    def test_hash_stable(self):
        self.assertEqual(_hash("https://example.com/a"), _hash("https://example.com/a"))
        self.assertNotEqual(_hash("https://example.com/a"), _hash("https://example.com/b"))

    def test_load_existing_hashes_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as f:
            f.write("no hashes here")
            path = f.name
        try:
            self.assertEqual(load_existing_hashes(path), set())
        finally:
            os.unlink(path)

    def test_score_entry_recency_and_keywords(self):
        e = KnowledgeEntry(title="Rarity and demand in vintage watches", year=2026, key_finding="auction prices", relevance="high")
        config = {"domain_keywords": ["rarity", "demand", "auction"]}
        score = score_entry(e, config["domain_keywords"])
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        # Older entry should score lower, all else equal.
        old = KnowledgeEntry(title="Rarity and demand in vintage watches", year=2010, key_finding="auction prices", relevance="high")
        self.assertLess(score_entry(old, config["domain_keywords"]), score)

    def test_append_dedups_duplicates(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as f:
            f.write("# Brain\n")
            path = f.name
        try:
            entries = [
                KnowledgeEntry(title="A", url="https://a.com", key_finding="kf", relevance="r"),
                KnowledgeEntry(title="A", url="https://a.com", key_finding="kf", relevance="r"),
                KnowledgeEntry(title="B", url="https://b.com", key_finding="kf", relevance="r"),
            ]
            added = append_entries(entries, path, ["rarity"])
            self.assertEqual(added, 2)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.assertIn("https://a.com", text)
            self.assertIn("https://b.com", text)
        finally:
            os.unlink(path)

    def test_seed_provider_returns_entries(self):
        config = load_config("tools/knowledge_sources.json")
        entries = asyncio.run(StaticSeedProvider().search(config))
        self.assertGreater(len(entries), 0)
        self.assertTrue(all(e.url for e in entries))
        self.assertTrue(all(e.title for e in entries))

    def test_seed_entries_file_is_valid_json(self):
        config = load_config("tools/knowledge_sources.json")
        entries = asyncio.run(StaticSeedProvider().search(config))
        for e in entries:
            self.assertGreater(len(e.hash), 0)
            self.assertIsInstance(e.year, int)


if __name__ == "__main__":
    unittest.main()
