import uuid
from decimal import Decimal

from pydantic import BaseModel


class BaseSchema(BaseModel):
    title: str
    description: str

    class Config:
        orm_mode = True


class MenuSchemaList(BaseSchema):
    id: uuid.UUID
    submenus_count: int = 0
    dishes_count: int = 0


class MenuSchema(BaseSchema):
    id: uuid.UUID
    submenus_count: int = 0
    dishes_count: int = 0


class SubmenuSchemaList(BaseSchema):
    id: uuid.UUID
    dishes_count: int = 0
    # menu_id: uuid.UUID


class SubmenuSchema(BaseSchema):
    id: uuid.UUID
    dishes_count: int = 0


class DishSchemaList(BaseSchema):
    id: uuid.UUID
    # submenu_id: int
    price: str


class DishSchema(BaseSchema):
    # submenu_id: int
    price: str
