from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, oauth2_refresh_scheme
from app.db_depends import get_async_db
from app.models.users import User as UserModel
from app.schemas import TaskRead
from app.schemas.users import (UserRegister,
                               UserRead as UserSchema,
                               UserBasicSchema,
                               UserUpdate,
                               UserAdminUpdate)
from app.services.task_service import TaskService
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post('/', response_model=UserBasicSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserRegister, db: AsyncSession = Depends(get_async_db)):
    """
    Регистрирует нового пользователя.
    """
    user_service = UserService(db=db)

    try:
        return await user_service.register_user(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

@router.get('/me', response_model=UserSchema)
async def get_user_my(db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_user)):
    user_service = UserService(db=db)
    my_profile = await user_service.get_my_profile(current_user)
    return my_profile

@router.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_async_db)):
    """
    Аутентифицирует пользователя и возвращает access_token и refresh_token.
    """
    user_service = UserService(db=db)

    try:
        return await user_service.login_user(form_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password",
                            headers={"WWW-Authenticate": "Bearer"})


@router.post('/refresh-token')
async def refresh_tokens(refresh_token: str = Depends(oauth2_refresh_scheme), db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет access_token с помощью refresh_token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"}
    )
    user_service = UserService(db=db)
    try:
        return await user_service.refresh_token(refresh_token)
    except ValueError as e:
        raise credentials_exception


@router.get('/{user_id}/tasks', response_model=list[TaskRead])
async def get_user_assigned_tasks(user_id: int,
                                  db: AsyncSession = Depends(get_async_db),
                                  current_user: UserModel = Depends(get_current_user)):
    task_service = TaskService(db=db)
    result = await task_service.get_user_tasks(user_id, current_user)
    return result


@router.get('/{user_id}', response_model=UserSchema)
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_db),
                   current_user: UserModel = Depends(get_current_user)):
    user_service = UserService(db=db)
    try:
        user = await user_service.get_user(user_id, current_user)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Произошла ошибка сервера")

@router.patch('/{user_id}', response_model=UserSchema)
async def update_user(user_id: int, user_admin_data: Optional[UserAdminUpdate], user: UserUpdate,
                      db: AsyncSession = Depends(get_async_db),
                      current_user: UserModel = Depends(get_current_user)):
    user_service = UserService(db=db)
    try:
        updated_user = await user_service.update_user(user_id,
                                                      user=user,
                                                      admin_data=user_admin_data,
                                                      current_user=current_user)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get('/', response_model=list[UserBasicSchema])
async def get_users(db: AsyncSession = Depends(get_async_db),
                    _: UserModel = Depends(get_current_user)):
    user_service = UserService(db=db)
    try:
        result = await user_service.get_users()
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))















