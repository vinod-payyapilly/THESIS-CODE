from fastapi import APIRouter, Depends
from app.config.settings import settings
from app.endpoints import llm_model_service
from app.endpoints import diagram_service

router = APIRouter()

router.include_router(llm_model_service.router)
router.include_router(diagram_service.router)

