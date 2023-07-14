from sqlalchemy import select
from sqlalchemy.orm import query
import strawberry
from uuid import UUID
from datetime import datetime
from typing import Annotated, TYPE_CHECKING

from strawberry.types import Info

from fileshare.database.engine import get_session
from fileshare.database.models import File, Share
from fileshare.graphql.types import ErrorType

if TYPE_CHECKING:
    from fileshare.graphql.share.types import ShareType


async def resolve_shares(root: "FileType", info: Info) -> list[Annotated["ShareType", strawberry.lazy("fileshare.graphql.share.types")]]:
    from fileshare.graphql.share.types import ShareType
    async with get_session() as session:
        query_shares = select(Share).filter(Share.file_id==root.id)
        result = await session.execute(query_shares)
        shares = result.scalars().all()
        return [ShareType.from_instance(s) for s in shares]

@strawberry.type
class FileType:
    id: UUID
    created: datetime
    updated: datetime
    active: bool
    file_name: str
    share_count: int
    download_count: int
    shares: list[Annotated["ShareType", strawberry.lazy("fileshare.graphql.share.types")]] = strawberry.field(resolver=resolve_shares)

    @classmethod
    def from_instance(cls, instance: File):
        return cls(
            id=instance.id,
            created=instance.created,
            updated=instance.updated,
            active=instance.active,
            file_name=instance.object_name,
            share_count=instance.share_count,
            download_count=instance.download_count
        )

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
