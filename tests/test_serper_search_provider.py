import httpx
import pytest
import respx

from app.search.serper_provider import SerperSearchProvider


@pytest.mark.anyio
@respx.mock
async def test_serper_search_provider_returns_results(monkeypatch):
    monkeypatch.setattr(
        "app.core.config.settings.SERPER_API_KEY",
        "fake-key",
    )

    url = "https://google.serper.dev/search"

    respx.post(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "organic": [
                    {
                        "title": "Example Result",
                        "link": "https://example.com",
                        "snippet": "Example snippet",
                    }
                ]
            },
        )
    )

    provider = SerperSearchProvider()

    results = await provider.search("test query", max_results=1)

    assert len(results) == 1
    assert results[0].title == "Example Result"
    assert str(results[0].url) == "https://example.com/"
    assert results[0].source == "serper"