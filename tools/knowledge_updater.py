# -*- coding: utf-8 -*-
"""SECOND-KNOWLEDGE-BRAIN updater.

Production-grade crawler that:

1. Loads source/query configuration from ``tools/knowledge_sources.json``.
2. Optionally fetches live candidates from DuckDuckGo (``duckduckgo-search``)
   and/or crawl4ai (``crawl4ai``).
3. Always seeds canonical authoritative references from ``tools/seed_entries.json``.
4. Scores candidates by recency + domain-keyword relevance.
5. De-duplicates by URL/title hash before appending.
6. Appends dated entries to ``SECOND-KNOWLEDGE-BRAIN.md``.

Run dry-run:
    python tools/knowledge_updater.py --dry-run

Seed canonical sources:
    python tools/knowledge_updater.py --seed-only

Weekly cron (production):
    python tools/knowledge_updater.py
"""
from __future__ import annotations

import argparse
import asyncio
import datetime
import hashlib
import json
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BRAIN = os.path.join(HERE, "..", "SECOND-KNOWLEDGE-BRAIN.md")
SOURCES_PATH = os.path.join(HERE, "knowledge_sources.json")
SEED_PATH = os.path.join(HERE, "seed_entries.json")


# ---------------------------------------------------------------------------
# Hashing / deduplication
# ---------------------------------------------------------------------------
def _hash(url: str, title: str = "") -> str:
    """Stable 16-char hash for deduplication."""
    payload = f"{url or ''}|{title or ''}".strip().lower()
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def load_existing_hashes(path: str) -> Set[str]:
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return set(re.findall(r"<!--hash:([0-9a-f]{16})-->", text))


# ---------------------------------------------------------------------------
# Entry model
# ---------------------------------------------------------------------------
class KnowledgeEntry:
    def __init__(
        self,
        title: str,
        authors: str = "",
        year: Optional[int] = None,
        venue: str = "",
        url: str = "",
        key_finding: str = "",
        relevance: str = "",
    ):
        self.title = title.strip()
        self.authors = authors.strip()
        self.year = year or datetime.date.today().year
        self.venue = venue.strip()
        self.url = url.strip()
        self.key_finding = key_finding.strip()
        self.relevance = relevance.strip()
        self.hash = _hash(self.url, self.title)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "venue": self.venue,
            "url": self.url,
            "key_finding": self.key_finding,
            "relevance": self.relevance,
            "hash": self.hash,
        }

    def __repr__(self) -> str:
        return f"KnowledgeEntry({self.title!r}, {self.url!r})"


# ---------------------------------------------------------------------------
# Search providers
# ---------------------------------------------------------------------------
class SearchProvider(ABC):
    @abstractmethod
    async def search(self, config: Dict[str, Any]) -> List[KnowledgeEntry]:
        ...


class DuckDuckGoProvider(SearchProvider):
    """Use duckduckgo-search if available.  Requires the ``search`` extra."""

    async def search(self, config: Dict[str, Any]) -> List[KnowledgeEntry]:
        try:
            from duckduckgo_search import DDGS
        except Exception as exc:  # pragma: no cover
            print(f"[warn] duckduckgo-search not available: {exc}")
            return []

        entries: List[KnowledgeEntry] = []
        queries = config.get("queries", [])
        sources = config.get("sources", [])
        for query in queries:
            for source in sources:
                full_query = f"{query} {source.get('name', '')}"
                try:
                    with DDGS() as ddgs:
                        results = ddgs.text(full_query, max_results=3)
                    for r in results:
                        entries.append(
                            KnowledgeEntry(
                                title=r.get("title", ""),
                                authors=source.get("name", "Web search"),
                                year=datetime.date.today().year,
                                venue=source.get("name", ""),
                                url=r.get("href", ""),
                                key_finding=r.get("body", "")[:250],
                                relevance=f"Live search result from {source.get('name', '')}",
                            )
                        )
                except Exception as exc:  # pragma: no cover
                    print(f"[warn] DDGS search failed for '{full_query}': {exc}")
        return entries


class Crawl4aiProvider(SearchProvider):
    """Use crawl4ai to fetch configured source homepages.  Requires the ``crawl`` extra."""

    async def search(self, config: Dict[str, Any]) -> List[KnowledgeEntry]:
        try:
            from crawl4ai import AsyncWebCrawler
        except Exception as exc:  # pragma: no cover
            print(f"[warn] crawl4ai not installed: {exc}")
            return []

        entries: List[KnowledgeEntry] = []
        sources = config.get("sources", [])
        async with AsyncWebCrawler(verbose=False) as crawler:
            for source in sources:
                url = source.get("url", "")
                if not url:
                    continue
                try:
                    res = await crawler.arun(url=url)
                    md = (getattr(res, "markdown", "") or "")[:400]
                    entries.append(
                        KnowledgeEntry(
                            title=f"{source.get('name', '')} homepage",
                            authors=source.get("name", ""),
                            year=datetime.date.today().year,
                            venue=source.get("name", ""),
                            url=url,
                            key_finding=md,
                            relevance="Crawled authoritative source homepage.",
                        )
                    )
                except Exception as exc:  # pragma: no cover
                    print(f"[warn] crawl failed for {url}: {exc}")
        return entries


