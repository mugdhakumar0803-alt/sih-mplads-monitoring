from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    database_url: str = "postgresql+psycopg2://user:password@localhost:5432/mplads"

    # JWT
    secret_key: str = "CHANGE_ME_IN_PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Report signing
    report_private_key_path: str = "app/signing/keys/report_private.pem"
    report_public_key_path: str = "app/signing/keys/report_public.pem"

    api_title: str = "MPLADS Monitoring System"
    api_version: str = "1.0.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
