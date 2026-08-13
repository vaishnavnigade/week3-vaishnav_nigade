# DeclarativeBase is SQLAlchemy's base class for defining ORM models declaratively.
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class inherited by all SQLAlchemy ORM models."""

    # No custom behavior needed; models inherit the shared metadata from this class.
    pass


