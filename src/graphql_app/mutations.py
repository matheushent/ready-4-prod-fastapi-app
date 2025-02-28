"""Core module for the GraphQL mutations."""

from typing import Optional

import strawberry

from src.graphql_app import resolvers
from src.graphql_app.miscellanious import Info
from src.graphql_app.types import Category, GenericSuccess, Transaction


@strawberry.type
class Mutation:
    """Mutation class."""

    @strawberry.mutation
    async def create_transaction(
        self,
        info: Info,
        name: str,
        value: float,
        category_name: str,
        description: Optional[str] = None,
    ) -> Transaction:
        """Mutation definition for creating a transaction."""
        return await resolvers.create_transaction(
            info=info,
            name=name,
            value=value,
            category_name=category_name,
            description=description,
        )

    @strawberry.mutation
    async def delete_transaction(self, info: Info, transaction_id: int) -> GenericSuccess:
        """Mutation definition for deleting a transaction."""
        return await resolvers.delete_transaction(info=info, transaction_id=transaction_id)

    @strawberry.mutation
    async def create_category(self, info: Info, name: str) -> Category:
        """Mutation definition for creating a category."""
        return await resolvers.create_category(info=info, name=name)

    @strawberry.mutation
    async def delete_category(self, info: Info, category_id: int) -> GenericSuccess:
        """Mutation definition for deleting a category."""
        return await resolvers.delete_category(info=info, category_id=category_id)

    @strawberry.mutation
    async def update_transaction_category(
        self, info: Info, transaction_id: int, category_id: int
    ) -> Transaction:
        """Mutation definition for updating the category of a transaction."""
        return await resolvers.update_transaction_category(
            info=info, transaction_id=transaction_id, category_id=category_id
        )

    @strawberry.mutation
    async def update_transaction_description(
        self, info: Info, transaction_id: int, description: str
    ) -> Transaction:
        """Mutation definition for updating the description of a transaction."""
        return await resolvers.update_transaction_description(
            info=info, transaction_id=transaction_id, description=description
        )
