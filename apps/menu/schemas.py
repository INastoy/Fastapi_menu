import uuid

from pydantic import BaseModel


class BaseSchema(BaseModel):
    title: str
    description: str

    class Config:
        orm_mode = True


class MenuSchema(BaseSchema):
    id: uuid.UUID
    submenus_count: int = 0
    dishes_count: int = 0


class SubmenuSchema(BaseSchema):
    id: uuid.UUID
    dishes_count: int = 0


class DishSchema(BaseSchema):
    id: uuid.UUID
    price: str


class DishBaseSchema(BaseSchema):
    price: str
