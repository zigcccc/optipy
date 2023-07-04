from datetime import datetime
from typing import Optional

from pydantic import BaseModel, UUID4, Field

from optipy.utils.strings import to_camel


class CategoryBase(BaseModel):
    category_name: str
    importance: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        alias_generator = to_camel


class CategoryIn(CategoryBase):
    importance: Optional[int] = Field(default=50, le=100, ge=0)


class CategoryUpdate(CategoryBase):
    category_name: Optional[str]
    importance: Optional[int] = Field(le=100, ge=0)


class CategoryOut(CategoryBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
