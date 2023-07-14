from typing import Tuple
from sqlalchemy import Select, select
from sqlalchemy.sql import func
import strawberry
from uuid import UUID
from strawberry.types import Info

from fileshare.database.engine import get_session
from fileshare.database.models import File
from fileshare.graphql.file.inputs import FileFilterInput, FileSortField, FileSortInput
from fileshare.graphql.file.types import FileType, FileNotFoundError
from fileshare.graphql.helpers import get_countable_connection
from fileshare.graphql.types import CountableConnection, OrderDirection, PaginationError


def apply_file_filters(q: Select[Tuple[File]], filters: FileFilterInput | None) -> Select[Tuple[File]]:
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

def apply_file_sort(q: Select[Tuple[File]], sort: FileSortInput | None) -> Select[Tuple[File]]:
    if not sort:
        sort = FileSortInput(direction=OrderDirection.DESC, field=FileSortField.UPDATED)

    return q.order_by(*sort.items)


@strawberry.type
class FileQuery:
    """A query class for Files"""

    @strawberry.field
    async def file(
        self,
        info: Info,
        id: UUID
    ) -> FileType | FileNotFoundError:

        async with get_session() as session:
            file_query = select(File).filter(File.id == id)
            result = await session.execute(file_query)
            file = result.scalar()
            if file:
                return FileType.from_instance(file)
            else:
                return FileNotFoundError(code="file_not_found", message=f"Could not find file with ID '{str(id)}'.")


    @strawberry.field
    async def files(
        self,
        info: Info,
        filter: FileFilterInput | None = None,
        sort: FileSortInput | None = None,
        after: str | None = None,
        first: int | None = None,
        before: str | None = None,
        last: int | None = None
    ) -> CountableConnection[FileType] | PaginationError:

        async with get_session() as session:

            files_query = select(File)
            if filter is not None:
                files_query = apply_file_filters(files_query, filter)
            files_query = apply_file_sort(files_query, sort)

            return await get_countable_connection(session, files_query, FileType.from_instance, before, after, first, last)
