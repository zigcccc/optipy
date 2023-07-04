from uuid import uuid4

from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from todoist.db.models import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid4,
    )
    sub = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)

    todos = relationship("Todo", back_populates="owner")
