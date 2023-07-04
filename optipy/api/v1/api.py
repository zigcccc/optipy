from fastapi import APIRouter

from optipy.apps.users import endpoints as users_endpoints
from optipy.apps.categories import endpoints as categories_endpoints

api_router = APIRouter()

api_router.include_router(users_endpoints.router)
api_router.include_router(categories_endpoints.router)
