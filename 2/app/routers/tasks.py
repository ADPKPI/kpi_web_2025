from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict
from datetime import datetime
from .. import schemas, crud, auth
from ..database import get_db

router = APIRouter(
    prefix="/tasks",
    tags=["Завдання"],
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="app/templates")

PRIORITY_MAP = {
    "low": 1,
    "medium": 3,
    "high": 5
}

@router.get("", response_class=HTMLResponse, summary="Список завдань")
async def tasks_page(
    request: Request,
    current_user: Dict = Depends(auth.get_current_user)
):
    """
    Відображає сторінку зі списком завдань користувача
    """
    with get_db() as db:
        tasks = crud.get_tasks(db, current_user['id'])
        categories = crud.get_categories(db)
        return templates.TemplateResponse(
            "tasks.html",
            {
                "request": request,
                "current_user": current_user,
                "tasks": tasks,
                "categories": categories
            }
        )

@router.get("/search", response_class=HTMLResponse, summary="Поиск задач")
async def search_tasks_page(
    request: Request,
    search_query: str = "",
    current_user: Dict = Depends(auth.get_current_user)
):
    """
    Пошук задач по назві та опису
    """
    with get_db() as db:
        tasks = crud.search_tasks(db, search_query)
        categories = crud.get_categories(db)
        return templates.TemplateResponse(
            "tasks.html",
            {
                "request": request,
                "current_user": current_user,
                "tasks": tasks,
                "categories": categories,
                "search_query": search_query
            }
        )

@router.post("", summary="Створення нового завдання")
async def create_task(
    request: Request,
    title: str = Form(...),
    description: str = Form(None),
    category_id: int = Form(...),
    status: str = Form("pending"),
    priority: str = Form("medium"),
    due_date: Optional[str] = Form(None),
    current_user: Dict = Depends(auth.get_current_user)
):
    """
    Створення нового завдання:
    - **title**: назва завдання
    - **description**: опис завдання
    - **category_id**: ID категорії
    - **status**: статус завдання (pending, in_progress, completed)
    - **priority**: пріоритет завдання (low, medium, high)
    - **due_date**: термін виконання (YYYY-MM-DD)
    """
    try:
        priority_value = PRIORITY_MAP.get(priority.lower(), 3)
        
        task_data = schemas.TaskCreate(
            title=title,
            description=description,
            category_id=category_id,
            status=status,
            priority=priority_value,
            due_date=datetime.strptime(due_date, "%Y-%m-%d") if due_date else None
        )
        
        with get_db() as db:
            task = crud.create_task(db, task_data, current_user['id'])
            return RedirectResponse(url="/tasks", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{task_id}", summary="Оновлення завдання")
async def update_task(
    request: Request,
    task_id: int,
    title: str = Form(...),
    description: str = Form(None),
    category_id: int = Form(...),
    status: str = Form(...),
    priority: str = Form(None),
    due_date: Optional[str] = Form(None),
    current_user: Dict = Depends(auth.get_current_user)
):
    """
    Оновлення існуючого завдання:
    - **task_id**: ID завдання
    - **title**: назва завдання
    - **description**: опис завдання
    - **category_id**: ID категорії
    - **status**: статус завдання
    - **priority**: пріоритет завдання (low, medium, high)
    - **due_date**: термін виконання (YYYY-MM-DD)
    """
    try:
        with get_db() as db:
            task = crud.get_task(db, task_id)
            if not task or task['user_id'] != current_user['id']:
                raise HTTPException(status_code=404, detail="Task not found")
            
            priority_value = PRIORITY_MAP.get(priority.lower(), task['priority']) if priority else task['priority']
            
            task_data = schemas.TaskUpdate(
                title=title,
                description=description,
                category_id=category_id,
                status=status,
                priority=priority_value,
                due_date=datetime.strptime(due_date, "%Y-%m-%d") if due_date else None
            )
            crud.update_task(db, task_id, task_data, current_user['id'])
            return RedirectResponse(url="/tasks", status_code=303)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{task_id}", summary="Видалення завдання")
async def delete_task(
    task_id: int,
    current_user: Dict = Depends(auth.get_current_user)
):
    """
    Видалення завдання:
    - **task_id**: ID завдання для видалення
    """
    try:
        with get_db() as db:
            task = crud.get_task(db, task_id)
            if not task or task['user_id'] != current_user['id']:
                raise HTTPException(status_code=404, detail="Task not found")
            crud.delete_task(db, task_id, current_user['id'])
            return RedirectResponse(url="/tasks", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 