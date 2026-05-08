import httpx
import pytest
import respx

from app.crawler.http_client import create_async_client, fetch_html_async


@pytest.mark.anyio
@respx.mock
async def test_fetch_html_async_success():
    url = "https://example.com/article"

    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            headers={"content-type": "text/html"},
            text="<html><body><h1>Hello</h1></body></html>",
        )
    )

    async with await create_async_client() as client:
        status_code, html, error = await fetch_html_async(client, url)

    assert status_code == 200
    assert "<h1>Hello</h1>" in html
    assert error is None


@pytest.mark.anyio
@respx.mock
async def test_fetch_html_async_rejects_non_html():
    url = "https://example.com/file.pdf"

    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            headers={"content-type": "application/pdf"},
            content=b"fake-pdf",
        )
    )

    async with await create_async_client() as client:
        status_code, html, error = await fetch_html_async(client, url)

    assert status_code == 200
    assert html is None
    assert "Unsupported content type" in error


@pytest.mark.anyio
@respx.mock
async def test_fetch_html_async_handles_404():
    url = "https://example.com/missing"

    respx.get(url).mock(
        return_value=httpx.Response(
            404,
            headers={"content-type": "text/html"},
            text="Not Found",
        )
    )

    async with await create_async_client() as client:
        status_code, html, error = await fetch_html_async(client, url)

    assert status_code == 404
    assert html is None
    assert error is not None