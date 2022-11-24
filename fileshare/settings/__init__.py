from pydantic import BaseSettings, Field

from fileshare.settings.database import DatabaseSettings
from fileshare.settings.minio import MinioSettings

class Settings(BaseSettings):

    """A Settings class for storing the fileshare application configuration."""

    minio: MinioSettings
    database: DatabaseSettings

    class Config:
        env_prefix = ""
        env_nested_delimiter = "__"

settings = Settings()
