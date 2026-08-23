"""SQLAlchemy declarative base for OrchFlow persistence."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""
