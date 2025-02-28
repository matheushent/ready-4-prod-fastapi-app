"""Declare the Base class to be publicly accessible."""

from sqlalchemy.orm import declarative_base


class BaseDeclarative:
    """Base class for all models."""

    __allow_unmapped__ = True


Base = declarative_base(cls=BaseDeclarative)
