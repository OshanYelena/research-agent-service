from app.core.tracing import get_tracer


def test_get_tracer_returns_tracer():
    tracer = get_tracer("test")

    assert tracer is not None