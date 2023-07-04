from datetime import datetime
from pydantic import BaseModel, UUID4

from todoist.utils.strings import to_camel
from todoist.users.schemas import User


class TodoBase(BaseModel):
    title: str


class TodoCreate(TodoBase):
    pass


class TodoOut(TodoBase):
    id: UUID4
    created_at: datetime
    owner: User
    is_completed: bool

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
