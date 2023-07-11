import strawberry
from datetime import datetime
from uuid import UUID
from typing import Annotated, TYPE_CHECKING

from fileshare.graphql.types import ErrorType

if TYPE_CHECKING:
    from fileshare.graphql.file.types import FileType

@strawberry.type
class ShareType:
    id: UUID
    created = datetime
    updated = datetime | None
    file: Annotated["FileType", strawberry.lazy("fileshare.graphql.file.types")]
    key: str
    expiry: datetime
    download_limit: int
    download_count: int

@strawberry.type
class AddShareError(ErrorType):
    pass

@strawberry.type
class AddShareResult:
    share: ShareType
    errors: list[AddShareError]

@strawberry.type
class RemoveShareError(ErrorType):
    pass

@strawberry.type
class RemoveShareResult:
    share: ShareType
    errors: list[RemoveShareError]
