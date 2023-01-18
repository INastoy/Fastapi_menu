import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


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
    dishes_count: int = 0
    # menu_id: int


class DishSchema(BaseSchema):
    # submenu_id: int
    price: Decimal
