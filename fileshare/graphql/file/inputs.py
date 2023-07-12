import strawberry

from enum import Enum
from uuid import UUID

from fileshare.graphql.inputs import DateTimeRange, IntRange
from fileshare.graphql.types import OrderDirection

from sqlalchemy import desc, asc
from fileshare.database.models import File

@strawberry.input
class FileFilterInput:
    id:                list[UUID] | None = None
    name:               list[str] | None = None
    search:                   str | None = None
    created:        DateTimeRange | None = None
    updated:        DateTimeRange | None = None
    active:                  bool | None = None
    share_count:         IntRange | None = None
    download_count:      IntRange | None = None

@strawberry.enum
class FileSortField(Enum):
    FILE_NAME      = ["object_name", "updated", "created"]
    CREATED        = ["created", "updated"]
    UPDATED        = ["updated", "created"]
    SHARE_COUNT    = ["share_count", "updated", "created"]
    DOWNLOAD_COUNT = ["download_count", "updated", "created"]

@strawberry.input
class FileSortInput:
    direction: OrderDirection
    field: FileSortField

    @property
    def items(self):
        args = []
        order = desc if self.direction.value == "desc" else asc
        for col in self.field.value:
            args.append(order(getattr(File, col)))
        return args
