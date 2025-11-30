from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Literal  # Используем Literal для ENVIRONMENT

import os

CURRENT_ENV = os.getenv('ENVIRONMENT', 'local')

# 2. Определяем список файлов, основываясь на CURRENT_ENV
if CURRENT_ENV == 'docker':
    # Для Docker Compose: только .env
    ENV_FILES = ('.env',)
else:
    # Для локальной разработки: .env.local (приоритет) и .env
    ENV_FILES = ('.env.local', '.env')


class Settings(BaseSettings):

    SECRET_KEY: str
    ALGORITHM: str = 'HS256'

    DATABASE_URL: str

    CORS_ALLOW_ORIGINS: List[str] = ["*"]
    HOST: str = '0.0.0.0'
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file='.env', # '.env.local',
        env_file_encoding='utf-8')
    # """
    # Настройки приложения с автоматическим переключением .env файлов.
    # """
    # SECRET_KEY: str
    # ALGORITHM: str = 'HS256'
    #
    # DATABASE_URL: str
    #
    # CORS_ALLOW_ORIGINS: List[str] = ["*"]
    # HOST: str = '0.0.0.0'
    # PORT: int = 8000
    #
    # # ENVIRONMENT должна быть определена, используя Literal для указания допустимых значений
    # ENVIRONMENT: Literal['local', 'docker'] = 'local'
    #
    # model_config = SettingsConfigDict(
    #     # Здесь мы используем заранее определенный кортеж ENV_FILES
    #     env_file=ENV_FILES,
    #     env_file_encoding='utf-8',
    #     extra='ignore'
    # )

settings = Settings()




print("--- Проверка DATABASE_URL ---")
print(f"Активный хост БД: {settings.DATABASE_URL.split('@')[1].split(':')[0]}")
print("--- --------------------- ---")
