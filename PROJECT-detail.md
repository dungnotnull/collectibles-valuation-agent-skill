# PROJECT-detail.md — Collectibles Valuation (stamps/coins/watches/antiques/cards)

## Executive Summary
`collectibles-valuation` is a Claude Skill that turns Claude into **a multi-category appraiser fluent in numismatics, philately, horology, trading-card grading, and antiques provenance research**. It ingests domain inputs, screens for safety/compliance where required, selects a world-renowned evaluation framework, gathers fresh evidence, scores the subject across 5 dimensions, and outputs a prioritized improvement roadmap. It is part of the **Lifestyle & Personal** cluster.

## Problem Statement
Collectors and inheritors cannot reliably value items across stamps, coins, watches, antiques, and cards because grading standards, comparables, and authenticity signals differ by category and are easy to fake.

Domain context: practitioners need reproducible, evidence-graded evaluation rather than ad-hoc opinion. This skill enforces a research-first harness with explicit quality gates and a self-improving knowledge base.

## Target Users & Use Cases
- Primary: practitioners, learners, and decision-makers in this domain.
- Trigger examples:
1. **1916-D Mercury dime** — User describes a worn 1916-D dime. Expect Sheldon-grade estimate, authentication warnings (common counterfeit), comps-based range, and grading recommendation.
2. **Sealed vintage Pokemon card** — Raw Base Set Charizard. Expect PSA grading scenario modeling and value range by grade, plus authenticity red flags.
3. **Inherited pocket watch, unknown maker** — Limited photos. Expect framework-selector to request hallmarks/serials, graceful low-confidence range, provenance research steps.
4. **Antique vase for insurance** — Purpose is insurance scheduling. Expect replacement-value (cost) approach vs fair-market distinction and USPAP-style documentation.
5. **Suspected forgery / too-good deal** — Stamp offered far below market. Expect authenticity-confidence scoring to dominate and a fraud-caution roadmap.

## Harness Architecture
```
/collectibles-valuation  (main.md)
   |
   v
[1] sub-profile-intake        -> structured intake
   |
   v
[2] framework selection  -> choose named framework
   |
   v
[3] research (WebSearch/WebFetch)        -> evidence (graceful deg: SECOND-KNOWLEDGE-BRAIN.md)
   |
   v
[4] scoring engine                       -> 0-100 multi-dimensional score
   |
   v
[5] improvement roadmap                  -> effort x impact prioritized actions
   |
   v
[6] quality-gate / devil's advocate      -> final professional artifact
```

## Full Sub-Skill Catalog
#### `sub-profile-intake`
- **Purpose:** Identify category, item attributes, condition, provenance evidence, and the purpose of valuation (insurance, sale, estate).
- **Inputs:** structured outputs from prior stage + user-supplied data
- **Outputs:** validated, structured payload for the next stage
- **Tools:** Read, Write
- **Quality gate:** output schema validated before proceeding

#### `sub-framework-selector`
- **Purpose:** Select the correct category grading standard and valuation approach (market/cost/income).
- **Inputs:** structured outputs from prior stage + user-supplied data
- **Outputs:** validated, structured payload for the next stage
- **Tools:** Read, Write, WebSearch/WebFetch
- **Quality gate:** output schema validated before proceeding

#### `sub-scoring-engine`
- **Purpose:** Score rarity, condition/grade, authenticity confidence, and demand into a defensible value range with confidence band.
- **Inputs:** structured outputs from prior stage + user-supplied data
- **Outputs:** validated, structured payload for the next stage
- **Tools:** Read, Write, WebSearch/WebFetch
- **Quality gate:** output schema validated before proceeding

#### `sub-improvement-roadmap`
- **Purpose:** Recommend authentication, professional grading, and sale-channel actions ranked by value-uplift vs cost.
- **Inputs:** structured outputs from prior stage + user-supplied data
- **Outputs:** validated, structured payload for the next stage
- **Tools:** Read, Write
- **Quality gate:** output schema validated before proceeding


