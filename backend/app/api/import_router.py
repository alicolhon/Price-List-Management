from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import shutil
import os
import logging

from app.db.database import get_db
from app.core.config import settings
from app.services.importer import import_excel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/import", tags=["import"])

_import_status = {"status": "idle", "message": "No import started"}


@router.get("/status")
async def get_import_status():
    return _import_status


@router.post("/upload")
async def upload_and_import(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    force: bool = False,
):
    """Upload an .xlsb file and trigger import."""
    os.makedirs("./data", exist_ok=True)
    dest = "./data/price_list.xlsb"
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    _import_status["status"] = "running"
    _import_status["message"] = "Import started..."

    async def _run():
        try:
            result = await import_excel(db, dest, force=force)
            _import_status["status"] = "done"
            _import_status["message"] = str(result)
        except Exception as e:
            _import_status["status"] = "error"
            _import_status["message"] = str(e)
            logger.exception("Import failed")

    background_tasks.add_task(_run)
    return {"status": "started", "file": dest}


@router.post("/run")
async def run_import(
    db: AsyncSession = Depends(get_db),
    force: bool = False,
):
    """Trigger import from the default path (if file already placed in ./data/)."""
    os.makedirs("./data", exist_ok=True)
    result = await import_excel(db, settings.EXCEL_PATH, force=force)
    return result
