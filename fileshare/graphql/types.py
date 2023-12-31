from enum import Enum
from typing import Generic, List, Optional, TypeVar

import strawberry

GenericType = TypeVar("GenericType")


@strawberry.enum
class OrderDirection(Enum):
    """An enum for sort order directions"""

    ASC = "asc"
    DESC = "desc"


@strawberry.type
class Connection(Generic[GenericType]):
    """Represents a paginated relationship between two entities"""

    page_info: "PageInfo"
    edges: List["Edge[GenericType]"]


@strawberry.type
class CountableConnection(Connection[GenericType]):
    """Represents a paginated relationship between two entities"""

    count: int


@strawberry.type
class PageInfo:
    """Pagination context to navigate objects with cursor-based pagination

    Instead of classic offset pagination via `page` and `limit` parameters,
    here we have a cursor of the last object and we fetch items starting from that one

    Read more at:
        - https://graphql.org/learn/pagination/#pagination-and-edges
        - https://relay.dev/graphql/connections.htm
    """

    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str]
    end_cursor: Optional[str]


@strawberry.type
class Edge(Generic[GenericType]):
    """An edge may contain additional information of the relationship. This is the trivial case"""

    node: GenericType
    cursor: str


@strawberry.type
class ErrorType:
    """A type for representing error messages"""

    code: str
    message: str

@strawberry.type
class PaginationError(ErrorType):
    """A type for representing errors raised during pagination"""
    pass
