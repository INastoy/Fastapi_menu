import uuid
from decimal import Decimal

from sqlalchemy import Column, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class AbstractModel(Base):
    __abstract__ = True

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: str = Column(String)
    description: str = Column(String)


class Menu(AbstractModel):
    __tablename__ = 'menus'

    submenus = relationship('Submenu', cascade='all, delete')


class Submenu(AbstractModel):
    __tablename__ = 'submenus'

    menu_id: UUID = Column(
        UUID(as_uuid=True),
        ForeignKey(Menu.id, onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
    )
    dishes = relationship('Dish', cascade='all, delete')


class Dish(AbstractModel):
    __tablename__ = 'dishes'

    price: Decimal = Column(Numeric(10, 2))
    submenu_id: UUID = Column(
        UUID(as_uuid=True),
        ForeignKey(Submenu.id, onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
    )
