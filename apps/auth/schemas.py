import uuid

from pydantic import BaseModel, EmailStr, Field, validator


class BaseUserSchema(BaseModel):
    email: EmailStr
    username: str

    class Config:
        orm_mode = True


class UserCreateSchema(BaseUserSchema):
    password: str = Field(min_length=6, max_length=30)

    class Config:
        schema_extra = {
            'example': {
                'email': 'example@example.com',
                'username': 'username',
                'password': 'password'
            }
        }


class UserAuthSchema(BaseUserSchema):
    password_hash: str


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
