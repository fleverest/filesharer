import strawberry

from uuid import UUID
from strawberry.types import Info

from sqlalchemy.orm import Query
from sqlalchemy.sql import func

from fileshare.database.engine import get_db
from fileshare.database.models import Share
from fileshare.graphql.share.inputs import ShareFilterInput, ShareSortField, ShareSortInput
from fileshare.graphql.share.types import ShareType, ShareNotFoundError
from fileshare.graphql.helpers import get_countable_connection
from fileshare.graphql.types import CountableConnection, OrderDirection, PaginationError

def apply_share_filters(q: Query, filters: ShareFilterInput | None) -> Query:
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

def apply_share_sort(q: Query, sort: ShareSortInput | None) -> Query:
    if not sort:
        sort = ShareSortInput(direction=OrderDirection.DESC, field=ShareSortField.UPDATED)

    return q.order_by(*sort.items)

@strawberry.type
class ShareQuery:
    """A query class for Shares"""

    @strawberry.field
    def share(
        self,
        info: Info,
        id: UUID | None,
        key: str | None
    ) -> ShareType | ShareNotFoundError:
        if id is None and key is None:
            return ShareNotFoundError(code="share_not_found", message="Shares can only be looked up via ID or key.")
        session = next(get_db())
        q = session.query(Share)
        if id is not None:
            q = q.filter(Share.id == id)
        if key is not None:
            q = q.filter(Share.key == key)
        share = q.first()
        if share:
            return ShareType(**share.as_dict())
        else:
            return ShareNotFoundError(code="share_not_found", message=f"Could not find share with given ID and/or key.")
