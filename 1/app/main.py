from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db
from .config import settings
from .routers import auth, tasks, categories, users
from .auth import get_current_user_optional

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Manager",
    description="""
    Прохоренко Артем | ІО-23 | Лабораторна робота №1
    Система управління завданнями з можливостями:
    * Аутентифікація користувачів
    * Управління завданнями
    * Управління категоріями (для адміністраторів)
    * Управління користувачами (для адміністраторів)
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router, tags=["Аутентифікація"])
app.include_router(tasks.router, tags=["Завдання"])
app.include_router(categories.router, tags=["Категорії"])
app.include_router(users.router, tags=["Користувачі"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, current_user: models.User = Depends(get_current_user_optional)):
    """
    Головна сторінка додатку
    """
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("base.html", {"request": request, "current_user": current_user}) 