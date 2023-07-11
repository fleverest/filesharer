import strawberry

from enum import Enum
from uuid import UUID

from fileshare.graphql.inputs import DateTimeRange, IntRange
from fileshare.graphql.types import OrderDirection

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
    FILE_NAME      = ["file_name", "updated"]
    OBJECT_NAME    = ["object_name", "updated"]
    DOWNLOADS      = ["downloads", "updated"]
    CREATED        = ["created"]
    UPDATED        = ["updated"]
    SHARE_COUNT    = ["share_count", "updated"]
    DOWNLOAD_COUNT = ["download_count", "updated"]

@strawberry.input
class FileSortInput:
    direction: OrderDirection
    field: FileSortField

    @property
    def items(self) -> list[str]:
        out = []
        for value in self.field.value:
            sorter = "file_" + value
            if self.direction == OrderDirection.DESC:
                sorter += " DESC"
            out.append(sorter)
        return out
