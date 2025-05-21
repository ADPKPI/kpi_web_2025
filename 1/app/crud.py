from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional
from datetime import date, datetime
from .auth import get_password_hash
from fastapi import HTTPException, status

def get_user(db: Session, user_id: int) -> Optional[models.User]:

    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User with this username already exists")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate) -> models.User:
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.username != db_user.username:
        existing_user = get_user_by_username(db, user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this username already exists")
    
    db_user.username = user.username
    if user.password:
        db_user.hashed_password = get_password_hash(user.password)
    if user.role:
        db_user.role = user.role
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> None:
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Видалення всіх завдань користувача
    db.query(models.Task).filter(models.Task.user_id == user_id).delete()
    
    db.delete(db_user)
    db.commit()

def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_category_by_name(db: Session, name: str) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.name == name).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[models.Category]:
    return db.query(models.Category).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    db_category = get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: int, category: schemas.CategoryUpdate) -> models.Category:
    db_category = get_category(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Перевірка чи нова назва вже зайнята
    if category.name != db_category.name:
        existing_category = get_category_by_name(db, category.name)
        if existing_category:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    db_category.name = category.name
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int) -> None:
    db_category = get_category(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Видалення всіх завдань у цій категорії
    db.query(models.Task).filter(models.Task.category_id == category_id).delete()
    
    db.delete(db_category)
    db.commit()

def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(
    db: Session,
    user_id: int,
) -> List[models.Task]:
    return db.query(models.Task).filter(models.Task.user_id == user_id).all()

def create_task(db: Session, task: schemas.TaskCreate, user_id: int) -> models.Task:
    category = get_category(db, task.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db_task = models.Task(
        **task.dict(),
        user_id=user_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task: schemas.TaskUpdate, user_id: int) -> models.Task:
    db_task = get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if db_task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Перевірка чи існує категорія
    if task.category_id != db_task.category_id:
        category = get_category(db, task.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    for key, value in task.dict(exclude_unset=True).items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int, user_id: int) -> None:
    db_task = get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if db_task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    db.delete(db_task)
    db.commit() 