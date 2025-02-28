"""Core module for defining general helper functions used by the GraphQL resolvers."""

import operator
import re
from dataclasses import dataclass
from typing import Any, Sequence, Type

import strawberry
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, subqueryload
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.functions import func

from src.graphql_app import types
from src.graphql_app.miscellanious import Info
from src.sql_app import models


@dataclass
class FetchDataResponse:
    """Dataclass to store records fetched from the database and how many of them indeed exist."""

    total: int
    records: list[models.TransactionModel | models.CategoryModel]


def _build_items(
    records: Sequence[models.TransactionModel | models.CategoryModel],
    scalar_type: Type[types.Transaction] | Type[types.Category],
) -> list[types.Item]:
    """Build the GraphQL item type."""
    return [scalar_type.from_db_model(record) for record in records]


def convert_camel_case(name: str):
    """Convert camel case string to snake case."""
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    name = pattern.sub("_", name).lower()
    return name


def aggregate_filters(
    filters: types.JSON | None,
    table: Type[models.TransactionModel] | Type[models.CategoryModel],
) -> list[BinaryExpression]:
    """Generate a list of where statements based on input filters.

    The following is a list of supported operations:
    * gt - greater than (>)
    * lt - less than (<)
    * ge - greater or equal than (>=)
    * le - less or equal than (<=)
    * eq - equal to (==)
    * ne - not equal to (!=)
    * in - in list
    * contains - contain "a" in "b"

    Examples
    --------
    * Fetch transactions whose name contain the word "coffee"

    aggregate_filters(
        {
            "name": {"contains": "coffee"},
        },
        models.Transactions,
    )

    * Fetch transactions whose value is greater than 100

    aggregate_filters(
        {
            "value": {"gt": 100},
        },
        models.Transactions,
    )
    """
    where_statements: list[BinaryExpression] = []
    if filters is not None:
        for table_column, value in filters.items():
            table_column = convert_camel_case(table_column)
            ops = {
                "gt": operator.gt,
                "lt": operator.lt,
                "ge": operator.ge,
                "le": operator.le,
                "eq": operator.eq,
                "ne": operator.ne,
            }
            for comparison_operator, comparison_value in value.items():
                if comparison_operator == "in":
                    sqlalchemy_binary_expression = getattr(table, table_column).in_(
                        comparison_value
                    )
                elif comparison_operator == "contains" and isinstance(comparison_value, str):
                    # [Reference]
                    # (https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnElement.ilike)
                    comparison_value = f"%{comparison_value}%"
                    sqlalchemy_binary_expression = getattr(table, table_column).ilike(
                        comparison_value
                    )
                elif comparison_operator == "contains" and isinstance(comparison_value, list):
                    sqlalchemy_binary_expression = getattr(table, table_column).op("@>")(
                        comparison_value
                    )
                else:
                    sqlalchemy_binary_expression = ops[comparison_operator](
                        getattr(table, table_column), comparison_value
                    )
                where_statements.append(sqlalchemy_binary_expression)

    return where_statements


async def _count_rows(
    filters: types.JSON | None,
    table: Type[models.TransactionModel] | Type[models.CategoryModel],
    sess: AsyncSession,
) -> int:
    """Count the number of elements in the database based on supplied filters."""
    where_statements = aggregate_filters(filters, table)
    query = select(func.count()).select_from(table).where(*where_statements)

    result = await sess.execute(query)

    return result.scalars().one()


async def _fetch_data(
    info: Info,
    limit: int,
    model: Type[models.TransactionModel] | Type[models.CategoryModel],
    model_relations: list[InstrumentedAttribute[Any]],
    filters: types.JSON | None = None,
    subfilters: types.JSON | None = None,
    ordering: types.TransactionOrderingInput | None = None,
    offset: int = strawberry.UNSET,
) -> FetchDataResponse:  # pragma: no cover
    """Build the SQLAlchemy query based on common pattern and fetch the data."""
    offset = offset if offset is not strawberry.UNSET else 1
    and_filters = aggregate_filters(filters=filters, table=model)
    or_filters = aggregate_filters(subfilters, table=model)

    async with info.context.db_session(read_only=True) as sess:
        total = await _count_rows(filters=filters, table=model, sess=sess)
        query = (
            select(model)
            .where(*and_filters)
            .filter(or_(*or_filters))
            .offset((offset - 1) * limit)
            .limit(limit)
        )
        if ordering is not None:
            query = query.order_by(
                getattr(getattr(model, ordering.field.value), ordering.direction.value)()
            )
        for model_relation in model_relations:
            query = query.options(subqueryload(getattr(model, model_relation.key)))
        records = (await sess.execute(query)).scalars().all()

    return FetchDataResponse(total, records)


async def build_paginated_window(
    info: Info,
    limit: int,
    offset: int,
    model: Type[models.TransactionModel] | Type[models.CategoryModel],
    scalar_type: Type[types.Transaction] | Type[types.Category],
    model_relations: list[InstrumentedAttribute[Any]] = [],
    filters: types.JSON | None = None,
    subfilters: types.JSON | None = None,
    ordering: types.TransactionOrderingInput | None = None,
) -> types.PaginationWindow:
    """Build the GraphQL connection type."""
    data = await _fetch_data(
        info=info,
        limit=limit,
        model=model,
        model_relations=model_relations,
        filters=filters,
        subfilters=subfilters,
        ordering=ordering,
        offset=offset,
    )
    items = _build_items(data.records, scalar_type)
    return types.PaginationWindow(items=items, total_items_count=data.total)
