from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status, Query, Body
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from optipy.api.exceptions import ConflictErrorException, ObjectNotFoundException
from optipy.api.deps import get_db

from .schemas import CategoryIn, CategoryOut, CategoryUpdate
from .models import Category


router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryIn, db: Session = Depends(get_db)):
    """
    API endpoint to create a new category
    """
    try:
        db_category = Category(**category.dict())
        db.add(db_category)
        db.commit()

        return db_category

    except IntegrityError as e:
        db.rollback()

        if "duplicate key" in str(e):
            raise ConflictErrorException
        else:
            raise e


@router.get("/", response_model=Page[CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None),
):
    """
    API endpoint that lists all of the categories.
    The response is paginated.
    It (optionally) accepts `search` query param.
    """
    query = select(Category).order_by(Category.importance.desc())

    if search is not None:
        query = query.where(Category.category_name.ilike(f"%{search}%"))

    return paginate(db, query)


@router.get("/{id}/", response_model=CategoryOut)
def read_category(
    id: UUID,
    db: Session = Depends(get_db)
):
    try:
        return db.query(Category).filter_by(id=id).one()

    except NoResultFound:
        raise ObjectNotFoundException(id=id)


@router.patch("/{id}/", response_model=CategoryOut, status_code=status.HTTP_202_ACCEPTED)
def update_category(
    id: UUID,
    partial_category: CategoryUpdate = Body(),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(Category).filter_by(id=id)
        category = query.one()

        query.update(partial_category.dict(exclude_unset=True))
        db.commit()
        db.refresh(category)

        return category

    except NoResultFound:
        raise ObjectNotFoundException(id=id)

    except IntegrityError as e:
        db.rollback()

        if "duplicate key" in str(e):
            raise ConflictErrorException
        else:
            raise e


@router.delete("/{id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    id: UUID,
    db: Session = Depends(get_db)
):
    try:
        category = db.query(Category).filter_by(id=id).one()
        db.delete(category)
        db.commit()

        return None

    except NoResultFound:
        raise ObjectNotFoundException(id=id)

    except IntegrityError as e:
        db.rollback()
        raise e
