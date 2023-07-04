from datetime import datetime
from uuid import uuid4

from inflect import engine as inflect_engine

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base


p = inflect_engine()


class BaseClass(object):
    @declared_attr
    def __tablename__(cls):
        return p.plural(cls.__name__.lower())

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid4,
    )
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime,
        default=datetime.now,
        server_default=str(datetime.now()),
        onupdate=datetime.now,
        nullable=False,
    )


Base = declarative_base(cls=BaseClass)
