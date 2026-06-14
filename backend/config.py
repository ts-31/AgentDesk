from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://agentdesk:agentdesk_password@127.0.0.1:5433/agentdesk_db"

    class Config:
        env_file = ".env"


settings = Settings()
