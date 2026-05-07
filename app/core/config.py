from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Research Agent Service"
    APP_VERSION: str = "0.0.1"

    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    CRAWLER_TIMEOUT_SECONDS: float = 10.0
    CRAWLER_MAX_URLS: int = 5
    CRAWLER_MAX_CONTENT_CHARS: int = 50_000
    CRAWLER_USER_AGENT: str = "ResearchAgentService/0.1"
    CRAWLER_MAX_CONCURRENCY: int = 3

    OPENAI_API_KEY: str | None = None
    LLM_MODEL: str
    LLM_MAX_INPUT_CHARS: int = 12_000


    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()