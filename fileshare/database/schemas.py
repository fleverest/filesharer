from datetime import datetime
from pydantic import BaseModel


class Share(BaseModel):

    """A Base class for file-Shares"""

    file_id: int
    key: str
    expiry: datetime
    download_limit: int
    download_count: int

class ShareCreate(Share):

    """A class for creating file-shares"""

    pass

class File(BaseModel):

    """A Base class for Files"""

    id: int
    file_name: str
    object_name: str | None = None
    active: bool = True
    shares: list[Share] = []

class FileCreate(File):

    """A class for creating files"""

    pass
