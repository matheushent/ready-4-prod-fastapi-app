"""Core module for defining the ORM models."""

from datetime import datetime
from decimal import Decimal

from pendulum import DateTime as PendulumDateTime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, inspect
from sqlalchemy.orm import Mapped, Mapper, mapped_column, relationship
from sqlalchemy.orm.decl_api import declarative_mixin

from src.sql_app import Base


@declarative_mixin
class StaticReferenceMixin:
    """Common resources between all tables.

    The attributes define rows and the methods API-level resources.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=PendulumDateTime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=PendulumDateTime.utcnow(),
        onupdate=PendulumDateTime.utcnow(),
    )

    def as_dict(self: "StaticReferenceMixin", bound_relationships: bool = True):
        """Transform the SQLAlchemy model to a dictionary. It also returns the relations."""
        mapper: Mapper = inspect(self).mapper  # type: ignore
        cols = {col.key: getattr(self, col.key) for col in mapper.column_attrs}
        if bound_relationships:
            return {
                **cols,
                **{
                    rel: getattr(self, rel) if getattr(self, rel) is not None else []
                    for rel in mapper.relationships.keys()
                },
            }
        else:
            return cols


class TransactionModel(Base, StaticReferenceMixin):
    """Cluster table schema."""

    __tablename__ = "transactions"

    name: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    value: Mapped[Decimal] = mapped_column(Float(asdecimal=True), nullable=False)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )

    category: Mapped["CategoryModel"] = relationship(
        "CategoryModel",
        back_populates="transactions",
        lazy="subquery",
        uselist=False,
    )


class CategoryModel(Base, StaticReferenceMixin):
    """Category table schema."""

    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String, unique=True, index=True)

    transactions: Mapped[list["TransactionModel"]] = relationship(
        "TransactionModel",
        back_populates="category",
        lazy="subquery",
        uselist=True,
    )
