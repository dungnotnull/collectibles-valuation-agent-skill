---
name: collectibles-valuation-sub-improvement-roadmap
description: Recommend authentication, professional grading, and sale-channel actions ranked by value-uplift vs cost.
---

## Role
Sub-skill of `collectibles-valuation`. Acts as the **roadmap-generation stage**.

## Purpose
Convert scorecard gaps into a prioritized list of concrete actions that maximize value while controlling cost and risk.

## Inputs
- `IntakeProfile`.
- `Scorecard` from `sub-scoring-engine`.
- `FrameworkSelection`.

## Action templates

| Trigger | Action | Effort | Impact | Owner |
|---------|--------|--------|--------|-------|
| Condition < 70 or ungraded | Submit to category grading service (PCGS/NGC, PSA/BGS/CGC, APS, NAWCC specialist, ISA appraiser) | medium | high | Professional third-party service |
| Authenticity < 70 | Obtain authentication / certification | medium | high/critical | Professional third-party service |
| Provenance < 60 | Compile chain-of-custody documentation | low | medium | Owner/Collector |
| Demand / comparables missing | Research comparable sales (Heritage, Sotheby's, eBay sold, catalogues) | low | high | Owner with auction support |
| Purpose = insurance | Obtain formal replacement-cost appraisal per USPAP/ISA | medium | critical | ISA/AAA-accredited appraiser |
| Purpose = sale | Select optimal sale channel (specialty auction, dealer, marketplace) | low | high | Owner with channel support |
| Red flags present | Halt transaction; engage forensic expert / law enforcement | low | critical | Forensic expert / law enforcement |

## Prioritization formula
1. Convert effort to cost: low=0.5, medium=1.5, high=2.5.
2. Convert impact to weight: critical=4.0, high=3.0, medium=2.0, low=1.0.
3. Add urgency: +2.0 for critical-impact authenticity/fraud actions.
4. Priority score = impact_weight − effort_cost + urgency.
5. Sort descending.

## Output schema
```json
{
  "roadmap": [
    {
      "action": "Obtain authentication/certification from PCGS/NGC or a reputable numismatist",
      "rationale": "Authenticity confidence is 42/100; third-party authentication removes the largest risk to value.",
      "effort": "medium",
      "impact": "high",
      "expected_effect": "Removes authenticity risk; often required for high-value transactions.",
      "owner": "Professional third-party service",
      "dimension": "authenticity",
      "priority_score": 3.2
    }
  ]
}
```

## Quality Gate
- [ ] Every action has effort, impact, rationale, owner, and expected effect.
- [ ] Actions are sorted by priority score (effort × impact + urgency).
- [ ] Authentication red flags produce a fraud-caution action at the top.
- [ ] Roadmap items reference the same framework used in scoring.
