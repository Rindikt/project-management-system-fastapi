import pytest

from app.services.user_service import UserService
from app.schemas.users import UserRegister
from app.models import User as UserModel
from app.auth import hash_password
from app.models.users import UserRole
from app.auth import create_access_token


@pytest.fixture(scope='function')
def user_factory(async_db_session):
    """
    Фабрика, которая возвращает асинхронную функцию для создания
    и сохранения пользователя с указанной ролью в БД.
    Это устраняет дублирование кода между test_user, owner_user и admin_user.
    """
    async  def _user_factory(
            email: str,
            role: UserRole,
            password: str = '12345Qwert',
            first_name: str = 'Тестовый',
            last_name: str = 'Пользователь',
            position: str = 'Tester') -> UserModel:

        data_for_model = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'position': position,
            'hashed_password': hash_password(password),  # Используем функцию хэширования
            'role': role
        }
        user = UserModel(**data_for_model)

        async_db_session.add(user)
        await async_db_session.flush()
        await async_db_session.refresh(user)
        return user
    return _user_factory

@pytest.fixture(scope='function')
async def test_user_data(user_factory):
    """Создает стандартного пользователя (Member)."""
    return await user_factory(
        email='member@test.com',
        role=UserRole.member,
        first_name='Броксигар',
        last_name='Саурфанг'
    )

@pytest.fixture(scope='function')
async def owner_user_data(user_factory):
    """Создает пользователя-владельца (Owner)."""
    return await user_factory(
        email='owner@test.com',
        role=UserRole.owner,
        first_name='Артас',
        last_name='Менетил',
    )

@pytest.fixture(scope='function')
async def second_owner_user_data(user_factory):
    """Создает пользователя-владельца (Owner)."""
    return await user_factory(
        email='second_owner@test.com',
        role=UserRole.owner,
        first_name='Утер',
        last_name='Светоносный',
    )


@pytest.fixture(scope='function')
async def admin_user_data(user_factory):
    """Создает пользователя-администратора (Admin)."""
    return await user_factory(
        email='admin@test.com',
        role=UserRole.admin,
        first_name='Илидан',
        last_name='Ярость_бури'
    )


@pytest.fixture(scope='function')
def auth_header_factory():
    """
    Фабрика, которая принимает объект пользователя (UserModel) и возвращает
    готовый заголовок авторизации. Это устраняет дублирование.
    """
    def _auth_header_factory(user: UserModel):

        token_data = {
            'sub': user.email,
            'role': user.role.name,
            'id': user.id
        }
        token = create_access_token(token_data)
        return {
            "Authorization": f"Bearer {token}"
        }
    return _auth_header_factory


@pytest.fixture(scope='function')
async def auth_header_member(test_user_data, auth_header_factory):
    """Возвращает заголовок для обычного пользователя (member)."""
    return auth_header_factory(test_user_data)

@pytest.fixture(scope='function')
async def auth_header_owner(owner_user_data, auth_header_factory):
    """Возвращает заголовок для владельца (owner)."""
    return auth_header_factory(owner_user_data)

@pytest.fixture(scope='function')
async def auth_header_second_owner(second_owner_user_data, auth_header_factory):
    """Возвращает заголовок для второго владельца (owner)."""
    return auth_header_factory(second_owner_user_data)

@pytest.fixture(scope='function')
async def auth_header_admin(admin_user_data, auth_header_factory):
    """Возвращает заголовок для администратора (admin)."""
    return auth_header_factory(admin_user_data)

@pytest.fixture
def invalid_password_case(owner_user_data):
    """Возвращает данные для логина с неверным паролем."""
    return {
        'username': owner_user_data.email,
        'password': 'WrongPassword123',
    }

@pytest.fixture
def invalid_email_case():
    return {
        'username': 'incorrect_email@mail.com',
        'password': '12345qwert',
    }

