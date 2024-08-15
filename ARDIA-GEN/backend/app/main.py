from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from app.config.settings import settings
from contextlib import asynccontextmanager
import httpx
from app.routes.api import router as api_router

origins = ["*"]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialise the Client on startup and add it to the state
    # http://127.0.0.1:8001/ is the base_url of the other server that requests should be forwarded to
    async with httpx.AsyncClient(base_url=settings.OLLAMA_URL) as client:
        yield {'client': client}

app = FastAPI(title=settings.NAME,version=settings.VERSION,lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    #allow_origins=origins,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    #expose_headers=["*"]
)

app.include_router(api_router)

@app.get("/info", tags=["info"])
def get_day_of_week():
    print("Incoming request...")
    return {
        "msg": "backend is running"
    }
