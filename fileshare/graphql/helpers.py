import binascii
from base64 import b64encode, b64decode
from sqlakeyset import BadBookmark, unserialize_bookmark
from sqlakeyset.asyncio import select_page

from typing import Any, Callable, Tuple
from sqlakeyset.sqla import AsyncSession

from sqlalchemy import Select

from fileshare.settings import settings
from fileshare.graphql.types import CountableConnection, Edge, PageInfo, PaginationError


class CursorB64DecodeError(Exception):
    """An exception to be raised when a cursor passed is invalid b64"""
    pass

def to_b64(cursor: str) -> str:
    """Encodes a cursor string as base64"""
    return b64encode(cursor.encode("utf-8")).decode("ascii")

def from_b64(cursor: str) -> str:
    """Decodes a base64 cursor string"""
    try:
        return b64decode(cursor.encode("ascii")).decode("utf-8")
    except binascii.Error:
        raise CursorB64DecodeError(f"Cursor '{cursor}' is not a valid b64-encoded string.")

async def get_countable_connection(
    session: AsyncSession,
    query: Select[Tuple[Any]],
    resolve_node: Callable,
    before: str | None = None,
    after: str | None = None,
    first: int | None = None,
    last: int | None = None,
    ) -> CountableConnection[Any] | PaginationError:

    if after is not None:
        if before is not None:
            return PaginationError(code="paging_direction_conflict", message="Results can only be fetched before OR after a cursor, not both.")
        if last is not None:
            return PaginationError(code="page_direction_conflict", message="Results can only be fetched first-after or last-before.")
        if first is None:
            first = settings.graphql.default_page_size
        elif first > settings.graphql.pagination_limit or first <= 0:
            return PaginationError(code="page_size_invalid", message=f"Results are limited to between 0 and {settings.graphql.pagination_limit} entries.")
        try:
            page = await select_page(
                session,
                query,
                per_page=first,
                after=unserialize_bookmark(from_b64(after)).place
            )
        except (BadBookmark, CursorB64DecodeError) :
            return PaginationError(code="cursor_invalid", message=f"Cursor could not be deserialized.")

    elif before is not None:
        if after is not None:
            return PaginationError(code="paging_direction_conflict", message="Results can only be fetched before OR after a cursor, not both.")
        if first is not None:
            return PaginationError(code="page_direction_conflict", message="Results can only be fetched first-after or last-before.")
        if last is None:
            last = settings.graphql.default_page_size
        elif last > settings.graphql.pagination_limit or last <= 0:
            return PaginationError(code="page_size_invalid", message=f"Results are limited to between 0 and {settings.graphql.pagination_limit} entries.")
        try:
            page = await select_page(
                session,
                query,
                per_page=last,
                before=unserialize_bookmark(from_b64(before)).place
            )
        except BadBookmark:
            return PaginationError(code="cursor_invalid", message="Cursor could not be deserialized.")

    else:
        # Default to first-after if neither after nor before cursors are specified
        if last is not None:
            return PaginationError(code="page_direction_conflict", message="Results can only be fetched first-after the start of the result set.")
        if first is None:
            first = settings.graphql.default_page_size
        elif first > settings.graphql.pagination_limit or first <= 0:
            return PaginationError(code="page_size_invalid", message=f"Results are limited to between 0 and {settings.graphql.pagination_limit} entries.")
        try:
            page = await select_page(
                session,
                query,
                per_page=first
            )
        except BadBookmark:
            return PaginationError(code="cursor_invalid", message=f"Cursor could not be deserialized.")


    bookmark_items = list(page.paging.bookmark_items())

    return CountableConnection(
        count=len(page),
        page_info=PageInfo(
            has_next_page=page.paging.has_next,
            has_previous_page=page.paging.has_previous,
            start_cursor=to_b64(bookmark_items[0][0]) if bookmark_items else None,
            end_cursor=to_b64(bookmark_items[-1][0]) if bookmark_items else None
        ),
        edges=[
            Edge(
                node=resolve_node(node),
                cursor=to_b64(bookmark)
            ) for bookmark, (node,) in bookmark_items
        ]
    )
