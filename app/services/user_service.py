from typing import Optional

import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.users import User as UserModel, UserRole
from app.models.tasks import Task as TaskModel
from app.schemas.users import UserRegister, UserUpdate, UserAdminUpdate
from app.auth import (hash_password,
                      verify_password,
                      create_access_token,
                      create_refresh_token)


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> UserModel|None:
        """Находит пользователя по email."""
        result = await self.db.scalar(
            select(UserModel).where(UserModel.email == email)
        )
        return result

    async def create_user_with_role(self, user_in: dict, role: UserRole) -> UserModel:
        """
        Создает пользователя с явно указанной ролью (admin/owner).
        Используется только для инициализации системы.
        """
        if await self.get_by_email(user_in["email"]):
            raise ValueError('Пользователь с таким email уже существует.')

        new_user = UserModel(
            email=user_in["email"],
            hashed_password=hash_password(user_in["password"]),
            first_name=user_in["first_name"],
            last_name=user_in["last_name"],
            role=role,
        )
        if user_in.get('position'):
            new_user.position = user_in['position']

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user



    async def register_user(self, user: UserRegister) -> UserModel:
        """
        Регистрирует нового пользователя.
        """
        result = await self.db.scalar(
            select(UserModel).where(UserModel.email == user.email)
        )
        if result:
            raise ValueError('Email already registered')
        new_user = UserModel(
            email=user.email,
            hashed_password=hash_password(user.password),
            first_name=user.first_name,
            last_name=user.last_name,
            role=UserRole.member
        )
        if user.position:
            new_user.position = user.position

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def login_user(self, from_data: OAuth2PasswordRequestForm):
        """
        Аутентифицирует пользователя и возвращает access_token и refresh_token.
        """
        user = await self.db.scalar(
            select(UserModel).where(UserModel.email == from_data.username,
                                    UserModel.is_active == True))
        if not user:
            raise ValueError('Invalid email or password')

        if not verify_password(from_data.password, user.hashed_password):
            raise ValueError('Invalid email or password')

        access_token = create_access_token(data={"sub": user.email, "role": user.role.name, "id": user.id})
        refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role.name, "id": user.id})
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    async def refresh_token(self, refresh_token: str):
        """
        Обновляет access_token с помощью refresh_token.
        """
        try:
            payload = jwt.decode(refresh_token,settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get('sub')
            if not email:
                raise ValueError('No email')
        except jwt.PyJWTError:
            raise ValueError('Invalid token')
        user = await self.db.scalar(
            select(UserModel)
            .where(UserModel.email == email,
                   UserModel.is_active == True)
        )
        if user is None:
            raise ValueError('No such user')
        access_token = create_access_token(data={"sub": user.email, "role": user.role.name, "id": user.id})
        return {"access_token": access_token, "token_type": "bearer"}

    async def get_user(self, user_id: int, current_user) -> UserModel:
        result = await self.db.scalar(
            select(UserModel)
            .options(selectinload(UserModel.assigned_tasks)
                     .selectinload(TaskModel.project),
                     selectinload(UserModel.assigned_tasks)
                     .selectinload(TaskModel.author),
                     selectinload(UserModel.owned_projects))
            .where(UserModel.id == user_id)
        )
        if not result:
            raise ValueError('User not found')
        assigned_tasks_list = result.assigned_tasks
        _ = result.owned_projects

        task_count = len(assigned_tasks_list) if assigned_tasks_list is not None else 0
        setattr(result, 'tasks_count', task_count)
        return result

    async def update_user(self, user_id: int,
                          user: UserUpdate,
                          current_user,
                          admin_data: Optional[UserAdminUpdate] = None,) -> UserModel:
        is_admin = current_user.role == UserRole.admin
        is_self = current_user.id == user_id
        if not is_self and not admin_data:
            raise PermissionError("У вас нет прав для редактирования профиля другого пользователя.")

        result = await self.db.scalar(select(UserModel).where(UserModel.id == user_id))
        if not result:
            raise ValueError('User not found')

        update_data = user.model_dump(exclude_unset=True)

        if admin_data:
            admin_update_data = admin_data.model_dump(exclude_unset=True)
            if not admin_update_data:
                pass

            else:
                if not is_admin:
                    raise PermissionError("Только администратор может изменять должность и роль.")

                update_data.update(admin_update_data)

        if not update_data:
            return result
        updated_user = update(UserModel).where(UserModel.id == user_id).values(**update_data)
        await self.db.execute(updated_user)
        await self.db.commit()
        stmt = (
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(
                selectinload(UserModel.assigned_tasks).selectinload(TaskModel.project),
                selectinload(UserModel.assigned_tasks).selectinload(TaskModel.author),
                selectinload(UserModel.owned_projects)
            )
        )
        final_user_result = await self.db.scalar(stmt)
        if not final_user_result:
            raise ValueError('User not found after update')

        return final_user_result

    async def get_users(self):
        result = (await self.db.scalars(
            select(UserModel)
            .where(UserModel.is_active == True)
            .order_by(UserModel.first_name))).all()
        if not result:
            raise ValueError('Users not found')
        return result

    async def get_my_profile(self, current_user: UserModel):
        result = await self.db.scalar(
            select(UserModel)
            .where(UserModel.email == current_user.email)
            .options(
                selectinload(UserModel.assigned_tasks).selectinload(TaskModel.project),
                selectinload(UserModel.assigned_tasks).selectinload(TaskModel.author),
                selectinload(UserModel.owned_projects)
            )
        )
        if not result:
            raise ValueError('User not found')

        assigned_tasks_list = result.assigned_tasks
        _ = result.owned_projects

        task_count = len(assigned_tasks_list) if assigned_tasks_list is not None else 0
        setattr(result, 'tasks_count', task_count)

        return result








