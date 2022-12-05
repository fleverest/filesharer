from base64 import b64decode, b64encode
from collections.abc import Sequence
from typing import Optional, TypeVar, Union, Generic

from sqlalchemy.orm import Query

from fileshare.settings import settings

GenericType = TypeVar("GenericType")


def reverse_ordering(ordering_tuple: list[str]):
    """
    Given an order_by tuple such as `('-created', 'uuid')` reverse the
    ordering and return a new tuple, eg. `('created', '-uuid')`.
    """

    def invert(x):
        return x[1:] if (x.startswith("-")) else "-" + x

    return tuple([invert(item) for item in ordering_tuple])


class InvalidCursor(Exception):
    """An exception raised when trying to decode an invalid cursor."""

    pass


class CursorPage(Sequence):
    """A class representing a page of objects."""

    def __init__(
        self,
        items: Query,
        paginator: "CursorPaginator",
        has_next: bool = False,
        has_previous: bool = False,
    ):
        self.items = items
        self.paginator = paginator
        self.has_next = has_next
        self.has_previous = has_previous

    def __len__(self):
        return self.items.count()

    def __getitem__(self, key: Union[int, slice]):
        return self.items.__getitem__(key)

    def __repr__(self):
        item_reps = ", ".join([repr(i) for i in self.items.limit(10).all()])
        if self.items.count() > 10:
            item_reps += "..."
        return f"<Page: [{item_reps}]>"


class CursorPaginator:
    """An object which defines pagination for a queryset."""

    delimiter = "|"
    invalid_cursor_message = "Invalid Cursor"

    def __init__(self, queryset: Query, ordering: list[str]):
        if not ordering:
            raise ValueError("Ordering must be applied for cursor pagination.")
        self.queryset = queryset.order_by(*ordering)
        self.ordering = ordering

    def page(
        self,
        first: Optional[int] = None,
        last: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> CursorPage:
        qs = self.queryset
        page_size = first or last
        if page_size is None:
            page_size = settings.graphql.default_page_size
        if page_size > settings.graphql.pagination_limit:
            raise ValueError("Exceeded maximum pagination limit.")

        if after is not None:
            qs = self.apply_cursor(after, qs)
        if before is not None:
            qs = self.apply_cursor(before, qs, reverse=True)
        if first is not None:
            qs = qs[: first + 1]
        if last is not None:
            if first is not None:
                raise ValueError("Cannot process first and last.")
            qs = qs.order_by(*reverse_ordering(self.ordering))[: last + 1]

        qs = qs.all()
        items = qs[:page_size]
        if last is not None:
            items.reverse()
        has_additional = len(qs) > len(items)
        additional_kwargs = {}
        if first is not None:
            additional_kwargs["has_next"] = has_additional
            additional_kwargs["has_previous"] = bool(after)
        elif last is not None:
            additional_kwargs["has_previous"] = has_additional
            additional_kwargs["has_next"] = bool(before)

        return CursorPage(items, self, **additional_kwargs)

    def apply_cursor(
        self,
        cursor: str,
        queryset: Query,
        reverse: bool = False,
    ) -> Query:
        position = self.decode_cursor(cursor)

        filtering = Q()
        q_equality = {}

        position_values = [Value(pos, output_field=TextField()) for pos in position]

        for ordering, value in zip(self.ordering, position_values):
            is_reversed = ordering.startswith("-")
            o = ordering.lstrip("-")
            if reverse != is_reversed:
                comparison_key = "{}__lt".format(o)
            else:
                comparison_key = "{}__gt".format(o)

            q = {comparison_key: value}
            q.update(q_equality)
            filtering |= Q(**q)

            equality_key = "{}__exact".format(o)
            q_equality.update({equality_key: value})

        return queryset.filter(filtering)

    def decode_cursor(self, cursor: str) -> list[str]:
        try:
            orderings = b64decode(cursor.encode("ascii")).decode("utf8")
            return orderings.split(self.delimiter)
        except (TypeError, ValueError):
            raise InvalidCursor(self.invalid_cursor_message)

    def encode_cursor(self, position: list[str]) -> str:
        encoded = b64encode(self.delimiter.join(position).encode("utf8")).decode(
            "ascii"
        )
        return encoded

    def position_from_instance(self, instance: CursorPage) -> list[str]:
        position = []
        for order in self.ordering:
            parts = order.lstrip("-").split("__")
            attr = instance
            while parts:
                attr = getattr(attr, parts[0])
                parts.pop(0)
            position.append(str(attr))
        return position

    def cursor(self, instance: CursorPage) -> str:
        return self.encode_cursor(self.position_from_instance(instance))
