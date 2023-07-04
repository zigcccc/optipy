from sqlalchemy import Column, Integer, String

from optipy.db.models import Base
from optipy.db.constants import STRING_LENGTH_MEDIUM


class Category(Base):
    importance = Column(Integer, default=50, nullable=False)
    category_name = Column(
        String(STRING_LENGTH_MEDIUM),
        unique=True,
        nullable=False,
    )
