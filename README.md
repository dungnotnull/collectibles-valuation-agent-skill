# collectibles-valuation

A research-first, framework-grounded valuation harness for stamps, coins, watches, trading cards, and antiques. It turns a structured description of an item into a defensible multi-dimensional score and a prioritized improvement roadmap, grounded in named world-renowned frameworks.

## What it does

1. **Intake** — validates category, condition, provenance, and purpose.
2. **Framework selection** — chooses the correct grading standard and valuation approach.
3. **Scoring** — produces five 0-100 dimension scores (Rarity, Condition, Authenticity, Demand/Liquidity, Provenance) with citations.
4. **Roadmap** — ranks authentication, grading, and sale-channel actions by effort × impact.
5. **Devil's advocate** — challenges every score and recommendation before final output.

## Repository layout

```
.
├── src/collectibles_valuation/   # production Python harness
│   ├── schema.py                 # dataclass schemas
│   ├── frameworks.py             # framework selection + conversion rules
│   ├── intake.py                 # intake validation
│   ├── scoring.py                # multi-dimensional scoring engine
│   ├── roadmap.py                # prioritized action generator
│   ├── devils_advocate.py        # quality gate
│   └── orchestrator.py           # end-to-end harness
├── skills/                       # Claude/Codex skill instructions
│   ├── main.md
│   ├── sub-profile-intake.md
│   ├── sub-framework-selector.md
│   ├── sub-scoring-engine.md
│   └── sub-improvement-roadmap.md
├── tools/                        # knowledge-base updater
│   ├── knowledge_updater.py
│   ├── knowledge_sources.json
│   └── seed_entries.json
├── tests/                        # automated scenario + unit tests
├── docs/
│   ├── CROSS-SKILL-WIRING.md
│   └── SCHEMAS.md
├── SECOND-KNOWLEDGE-BRAIN.md     # living knowledge base
├── PROJECT-detail.md
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md
└── CLAUDE.md
```

## Quick start

```bash
# No runtime dependencies required for the core engine.
PYTHONPATH=src python -c "
from collectibles_valuation import ValuationHarness
report = ValuationHarness().run_to_json({
    'category': 'coin',
    'item_name': '1916-D Mercury dime',
    'description': 'Worn 1916-D Mercury dime',
    'purpose': 'sale',
    'condition_description': 'worn',
    'year_or_date': '1916',
    'mint_mark_if_any': 'D',
    'photos_available': False,
    'rarity_signals': ['1916-D Mercury dime', 'key date'],
    'market_signals': ['high demand'],
    'authentication': ['none'],
    'provenance': {'notes': 'acquired from estate'},
})
print(report)
"
```

## Running tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Knowledge-base updater

The `tools/knowledge_updater.py` script keeps `SECOND-KNOWLEDGE-BRAIN.md` current. It supports live DuckDuckGo / crawl4ai providers and a zero-network static seed provider for canonical sources.

```bash
# Seed canonical authoritative sources (no network)
python tools/knowledge_updater.py --seed-only

# Dry-run live providers (requires optional `crawl4ai` / `duckduckgo-search`)
python tools/knowledge_updater.py --dry-run --providers crawl4ai,duckduckgo
```

## Design principles

- **Named frameworks only** — Sheldon/PCGS/NGC, PSA/BGS/CGC, NAWCC, APS/Scott, ISA/USPAP, comparable-sales.
- **Evidence hierarchy** — systematic review > meta-analysis > empirical > expert opinion.
- **No fabricated facts** — confidence bands and limitations are explicit.
- **Production-grade** — zero core dependencies, deterministic, fully tested.

## License

MIT — see `pyproject.toml`.
