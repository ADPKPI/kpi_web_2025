from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Dict
from .. import schemas, crud, auth
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=["Користувачі"],
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse, summary="Список користувачів")
async def users_page(
    request: Request,
    current_user: Dict = Depends(auth.get_current_user)
):
    """
    Відображає сторінку зі списком користувачів (тільки для адміністраторів)
    """
    if current_user['role'] != "admin":
        return templates.TemplateResponse(
            "users.html",
            {
                "request": request,
                "current_user": current_user,
                "users": None,
                "error": "Insufficient permissions"
            }
        )
    with get_db() as db:
        users = crud.get_users(db)
        return templates.TemplateResponse(
            "users.html",
            {"request": request, "current_user": current_user, "users": users}
        )

@router.post("", summary="Створення нового користувача")
async def create_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("user"),
    current_user: Dict = Depends(auth.get_current_user)
):
    """
    Створення нового користувача (тільки для адміністраторів):
    - **username**: ім'я користувача
    - **password**: пароль користувача
    - **role**: роль користувача (user/admin)
    """
    if current_user['role'] != "admin":
        return templates.TemplateResponse(
            "users.html",
            {
                "request": request,
                "current_user": current_user,
                "users": None,
                "error": "Insufficient permissions"
            }
        )
    try:
        with get_db() as db:
            crud.create_user(db, schemas.UserCreate(username=username, password=password, role=role))
            return RedirectResponse(url="/users", status_code=303)
    except HTTPException as e:
        with get_db() as db:
            users = crud.get_users(db)
            return templates.TemplateResponse(
                "users.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "users": users,
                    "error": str(e.detail)
                }
            )

@router.put("/{user_id}", summary="Оновлення користувача")
async def update_user(
    request: Request,
    user_id: int,
    username: str = Form(...),
    role: str = Form(...),
    current_user: Dict = Depends(auth.get_current_user)
):
    """
    Оновлення даних користувача (тільки для адміністраторів):
    - **user_id**: ID користувача
    - **username**: нове ім'я користувача
    - **role**: нова роль користувача (user/admin)
    """
    if current_user['role'] != "admin":
        return templates.TemplateResponse(
            "users.html",
            {
                "request": request,
                "current_user": current_user,
                "users": None,
                "error": "Insufficient permissions"
            }
        )
    try:
        with get_db() as db:
            crud.update_user(db, user_id, schemas.UserUpdate(username=username, role=role))
            return RedirectResponse(url="/users", status_code=303)
    except HTTPException as e:
        with get_db() as db:
            users = crud.get_users(db)
            return templates.TemplateResponse(
                "users.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "users": users,
                    "error": str(e.detail)
                }
            )

@router.delete("/{user_id}", summary="Видалення користувача")
async def delete_user(
    request: Request,
    user_id: int,
    current_user: Dict = Depends(auth.get_current_user)
):
    """
    Видалення користувача (тільки для адміністраторів):
    - **user_id**: ID користувача для видалення
    """
    if current_user['role'] != "admin":
        return templates.TemplateResponse(
            "users.html",
            {
                "request": request,
                "current_user": current_user,
                "users": None,
                "error": "Insufficient permissions"
            }
        )
    with get_db() as db:
        crud.delete_user(db, user_id)
        return RedirectResponse(url="/users", status_code=303) 