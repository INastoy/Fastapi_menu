import uuid

from pydantic import BaseModel, validator


class BaseUserSchema(BaseModel):
    email: str
    username: str

    class Config:
        orm_mode = True


class UserCreateSchema(BaseUserSchema):
    password: str


class UserSchema(BaseUserSchema):
    id: uuid.UUID

    @validator('id')
    def validate_uuid(cls, value):
        if value:
            return str(value)
        return value


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = 'bearer'
