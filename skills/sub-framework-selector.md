---
name: collectibles-valuation-sub-framework-selector
description: Select the correct category grading standard and valuation approach (market/cost/income).
---

## Role
Sub-skill of `collectibles-valuation`. Acts as the **framework-selection stage**.

## Purpose
Choose the named grading standard and valuation approach that fit the subject and the purpose, then justify the choice to the user.

## Inputs
- Validated `IntakeProfile` from `sub-profile-intake`.

## Framework table

| Category | Primary framework | Primary scale | Typical valuation approach |
|----------|-------------------|---------------|----------------------------|
| coin | Sheldon Coin Grading Scale / PCGS-NGC | 1-70 | market |
| trading_card | PSA/BGS/CGC card grading | 1-10 | market |
| stamp | APS philatelic grading / Scott catalogue | qualitative | market |
| watch | NAWCC watch condition grading | qualitative | market / cost |
| antique | ISA/USPAP appraisal principles | qualitative | cost / market / income |

All categories also reference the **Comparable-sales market approach** as supporting evidence.

## Selection rules
1. Map `category` → primary framework from the table above.
2. Map `purpose` → primary valuation approach:
   - `sale` → **market**
   - `insurance` → **cost** (with fair-market reference)
   - `estate` → **market** + **cost**
   - `appraisal` → **market** + **cost** + **income**
   - `authentication` → **market** reference only
3. Write a one-sentence justification citing the framework and purpose.

## Output schema
```json
{
  "category": "coin",
  "frameworks": ["Sheldon Coin Grading Scale / PCGS-NGC", "Comparable-sales market approach"],
  "primary_scale": "sheldon_70",
  "valuation_approaches": ["market"],
  "justification": "Coin sale valuation applies the Sheldon 1-70 scale (PCGS/NGC) for grade-derived pricing and the comparable-sales approach for market evidence; market approach is primary."
}
```

## Quality Gate
- [ ] Framework selection cites a named, citable standard.
- [ ] Valuation approach matches the stated purpose.
- [ ] Justification is written in the output and surfaced to the user.
- [ ] If maker/hallmark/serial is unknown for a watch, the justification requests additional evidence and flags low confidence.
