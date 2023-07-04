from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from todoist.api.exceptions import ConflictErrorException, ObjectNotFoundException
from todoist.api.deps import get_db, get_current_user, User

from .schemas import TodoOut, TodoCreate
from .models import Todo


router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    API endpoint to create a new todo
    """
    try:
        db_todo = Todo(title=todo.title, owner_id=user.id)
        db.add(db_todo)
        db.commit()

        return db_todo

    except IntegrityError as e:
        db.rollback()

        if "duplicate key" in str(e):
            raise ConflictErrorException
        else:
            raise e


@router.get("/", response_model=Page[TodoOut])
def list_todos(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    search: Optional[str] = Query(None),
):
    """
    API endpoint that lists all of the todos belonging to the authenticated user.
    The response is paginated. It (optionally) accepts `search` query param.
    """
    query = select(Todo)\
        .where(Todo.owner_id == user.id)\
        .order_by(Todo.created_at.desc())

    if search is not None:
        query = query.where(Todo.title.ilike(f"%{search}%"))

    return paginate(db, query)


@router.post("/{todo_id}/toggle/", response_model=TodoOut)
def toggle_todo_completed_state(
    todo_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Todo).filter_by(owner_id=user.id, id=todo_id)
    todo = query.first()

    if todo is None:
        raise ObjectNotFoundException(id=todo_id)

    try:
        query.update({Todo.is_completed: not todo.is_completed})
        db.commit()
        db.refresh(todo)
    except IntegrityError as e:
        db.rollback()
        raise e

    return todo
