from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import models, schemas, crud, auth
from ..database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Аутентифікація"],
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse, summary="Сторінка входу")
async def login_page(request: Request):
    """
    Відображає сторінку входу в систему
    """
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", summary="Вхід в систему")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """
    Аутентифікація користувача:
    - **username**: ім'я користувача
    - **password**: пароль користувача
    """
    user = auth.authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid username or password"}
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/tasks", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@router.get("/register", response_class=HTMLResponse, summary="Сторінка реєстрації")
async def register_page(request: Request):
    """
    Відображає сторінку реєстрації нового користувача
    """
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", summary="Реєстрація нового користувача")
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("user"),
    db: Session = Depends(get_db)
):
    """
    Реєстрація нового користувача:
    - **username**: ім'я користувача
    - **password**: пароль користувача
    - **role**: роль користувача (за замовчуванням "user")
    """
    try:
        user = crud.create_user(db, schemas.UserCreate(username=username, password=password, role=role))
        return RedirectResponse(url="/auth/login", status_code=303)
    except HTTPException as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": str(e.detail)}
        )

@router.get("/logout", summary="Вихід з системи")
async def logout():
    """
    Вихід з системи та видалення токена доступу
    """
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response 