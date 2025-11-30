from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, EmailStr
from app.models.users import UserRole


class UserRegister(BaseModel):
    email: EmailStr = Field(description='Email пользователя')
    password: str = Field( min_length= 8, description='Пароль (минимум 8 символов)')
    first_name: str = Field(min_length=2, max_length=20, description='Имя сотрудника')
    last_name: str = Field(min_length=2, max_length=20, description='Фамилия сотрудника')
    position: str|None = Field(max_length=50, description='Должность сотрудника')


class UserUpdate(BaseModel):
    first_name: str = Field(min_length=2, max_length=20, description='Имя сотрудника')
    last_name: str = Field(min_length=2, max_length=20, description='Фамилия сотрудника')

class UserAdminUpdate(BaseModel):
    position: str|None = Field(None,max_length=50, description='Должность сотрудника')
    role: Optional[UserRole] = Field(None, description='Роль сотрудника')


class UserReadSchema(BaseModel):
    id: int
    email: EmailStr = Field(description='Email сотрудника')
    first_name: str = Field(min_length=2, max_length=20, description='Имя сотрудника')
    last_name: str = Field(min_length=2, max_length=20, description='Фамилия сотрудника')
    model_config = ConfigDict(from_attributes=True)

class UserBasicSchema(UserReadSchema):

    position: str|None = Field(max_length=50, description='Должность сотрудника')
    role: UserRole = Field(description='Роль сотрудника')
    is_active: bool = Field(default=True, description='Статус работы сотрудника')



class UserRead(UserBasicSchema):

    tasks_count: Optional[int] = Field(None, description='Количество задач, назначенных пользователю')
    assigned_tasks: list['TaskRead'] = Field(description='Задачи сотрудника',
                                             default_factory=list)

    owned_projects: list['ProjectBasic'] = Field(description='Проекты сотрудника',
                                                 default_factory=list)


class UserLoginSchema(BaseModel):
    """
    Минимальная схема для возврата данных при входе.
    Содержит только то, что нужно фронтенду (ID, Role, Name).
    """
    id: int
    user_id: Optional[int] = None
    email: EmailStr
    first_name: str = Field(description='Имя сотрудника')
    last_name: str = Field(description='Фамилия сотрудника')
    role: UserRole = Field(description='Роль сотрудника')

    model_config = ConfigDict(from_attributes=True)



