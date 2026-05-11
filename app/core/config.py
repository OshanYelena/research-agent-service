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

    CRAWLER_BLOCKED_DOMAINS: str = "localhost,127.0.0.1,0.0.0.0"
    CRAWLER_MIN_CONTENT_CHARS: int = 200

    BRAVE_SEARCH_API_KEY: str | None = None
    SEARCH_MAX_RESULTS: int = 5

    SERPER_API_KEY: str | None = None

    SEARCH_TIMEOUT_SECONDS: float = 20.0

    @property
    def blocked_domains(self) -> set[str]:
        return {
            domain.strip().lower()
            for domain in self.CRAWLER_BLOCKED_DOMAINS.split(",")
            if domain.strip()
        }

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()