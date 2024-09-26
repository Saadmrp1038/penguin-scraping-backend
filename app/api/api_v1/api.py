from fastapi import APIRouter
from app.api.api_v1.endpoints import scrape

router = APIRouter()
router.include_router(scrape.router, prefix="/scrape", tags=["scrape"])
