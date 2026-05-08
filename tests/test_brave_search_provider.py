# import httpx
# import pytest
# import respx
#
# from app.search.brave_provider import BraveSearchProvider
#
#
# @pytest.mark.anyio
# @respx.mock
# async def test_brave_search_provider_returns_results(monkeypatch):
#     monkeypatch.setattr(
#         "app.core.config.settings.BRAVE_SEARCH_API_KEY",
#         "fake-key",
#     )
#
#     url = "https://api.search.brave.com/res/v1/web/search"
#
#     respx.get(url).mock(
#         return_value=httpx.Response(
#             200,
#             json={
#                 "web": {
#                     "results": [
#                         {
#                             "title": "Example Result",
#                             "url": "https://example.com",
#                             "description": "Example snippet",
#                         }
#                     ]
#                 }
#             },
#         )
#     )
#
#     provider = BraveSearchProvider()
#
#     results = await provider.search("test query", max_results=1)
#
#     assert len(results) == 1
#     assert results[0].title == "Example Result"
#     assert str(results[0].url) == "https://example.com/"
#     assert results[0].source == "brave"