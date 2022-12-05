import strawberry

from uuid import UUID
from datetime import datetime

from fileshare.graphql.types import ErrorType


@strawberry.type
class FileType:
    id: UUID
    created: datetime
    updated: datetime
    active: bool
    file_name: str
#    shares: list[Shares]

@strawberry.type
class FileCreateSuccess:
    file: FileType

@strawberry.type
class FileCreateError:
    errors: list[ErrorType]

FileCreateResult = strawberry.union(
    "FileCreateResult",
    (
        FileCreateSuccess,
        FileCreateError
    )
)
