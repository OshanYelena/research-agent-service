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
                <p>This is the first paragraph.</p>
                <p>This is the second paragraph.</p>
            </article>
        </body>
    </html>
    """

    title, text = extract_text_from_html(html)

    assert title is not None
    assert "Test Article" in text
    assert "first paragraph" in text
    assert "alert" not in text