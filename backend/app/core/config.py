from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Health Intelligence API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg2://health:health@db:5432/health"
    cors_origins: list[str] = ["http://localhost:3000"]

    pii_schema: str = "pii"
    phi_schema: str = "phi"

    jwt_secret_key: str = "change-me-super-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    field_encryption_key: str = "change-me-field-encryption-key"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
