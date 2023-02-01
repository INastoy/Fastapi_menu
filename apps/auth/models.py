import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


class AbstractUser(Base):
    __abstract__ = True

    id: str = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: str = Column(String, unique=True)
    username: str = Column(String, unique=True)
    password_hash: str = Column(String)


class User(AbstractUser):
    __tablename__ = 'users'
