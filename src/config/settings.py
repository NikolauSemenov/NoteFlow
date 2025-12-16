from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8080

    project_name: str
    project_version: str

    postgres_dsn: PostgresDsn

    @property
    def api_prefix(self) -> str:
        return f"/{self.project_name}/api/{self.project_version}"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
    )


settings = Settings()
