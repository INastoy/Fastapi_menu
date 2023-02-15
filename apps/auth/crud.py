from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.hash import bcrypt
from pydantic import ValidationError
from sqlalchemy import insert, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.database import Session, get_session
from core.settings import JWT_ALGORITHM, JWT_EXPIRATION, JWT_SECRET

from .models import User
from .schemas import TokenSchema, UserAuthSchema, UserCreateSchema, UserSchema

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/v1/auth/sing_in')


# def get_current_user(token: str = Depends(oauth2_scheme)) -> UserSchema:
#     return UserCRUD.validate_token(token)


class UserCRUD:
    def __init__(self, session: Session = Depends(get_session)):
        self.session: AsyncSession = session
        self.model: type[User] = User

    async def create(self, user_data: UserCreateSchema) -> TokenSchema:
        user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=await self._hash_password(user_data.password),
        )
        try:
            cursor: CursorResult = await self.session.execute(
                insert(User).values(**UserAuthSchema.from_orm(user).dict())
            )
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER, detail='User already exists')
        await self.session.commit()
        user.id = cursor.inserted_primary_key[0]

        return await self._create_token(user)

    async def authenticate(self, username: str, password: str) -> TokenSchema:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        user = await self.session.scalar(select(User).filter(User.username == username))
        if not user or not await self._verify_password(password, user.password_hash):
            raise exception

        return await self._create_token(user)

    @classmethod
    # def get_current_user(token: str = Depends(oauth2_schema)) -> UserSchema:
    async def get_current_user(
            cls,
            token: OAuth2PasswordBearer(tokenUrl='api/v1/auth/sing_in') = Depends()) -> UserSchema:  # type: ignore
        return await cls._validate_token(token)

    @staticmethod
    async def _verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)

    @staticmethod
    async def _hash_password(password: str) -> str:
        return bcrypt.hash(password)

    @staticmethod
    async def _validate_token(token: str) -> UserSchema:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_data = payload.get('user')
            user = UserSchema.parse_obj(user_data)
        except JWTError:
            raise exception
        except ValidationError:
            raise exception

        return user

    @staticmethod
    async def _create_token(user: User) -> TokenSchema:
        user_data = UserSchema.from_orm(user)
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(seconds=JWT_EXPIRATION),
            'sub': str(user_data.id),
            'user': user_data.dict(),
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        return TokenSchema(access_token=token)
