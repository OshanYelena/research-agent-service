def attach_citation_ids(sources: list[dict]) -> list[dict]:
    cited_sources = []

    for index, source in enumerate(sources, start=1):
        cited_sources.append(
            {
                **source,
                "citation_id": index,
            }
        )

    return cited_sources