class StaticSeedProvider(SearchProvider):
    """Load canonical seed entries from JSON.  Zero-network dependency."""

    async def search(self, config: Dict[str, Any]) -> List[KnowledgeEntry]:
        if not os.path.exists(SEED_PATH):
            print(f"[warn] seed file not found: {SEED_PATH}")
            return []
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        entries = []
        for item in data:
            entries.append(
                KnowledgeEntry(
                    title=item.get("title", ""),
                    authors=item.get("authors", ""),
                    year=item.get("year") or datetime.date.today().year,
                    venue=item.get("venue", ""),
                    url=item.get("url", ""),
                    key_finding=item.get("key_finding", ""),
                    relevance=item.get("relevance", ""),
                )
            )
        return entries


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
def score_entry(entry: KnowledgeEntry, domain_keywords: List[str]) -> float:
    """Recency + keyword relevance score in [0, 1]."""
    now = datetime.date.today().year
    recency = max(0.0, 1.0 - (now - entry.year) / 10.0)
    text = f"{entry.title} {entry.key_finding} {entry.relevance}".lower()
    hits = sum(1 for k in domain_keywords if k in text)
    relevance = min(1.0, hits / max(1, len(domain_keywords)))
    return round(0.5 * recency + 0.5 * relevance, 3)


# ---------------------------------------------------------------------------
# Append / persistence
# ---------------------------------------------------------------------------
def append_entries(
    entries: List[KnowledgeEntry],
    path: str,
    domain_keywords: List[str],
    since: Optional[datetime.date] = None,
) -> int:
    existing = load_existing_hashes(path)
    added = 0
    lines: List[str] = []
    today = datetime.date.today().isoformat()

    filtered = [
        e for e in entries
        if since is None or datetime.date(e.year, 1, 1) >= since
    ]
    for e in sorted(filtered, key=lambda x: score_entry(x, domain_keywords), reverse=True):
        if e.hash in existing:
            continue
        sc = score_entry(e, domain_keywords)
        lines.append(
            f"- {today} | score={sc} | **{e.title}** | {e.authors} "
            f"| {e.year} | {e.venue} | {e.url} | "
            f"Finding: {e.key_finding[:160]} | Relevance: {e.relevance[:120]} "
            f"<!--hash:{e.hash}-->"
        )
        existing.add(e.hash)
        added += 1

    if added:
        header = f"\n### Crawl {today} (+{added})\n"
        with open(path, "a", encoding="utf-8") as f:
            f.write(header + "\n".join(lines) + "\n")
    print(f"[ok] appended {added} new entries to {path}")
    return added


# ---------------------------------------------------------------------------
# CLI / main
# ---------------------------------------------------------------------------
def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Update SECOND-KNOWLEDGE-BRAIN.md")
    ap.add_argument("--brain", default=DEFAULT_BRAIN, help="Path to knowledge-brain markdown file")
    ap.add_argument("--sources", default=SOURCES_PATH, help="Path to knowledge_sources.json")
    ap.add_argument("--seed-only", action="store_true", help="Only append static seed entries")
    ap.add_argument("--dry-run", action="store_true", help="Print candidate entries without appending")
    ap.add_argument("--since", help="ISO date YYYY-MM-DD; skip entries older than this")
    ap.add_argument(
        "--providers",
        default="seed,crawl4ai,duckduckgo",
        help="Comma-separated search provider order (default: seed,crawl4ai,duckduckgo)",
    )
    return ap.parse_args()


async def collect_candidates(config: Dict[str, Any], providers: List[str]) -> List[KnowledgeEntry]:
    registry: Dict[str, SearchProvider] = {
        "seed": StaticSeedProvider(),
        "crawl4ai": Crawl4aiProvider(),
        "duckduckgo": DuckDuckGoProvider(),
    }
    candidates: List[KnowledgeEntry] = []
    for name in providers:
        provider = registry.get(name.strip().lower())
        if not provider:
            print(f"[warn] unknown provider '{name}'")
            continue
        try:
            batch = await provider.search(config)
            print(f"[info] provider '{name}' returned {len(batch)} entries")
            candidates.extend(batch)
        except Exception as exc:
            print(f"[warn] provider '{name}' failed: {exc}")
    return candidates


def main() -> int:
    args = parse_args()
    config = load_config(args.sources)
    providers = [p for p in args.providers.split(",") if p.strip()]

    if args.seed_only and "seed" not in providers:
        providers.insert(0, "seed")

    since: Optional[datetime.date] = None
    if args.since:
        since = datetime.date.fromisoformat(args.since)

    try:
        candidates = asyncio.run(collect_candidates(config, providers))
    except Exception as exc:
        print(f"[warn] collection stage failed: {exc}")
        candidates = []

    # Always include seed if the brain file is empty (first run)
    if not os.path.exists(args.brain) or os.path.getsize(args.brain) == 0:
        print("[info] knowledge brain empty; forcing seed provider")
        seed_entries = asyncio.run(StaticSeedProvider().search(config))
        candidates = seed_entries + candidates

    if args.dry_run:
        for e in sorted(candidates, key=lambda x: score_entry(x, config.get("domain_keywords", [])), reverse=True):
            print(json.dumps(e.as_dict(), indent=2, ensure_ascii=False))
        return 0

    append_entries(candidates, args.brain, config.get("domain_keywords", []), since=since)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
