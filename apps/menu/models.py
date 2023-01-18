import uuid
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AbstractModel(Base):
    __abstract__ = True

    id: str = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: str = Column(String)
    description: str = Column(String)


class Menu(AbstractModel):
    __tablename__ = 'menus'


class Submenu(AbstractModel):
    __tablename__ = 'submenus'

    menu_id: str = Column(UUID(as_uuid=True), ForeignKey(Menu.id, onupdate='CASCADE', ondelete='CASCADE'), nullable=False)


class Dish(AbstractModel):
    __tablename__ = 'dishes'

    price: Decimal = Column(Numeric(10, 2))
    submenu_id: str = Column(UUID(as_uuid=True), ForeignKey(Submenu.id, onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
