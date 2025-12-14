from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    POSTGRES_HOST: str = Field(validation_alias=AliasChoices("POSTGRES_HOST", "PG_HOST"))
    POSTGRES_PORT: int = Field(validation_alias=AliasChoices("POSTGRES_PORT", "PG_PORT"))
    POSTGRES_USER: str = Field(validation_alias=AliasChoices("POSTGRES_USER", "PG_USER"))
    POSTGRES_DB: str = Field(validation_alias=AliasChoices("POSTGRES_DB", "PG_DB"))
    POSTGRES_PASSWORD: str = Field(
        validation_alias=AliasChoices("POSTGRES_PASSWORD", "PG_PASSWORD")
    )
    BOT_TOKEN: str | None = None

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        extra="ignore",
    )


settings = Settings()
