"""This module defines all GraphQL resolvers for the FastAPI application.

Resolvers are responsible for handling the logic of GraphQL queries, mutations, and subscriptions.
"""

from typing import Optional

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import subqueryload
from sqlalchemy.sql import Delete, Insert, Select

from src.graphql_app.helpers import build_paginated_window
from src.graphql_app.miscellanious import Info
from src.graphql_app.types import (
    JSON,
    Category,
    CategoryOrderingInput,
    GenericSuccess,
    PaginationWindow,
    Transaction,
    TransactionOrderingInput,
)
from src.sql_app import models


async def list_transactions(
    info: Info,
    limit: int = 10,
    offset: int = 1,
    filters: Optional[JSON] = None,
    subfilters: Optional[JSON] = None,
    ordering: Optional[TransactionOrderingInput] = None,
) -> PaginationWindow[Transaction]:
    """Get all clusters."""
    return await build_paginated_window(
        info=info,
        limit=limit,
        offset=offset,
        model=models.TransactionModel,
        scalar_type=Transaction,
        model_relations=[models.TransactionModel.category],
        filters=filters,
        subfilters=subfilters,
        ordering=ordering,
    )


async def list_categories(
    info: Info,
    limit: int = 10,
    offset: int = 1,
    filters: Optional[JSON] = None,
    subfilters: Optional[JSON] = None,
    ordering: Optional[CategoryOrderingInput] = None,
) -> PaginationWindow[Category]:
    """Get all clusters."""
    return await build_paginated_window(
        info=info,
        limit=limit,
        offset=offset,
        model=models.CategoryModel,
        scalar_type=Category,
        model_relations=[models.CategoryModel.transactions],
        filters=filters,
        subfilters=subfilters,
        ordering=ordering,
    )


async def create_transaction(
    info: Info,
    name: str,
    value: float,
    category_name: str,
    description: Optional[str] = None,
) -> Transaction:
    """Create a transaction."""
    query: Select | Insert
    async with info.context.db_session(read_only=False) as sess:
        query = select(models.CategoryModel).where(models.CategoryModel.name == category_name)
        category: models.CategoryModel | None = (await sess.execute(query)).scalar_one_or_none()
        if category is None:
            raise ValueError(f"Category {category_name} not found.")

        query = (
            insert(models.TransactionModel)
            .values(
                name=name,
                description=description,
                value=value,
                category_id=category.id,
            )
            .returning(models.TransactionModel)
            .options(subqueryload(models.TransactionModel.category))
        )
        transaction = (await sess.execute(query)).scalar_one()
        await sess.commit()
        await sess.refresh(transaction)
    return Transaction.from_db_model(transaction)


async def create_category(info: Info, name: str) -> Category:
    """Create a category."""
    query: Insert | Select
    async with info.context.db_session(read_only=False) as sess:
        query = select(models.CategoryModel).where(models.CategoryModel.name == name)
        category = (await sess.execute(query)).scalar_one_or_none()
        if category is not None:
            raise ValueError(f"Category {name} already exists")

        query = (
            insert(models.CategoryModel)
            .values(name=name)
            .returning(models.CategoryModel)
            .options(subqueryload(models.CategoryModel.transactions))
        )
        category = (await sess.execute(query)).scalar_one()
        await sess.commit()
        await sess.refresh(category)
    return Category.from_db_model(category)


async def delete_transaction(info: Info, transaction_id: int) -> GenericSuccess:
    """Delete a transaction."""
    async with info.context.db_session(read_only=False) as sess:
        query = select(models.TransactionModel).where(models.TransactionModel.id == transaction_id)
        transaction = (await sess.execute(query)).scalar_one_or_none()
        if transaction is None:
            raise ValueError(f"Transaction {transaction_id} not found.")
        query = delete(models.TransactionModel).where(models.TransactionModel.id == transaction_id)
        await sess.execute(query)
        await sess.commit()
    return GenericSuccess(success=True, message=f"Transaction {transaction_id} deleted.")


async def delete_category(info: Info, category_id: int) -> GenericSuccess:
    """Delete a category."""
    async with info.context.db_session(read_only=False) as sess:
        query: Select | Delete
        query = select(models.CategoryModel).where(models.CategoryModel.id == category_id)
        category = (await sess.execute(query)).scalar_one_or_none()
        if category is None:
            raise ValueError(f"Category with id {category_id} not found.")
        query = delete(models.CategoryModel).where(models.CategoryModel.id == category_id)
        await sess.execute(query)
        await sess.commit()
    return GenericSuccess(success=True, message=f"Category {category_id} deleted.")


async def update_transaction_category(
    info: Info, transaction_id: int, category_id: int
) -> Transaction:
    """Update the category of a transaction."""
    async with info.context.db_session(read_only=False) as sess:
        query = select(models.TransactionModel).where(models.TransactionModel.id == transaction_id)
        transaction = (await sess.execute(query)).scalar_one_or_none()
        if transaction is None:
            raise ValueError(f"Transaction {transaction_id} not found.")

        query = select(models.CategoryModel).where(models.CategoryModel.id == category_id)
        category = (await sess.execute(query)).scalar_one_or_none()
        if category is None:
            raise ValueError(f"Category {category_id} not found.")

        transaction.category_id = category.id
        await sess.commit()
        await sess.refresh(transaction)
    return Transaction.from_db_model(transaction)


async def update_transaction_description(
    info: Info, transaction_id: int, description: str
) -> Transaction:
    """Update the description of a transaction."""
    async with info.context.db_session(read_only=False) as sess:
        query = select(models.TransactionModel).where(models.TransactionModel.id == transaction_id)
        transaction = (await sess.execute(query)).scalar_one_or_none()
        if transaction is None:
            raise ValueError(f"Transaction {transaction_id} not found.")

        transaction.description = description
        await sess.commit()
        await sess.refresh(transaction)
    return Transaction.from_db_model(transaction)
