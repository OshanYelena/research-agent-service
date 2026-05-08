def expand_query(query: str) -> list[str]:
    cleaned_query = " ".join(query.split())

    expanded_queries = [
        cleaned_query,
        f"{cleaned_query} latest",
        f"{cleaned_query} overview",
    ]

    seen = set()
    unique_queries = []

    for item in expanded_queries:
        normalized = item.lower()

        if normalized not in seen:
            seen.add(normalized)
            unique_queries.append(item)

    return unique_queries