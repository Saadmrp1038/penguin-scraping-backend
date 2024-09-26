from fastapi import FastAPI
from app.api.api_v1.api import router as api_router

app = FastAPI()

app.include_router(api_router, prefix="/api/v1")

# Dummy Endpoint
@app.get("/")
async def get_question_by_id():
   return "Penguin Lab"
