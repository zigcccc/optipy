from pydantic import BaseModel, UUID4

from todoist.utils.schema import ORMConfig


class UserBase(BaseModel):
    pass


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: UUID4
    is_active: bool

    class Config(ORMConfig):
        pass
