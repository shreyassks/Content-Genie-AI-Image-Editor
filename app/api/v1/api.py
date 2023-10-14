from fastapi import APIRouter

from api.v1.endpoints import replace_anything
from api.v1.endpoints import fill_anything
from api.v1.endpoints import remove_anything
from api.v1.endpoints import upload_image
from api.v1.endpoints import captioning_api

v1_router = APIRouter()

v1_router.include_router(fill_anything.router, prefix="/v1")
v1_router.include_router(replace_anything.router, prefix="/v1")
v1_router.include_router(remove_anything.router, prefix="/v1")
v1_router.include_router(upload_image.router, prefix="/v1")
v1_router.include_router(captioning_api.router, prefix="/v1")
