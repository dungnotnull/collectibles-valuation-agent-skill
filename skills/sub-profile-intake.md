---
name: collectibles-valuation-sub-profile-intake
description: Identify category, item attributes, condition, provenance evidence, and the purpose of valuation (insurance, sale, estate).
---

## Role
Sub-skill of `collectibles-valuation`. Acts as the **intake / data-gathering stage**.

## Purpose
Collect enough structured information so the scoring engine can produce a defensible valuation without fabricating facts. If required fields are missing, return a list of targeted questions rather than a partial valuation.

## Inputs
- The user request and any artifacts supplied (photos, documents, prior appraisals).
- Structured output from the previous harness stage (if any).

## Procedure
1. Identify `category` from the user's first message. Valid values:
   - `coin`, `stamp`, `watch`, `trading_card`, `antique`.
2. Identify `purpose`. Valid values:
   - `sale`, `insurance`, `estate`, `appraisal`, `authentication`.
3. Validate required fields per category:

| Category | Required fields |
|----------|-----------------|
| coin | `item_name`, `description`, `condition_description`, `year_or_date`, `mint_mark_if_any` |
| trading_card | `item_name`, `description`, `condition_description`, `set_name`, `year_released` |
| stamp | `item_name`, `description`, `condition_description`, `country`, `issue_year` |
| watch | `item_name`, `description`, `condition_description`, `maker_if_known`, `serial_or_hallmark` |
| antique | `item_name`, `description`, `condition_description`, `dimensions_or_material`, `maker_marks` |

4. Always collect:
   - `authentication` (certificates, grading slabs, expertization letters — `["none"]` if none)
   - `provenance` (receipts, chain of custody, exhibition history, notes)
   - `photos_available` (boolean)
   - `market_signals` and `rarity_signals` (when offered)
   - `red_flags` (e.g., "too good to be true", "missing hallmark", "unclear photos")
5. Record assumptions and confidence flags.

## Output schema
```json
{
  "category": "coin",
  "item_name": "1916-D Mercury dime",
  "description": "Worn but full-date Mercury dime",
  "purpose": "sale",
  "condition": {
    "textual_description": "worn",
    "raw_grade_value": null,
    "scale": "sheldon_70",
    "defects": [],
    "photos_available": false
  },
  "provenance": {
    "chain_of_custody": [],
    "receipts": [],
    "certificates": [],
    "exhibition_history": [],
    "notes": "acquired from estate collection"
  },
  "authentication": ["none"],
  "market_signals": ["high demand"],
  "rarity_signals": ["1916-D Mercury dime", "key date"],
  "red_flags": [],
  "missing_fields": []
}
```

## Quality Gate
- [ ] `category` and `purpose` are valid enum values.
- [ ] All category-specific required fields are present.
- [ ] `authentication` and `provenance` fields are present (even if empty/`none`).
- [ ] If `missing_fields` is non-empty, output only the questions and stop here.

## Example questions for missing data
- "What year or date appears on the coin?"
- "Can you photograph any serial numbers, hallmarks, or case marks on the watch?"
- "Do you have a receipt, prior auction record, or certificate of authenticity?"
