import strawberry
from datetime import datetime
from uuid import UUID
from typing import Annotated, TYPE_CHECKING

from strawberry.types import Info
from fileshare.database.engine import get_db
from fileshare.database.models import File, Share

from fileshare.graphql.types import ErrorType

if TYPE_CHECKING:
    from fileshare.graphql.file.types import FileType

def resolve_file(root: "ShareType", info: Info) -> Annotated["FileType", strawberry.lazy("fileshare.graphql.file.types")]:
    from fileshare.graphql.file.types import FileType
    session = next(get_db())
    db_file = session.query(File).filter(File.id==root.file_id).first()
    if db_file:
        return FileType(**db_file.as_dict())
    else:
        return FileType(id=UUID(), created=datetime.now(), updated=datetime.now(), active=False, file_name="FILE NOT FOUND", share_count=0, download_count=0)

@strawberry.type
class ShareType:
    id: UUID
    file_id: UUID
    created: datetime
    updated: datetime
    key: str
    expiry: datetime
    download_limit: int
    download_count: int
    file: Annotated["FileType", strawberry.lazy("fileshare.graphql.file.types")] = strawberry.field(resolver=resolve_file)

    @classmethod
    def from_instance(cls, instance: Share):
        return cls(
            id=instance.id,
            file_id=instance.file_id,
            created=instance.created,
            updated=instance.updated,
            key=instance.key,
            expiry=instance.expiry,
            download_limit=instance.download_limit,
            download_count=instance.download_count
        )

@strawberry.type
class ShareNotFoundError(ErrorType):
    pass

@strawberry.type
class AddShareError(ErrorType):
    pass

@strawberry.type
class RemoveShareError(ErrorType):
    pass

@strawberry.type
class RemoveSharesResult:
    shares: list[ShareType]
    errors: list[RemoveShareError]
