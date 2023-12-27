from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    host: str = Field()
    port: int = Field()
    log_level: str = Field(default="INFO")
    debug_mode: str = Field(default=False)

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
