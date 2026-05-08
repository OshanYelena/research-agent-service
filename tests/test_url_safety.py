from app.crawler.url_safety import deduplicate_urls, is_url_allowed


def test_allows_https_url():
    allowed, reason = is_url_allowed("https://example.com")

    assert allowed is True
    assert reason is None


def test_rejects_file_scheme():
    allowed, reason = is_url_allowed("file:///etc/passwd")

    assert allowed is False
    assert "scheme not allowed" in reason


def test_rejects_blocked_domain():
    allowed, reason = is_url_allowed("http://localhost:8000")

    assert allowed is False
    assert "blocked" in reason


def test_deduplicate_urls():
    urls = [
        "https://example.com",
        "https://example.com",
        "https://example.org",
    ]

    result = deduplicate_urls(urls)

    assert result == [
        "https://example.com",
        "https://example.org",
    ]