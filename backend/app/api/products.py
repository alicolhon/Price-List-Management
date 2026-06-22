from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from typing import Optional
import logging

from app.db.database import get_db
from app.models.product import Product
from app.models.reference import NpClassDeviation
from app.schemas.product import (
    ProductRead, ProductUpdate, ProductWithCalc, ProductListResponse,
    CalculationResult, SummaryStats,
)
from app.services.formula_engine import PriceInputs, calculate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/products", tags=["products"])


def _build_calc(product: Product, np_devs: dict) -> CalculationResult:
    """Build PriceInputs from a Product ORM object and run formula engine."""
    pg1 = product.pg1_current or ""
    devs = np_devs.get(pg1, {})

    inputs = PriceInputs(
        material_10=product.material_10,
        pg1_current=pg1,
        discount_group_current=product.discount_group_current or "",
        discount_group_future=product.discount_group_future or "",
        max_basic_discount_current=product.max_basic_discount_current,
        max_add_discount_current=product.max_add_discount_current,
        future_basic_discount=product.future_basic_discount,
        future_add_discount=product.future_add_discount,
        bonus_sde=product.bonus_sde,
        rrp_current_01_2026=product.rrp_current_01_2026,
        rrp_future_04_2026=product.rrp_future_04_2026,
        np_platinum_lc=product.np_platinum_lc,
        np_platinum_manual_override=product.np_platinum_manual_override or False,
        npp_current_imported=getattr(product, 'npp_current_de21_imported', None),
        npp_future_imported=getattr(product, 'npp_future_de21_imported', None),
        ipp_final_current_imported=getattr(product, 'ipp_final_current_imported', None),
        ipp_final_future_imported=getattr(product, 'ipp_final_future_imported', None),
        current_margin_imported=getattr(product, 'current_margin_imported', None),
        new_margin_imported=getattr(product, 'new_margin_imported', None),
        current_violation_imported=getattr(product, 'current_violation_imported', None),
        future_violation_imported=getattr(product, 'future_violation_imported', None),
        npp_pl_intercars=product.npp_pl_intercars,
        npp_autonet=product.npp_autonet,
        npp_truck=product.npp_truck,
        npp_lkq=product.npp_lkq,
        minimum_npp_eur=product.minimum_npp_eur,
        maximum_npp_eur=product.maximum_npp_eur,
        deviation_gold=devs.get("gold"),
        deviation_silver=devs.get("silver"),
        deviation_bronze=devs.get("bronze"),
    )

    result = calculate(inputs, qty_12m=product.qty_12m)

    return CalculationResult(
        material_10=product.material_10,
        **{k: v for k, v in result.__dict__.items()},
    )


async def _get_np_devs(db: AsyncSession) -> dict:
    """Cache NP class deviations keyed by PG1 code."""
    rows = await db.execute(select(NpClassDeviation))
    devs: dict = {}
    for row in rows.scalars():
        devs[row.pg1_code] = {
            "gold": row.deviation_gold,
            "silver": row.deviation_silver,
            "bronze": row.deviation_bronze,
        }
    return devs


@router.get("", response_model=ProductListResponse)
async def list_products(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    pg1: Optional[str] = Query(None),
    pg2: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    abc_sales: Optional[str] = Query(None),
    violation: Optional[str] = Query(None),  # 'any' | 'MIN' | 'MAX' | 'ROTTEN_APPLE'
    discount_group: Optional[str] = Query(None),
    with_calc: bool = Query(True),
):
    stmt = select(Product)

    if search:
        s = f"%{search}%"
        stmt = stmt.where(
            or_(
                Product.material_10.ilike(s),
                Product.description_en.ilike(s),
                Product.description_de.ilike(s),
            )
        )
    if pg1:
        stmt = stmt.where(Product.pg1_current == pg1)
    if pg2:
        stmt = stmt.where(Product.pg2_current == pg2)
    if status:
        stmt = stmt.where(Product.status == status)
    if abc_sales:
        stmt = stmt.where(Product.abc_sales == abc_sales)
    if discount_group:
        stmt = stmt.where(Product.discount_group_current == discount_group)

    np_devs = await _get_np_devs(db) if with_calc else {}

    if violation:
        # Violation is a calculated field — fetch all matching rows, filter in Python, then paginate
        all_rows = (await db.execute(stmt)).scalars().all()
        filtered = []
        for p in all_rows:
            calc = _build_calc(p, np_devs)
            viol = calc.future_violation
            if violation == "any":
                if viol == "OK":
                    continue
            elif viol != violation:
                continue
            filtered.append(ProductWithCalc(**ProductRead.model_validate(p).model_dump(), calc=calc))
        total = len(filtered)
        start = (page - 1) * page_size
        items = filtered[start: start + page_size]
    else:
        # Normal path: SQL count + paginate
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        rows = (await db.execute(stmt)).scalars().all()
        items = []
        for p in rows:
            calc = _build_calc(p, np_devs) if with_calc else None
            items.append(ProductWithCalc(**ProductRead.model_validate(p).model_dump(), calc=calc))

    return ProductListResponse(total=total, page=page, page_size=page_size, items=items)


