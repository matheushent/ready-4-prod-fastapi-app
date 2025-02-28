"""Define miscellaneous functions/classes for the GraphQL app."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Self

from graphql import GraphQLError, ValidationRule
from graphql.language.ast import FieldNode
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext
from strawberry.types import Info as _Info
from strawberry.types.info import RootValueType

from src.sql_app.models import CategoryModel, TransactionModel
from src.sql_app.session_manager import create_async_session


class Context(BaseContext):
    """Context class to override the default context from Strawberry."""

    @asynccontextmanager
    async def db_session(self, read_only: bool = True) -> AsyncGenerator[AsyncSession, None]:
        """Store the database session in the context."""
        session = await create_async_session(read_only)
        async with session() as sess:
            try:
                await sess.begin()
                yield sess
            except Exception as err:
                logger.error(f"Error: {err}")
                await sess.rollback()
                raise err
            finally:
                await sess.close()


Info = _Info[Context, RootValueType]


class CommonMethods:
    """Define common methods for the GraphQL types."""

    @classmethod
    def from_db_model(
        cls, table: TransactionModel | CategoryModel, extra: dict[str, str] = {}
    ) -> Self:
        """Generate the Strawberry type from the SQLAlchemy model."""
        return cls(**table.as_dict(), **extra)

    @classmethod
    def __name__(cls) -> str:
        """Return the name of the class."""
        return cls.__name__()


class ValidateQueryParams(ValidationRule):
    """Validate the query parameters values."""

    def enter_field(self, node: FieldNode, *args: Any) -> None:
        """Check the offset value."""
        if node.arguments is not None:
            for argument in node.arguments:
                if argument.name.value == "offset":
                    if int(argument.value.value) < 1:
                        self.report_error(
                            GraphQLError(
                                "The offset value must be greater than or equal to 1.",
                                [argument],
                            )
                        )
                elif argument.name.value == "limit":
                    if int(argument.value.value) < 1:
                        self.report_error(
                            GraphQLError(
                                "The limit value must be greater than or equal to 1.",
                                [argument],
                            )
                        )


async def get_context() -> Context:
    """Fetch the Strawberry context."""
    return Context()
