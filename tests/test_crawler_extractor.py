from app.crawler.extractor import extract_text_from_html


def test_extract_text_from_html():
    html = """
    <html>
        <head>
            <title>Test Article</title>
            <script>alert("bad")</script>
        </head>
        <body>
            <article>
                <h1>Test Article</h1>
                <p>This is the first paragraph with enough meaningful content for extraction testing.</p>
                <p>This is the second paragraph with additional content so the minimum threshold is satisfied.</p>
                <p>This is the third paragraph to make the article long enough for the crawler extractor.</p>
                <p>This is the fourth paragraph to improve extraction quality scoring.</p>
                <p>This is the fifth paragraph with additional semantic content.</p>
            </article>
        </body>
    </html>
    """

    title, text, quality, score = extract_text_from_html(html)

    assert title is not None
    assert "Test Article" in text
    assert "first paragraph" in text
    assert "alert" not in text

    assert quality in {"medium", "high"}
    assert score >= 0.7


def test_extract_text_marks_short_content_as_low_quality():
    html = """
    <html>
        <head><title>Short Page</title></head>
        <body><p>Too short.</p></body>
    </html>
    """

    title, text, quality, score = extract_text_from_html(html)

    assert title == "Short Page"
    assert "Too short" in text

    assert quality in {"very_low", "low"}
    assert score <= 0.4