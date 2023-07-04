from sqlalchemy import Column, String, Boolean

from optipy.db.models import Base


class User(Base):
    sub = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
