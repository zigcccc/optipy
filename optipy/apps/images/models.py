from sqlalchemy import Column, String

from optipy.db.models import Base


class Image(Base):
    url = Column(String, nullable=False)
    filename = Column(String, nullable=False)
