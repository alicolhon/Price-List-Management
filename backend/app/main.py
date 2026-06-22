import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.core.config import settings
from app.db.database import init_db, AsyncSessionLocal
from app.api.products import router as products_router
from app.api.import_router import router as import_router
from app.api.reference import router as reference_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _auto_import_if_empty() -> None:
    """Import the Excel file in the background if the DB is empty and the file exists."""
    excel_path = settings.EXCEL_PATH
    if not os.path.exists(excel_path):
        logger.info("Auto-import skipped: %s not found", excel_path)
        return

    from sqlalchemy import text
    from app.services.importer import import_excel

    async with AsyncSessionLocal() as db:
        count = (await db.execute(text("SELECT COUNT(*) FROM products"))).scalar() or 0
        if count > 0:
            logger.info("Auto-import skipped: DB already has %d products", count)
            return

    logger.info("Auto-import: empty DB + Excel found → importing %s …", excel_path)
    async with AsyncSessionLocal() as db:
        try:
            result = await import_excel(db, excel_path, force=False)
            logger.info("Auto-import complete: %s", result)
        except Exception as exc:
            logger.error("Auto-import failed: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("./data", exist_ok=True)
    await init_db()
    logger.info("Database initialized")
    asyncio.create_task(_auto_import_if_empty())
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
