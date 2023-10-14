from fastapi import APIRouter

root_router = APIRouter()


@root_router.get("/")
def read_root():
    return {"About": "Khoros Image Generation API"}


@root_router.get("/health")
def get_health():
    """To check the service health"""
    return {"status": "ok"}
