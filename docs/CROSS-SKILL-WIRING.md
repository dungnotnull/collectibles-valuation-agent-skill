# Cross-Skill Wiring — Lifestyle & Personal cluster

## Scope

`collectibles-valuation` belongs to the **Lifestyle & Personal** cluster. Its
sub-skills are intentionally written as reusable **stages** that other
cluster skills can import or reference without divergence.

## Reusable assets

| Asset | Location | Reuse contract |
|-------|----------|----------------|
| JSON schemas | `src/collectibles_valuation/schema.py` | Any skill may import dataclasses and `serialize()`. |
| Framework registry | `src/collectibles_valuation/frameworks.py` | Named frameworks and grading conversions are shared across categories. |
| Intake patterns | `skills/sub-profile-intake.md` | Copy/adapt required-field tables for any valuation-like skill. |
| Scoring dimensions | `docs/SCHEMAAS.md` | The five dimensions (Rarity, Condition, Authenticity, Demand, Provenance) are cluster-wide. |
| Roadmap prioritization | `skills/sub-improvement-roadmap.md` | Effort × Impact ranking is cluster-agnostic. |

## Shared conventions

1. **Input contracts**
   - `category` is one of: `coin`, `stamp`, `watch`, `trading_card`, `antique`.
   - `purpose` is one of: `sale`, `insurance`, `estate`, `appraisal`, `authentication`.
   - Missing required fields MUST return a list of targeted questions, not a fabricated valuation.

2. **Output contracts**
   - Every dimension score carries a `justification` and at least one `citation`.
   - Roadmap actions carry `effort`, `impact`, `owner`, and `expected_effect`.
   - The final artifact states assumptions, limitations, and confidence band.

3. **Framework scales**
   - Coins: Sheldon 1-70 / PCGS-NGC.
   - Cards: PSA/BGS/CGC 1-10.
   - Stamps: APS / Scott catalogue.
   - Watches: NAWCC condition grading.
   - Antiques: ISA/USPAP cost/market/income approach.

4. **Knowledge base**
   - `SECOND-KNOWLEDGE-BRAIN.md` is the shared fallback when live search is unavailable.
   - `tools/knowledge_updater.py` is the single updater; sibling skills should not fork it.

## Integration checklist for sibling skills

- [ ] Import or mirror the five scoring dimensions.
- [ ] Re-use the framework registry rather than inventing category-specific scales.
- [ ] Align confidence-band language (`high` / `medium` / `low`).
- [ ] Route missing-field handling through `sub-profile-intake` patterns.
- [ ] Reference `SECOND-KNOWLEDGE-BRAIN.md` as the offline knowledge fallback.
