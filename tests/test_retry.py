import pytest

from app.summarization.retry import retry_async


@pytest.mark.anyio
async def test_retry_async_succeeds_after_failure(monkeypatch):
    monkeypatch.setattr("app.core.config.settings.LLM_MAX_RETRIES", 2)

    calls = {"count": 0}

    async def flaky_operation():
        calls["count"] += 1

        if calls["count"] < 2:
            raise RuntimeError("temporary failure")

        return "success"

    result = await retry_async(
        operation=flaky_operation,
        operation_name="test_operation",
    )

    assert result == "success"
    assert calls["count"] == 2


@pytest.mark.anyio
async def test_retry_async_raises_after_max_retries(monkeypatch):
    monkeypatch.setattr("app.core.config.settings.LLM_MAX_RETRIES", 1)

    calls = {"count": 0}

    async def failing_operation():
        calls["count"] += 1
        raise RuntimeError("permanent failure")

    with pytest.raises(RuntimeError):
        await retry_async(
            operation=failing_operation,
            operation_name="test_operation",
        )

    assert calls["count"] == 2