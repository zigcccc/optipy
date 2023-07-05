from datetime import datetime

from pydantic import BaseModel, Field, AnyUrl, UUID4

from optipy.utils.strings import to_camel


class ImageBase(BaseModel):
    url: AnyUrl
    filename: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        alias_generator = to_camel


class ImageIn(BaseModel):
    pass


class ImageOut(ImageBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
