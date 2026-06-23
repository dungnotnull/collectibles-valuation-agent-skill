# CLAUDE.md — Collectibles Valuation (stamps/coins/watches/antiques/cards) (idea 110)

## Skill Identity
- **Name / slug:** `collectibles-valuation`
- **Tagline:** Collectibles Valuation (stamps/coins/watches/antiques/cards)
- **Source idea:** #110 (`ideas.md`)
- **Cluster:** Lifestyle & Personal (`lifestyle-personal`)
- **Current phase:** Phase 5 — Integration & Cross-Skill Wiring (complete)

## Problem This Skill Solves
Collectors and inheritors cannot reliably value items across stamps, coins, watches, antiques, and cards because grading standards, comparables, and authenticity signals differ by category and are easy to fake.

This skill becomes **a multi-category appraiser fluent in numismatics, philately, horology, trading-card grading, and antiques provenance research**. It is research-first, grounds every score in named world-renowned frameworks, challenges its own assumptions before concluding, and produces a professional artifact: a multi-dimensional score plus a prioritized improvement roadmap.

## Harness Flow Summary
1. **Intake** → `sub-profile-intake` gathers structured inputs and stops for missing data.
2. **Gate / framework** → the correct evaluation framework is selected and justified.
3. **Research** → `WebSearch`/`WebFetch` enrich evidence from authoritative sources (graceful degradation to `SECOND-KNOWLEDGE-BRAIN.md` if unavailable).
4. **Scoring** → `sub-scoring-engine` produces a 0–100 multi-dimensional score.
5. **Roadmap** → prioritized improvement plan (effort × impact).
6. **Quality gate** → devil's-advocate review before final output.

_No hard safety/compliance gate; standard quality gates apply._

## Sub-skills
- `skills/sub-profile-intake.md` — Identify category, item attributes, condition, provenance evidence, and the purpose of valuation (insurance, sale, estate).
- `skills/sub-framework-selector.md` — Select the correct category grading standard and valuation approach (market/cost/income).
- `skills/sub-scoring-engine.md` — Score rarity, condition/grade, authenticity confidence, and demand into a defensible value range with confidence band.
- `skills/sub-improvement-roadmap.md` — Recommend authentication, professional grading, and sale-channel actions ranked by value-uplift vs cost.

## Tools Required
- `WebSearch`, `WebFetch` — live evidence gathering
- `Read`, `Write` — artifact production
- `python` — run `tools/knowledge_updater.py` and the local `src/collectibles_valuation` harness

## Knowledge Sources (crawl targets)
- PCGS / NGC price guides
- PSA population reports
- Heritage Auctions & Sotheby's realized prices
- NAWCC research library
- Scott / Stanley Gibbons catalogues
- USPAP / ISA appraisal standards

## Supporting Tools
- `tools/knowledge_updater.py` — crawl4ai/duckduckgo pipeline that grows `SECOND-KNOWLEDGE-BRAIN.md` (weekly cron recommended).
- `src/collectibles_valuation/` — deterministic Python harness with schemas, scoring engine, and roadmap generator.

## Active Development Tasks
- [x] Scaffold all required deliverables
- [x] Author main harness + 4 sub-skills
- [x] Define scoring dimensions: Rarity, Condition/Grade, Authenticity confidence, Demand/Liquidity, Provenance
- [x] Implement production-grade Python engine (schemas, intake, scoring, roadmap, devil's advocate)
- [x] Expand SECOND-KNOWLEDGE-BRAIN with canonical authoritative sources (seeded)
- [x] Add 5+ automated regression scenarios
- [x] Add cross-skill wiring docs and sibling-skill conventions
- [x] Package with pyproject.toml, README, requirements
- [x] All phases complete

## Cross-Skill Wiring
- `docs/CROSS-SKILL-WIRING.md` documents how this skill's sub-skills, schemas, and scoring scales are designed for reuse across the Lifestyle & Personal cluster.
- Shared conventions: five dimensions, named frameworks, effort/impact roadmap, explicit confidence band.

## Related Root Docs
- `PROJECT-detail.md` — full technical spec
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — phase roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` — living knowledge base
- `docs/SCHEMAS.md` — canonical input/output schemas
- `README.md` — project overview and quick start
