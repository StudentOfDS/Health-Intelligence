from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Health Intelligence API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg2://health:health@db:5432/health"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
