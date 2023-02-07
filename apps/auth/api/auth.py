from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from apps.auth.crud import UserCRUD
from apps.auth.schemas import TokenSchema, UserCreateSchema, UserSchema
from core.openapi.responses import RESPONSE_303, RESPONSE_401, RESPONSE_404

router = APIRouter(prefix='/auth', tags=['auth'])


@router.get('/user', response_model=UserSchema, status_code=HTTP_200_OK, responses=RESPONSE_404)
async def get_user(current_user: UserSchema = Depends(UserCRUD.get_current_user)):
    """Возвращает данные текущего пользователя"""
    return current_user


@router.post('/sing_up', response_model=TokenSchema, status_code=HTTP_201_CREATED, responses=RESPONSE_303)
async def sign_up(user_data: UserCreateSchema, user: UserCRUD = Depends()):
    """Регистрирует нового пользователя"""
    return await user.create(user_data)


@router.post('/sing_in', response_model=TokenSchema, status_code=HTTP_200_OK, responses=RESPONSE_401)
async def sign_in(form_data: OAuth2PasswordRequestForm = Depends(), user: UserCRUD = Depends()):
    """Аутентифицирует пользователя"""
    return await user.authenticate(form_data.username, form_data.password)
