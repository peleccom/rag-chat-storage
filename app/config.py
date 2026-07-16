from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = "db"
    db_port: int = 5432
    db_user: str = "ragchat"
    db_password: str = "ragchat_secret"
    db_name: str = "ragchat"

    api_key: str

    rate_limit_per_minute: int = 60

    cors_origins: str = "*"

    log_level: str = "INFO"

    env_name: str = "local"

    database_url: str | None = None

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
