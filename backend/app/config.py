from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    database_url: str

    secret_key: str

    algorithm: str = "HS256"

    access_token_expire_minutes: int = 30

    jwt_issuer: str = "mplads-monitoring"

    jwt_audience: str = "mplads-api"

    report_private_key_path: str = (
        "app/signing/keys/report_private.pem"
    )

    report_public_key_path: str = (
        "app/signing/keys/report_public.pem"
    )

    api_title: str = "MPLADS Monitoring System"

    api_version: str = "1.0.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()