# -*- coding: utf-8 -*-
"""Intake validation and missing-field detection.

The intake stage is the first quality gate: it guarantees that the scoring
engine has enough structured information to produce a defensible valuation.
When information is missing it returns targeted questions rather than
fabricating data.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .schema import Category, ConditionEvidence, IntakeProfile, ProvenanceEvidence, ValuationPurpose


REQUIRED_ALL = ["category", "item_name", "description", "purpose"]

CATEGORY_REQUIRED: Dict[Category, List[str]] = {
    Category.COIN: ["condition_description", "year_or_date", "mint_mark_if_any"],
    Category.CARD: ["condition_description", "set_name", "year_released"],
    Category.STAMP: ["condition_description", "country", "issue_year"],
    Category.WATCH: ["condition_description", "maker_if_known", "serial_or_hallmark"],
    Category.ANTIQUE: ["condition_description", "dimensions_or_material", "maker_marks"],
}

CATEGORY_QUESTIONS: Dict[Category, Dict[str, str]] = {
    Category.COIN: {
        "condition_description": "What is the visible condition (e.g., Good, Fine, Very Fine, or a numeric grade)?",
        "year_or_date": "What is the date/year on the coin?",
        "mint_mark_if_any": "Is there a mint mark (e.g., D, S, P, none)?",
        "authentication": "Has it been authenticated or certified by PCGS, NGC, ANACS, or another service?",
        "provenance": "Do you have receipts, prior auction records, or a chain of ownership?",
    },
    Category.CARD: {
        "condition_description": "Describe the card's condition: corners, edges, surface, centering, and whether it is sealed/raw.",
        "set_name": "Which set is the card from (e.g., Base Set, 1st Edition)?",
        "year_released": "What year was the card released?",
        "authentication": "Has it been graded by PSA, BGS, CGC, or another card grader?",
        "provenance": "Where did you acquire it, and do you have purchase records?",
    },
    Category.STAMP: {
        "condition_description": "Describe perforations, centering, gum, cancellation, and faults.",
        "country": "What country issued the stamp?",
        "issue_year": "What year was it issued (or approximate)?",
        "authentication": "Has it been expertized by the APS, PF, or another philatelic authority?",
        "provenance": "Do you have a prior collection inventory, auction record, or dealer receipt?",
    },
    Category.WATCH: {
        "condition_description": "Describe the case, dial, hands, movement, and any damage or restoration.",
        "maker_if_known": "Do you see a maker signature, brand, or caliber number?",
        "serial_or_hallmark": "Can you photograph any serial numbers, hallmarks, or case marks?",
        "authentication": "Has it been appraised or authenticated by a dealer/auction house (e.g., NAWCC member)?",
        "provenance": "Do you have service records, original box/papers, or ownership history?",
    },
    Category.ANTIQUE: {
        "condition_description": "Describe overall condition, restoration, and damage.",
        "dimensions_or_material": "What are the dimensions and materials (e.g., porcelain, bronze, wood)?",
        "maker_marks": "Are there maker marks, signatures, labels, or country-of-origin stamps?",
        "authentication": "Has it been examined by an ISA or AAA-accredited appraiser?",
        "provenance": "Do you have auction records, purchase receipts, or exhibition history?",
    },
}


def _field_present(raw: Dict[str, Any], key: str) -> bool:
    value = raw.get(key)
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    if isinstance(value, list) and not value:
        return False
    if isinstance(value, dict) and not value:
        return False
    return True


def _extract_condition(raw: Dict[str, Any]) -> ConditionEvidence:
    cond = raw.get("condition", {})
    if isinstance(cond, str):
        cond = {"textual_description": cond}
    return ConditionEvidence(
        raw_grade_value=cond.get("raw_grade_value") if cond.get("raw_grade_value") is not None else raw.get("raw_grade_value"),
        scale=cond.get("scale") if cond.get("scale") is not None else raw.get("scale"),
        textual_description=cond.get("textual_description") if cond.get("textual_description") is not None else raw.get("condition_description"),
        defects=list(cond.get("defects", raw.get("defects", []))),
        photos_available=bool(raw.get("photos_available", cond.get("photos_available", False))),
    )


def _extract_provenance(raw: Dict[str, Any]) -> ProvenanceEvidence:
    prov = raw.get("provenance", {})
    if isinstance(prov, str):
        return ProvenanceEvidence(notes=prov)
    return ProvenanceEvidence(
        chain_of_custody=list(prov.get("chain_of_custody", raw.get("provenance_chain", []))),
        receipts=list(prov.get("receipts", raw.get("receipts", []))),
        certificates=list(prov.get("certificates", raw.get("certificates", []))),
        exhibition_history=list(prov.get("exhibition_history", raw.get("exhibition_history", []))),
        notes=prov.get("notes", raw.get("provenance_notes")),
    )


def build_intake(raw: Dict[str, Any]) -> IntakeProfile:
    """Validate raw input and return a structured intake profile.

    If required fields are missing, ``profile.missing_fields`` and
    ``profile.next_questions`` are populated instead of raising.
    """
    missing: List[str] = []
    questions: List[str] = []

    for key in REQUIRED_ALL:
        if not _field_present(raw, key):
            missing.append(key)
            questions.append(f"Please provide the {key.replace('_', ' ')}.")

    category = Category(raw.get("category", "").lower()) if raw.get("category") else None
    purpose = ValuationPurpose(raw.get("purpose", "").lower()) if raw.get("purpose") else None

    if category is None:
        # Cannot ask category-specific questions yet.
        return IntakeProfile(
            category=Category.COIN,  # placeholder; missing_fields blocks progress
            item_name=raw.get("item_name", ""),
            description=raw.get("description", ""),
            purpose=ValuationPurpose.APPRAISAL,
            condition=_extract_condition(raw),
            provenance=_extract_provenance(raw),
            missing_fields=missing,
        )

    for key in CATEGORY_REQUIRED.get(category, []):
        mapped = key
        if key == "condition_description":
            cond = raw.get("condition", {})
            has_condition = _field_present(cond, "textual_description") or _field_present(raw, "condition_description")
            if not has_condition:
                missing.append(mapped)
                questions.append(CATEGORY_QUESTIONS[category]["condition_description"])
        elif not _field_present(raw, mapped):
            missing.append(mapped)
            q = CATEGORY_QUESTIONS[category].get(mapped, f"Please provide {mapped.replace('_', ' ')}.")
            questions.append(q)

    if not _field_present(raw, "authentication") and not raw.get("provenance", {}).get("certificates"):
        missing.append("authentication")
        if "authentication" in CATEGORY_QUESTIONS[category]:
            questions.append(CATEGORY_QUESTIONS[category]["authentication"])

    if not _field_present(raw, "provenance") and not raw.get("provenance"):
        missing.append("provenance")
        if "provenance" in CATEGORY_QUESTIONS[category]:
            questions.append(CATEGORY_QUESTIONS[category]["provenance"])

    condition = _extract_condition(raw)
    provenance = _extract_provenance(raw)

    return IntakeProfile(
        category=category,
        item_name=raw.get("item_name", ""),
        description=raw.get("description", ""),
        purpose=purpose or ValuationPurpose.APPRAISAL,
        condition=condition,
        provenance=provenance,
        acquisition_history=raw.get("acquisition_history"),
        authentication=list(raw.get("authentication", [])),
        market_signals=list(raw.get("market_signals", [])),
        rarity_signals=list(raw.get("rarity_signals", [])),
        red_flags=list(raw.get("red_flags", [])),
        requested_currency=raw.get("requested_currency", "USD"),
        missing_fields=missing,
        metadata=dict(raw.get("metadata", {})),
    )
