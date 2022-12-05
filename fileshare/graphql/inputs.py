from datetime import date, datetime
from typing import Generic, TypeVar

import strawberry

GenericType = TypeVar("GenericType")


# abstract class
@strawberry.input
class Range(Generic[GenericType]):
    """An abstract range class"""

    # Lower bound
    gte: GenericType
    # Upper bound
    lte: GenericType

    def __init__(self, gte: GenericType, lte: GenericType, *args, **kwargs):
        self.gte = gte
        self.lte = lte
        super().__init__(*args, **kwargs)


@strawberry.input
class IntRange(Range[int]):
    """A strawberry input for integer ranges"""

    # Lower bound
    gte: int
    # Upper bound
    lte: int


@strawberry.input
class DateRange(Range[date]):
    """A strawberry input for date ranges"""

    # Lower bound
    gte: date
    # Upper bound
    lte: date


@strawberry.input
class DateTimeRange(Range[datetime]):
    """A strawberry input for date ranges"""

    # Lower bound
    gte: datetime
    # Upper bound
    lte: datetime
