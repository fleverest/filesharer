from pydantic import BaseModel

class MinioSettings(BaseModel):

    """A class for storing the Minio client configuration"""

    endpoint: str
    bucket: str
    access_key: str
    secret_key: str
    upload_expire: int
    download_expire: int
