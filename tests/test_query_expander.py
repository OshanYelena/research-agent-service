from app.search.query_expander import expand_query


def test_expand_query_returns_original_query_first():
    queries = expand_query("ai agent frameworks")

    assert queries[0] == "ai agent frameworks"


def test_expand_query_removes_extra_spaces():
    queries = expand_query("  ai   agent   frameworks  ")

    assert queries[0] == "ai agent frameworks"


def test_expand_query_returns_unique_queries():
    queries = expand_query("latest")

    assert len(queries) == len(set(query.lower() for query in queries))