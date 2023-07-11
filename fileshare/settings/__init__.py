from pydantic import BaseSettings

from fileshare.settings.database import DatabaseSettings
from fileshare.settings.minio import MinioSettings
from fileshare.settings.graphql import GraphQLSettings

class Settings(BaseSettings):

    """A Settings class for storing the fileshare application configuration."""

    minio: MinioSettings
    database: DatabaseSettings
    graphql: GraphQLSettings

    class Config:
        env_prefix = ""
        env_nested_delimiter = "__"

settings = Settings()