## Evaluation Frameworks (world-renowned, citable)
- Sheldon Coin Grading Scale (1-70) / PCGS-NGC standards
- PSA/BGS/CGC card grading scales
- NAWCC & watch condition grading
- Philatelic grading (APS) & Scott catalogue
- ISA/USPAP appraisal principles
- Provenance & chain-of-custody documentation
- Comparable-sales (comps) market approach

## Scoring Model
| Dimension | Range | Notes |
|-----------|-------|-------|
| Rarity | 0–100 | Weighted contribution to the composite index |
| Condition/Grade | 0–100 | Weighted contribution to the composite index |
| Authenticity confidence | 0–100 | Weighted contribution to the composite index |
| Demand/Liquidity | 0–100 | Weighted contribution to the composite index |
| Provenance | 0–100 | Weighted contribution to the composite index |

Composite = weighted mean of dimensions (weights justified per case, surfaced to the user). Every dimension score must cite at least one framework criterion or evidence source.

## Skill File Format Specification
Frontmatter: `name`, `description`. Required sections in `main.md`: Role & Persona, Workflow (Harness Flow), Sub-skills Available, Tools, Output Format, Quality Gates.

## E2E Execution Flow
1. Parse user request; if inputs missing, run intake questions.
2. Select framework based on subject characteristics.
3. Gather evidence (prefer Systematic Review > Meta-analysis > RCT/empirical > expert opinion).
4. Score each dimension with cited justification.
5. Build prioritized roadmap.
6. Run devil's-advocate quality gate; revise; present artifact.
- Error handling: missing data → state assumptions + confidence; tool failure → degrade to knowledge base and signal limitation.

## SECOND-KNOWLEDGE-BRAIN Integration
- Sources: PCGS / NGC price guides, PSA population reports, Heritage Auctions & Sotheby's realized prices, NAWCC research library, Scott / Stanley Gibbons catalogues.
- Crawl queries: auction realized price trends collectibles, trading card grading population report, counterfeit detection numismatics, vintage watch market index.
- Append format: dated entries with Title, Authors, Year, Venue, DOI/URL, key finding, relevance.

## Supporting Tools Spec — `knowledge_updater.py`
- Inputs: source list + query list (above), `--since` date.
- Outputs: appended, de-duplicated entries in `SECOND-KNOWLEDGE-BRAIN.md`.
- Schedule: weekly cron.

## Quality Gates (must be true before final output)
- [ ] Framework selection justified
- [ ] Every score cites a framework criterion or evidence source
- [ ] Roadmap items have effort + impact + owner
- [ ] Assumptions and confidence stated; limitations disclosed
- [ ] Devil's-advocate pass completed

## Test Scenarios (≥5)
1. **1916-D Mercury dime** — User describes a worn 1916-D dime. Expect Sheldon-grade estimate, authentication warnings (common counterfeit), comps-based range, and grading recommendation.
2. **Sealed vintage Pokemon card** — Raw Base Set Charizard. Expect PSA grading scenario modeling and value range by grade, plus authenticity red flags.
3. **Inherited pocket watch, unknown maker** — Limited photos. Expect framework-selector to request hallmarks/serials, graceful low-confidence range, provenance research steps.
4. **Antique vase for insurance** — Purpose is insurance scheduling. Expect replacement-value (cost) approach vs fair-market distinction and USPAP-style documentation.
5. **Suspected forgery / too-good deal** — Stamp offered far below market. Expect authenticity-confidence scoring to dominate and a fraud-caution roadmap.

## Key Design Decisions
1. Research-first; no memory-only claims when search is possible.
2. Named frameworks only — never ad hoc criteria.
3. Framework-selector adapts to subject; no one-size scoring.
4. Multi-dimensional score + prioritized roadmap are mandatory outputs.
5. Self-improving knowledge base via weekly crawl.
