import strawberry
from uuid import UUID
from datetime import datetime
from typing import Annotated, TYPE_CHECKING

from fileshare.graphql.types import ErrorType

if TYPE_CHECKING:
    from fileshare.graphql.share.types import ShareType


@strawberry.type
class FileType:
    id: UUID
    created: datetime
    updated: datetime | None
    active: bool
    file_name: str
    share_count: int
    download_count: int
    shares: list[Annotated["ShareType", strawberry.lazy("fileshare.graphql.share.types")]]

@strawberry.type
class FileNotFoundError(ErrorType):
    pass

@strawberry.type
class AddFileError(ErrorType):
    pass

@strawberry.type
class AddFilesResult:
    added: list[FileType]
    errors: list[AddFileError]

@strawberry.type
class RemoveFileError(ErrorType):
    pass

@strawberry.type
class RemoveFilesResult:
    removed: list[FileType]
    errors: list[RemoveFileError]

@strawberry.type
class PaginationError(ErrorType):
    pass
