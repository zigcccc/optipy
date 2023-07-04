from fastapi import APIRouter

from todoist.todos.endpoints import router as todos_router
from todoist.users.endpoints import router as users_router

api_router = APIRouter()

api_router.include_router(todos_router)
api_router.include_router(users_router)
