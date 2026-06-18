from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://agentdesk:agentdesk_password@127.0.0.1:5433/agentdesk_db"
    xai_api_key: str = ""
    xai_model: str = "grok-3"
    rag_similarity_threshold: float = 0.75

    class Config:
        env_file = ".env"


settings = Settings()
