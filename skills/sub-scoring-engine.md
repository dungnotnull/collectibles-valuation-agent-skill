---
name: collectibles-valuation-sub-scoring-engine
description: Score rarity, condition/grade, authenticity confidence, and demand into a defensible value range with confidence band.
---

## Role
Sub-skill of `collectibles-valuation`. Acts as the **scoring stage**.

## Purpose
Translate the validated profile and selected framework into five 0-100 dimension scores, a weighted composite, a confidence band, and a defensible value index or monetary range.

## Inputs
- Validated `IntakeProfile`.
- `FrameworkSelection` from `sub-framework-selector`.
- Live evidence from `WebSearch`/`WebFetch` or fallback entries from `SECOND-KNOWLEDGE-BRAIN.md`.

## Dimensions

| Dimension | What it measures | Primary evidence |
|-----------|------------------|------------------|
| Rarity | Relative scarcity | mintage/survival, key-date indicators, population reports |
| Condition/Grade | Physical state | Sheldon/PSA/BGS/CGC/APS/NAWCC/ISA grade or qualitative description |
| Authenticity confidence | Likelihood the item is genuine | certificates, provenance, photos, red flags |
| Demand/Liquidity | Market interest | comparable sales, auction activity, category baseline |
| Provenance | Ownership history quality | receipts, chain of custody, certificates, exhibition history |

## Purpose-based weights

| Purpose | Condition | Rarity | Authenticity | Demand | Provenance |
|---------|-----------|--------|--------------|--------|------------|
| sale | 0.25 | 0.15 | 0.25 | 0.25 | 0.10 |
| insurance | 0.25 | 0.10 | 0.20 | 0.15 | 0.30 |
| estate | 0.20 | 0.20 | 0.20 | 0.20 | 0.20 |
| appraisal | 0.22 | 0.18 | 0.20 | 0.20 | 0.20 |
| authentication | 0.15 | 0.10 | 0.50 | 0.05 | 0.20 |

## Scoring rules
1. **Condition/Grade**
   - Sheldon 1-70 → linear map to 0-100.
   - PSA/BGS/CGC 1-10 → linear map to 0-100.
   - Qualitative words (mint, excellent, fine, good, fair, poor, worn) → band center.
   - Apply defect and photo-availability penalties.
2. **Rarity**
   - Key-date / iconic-item indicators → ~88.
   - Common / mass-produced signals → ~22.
   - Otherwise category baseline.
3. **Authenticity**
   - Baseline 50.
   - +22 if independent certification exists (ignore placeholders like `"none"`).
   - +6 to +12 for provenance chain.
   - +6 for clear photos.
   - −25 to −35 for red flags (too-good deal, missing hallmark, no provenance).
4. **Demand**
   - Strong signals → ~80; weak signals → ~30; otherwise category baseline.
5. **Provenance**
   - Additive score from chain of custody, receipts, certificates, exhibitions, and notes.

## Confidence band
- **High** — all required fields present, photos available, no dimension below 50, no fallback citations.
- **Medium** — some missing data, fallback citation used, or one dimension below 50.
- **Low** — missing required fields, no photos, critically low dimension, or significant red flags.

## Output schema
```json
{
  "dimensions": [
    {"dimension": "condition", "score": 17.0, "weight": 0.25, "justification": "Sheldon 'worn' band mapped to condition index; photos unavailable.", "citations": ["Sheldon Coin Grading Scale 1-70 (PCGS/NGC)", "Condition penalty: no photographs"]}
  ],
  "composite": 45.5,
  "confidence": "low",
  "value_index": 45.5,
  "value_range_low": 300.0,
  "value_range_high": 800.0,
  "currency": "USD",
  "assumptions": ["Framework: Sheldon Coin Grading Scale / PCGS-NGC", "Valuation purpose: sale", "Currency: USD", "Visual assessment based on description; photos not reviewed."],
  "limitations": ["No in-hand inspection; grading is an estimate.", "Monetary range requires comparable-sales research."]
}
```

## Quality Gate
- [ ] All five dimensions are scored.
- [ ] Every score has at least one citation (framework or evidence source).
- [ ] Weights sum to 1.0 and are surfaced to the user.
- [ ] Confidence band is justified by evidence quality.
