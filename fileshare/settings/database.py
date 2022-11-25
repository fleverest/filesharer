from pydantic import BaseModel

class DatabaseSettings(BaseModel):

    """A class for storing the Database configuration"""

    protocol: str
    hostname: str
    username: str
    password: str
    database: str
    port: str
