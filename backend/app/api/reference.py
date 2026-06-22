from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, distinct

from app.db.database import get_db
from app.models.product import Product
from app.models.reference import NpClassDeviation, EuTargetIncrease

router = APIRouter(prefix="/api/reference", tags=["reference"])


@router.get("/pg1")
async def list_pg1(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(
        select(distinct(Product.pg1_current), Product.pg1_description)
        .where(Product.pg1_current.isnot(None))
        .order_by(Product.pg1_current)
    )
    return [{"code": r[0], "description": r[1]} for r in rows]


@router.get("/pg2")
async def list_pg2(db: AsyncSession = Depends(get_db), pg1: str = None):
    stmt = (
        select(distinct(Product.pg2_current), Product.pg2_description)
        .where(Product.pg2_current.isnot(None))
    )
    if pg1:
        stmt = stmt.where(Product.pg1_current == pg1)
    rows = await db.execute(stmt.order_by(Product.pg2_current))
    return [{"code": r[0], "description": r[1]} for r in rows]


@router.get("/discount-groups")
async def list_discount_groups(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(
        select(distinct(Product.discount_group_current))
        .where(Product.discount_group_current.isnot(None))
        .order_by(Product.discount_group_current)
    )
    return [r[0] for r in rows]


@router.get("/np-deviations")
async def list_np_deviations(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(NpClassDeviation))
    return [
        {"pg1_code": r.pg1_code, "dgr": r.dgr, "gold": r.deviation_gold,
         "silver": r.deviation_silver, "bronze": r.deviation_bronze}
        for r in rows.scalars()
    ]
