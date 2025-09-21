from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    ALCHEMY_ECHO: str = 'False'

    @property
    def get_database_url(self) -> str:
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )

    @property
    def get_alchemy_echo(self) -> bool:
        return self.ALCHEMY_ECHO == 'True'


@lru_cache
def get_pg_settings() -> PostgresSettings:
    return PostgresSettings()
