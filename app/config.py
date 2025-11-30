from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from typing import Optional

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = 'HS256'

    DATABASE_URL: str

    CORS_ALLOW_ORIGINS: List[str] = ["*"]
    HOST: str = '0.0.0.0'
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8')

settings = Settings()



# import os
# from dotenv import load_dotenv
#
# load_dotenv()
# SECRET_KEY = os.getenv('SECRET_KEY', 'A_LONG_FALLBACK_KEY_FOR_DEV_ONLY_987654321')
# ALGORITHM = "HS256"