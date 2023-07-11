from sqlalchemy.orm import Query
from sqlalchemy.sql import func
import strawberry
from uuid import UUID
from strawberry.types import Info
from base64 import b64encode, b64decode
from sqlakeyset import get_page, unserialize_bookmark

from fileshare.database.engine import get_db
from fileshare.database.models import File
from fileshare.graphql.file.inputs import FileFilterInput, FileSortField, FileSortInput
from fileshare.graphql.file.types import FileType, FileNotFoundError
from fileshare.graphql.types import CountableConnection, OrderDirection, PageInfo, Edge
from fileshare.settings import settings


def to_b64(bookmark: str) -> str:
    return b64encode(bookmark.encode("utf-8")).decode("ascii")
def from_b64(bookmark: str) -> str:
    return b64decode(bookmark.encode("ascii")).decode("utf-8")

def apply_file_filters(q: Query, filters: FileFilterInput | None) -> Query:
    """Applies graphql filter input to the SQLAlchemy queryset"""
    if not filters:
        return q

    if filters.share_count is not None:
        q = q.filter(File.share_count.between(filters.share_count.gte, filters.share_count.lte))
    if filters.id is not None:
        q = q.filter(File.id.in_((*filters.id,)))
    if filters.name is not None:
        q = q.filter(File.name.in_((*filters.name,)))
    if filters.download_count is not None:
        q = q.filter(File.download_count.between(filters.download_count.gte, filters.download_count.lte))
    if filters.created is not None:
        q = q.filter(File.created.between(filters.created.gte, filters.created.lte))
    if filters.updated is not None:
        q = q.filter(File.updated.between(filters.updated.gte, filters.updated.lte))
    if filters.active is not None:
        q = q.filter(File.active == filters.active)
    if filters.search is not None:
        q = q.filter(File.tsvector.bool_op("@@")(func.plainto_tsquery(filters.search)))
    return q

def apply_file_sort(q: Query, sort: FileSortInput | None) -> Query:
    if not sort:
        sort = FileSortInput(direction=OrderDirection.ASC, field=FileSortField.CREATED)

    return q.order_by(*sort.items)


@strawberry.type
class FileQuery:
    """A query class for Files"""

    @strawberry.field
    def file(
        self,
        info: Info,
        id: UUID
    ) -> FileType | FileNotFoundError:

        session = next(get_db())
        file = session.query(File).filter(File.id == id).first()
        if file:
            return FileType(**file.as_dict())
        else:
            return FileNotFoundError(code="file_not_found", message=f"Could not find file with ID '{str(id)}'.")


    @strawberry.field
    def files(
        self,
        info: Info,
        filter: FileFilterInput | None = None,
        sort: FileSortInput | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> CountableConnection[FileType]:

        session = next(get_db())

        queryset = session.query(File)
        if filter is not None:
            queryset = apply_file_filters(queryset, filter)
        queryset = apply_file_sort(queryset, sort)

        if after:
            page = get_page(
                queryset,
                per_page=settings.graphql.default_page_size,
                after=unserialize_bookmark(from_b64(after)).place
            )
        elif before:
            page = get_page(
                queryset,
                per_page=settings.graphql.default_page_size,
                before=unserialize_bookmark(from_b64(before)).place
            )
        else:
            page = get_page(
                queryset,
                per_page=settings.graphql.default_page_size
            )
        bookmark_items = list(page.paging.bookmark_items())

        return CountableConnection(
            count=len(page),
            page_info=PageInfo(
                has_next_page=page.paging.has_next,
                has_previous_page=page.paging.has_previous,
                start_cursor=to_b64(bookmark_items[0][0]),
                end_cursor=to_b64(bookmark_items[-1][0])
            ),
            edges=[
                Edge(
                    node=FileType(**file.as_dict()),
                    cursor=to_b64(bookmark)
                ) for bookmark, file in bookmark_items
            ]
        )
