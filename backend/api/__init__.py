from fastapi import APIRouter

router = APIRouter()

from .model_endpoints import router as model_endpoints_router

router.include_router(model_endpoints_router)
