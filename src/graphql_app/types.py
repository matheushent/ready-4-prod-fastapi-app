"""Definition of the GraphQL types."""

import enum
import json
from datetime import datetime
from typing import Generic, List, NewType, Optional, TypeVar

import strawberry

from src.graphql_app.miscellanious import CommonMethods

GenericType = TypeVar("GenericType")

# [Reference](https://strawberry.rocks/docs/types/scalars#example-jsonscalar)
JSON = strawberry.scalar(
    NewType("JSON", dict),
    serialize=lambda v: v,
    parse_value=lambda v: json.loads(json.dumps(v)),
    description="The `JSON` scalar type represents JSON values as specified by ECMA-404",
)


@strawberry.type
class Edge(Generic[GenericType]):
    """An edge may contain additional information of the relationship."""

    node: GenericType
    cursor: str


@strawberry.type
class PageInfo:
    """Pagination context to navigate objects with cursor-based pagination.

    Instead of classic offset pagination via `page` and `limit` parameters,
    here we have a cursor of the last object and we fetch items starting from that one

    Read more at:
        - https://graphql.org/learn/pagination/#pagination-and-edges
        - https://relay.dev/graphql/connections.htm
    """

    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str] = None
    end_cursor: Optional[str] = None


@strawberry.type
class Connection(Generic[GenericType]):
    """Represents a paginated relationship between two entities.

    This pattern is used when the relationship itself has attributes.
    In a Facebook-based domain example, a friendship between two people
    would be a connection that might have a `friendshipStartTime`
    """

    page_info: PageInfo
    edges: List[Edge[GenericType]]
    total: int


Item = TypeVar("Item")


@strawberry.type
class PaginationWindow(Generic[Item]):
    """A window of items in a paginated list."""

    items: list[Item] = strawberry.field(description="The list of items in this pagination window.")
    total_items_count: int = strawberry.field(
        description="Total number of items in the filtered dataset."
    )


@strawberry.enum
class OrderingDirection(enum.Enum):
    """The ordering direction of a supplied field."""

    ASC = "asc"
    DESC = "desc"


@strawberry.type
class Transaction(CommonMethods):
    """Transaction type."""

    id: int
    created_at: datetime
    updated_at: datetime
    name: str
    description: Optional[str] = None
    value: float
    category_id: int
    category: "Category"


@strawberry.enum
class TransactionOrderingFilter(enum.Enum):
    """Available ordering for the transactions."""

    id = "id"
    created_at = "created_at"
    updated_at = "updated_at"
    name = "name"
    description = "description"
    value = "value"
    category_id = "category_id"


@strawberry.input
class TransactionOrderingInput:
    """Define the ordering input."""

    field: TransactionOrderingFilter
    direction: OrderingDirection = OrderingDirection.ASC


@strawberry.type
class Category(CommonMethods):
    """Category type."""

    id: int
    created_at: datetime
    updated_at: datetime
    name: str
    transactions: List[Transaction]


@strawberry.enum
class CategoryOrderingFilter(enum.Enum):
    """Available ordering for the categories."""

    id = "id"
    created_at = "created_at"
    updated_at = "updated_at"
    name = "name"


@strawberry.input
class CategoryOrderingInput:
    """Define the ordering input."""

    field: CategoryOrderingFilter
    direction: OrderingDirection = OrderingDirection.ASC


@strawberry.type
class GenericSuccess:
    """Generic success message."""

    success: bool = True
    message: str = "Success"
