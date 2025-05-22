import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from .config import settings


@contextmanager
def get_db():
    """Получение соединения с базой данных"""
    conn = psycopg2.connect(
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        cursor_factory=RealDictCursor
    )
    try:
        yield conn
    finally:
        conn.close() 