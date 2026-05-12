from app.core.config import settings

def test_request_timeout_setting_exists():

    assert settings.REQUEST_TIMEOUT_SECONDS > 0