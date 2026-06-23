# Schemas

This document describes the canonical input/output schema used by the
`collectibles-valuation` harness. It is the contract between the skill
instructions, the Python engine, and any sibling skills in the Lifestyle &
Personal cluster.

## Input schema (raw dict → IntakeProfile)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `category` | string | yes | `coin`, `stamp`, `watch`, `trading_card`, `antique` |
| `item_name` | string | yes | Short identifying name |
| `description` | string | yes | Free-form description |
| `purpose` | string | yes | `sale`, `insurance`, `estate`, `appraisal`, `authentication` |
| `condition_description` | string | yes | Qualitative condition or numeric grade |
| `raw_grade_value` | number | no | Numeric grade (e.g., 65 for Sheldon, 8 for PSA) |
| `scale` | string | no | `sheldon_70`, `psa_10`, `bgs_10`, `cgc_10`, `aps_stamp`, `nawcc_watch`, `isa_qualitative` |
| `photos_available` | boolean | no | Defaults false |
| `defects` | list[str] | no | Surface defects |
| `year_or_date` | string | coin only | Date on the item |
| `mint_mark_if_any` | string | coin only | Mint mark or `none` |
| `set_name` | string | card only | Set / issue |
| `year_released` | string | card only | Release year |
| `country` | string | stamp only | Issuing country |
| `issue_year` | string | stamp only | Issue year |
| `maker_if_known` | string | watch only | Brand / maker |
| `serial_or_hallmark` | string | watch only | Serial or case marks |
| `dimensions_or_material` | string | antique only | Size / medium |
| `maker_marks` | string | antique only | Visible signatures / stamps |
| `authentication` | list[str] | yes | Certificates; use `["none"]` if none |
| `provenance` | object | yes | `{chain_of_custody, receipts, certificates, exhibition_history, notes}` |
| `market_signals` | list[str] | no | Demand / liquidity signals |
| `rarity_signals` | list[str] | no | Rarity / key-date signals |
| `red_flags` | list[str] | no | Authenticity / fraud warnings |
| `metadata` | object | no | `{base_value, rarity_estimate, demand_estimate, ...}` |
| `requested_currency` | string | no | Defaults `USD` |

## Output schema (ValuationReport)

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `complete`, `complete_with_gate_warnings`, `incomplete` |
| `subject` | string | Item name |
| `purpose` | string | Valuation purpose |
| `framework` | object | `{category, frameworks, primary_scale, valuation_approaches, justification}` |
| `scorecard` | object | `{dimensions, composite, confidence, value_index, value_range_low, value_range_high, currency, assumptions, limitations}` |
| `scorecard.dimensions` | list | Each `{dimension, score, weight, justification, citations}` |
| `roadmap` | list | Each `{action, rationale, effort, impact, expected_effect, owner, dimension, priority_score}` |
| `quality_gate_checklist` | object | Boolean pass/fail per gate |
| `devil_advocate_notes` | list[str] | Challenges raised and resolved |
| `sources` | list[str] | All citations |
| `assumptions` | list[str] | Stated assumptions |
| `limitations` | list[str] | Stated limitations |
| `next_questions` | list[str] | Only present when `status == incomplete` |

## Scoring dimensions

All five dimensions are normalized to 0-100 and weighted by purpose:

1. **Rarity** — mintage, survival, key-date / iconic status.
2. **Condition/Grade** — mapped from the primary category grading scale.
3. **Authenticity confidence** — certificates, provenance, photos, red flags.
4. **Demand/Liquidity** — market signals and category baseline.
5. **Provenance** — chain of custody, receipts, certificates, exhibition history.

## Serialization

Use `collectibles_valuation.report_to_json(report)` to obtain a JSON-safe
dictionary. The core engine has no required runtime dependencies.
