import uvicorn
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from optipy.config import settings
from optipy.api.v1 import api

app = FastAPI()
add_pagination(app)

app.include_router(api.api_router, prefix="/v1")

if __name__ == "__main__":
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
