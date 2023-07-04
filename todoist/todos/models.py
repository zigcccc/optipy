from datetime import datetime
from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from todoist.db.models import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid4,
    )
    title = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime,
        default=datetime.now,
        server_default=str(datetime.now()),
        onupdate=datetime.now,
        nullable=False,
    )
    is_completed = Column(Boolean, default=False, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    owner = relationship("User", back_populates="todos")
