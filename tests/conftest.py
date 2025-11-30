import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base

from app.database import Base
from app.main import app
from app.db_depends import get_async_db
from app.models import Task, User, Project, ProjectMember
from fastapi.testclient import TestClient
from fixtures.user_fixtures import *
from fixtures.project_fixtures import *
from fixtures.task_fixtures import *


@pytest.fixture(scope='session')
async def async_test_engine():
    """
    Создает асинхронный движок в памяти и создает все таблицы.
    Используется ОДИН раз за всю тестовую сессию (session).
    """

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()

@pytest.fixture(scope='function')
async def async_db_session(async_test_engine):
    """
    Предоставляет асинхронную сессию БД с автоматическим ОТКАТОМ
    (ROLLBACK) после завершения КАЖДОЙ тестовой функции (function).
    """
    async with async_test_engine.connect() as connection:
        async with connection.begin() as transaction:
            session = AsyncSession(connection, expire_on_commit=False)
            yield session

            await transaction.rollback()

@pytest.fixture(scope='function')
def override_get_async_db(async_db_session):
    """
    Генератор, который переопределяет оригинальную зависимость
    get_async_db, возвращая нашу транзакционную тестовую сессию.
    """
    async def _get_async_db():
        yield async_db_session

    return _get_async_db

@pytest.fixture(scope='function')
def test_client(override_get_async_db):
    """
    Инициализирует тестовый клиент FastAPI, ПЕРЕОПРЕДЕЛЯЕТ
    зависимость БД на транзакционную тестовую сессию.
    """
    app.dependency_overrides[get_async_db] = override_get_async_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides = {}























