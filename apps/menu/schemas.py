import uuid

from pydantic import BaseModel, validator


class BaseSchema(BaseModel):
    title: str
    description: str

    class Config:
        orm_mode = True
        # schema_extra = {
        #     'example': {
        #         'title': 'My menu',
        #         'description': 'My menu description',
        #     },
        # }


class MenuSchema(BaseSchema):
    id: uuid.UUID
    submenus_count: int = 0
    dishes_count: int = 0

    @validator('id')
    def validate_uuid(cls, value):
        if value:
            return str(value)
        return value


class SubmenuSchema(BaseSchema):
    id: uuid.UUID
    dishes_count: int = 0

    @validator('id')
    def validate_uuid(cls, value):
        if value:
            return str(value)
        return value


class DishSchema(BaseSchema):
    id: uuid.UUID
    price: str

    @validator('id')
    def validate_uuid(cls, value):
        if value:
            return str(value)
        return value


class DishBaseSchema(BaseSchema):
    price: str
