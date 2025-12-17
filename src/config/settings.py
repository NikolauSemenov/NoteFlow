from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, RedisDsn

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8080

    project_name: str
    project_version: str

    postgres_dsn: PostgresDsn
    redis_dsn: RedisDsn
    redis_notes_prefix: str = "notes:v-1"
    redis_notes_ttl: int = 10

    @property
    def api_prefix(self) -> str:
        return f"/{self.project_name}/api/{self.project_version}"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
    )


settings = Settings()
