def reflect_on_research_quality(
    evidence_strength: str,
    source_sufficiency: dict,
    source_conflicts: dict,
) -> dict:
    is_sufficient = source_sufficiency.get("is_sufficient", False)
    has_conflicts = source_conflicts.get("has_conflict_signals", False)

    if evidence_strength == "strong" and is_sufficient and not has_conflicts:
        return {
            "confidence": "high",
            "decision": "answer",
            "reason": "Evidence is strong, source criteria are satisfied, and no conflict signals were detected.",
        }

    if evidence_strength in {"moderate", "strong"} and is_sufficient:
        return {
            "confidence": "medium",
            "decision": "answer_with_caution",
            "reason": "Evidence is usable, but limitations or conflict signals may exist.",
        }

    return {
        "confidence": "low",
        "decision": "answer_with_limitations",
        "reason": "Evidence is insufficient, weak, or incomplete.",
    }