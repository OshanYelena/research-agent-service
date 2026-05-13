def generate_follow_up_question(
    query: str,
    research_reflection: dict,
    source_sufficiency: dict,
) -> str | None:
    confidence = research_reflection.get("confidence")
    decision = research_reflection.get("decision")

    if confidence == "high" and decision == "answer":
        return None

    reasons = source_sufficiency.get("reasons", [])

    if any("Fewer than 2 usable sources" in reason for reason in reasons):
        return (
            f"I found limited usable source material for '{query}'. "
            "Would you like me to broaden the search scope or focus on official documentation?"
        )

    if any("Fresh/latest research" in reason for reason in reasons):
        return (
            f"I found some information for '{query}', but not enough high-quality recent sources. "
            "Should I prioritize official sources, recent blog posts, or open-source repositories?"
        )

    if confidence == "medium":
        return (
            f"I found useful but imperfect evidence for '{query}'. "
            "Would you like a deeper comparison, a shorter overview, or source-by-source analysis?"
        )

    return (
        f"The available evidence for '{query}' is limited. "
        "Would you like me to try a broader search strategy?"
    )