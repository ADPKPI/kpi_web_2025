from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")

    
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    
    DEBUG: bool = os.getenv("DEBUG")
    HOST: str = os.getenv("HOST")
    PORT: int = int(os.getenv("PORT"))
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }

@lru_cache()
def get_settings() -> Settings:
    """
    Отримання налаштувань з кешу
    """
    return Settings()

settings = get_settings()