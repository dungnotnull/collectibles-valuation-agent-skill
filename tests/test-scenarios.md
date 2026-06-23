# tests/test-scenarios.md — Collectibles Valuation (stamps/coins/watches/antiques/cards)

These scenarios validate the `collectibles-valuation` harness end-to-end. Each scenario has a corresponding automated regression test in `tests/test_harness.py`. Run all scenarios with:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

### Scenario 1: 1916-D Mercury dime
- **Input:** User describes a worn 1916-D dime. Expect Sheldon-grade estimate, authentication warnings (common counterfeit), comps-based range, and grading recommendation.
- **Expected harness behavior:**
  - Intake collects required fields; missing fields trigger targeted questions.
  - Framework selection is justified to the user.
  - Scoring covers all dimensions (Rarity, Condition/Grade, Authenticity confidence, Demand/Liquidity, Provenance) with cited justifications.
  - Roadmap is prioritized by effort × impact.
- **Pass criteria:** every score cites a framework/source; assumptions + limitations stated; devil's-advocate pass evident.

### Scenario 2: Sealed vintage Pokemon card
- **Input:** Raw Base Set Charizard. Expect PSA grading scenario modeling and value range by grade, plus authenticity red flags.
- **Expected harness behavior:**
  - Intake collects required fields; missing fields trigger targeted questions.
  - Framework selection is justified to the user.
  - Scoring covers all dimensions with cited justifications.
  - Roadmap is prioritized by effort × impact.
- **Pass criteria:** every score cites a framework/source; assumptions + limitations stated; devil's-advocate pass evident.

### Scenario 3: Inherited pocket watch, unknown maker
- **Input:** Limited photos. Expect framework-selector to request hallmarks/serials, graceful low-confidence range, provenance research steps.
- **Expected harness behavior:**
  - Intake returns `incomplete` status with targeted questions for serial/hallmark and maker.
  - Framework selection still cites NAWCC.
  - No scorecard produced until required data is supplied.
- **Pass criteria:** missing-field gate blocks progress; framework justified even when incomplete.

### Scenario 4: Antique vase for insurance
- **Input:** Purpose is insurance scheduling. Expect replacement-value (cost) approach vs fair-market distinction and USPAP-style documentation.
- **Expected harness behavior:**
  - Framework selection cites ISA/USPAP and cost approach.
  - Roadmap includes a formal replacement-cost appraisal action.
- **Pass criteria:** insurance-specific approach selected; roadmap contains critical insurance action.

### Scenario 5: Suspected forgery / too-good deal
- **Input:** Stamp offered far below market. Expect authenticity-confidence scoring to dominate and a fraud-caution roadmap.
- **Expected harness behavior:**
  - Authenticity dimension score is critically low.
  - Roadmap starts with a halt-transaction / forensic-expert action.
- **Pass criteria:** authenticity dominates; fraud-caution action has critical priority.

## Regression Checklist (run after any edit)
- [ ] Framework selection always justified
- [ ] Scorecard includes all 5 dimensions
- [ ] Roadmap items carry effort + impact + rationale + owner
- [ ] Graceful degradation when WebSearch/WebFetch unavailable
- [ ] Sources section lists every citation
- [ ] All 16 automated tests pass
