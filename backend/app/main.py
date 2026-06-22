import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.db.database import init_db
from app.api.products import router as products_router
from app.api.import_router import router as import_router
from app.api.reference import router as reference_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("./data", exist_ok=True)
    await init_db()
    logger.info("Database initialized")
    yield


app = FastAPI(
    title="MA-SMS Price List Management",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(import_router)
app.include_router(reference_router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


# Serve React frontend build in production
if os.path.exists("./static"):
    app.mount("/", StaticFiles(directory="./static", html=True), name="static")
