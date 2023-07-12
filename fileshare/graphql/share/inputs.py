import strawberry

from enum import Enum
from uuid import UUID

from fileshare.graphql.types import OrderDirection
from fileshare.graphql.inputs import DateTimeRange, IntRange

from sqlalchemy import desc, asc
from fileshare.database.models import Share

@strawberry.input
class ShareFilterInput:
    id:                list[UUID] | None = None
    file_id:           list[UUID] | None = None
    key:                list[str] | None = None
    created:        DateTimeRange | None = None
    updated:        DateTimeRange | None = None
    expiry:         DateTimeRange | None = None
    download_limit:      IntRange | None = None
    download_count:      IntRange | None = None

@strawberry.enum
class ShareSortField(Enum):
    CREATED        = ["created", "updated"]
    UPDATED        = ["updated", "created"]
    EXPIRY         = ["expiry", "updated", "created"]
    DOWNLOAD_COUNT = ["download_count", "updated", "created"]
    DOWNLOAD_LIMIT = ["download_limit", "updated", "created"]

@strawberry.input
class ShareSortInput:
    direction: OrderDirection
    field: ShareSortField

    @property
    def items(self):
        args = []
        order = desc if self.direction.value == "desc" else asc
        for col in self.field.value:
            args.append(order(getattr(Share, col)))
        return args
