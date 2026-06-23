# -*- coding: utf-8 -*-
"""Framework selection and evidence-to-score conversions.

Every conversion references a named, citable framework so the skill never
falls back to ad-hoc criteria.  Numeric mappings are deterministic and
version-controlled; they are surfaced to the user in the final report.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from .schema import (
    Category,
    ConditionEvidence,
    Dimension,
    FrameworkName,
    GradingScale,
    ValuationApproach,
    ValuationPurpose,
)

CATEGORY_FRAMEWORKS: dict[Category, List[FrameworkName]] = {
    Category.COIN: [FrameworkName.SHELDON_PCGS_NGC, FrameworkName.COMPARABLE_SALES],
    Category.CARD: [FrameworkName.PSA_BGS_CGC, FrameworkName.COMPARABLE_SALES],
    Category.STAMP: [FrameworkName.APS_SCOTT, FrameworkName.COMPARABLE_SALES],
    Category.WATCH: [FrameworkName.NAWCC, FrameworkName.COMPARABLE_SALES],
    Category.ANTIQUE: [FrameworkName.ISA_USPAP, FrameworkName.COMPARABLE_SALES],
}

CATEGORY_PRIMARY_SCALE: dict[Category, GradingScale] = {
    Category.COIN: GradingScale.SHELDON_70,
    Category.CARD: GradingScale.PSA_10,
    Category.STAMP: GradingScale.APS_STAMP,
    Category.WATCH: GradingScale.NAWCC_WATCH,
    Category.ANTIQUE: GradingScale.ISA_QUALITATIVE,
}

PURPOSE_APPROACH: dict[ValuationPurpose, List[ValuationApproach]] = {
    ValuationPurpose.SALE: [ValuationApproach.MARKET],
    ValuationPurpose.INSURANCE: [ValuationApproach.COST, ValuationApproach.MARKET],
    ValuationPurpose.ESTATE: [ValuationApproach.MARKET, ValuationApproach.COST],
    ValuationPurpose.APPRAISAL: [ValuationApproach.MARKET, ValuationApproach.COST, ValuationApproach.INCOME],
    ValuationPurpose.AUTHENTICATION: [ValuationApproach.MARKET],
}

# Named qualitative condition words mapped to a 0-100 condition score band.
QUALITY_WORDS = {
    "mint": 95.0,
    "gem": 92.0,
    "unc": 90.0,
    "uncirculated": 90.0,
    "pristine": 95.0,
    "excellent": 80.0,
    "fine": 65.0,
    "very fine": 75.0,
    "good": 55.0,
    "very good": 60.0,
    "fair": 35.0,
    "poor": 15.0,
    "worn": 25.0,
    "damaged": 10.0,
    "sealed": 88.0,
    "raw": 50.0,
    "ungraded": 45.0,
    "unknown": 35.0,
}

NAWCC_WORD_SCORES = {
    "mint": 95.0,
    "excellent": 82.0,
    "very good": 65.0,
    "good": 50.0,
    "fair": 30.0,
    "poor": 12.0,
}

APS_WORD_SCORES = {
    "superb": 95.0,
    "extremely fine": 85.0,
    "very fine": 70.0,
    "fine": 55.0,
    "average": 40.0,
    "faulty": 20.0,
}

ISA_WORD_SCORES = {
    "excellent": 85.0,
    "good": 65.0,
    "fair": 40.0,
    "poor": 20.0,
}

KEY_DATE_INDICATORS = {
    Category.COIN: [
        "1916-d", "1916 d", "mercury dime", "walking liberty half",
        "1909-s vdb", "1955 doubled die", "1937-d 3-leg",
    ],
    Category.STAMP: [
        "inverted jenny", "penny black", "mauritius", "treskilling yellow",
    ],
    Category.CARD: [
        "base set charizard", "black lotus", "mickey mantle 1952",
    ],
    Category.WATCH: [
        "patek philippe", "rolex submariner", "omega speedmaster",
    ],
}


def select_frameworks(
    category: Category, purpose: ValuationPurpose
) -> Tuple[List[FrameworkName], List[ValuationApproach], GradingScale, str]:
    """Return the framework set, valuation approach, primary grading scale,
    and a human-readable justification for a subject.
    """
    frameworks = CATEGORY_FRAMEWORKS[category][:]
    approaches = PURPOSE_APPROACH[purpose][:]
    scale = CATEGORY_PRIMARY_SCALE[category]

    if purpose == ValuationPurpose.INSURANCE:
        justification = (
            f"{category.value} valuation for insurance scheduling uses "
            f"{frameworks[0].value} for condition documentation and "
            f"{FrameworkName.ISA_USPAP.value} for replacement-cost / fair-market "
            f"distinction; {ValuationApproach.COST.value} approach is primary."
        )
    elif purpose == ValuationPurpose.SALE:
        justification = (
            f"{category.value} sale valuation applies {frameworks[0].value} "
            f"for grade-derived pricing and {FrameworkName.COMPARABLE_SALES.value} "
            f"for market evidence; {ValuationApproach.MARKET.value} approach is primary."
        )
    elif purpose == ValuationPurpose.ESTATE:
        justification = (
            f"Estate distribution requires both {ValuationApproach.MARKET.value} "
            f"and {ValuationApproach.COST.value} evidence under {FrameworkName.ISA_USPAP.value}."
        )
    elif purpose == ValuationPurpose.AUTHENTICATION:
        justification = (
            f"Authentication-first valuation centers on {FrameworkName.COMPARABLE_SALES.value} "
            f"for reference while the item is verified against {frameworks[0].value}."
        )
    else:
        justification = (
            f"General appraisal selects {frameworks[0].value} as the grading standard "
            f"and {FrameworkName.COMPARABLE_SALES.value} as the pricing evidence base."
        )
    return frameworks, approaches, scale, justification


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def normalize_condition_score(evidence: ConditionEvidence, category: Category) -> Tuple[float, str, List[str]]:
    """Convert raw grade or textual description into a 0-100 condition score.

    Returns:
        (score, reasoning, citations)
    """
    scale = evidence.scale or CATEGORY_PRIMARY_SCALE[category]
    raw = evidence.raw_grade_value
    citations: List[str] = []

    if raw is not None and scale == GradingScale.SHELDON_70:
        score = 1.0 + (raw - 1.0) / 69.0 * 99.0
        citations = [f"Sheldon Coin Grading Scale 1-70 (PCGS/NGC): grade {raw}"]
        return _clamp(score), f"Sheldon grade {raw}/70 mapped linearly to condition index.", citations

    if raw is not None and scale in (GradingScale.PSA_10, GradingScale.BGS_10, GradingScale.CGC_10):
        score = 1.0 + (raw - 1.0) / 9.0 * 99.0
        citations = [f"{scale.value.upper()} grading scale: grade {raw}/10"]
        return _clamp(score), f"{scale.value.upper()} grade {raw}/10 mapped linearly to condition index.", citations

    text = (evidence.textual_description or "").lower()
    word_scores: List[float] = []
    for word, value in QUALITY_WORDS.items():
        if word in text:
            word_scores.append(value)

    if scale == GradingScale.NAWCC_WATCH:
        for word, value in NAWCC_WORD_SCORES.items():
            if word in text:
                word_scores.append(value)
        citations = ["NAWCC watch condition grading (verbal condition bands)"]
    elif scale == GradingScale.APS_STAMP:
        for word, value in APS_WORD_SCORES.items():
            if word in text:
                word_scores.append(value)
        citations = ["APS philatelic grading (centering, condition, gum)"]
    elif scale == GradingScale.ISA_QUALITATIVE:
        for word, value in ISA_WORD_SCORES.items():
            if word in text:
                word_scores.append(value)
        citations = ["ISA/USPAP qualitative condition assessment"]
    else:
        citations = [f"{scale.value} qualitative description parsed to condition index"]

    if word_scores:
        score = sum(word_scores) / len(word_scores)
        reason = "Derived from qualitative description matching named condition bands."
    else:
        score = 40.0 if "unknown" in text else 50.0
        reason = "No specific condition language found; defaulting to moderate condition with low confidence."
        citations.append("Default fallback due to ambiguous condition evidence")

    for defect in evidence.defects:
        if defect.lower() in ("scratch", "dent", "tear", "crease", "hole", "rust", "corrosion", "water damage"):
            score -= 12.0
        else:
            score -= 6.0

    if not evidence.photos_available:
        score -= 8.0
        reason += " Photos unavailable; penalty applied."
        citations.append("Condition penalty: no photographs")

    return _clamp(score), reason, citations


def rarity_score(category: Category, signals: List[str], metadata: dict) -> Tuple[float, str, List[str]]:
    """Compute a 0-100 rarity score from explicit metadata or item signals."""
    if "rarity_estimate" in metadata:
        return _clamp(float(metadata["rarity_estimate"])), "Rarity provided by operator/appraiser.", ["Appraiser-supplied rarity estimate"]

    text = " ".join(signals).lower()
    name = metadata.get("item_name", "").lower()
    combined = f"{name} {text}"

    indicators = KEY_DATE_INDICATORS.get(category, [])
    hits = [i for i in indicators if i in combined]
    if hits:
        return (
            88.0,
            f"Key-date / iconic-item indicators detected ({', '.join(hits)}); high rarity."[:200],
            ["Key-date rarity heuristics keyed to catalogue references"],
        )

    if any(w in combined for w in ("common", "mass produced", "modern", "reprint")):
        return 22.0, "Signals indicate common / mass-produced item.", ["Catalogue rarity band: common issue"]
    if any(w in combined for w in ("limited", "low mintage", "scarce", "rare")):
        return 78.0, "Signals indicate limited supply / scarce issue.", ["Catalogue rarity band: scarce/rare"]

    defaults = {Category.COIN: 50.0, Category.CARD: 55.0, Category.STAMP: 48.0, Category.WATCH: 52.0, Category.ANTIQUE: 45.0}
    return defaults.get(category, 45.0), "No explicit rarity evidence; using category baseline.", ["Category rarity baseline"]


def demand_score(category: Category, signals: List[str], metadata: dict) -> Tuple[float, str, List[str]]:
    """Compute a 0-100 demand/liquidity score."""
    if "demand_estimate" in metadata:
        return _clamp(float(metadata["demand_estimate"])), "Demand provided by operator/appraiser.", ["Appraiser-supplied demand estimate"]

    text = " ".join(signals).lower()
    if any(w in text for w in ("hot", "trending", "high demand", "liquid", "auction interest")):
        return 80.0, "Strong market-interest signals.", ["Comparable-sales demand indicators"]
    if any(w in text for w in ("niche", "slow", "illiquid", "unwanted", "declining")):
        return 30.0, "Weak or niche demand signals.", ["Comparable-sales demand indicators"]

    defaults = {Category.COIN: 68.0, Category.CARD: 75.0, Category.STAMP: 50.0, Category.WATCH: 62.0, Category.ANTIQUE: 48.0}
    return defaults.get(category, 50.0), "No explicit demand evidence; using category baseline.", ["Category demand baseline"]


def authenticity_score(
    category: Category,
    authentication: List[str],
    provenance: dict,
    red_flags: List[str],
    photos_available: bool,
    metadata: dict,
) -> Tuple[float, str, List[str]]:
    """Compute a 0-100 authenticity-confidence score."""
    if "authenticity_estimate" in metadata:
        return _clamp(float(metadata["authenticity_estimate"])), "Authenticity provided by operator/appraiser.", ["Appraiser-supplied authenticity estimate"]

    score = 50.0
    citations: List[str] = ["Initial baseline: no expert authentication yet"]

    certs = [
        a for a in authentication
        if a.strip() and a.strip().lower() not in {"none", "n/a", "na", "no", "unknown", "pending"}
    ]
    if certs:
        score += 22.0
        citations.append(f"Certification(s) on file: {len(certs)}")

    chain = provenance.get("chain_of_custody", [])
    if len(chain) >= 2:
        score += 12.0
        citations.append("Provenance chain of custody documented")
    elif chain:
        score += 6.0
        citations.append("Limited provenance documentation")

    if photos_available:
        score += 6.0
        citations.append("Clear photographs available for visual authentication")

    if any(f.lower() in ("too good to be true", "price too low", "no serial", "missing hallmark", "unclear photos") for f in red_flags):
        score -= 35.0
        citations.append("Red-flag warning: transaction/item attributes undermine confidence")
    if any(f.lower() in ("seller unknown", "no provenance", "counterfeit risk") for f in red_flags):
        score -= 25.0
        citations.append("Red-flag warning: provenance or seller risk")

    return _clamp(score), "Authenticity confidence adjusted for certifications, provenance, photos, and risk flags.", citations


def provenance_score(provenance: dict, metadata: dict) -> Tuple[float, str, List[str]]:
    """Compute a 0-100 provenance strength score."""
    if "provenance_estimate" in metadata:
        return _clamp(float(metadata["provenance_estimate"])), "Provenance provided by operator/appraiser.", ["Appraiser-supplied provenance estimate"]

    score = 0.0
    citations: List[str] = []
    chain = provenance.get("chain_of_custody", [])
    receipts = provenance.get("receipts", [])
    certs = provenance.get("certificates", [])
    exhibitions = provenance.get("exhibition_history", [])
    notes = provenance.get("notes", "")

    if chain:
        score += min(30.0, 10.0 + (len(chain) - 1) * 8.0)
        citations.append("Chain-of-custody documentation")
    if receipts:
        score += min(25.0, 8.0 + (len(receipts) - 1) * 6.0)
        citations.append("Purchase/acquisition receipts")
    if certs:
        score += min(25.0, 8.0 + (len(certs) - 1) * 6.0)
        citations.append("Certificates or letters of authenticity")
    if exhibitions:
        score += min(15.0, 5.0 + (len(exhibitions) - 1) * 4.0)
        citations.append("Exhibition history")
    if notes and len(notes.strip()) >= 20:
        score += 10.0
        citations.append("Written provenance narrative")

    if score == 0.0:
        score = 15.0
        citations.append("No provenance evidence supplied")

    return _clamp(score), "Provenance strength computed from custody, receipts, certificates, exhibitions, and notes.", citations