@router.get("/summary", response_model=SummaryStats)
async def get_summary(db: AsyncSession = Depends(get_db)):
    """Return aggregate statistics for the summary bar."""
    all_products = (await db.execute(select(Product))).scalars().all()
    np_devs = await _get_np_devs(db)

    total = len(all_products)
    active = sum(1 for p in all_products if p.status and "active" in p.status.lower())

    violations = 0
    rotten = 0
    min_v = 0
    max_v = 0
    total_ipp_cur = 0.0
    total_ipp_fut = 0.0
    rrp_change_weighted = 0.0
    ipp_change_weighted = 0.0
    total_vol = 0.0

    for p in all_products:
        calc = _build_calc(p, np_devs)
        if calc.future_violation != "OK":
            violations += 1
        if calc.future_violation == "ROTTEN_APPLE":
            rotten += 1
        elif calc.future_violation == "MIN":
            min_v += 1
        elif calc.future_violation == "MAX":
            max_v += 1
        vol = calc.ipp_volume_current or 0
        total_ipp_cur += calc.ipp_volume_current or 0
        total_ipp_fut += calc.ipp_volume_future or 0
        if calc.rrp_change_pct is not None:
            rrp_change_weighted += calc.rrp_change_pct * vol
        if calc.ipp_change_pct is not None:
            ipp_change_weighted += calc.ipp_change_pct * vol
        total_vol += vol

    return SummaryStats(
        total_products=total,
        active_products=active,
        total_violations=violations,
        rotten_apples=rotten,
        min_violations=min_v,
        max_violations=max_v,
        total_ipp_volume_current=round(total_ipp_cur, 2),
        total_ipp_volume_future=round(total_ipp_fut, 2),
        weighted_rrp_change_pct=round(rrp_change_weighted / total_vol, 4) if total_vol else None,
        weighted_ipp_change_pct=round(ipp_change_weighted / total_vol, 4) if total_vol else None,
    )


@router.get("/{product_id}", response_model=ProductWithCalc)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    p = await db.get(Product, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    np_devs = await _get_np_devs(db)
    calc = _build_calc(p, np_devs)
    return ProductWithCalc(**ProductRead.model_validate(p).model_dump(), calc=calc)


@router.patch("/{product_id}", response_model=ProductWithCalc)
async def update_product(
    product_id: int,
    body: ProductUpdate,
    db: AsyncSession = Depends(get_db),
):
    p = await db.get(Product, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(p, field, value)

    await db.commit()
    await db.refresh(p)

    np_devs = await _get_np_devs(db)
    calc = _build_calc(p, np_devs)
    return ProductWithCalc(**ProductRead.model_validate(p).model_dump(), calc=calc)


@router.post("/{product_id}/simulate", response_model=CalculationResult)
async def simulate(
    product_id: int,
    body: ProductUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Simulate price calculation with new inputs WITHOUT saving to DB."""
    p = await db.get(Product, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")

    # Temporarily overlay the new values
    temp_data = {k: v for k, v in body.model_dump(exclude_unset=True).items() if v is not None}
    np_devs = await _get_np_devs(db)

    # Create a temporary product-like object by merging
    class TempProduct:
        pass

    temp = TempProduct()
    for col in Product.__table__.columns:
        setattr(temp, col.name, getattr(p, col.name))
    for k, v in temp_data.items():
        setattr(temp, k, v)

    calc = _build_calc(temp, np_devs)
    return calc
