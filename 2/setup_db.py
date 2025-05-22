import os
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import subprocess
import sys

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD= os.getenv("DB_PASSWORD")
DB_HOST= os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def run_docker_compose():
    print("Запуск PostgreSQL в Docker...")
    subprocess.run(["docker-compose", "up", "-d"], check=True)
    time.sleep(5)

def create_database():
    try:
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Створення бази даних {DB_NAME}...")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print("База даних створена успішно")
        else:
            print(f"База даних {DB_NAME} вже існує")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Помилка при створенні бази даних: {e}")
        sys.exit(1)

def create_tables():
    try:
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        with open('schema.sql', 'r') as file:
            schema_sql = file.read()
            cursor.execute(schema_sql)
        
        conn.commit()
        print("Таблиці створені успішно")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Помилка при створенні таблиць: {e}")
        sys.exit(1)

def create_admin_user():
    try:
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = %s", (ADMIN_USERNAME,))
        admin_exists = cursor.fetchone()
        
        if not admin_exists:
            print("Створення адміністратора...")
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash(ADMIN_PASSWORD)
            
            cursor.execute(
                """
                INSERT INTO users (username, hashed_password, role)
                VALUES (%s, %s, %s)
                """,
                (ADMIN_USERNAME, hashed_password, ADMIN_ROLE)
            )
            conn.commit()
            print("Адміністратор створений успішно")
        else:
            print("Адміністратор вже існує")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Помилка при створенні адміністратора: {e}")
        sys.exit(1)

def main():
    print("Початок налаштування бази даних...")

    run_docker_compose()
    create_database()
    create_tables()
    create_admin_user()

    print("Налаштування бази даних завершено успішно!")

if __name__ == "__main__":
    main() 