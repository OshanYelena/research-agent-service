from app.summarization.citations import attach_citation_ids


def test_attach_citation_ids():
    sources = [
        {"url": "https://example.com/a"},
        {"url": "https://example.com/b"},
    ]

    result = attach_citation_ids(sources)

    assert result[0]["citation_id"] == 1
    assert result[1]["citation_id"] == 2