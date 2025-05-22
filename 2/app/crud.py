from typing import List, Optional, Dict
from fastapi import HTTPException, status
from psycopg2.extras import RealDictCursor
from . import schemas
from .auth import get_password_hash
from .database import get_db

def get_user(db, user_id: int) -> Optional[Dict]:
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()

def get_user_by_username(db, username: str) -> Optional[Dict]:
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()

def get_users(db) -> List[Dict]:
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()

def create_user(db, user: schemas.UserCreate) -> Dict:
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "INSERT INTO users (username, hashed_password, role) VALUES (%s, %s, %s) RETURNING *",
            (user.username, get_password_hash(user.password), user.role)
        )
        result = cursor.fetchone()
        db.commit()
        return result

def update_user(db, user_id: int, user: schemas.UserUpdate) -> Dict:
    existing_user = get_user(db, user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.username != existing_user['username']:
        username_exists = get_user_by_username(db, user.username)
        if username_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "UPDATE users SET username = %s, role = %s WHERE id = %s RETURNING *",
            (user.username, user.role, user_id)
        )
        result = cursor.fetchone()
        db.commit()
        return result

def delete_user(db, user_id: int) -> None:
    existing_user = get_user(db, user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()

def get_category(db, category_id: int) -> Optional[Dict]:
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
        return cursor.fetchone()

def get_categories(db) -> List[Dict]:
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM categories")
        return cursor.fetchall()

def create_category(db, category: schemas.CategoryCreate) -> Dict:
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "INSERT INTO categories (name) VALUES (%s) RETURNING *",
            (category.name,)
        )
        result = cursor.fetchone()
        db.commit()
        return result

def update_category(db, category_id: int, category: schemas.CategoryUpdate) -> Dict:
    existing_category = get_category(db, category_id)
    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "UPDATE categories SET name = %s WHERE id = %s RETURNING *",
            (category.name, category_id)
        )
        result = cursor.fetchone()
        db.commit()
        return result

def delete_category(db, category_id: int) -> None:
    existing_category = get_category(db, category_id)
    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
        db.commit()

def get_task(db, task_id: int) -> Optional[Dict]:
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            SELECT t.*, c.name as category_name 
            FROM tasks t 
            LEFT JOIN categories c ON t.category_id = c.id 
            WHERE t.id = %s
        """, (task_id,))
        return cursor.fetchone()

def get_tasks(db, user_id: int) -> List[Dict]:
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            SELECT t.*, c.name as category_name 
            FROM tasks t 
            LEFT JOIN categories c ON t.category_id = c.id 
            WHERE t.user_id = %s
        """, (user_id,))
        return cursor.fetchall()

def create_task(db, task: schemas.TaskCreate, user_id: int) -> Dict:
    category = get_category(db, task.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            INSERT INTO tasks (title, description, status, priority, due_date, user_id, category_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            task.title,
            task.description,
            task.status,
            task.priority,
            task.due_date,
            user_id,
            task.category_id
        ))
        result = cursor.fetchone()
        db.commit()
        return result

def update_task(db, task_id: int, task: schemas.TaskUpdate, user_id: int) -> Dict:
    existing_task = get_task(db, task_id)
    if not existing_task or existing_task['user_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    category = get_category(db, task.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            UPDATE tasks 
            SET title = %s, description = %s, status = %s, priority = %s, 
                due_date = %s, category_id = %s
            WHERE id = %s AND user_id = %s
            RETURNING *
        """, (
            task.title,
            task.description,
            task.status,
            task.priority,
            task.due_date,
            task.category_id,
            task_id,
            user_id
        ))
        result = cursor.fetchone()
        db.commit()
        return result

def delete_task(db, task_id: int, user_id: int) -> None:
    existing_task = get_task(db, task_id)
    if not existing_task or existing_task['user_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s", (task_id, user_id))
        db.commit()

def search_tasks(db, search_query: str, skip: int = 0, limit: int = 100) -> List[Dict]:
    with db.cursor(cursor_factory=RealDictCursor) as cursor:
        if not search_query:
            query = """
            SELECT t.*, 
                   c.name as category_name,
                   1 as rank
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            ORDER BY t.id DESC
            LIMIT %s OFFSET %s
            """
            cursor.execute(query, (limit, skip))
            return cursor.fetchall()
        
        search_pattern = f"%{search_query}%"
        
        query = """
        SELECT DISTINCT t.*, 
               c.name as category_name,
               CASE 
                   WHEN t.title ILIKE %s THEN 1
                   WHEN t.description ILIKE %s THEN 0.5
                   ELSE 0
               END as rank
        FROM tasks t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.title ILIKE %s 
           OR (t.description IS NOT NULL AND t.description ILIKE %s)
        ORDER BY rank DESC, t.id DESC
        LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, (
            search_pattern,
            search_pattern,
            search_pattern,
            search_pattern,
            limit,
            skip
        ))
        return cursor.fetchall()