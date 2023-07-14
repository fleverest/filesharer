from typing import Tuple
from sqlalchemy import Select, select
import strawberry

from uuid import UUID
from strawberry.types import Info

from fileshare.database.engine import get_session
from fileshare.database.models import Share
from fileshare.graphql.share.inputs import ShareFilterInput, ShareSortField, ShareSortInput
from fileshare.graphql.share.types import ShareType, ShareNotFoundError
from fileshare.graphql.helpers import get_countable_connection
from fileshare.graphql.types import CountableConnection, OrderDirection, PaginationError


def apply_share_filters(q: Select[Tuple[Share]], filters: ShareFilterInput | None) -> Select[Tuple[Share]]:
    """Applies graphql filter input to the sqlalchemy queryset"""
    if not filters:
        return q

    if filters.id is not None:
        q = q.filter(Share.id.in_((*filters.id,)))
    if filters.file_id is not None:
        q = q.filter(Share.file_id.in_((*filters.file_id,)))
    if filters.key is not None:
        q = q.filter(Share.key.in_((*filters.key,)))
    if filters.created is not None:
        q = q.filter(Share.created.between(filters.created.gte, filters.created.lte))
    if filters.updated is not None:
        q = q.filter(Share.updated.between(filters.updated.gte, filters.updated.lte))
    if filters.expiry is not None:
        q = q.filter(Share.expiry.between(filters.expiry.gte, filters.expiry.lte))
    if filters.download_limit is not None:
        q = q.filter(Share.download_limit.between(filters.download_limit.gte, filters.download_limit.lte))
    if filters.download_count is not None:
        q = q.filter(Share.download_count.between(filters.download_count.gte, filters.download_count.lte))

    return q

def apply_share_sort(q: Select[Tuple[Share]], sort: ShareSortInput | None) -> Select[Tuple[Share]]:
    if not sort:
        sort = ShareSortInput(direction=OrderDirection.DESC, field=ShareSortField.UPDATED)

    return q.order_by(*sort.items)

@strawberry.type
class ShareQuery:
    """A query class for Shares"""

    @strawberry.field
    async def share(
        self,
        info: Info,
        id: UUID | None,
        key: str | None
    ) -> ShareType | ShareNotFoundError:
        if id is None and key is None:
            return ShareNotFoundError(code="share_not_found", message="Shares can only be looked up via ID or key.")
        async with get_session() as session:
            q = select(Share)
            if id is not None:
                q = q.filter(Share.id == id)
            if key is not None:
                q = q.filter(Share.key == key)
            result = await session.execute(q)
            share = result.scalar()
            if share:
                return ShareType.from_instance(share)
            else:
                return ShareNotFoundError(code="share_not_found", message=f"Could not find share with given ID and/or key.")

    @strawberry.field
    async def shares(
        self,
        info: Info,
        filter: ShareFilterInput | None = None,
        sort: ShareSortInput | None = None,
        after: str | None = None,
        first: int | None = None,
        before: str | None = None,
        last: int | None = None
    ) -> CountableConnection[ShareType] | PaginationError:

        async with get_session() as session:

            share_query = select(Share)
            if filter is not None:
                share_query = apply_share_filters(share_query, filter)
            share_query = apply_share_sort(share_query, sort)

            return await get_countable_connection(session, share_query, ShareType.from_instance, before, after, first, last)
