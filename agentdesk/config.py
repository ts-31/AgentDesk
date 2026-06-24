from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://agentdesk:agentdesk_password@127.0.0.1:5433/agentdesk_db"
    xai_api_key: str = ""
    xai_model: str = "grok-3"
    rag_similarity_threshold: float = 0.75

    # LangSmith observability (optional — tracing disabled if not set)
    langsmith_tracing: bool = False
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_api_key: str = ""
    langsmith_project: str = "agentdesk"

    # JWT Authentication
    # Override jwt_secret_key in .env for production — never commit the real secret.
    jwt_secret_key: str = "teamflow-dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440   # 24 hours
    refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
