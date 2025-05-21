from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import models, schemas, crud, auth
from ..database import get_db

router = APIRouter(
    prefix="/categories",
    tags=["Категорії"],
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse, summary="Список категорій")
async def categories_page(
    request: Request,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Відображає сторінку зі списком категорій (тільки для адміністраторів)
    """
    if current_user.role != "admin":
        return templates.TemplateResponse(
            "categories.html",
            {
                "request": request,
                "current_user": current_user,
                "categories": None,
                "error": "Insufficient permissions"
            }
        )
    categories = crud.get_categories(db)
    return templates.TemplateResponse(
        "categories.html",
        {"request": request, "current_user": current_user, "categories": categories}
    )

@router.post("", summary="Створення нової категорії")
async def create_category(
    request: Request,
    name: str = Form(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Створення нової категорії (тільки для адміністраторів):
    - **name**: назва категорії
    """
    if current_user.role != "admin":
        return templates.TemplateResponse(
            "categories.html",
            {
                "request": request,
                "current_user": current_user,
                "categories": None,
                "error": "Insufficient permissions"
            }
        )
    try:
        crud.create_category(db, schemas.CategoryCreate(name=name))
        return RedirectResponse(url="/categories", status_code=303)
    except HTTPException as e:
        categories = crud.get_categories(db)
        return templates.TemplateResponse(
            "categories.html",
            {
                "request": request,
                "current_user": current_user,
                "categories": categories,
                "error": str(e.detail)
            }
        )

@router.put("/{category_id}", summary="Оновлення категорії")
async def update_category(
    request: Request,
    category_id: int,
    name: str = Form(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Оновлення існуючої категорії (тільки для адміністраторів):
    - **category_id**: ID категорії
    - **name**: нова назва категорії
    """
    if current_user.role != "admin":
        return templates.TemplateResponse(
            "categories.html",
            {
                "request": request,
                "current_user": current_user,
                "categories": None,
                "error": "Insufficient permissions"
            }
        )
    try:
        crud.update_category(db, category_id, schemas.CategoryUpdate(name=name))
        return RedirectResponse(url="/categories", status_code=303)
    except HTTPException as e:
        categories = crud.get_categories(db)
        return templates.TemplateResponse(
            "categories.html",
            {
                "request": request,
                "current_user": current_user,
                "categories": categories,
                "error": str(e.detail)
            }
        )

@router.delete("/{category_id}", summary="Видалення категорії")
async def delete_category(
    request: Request,
    category_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Видалення категорії (тільки для адміністраторів):
    - **category_id**: ID категорії для видалення
    """
    if current_user.role != "admin":
        return templates.TemplateResponse(
            "categories.html",
            {
                "request": request,
                "current_user": current_user,
                "categories": None,
                "error": "Insufficient permissions"
            }
        )
    crud.delete_category(db, category_id)
    return RedirectResponse(url="/categories", status_code=303) 