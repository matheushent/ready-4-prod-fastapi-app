"""Core module for the GraphQL queries."""

import strawberry

from src.graphql_app.resolvers import list_categories, list_transactions
from src.graphql_app.types import Category, PaginationWindow, Transaction


@strawberry.type
class Query:
    """Query class."""

    transactions: PaginationWindow[Transaction] = strawberry.field(resolver=list_transactions)
    categories: PaginationWindow[Category] = strawberry.field(resolver=list_categories)
