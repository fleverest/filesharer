import strawberry

from enum import Enum
from uuid import UUID

from fileshare.graphql.inputs import DateRange, IntRange
from fileshare.graphql.types import OrderDirection

@strawberry.input
class FileFilterInput:
    id:             list[UUID] | None = None
    name:            list[str] | None = None
    search:                str | None = None
    downloads:        IntRange | None = None
    download_limit:   IntRange | None = None
    created:         DateRange | None = None
    updated:         DateRange | None = None
    active:               bool | None = None
    number_of_shares: IntRange | None = None

@strawberry.enum
class FileSortField(Enum):
    FILE_NAME        = ["file_name", "updated"]
    OBJECT_NAME      = ["object_name", "updated"]
    DOWNLOAD_LIMIT   = ["download_limit", "updated"]
    DOWNLOADS        = ["downloads", "updated"]
    CREATED          = ["created"]
    UPDATED          = ["updated"]
    SEARCH           = ["search_rank", "updated"]
    NUMBER_OF_SHARES = ["number_of_shares", "updated"]

@strawberry.input
class FileSortInput:
    direction: OrderDirection
    field: FileSortField

    @property
    def items(self) -> list[str]:
        out = []
        for value in self.field.value:
            sorter = ""
            if self.direction == OrderDirection.DESC:
                sorter += "-"
            sorter += value
            out.append(sorter)
        return out
