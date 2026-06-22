from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProductBase(BaseModel):
    material_10: str
    description_en: Optional[str] = None
    description_de: Optional[str] = None
    status: Optional[str] = None
    pg1_current: Optional[str] = None
    pg2_current: Optional[str] = None
    pg3_current: Optional[str] = None
    pg1_description: Optional[str] = None
    pg2_description: Optional[str] = None
    pg3_description: Optional[str] = None
    discount_group_current: Optional[str] = None
    discount_group_future: Optional[str] = None
    max_basic_discount_current: Optional[float] = None
    max_add_discount_current: Optional[float] = None
    future_basic_discount: Optional[float] = None
    future_add_discount: Optional[float] = None
    bonus_sde: Optional[float] = None
    predecessor: Optional[str] = None
    successor: Optional[str] = None
    abc_sales: Optional[str] = None
    abc_qty: Optional[str] = None
    abc_vehicle_population: Optional[str] = None
    qty_12m: Optional[float] = None
    ipp_12m: Optional[float] = None
    fg_pkw: Optional[bool] = None
    fg_nkw: Optional[bool] = None
    fg_krad: Optional[bool] = None
    fg_motor: Optional[bool] = None
    fepaa: Optional[float] = None
    hinweise_sms41: Optional[str] = None


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sales_org: Optional[str] = None
    material_13: Optional[str] = None
    eznrart: Optional[str] = None
    special_case: Optional[str] = None
    product_key: Optional[str] = None
    pg3_description: Optional[str] = None
    pg1_2026: Optional[str] = None
    pg2_2026: Optional[str] = None
    pg3_2026: Optional[str] = None
    pg_structure_change_2026: Optional[str] = None
    pg1_description_2026_en: Optional[str] = None
    pg2_description_2026_en: Optional[str] = None
    pg3_description_2026_en: Optional[str] = None

    # Historical RRP
    rrp_01_2023: Optional[float] = None
    rrp_04_2023: Optional[float] = None
    rrp_07_2023: Optional[float] = None
    rrp_10_2023: Optional[float] = None
    rrp_01_2024: Optional[float] = None
    rrp_04_2024: Optional[float] = None
    rrp_07_2024: Optional[float] = None
    rrp_10_2024: Optional[float] = None
    rrp_01_2025: Optional[float] = None
    rrp_04_2025: Optional[float] = None
    rrp_07_2025: Optional[float] = None
    rrp_10_2025: Optional[float] = None
    rrp_current_01_2026: Optional[float] = None

    # Editable price inputs
    rrp_future_04_2026: Optional[float] = None
    np_platinum_lc: Optional[float] = None
    np_platinum_manual_override: Optional[bool] = None
    reason_manual_override: Optional[str] = None
    minimum_npp_eur: Optional[float] = None
    maximum_npp_eur: Optional[float] = None
    exception_flag: Optional[str] = None
    ps_action: Optional[str] = None
    comment_rrp: Optional[str] = None
    comment_np: Optional[str] = None

    # Benchmarks
    npp_pl_intercars: Optional[float] = None
    npp_autonet: Optional[float] = None
    npp_truck: Optional[float] = None
    npp_lkq: Optional[float] = None
    zk76_truck: Optional[str] = None
    bonus_lkq: Optional[float] = None

    # Comments
    comment_04_2023: Optional[str] = None
    comment_07_2023: Optional[str] = None
    comment_04_2024: Optional[str] = None
    comment_07_2024: Optional[str] = None
    comment_01_2025: Optional[str] = None
    comment_04_2025: Optional[str] = None
    comment_07_2025: Optional[str] = None
    comment_10_2025: Optional[str] = None
    comment_01_2026: Optional[str] = None
    comment_04_2026: Optional[str] = None

    # Volume
    qty_ly_total: Optional[float] = None
    ipp_ly_total: Optional[float] = None
    ipp_volume_current_adj: Optional[float] = None
    ipp_volume_future_adj: Optional[float] = None
    rrp_volume_current_adj: Optional[float] = None
    rrp_volume_future_adj: Optional[float] = None


class ProductUpdate(BaseModel):
    """Only the editable fields the product specialist can change."""
    rrp_future_04_2026: Optional[float] = None
    np_platinum_lc: Optional[float] = None
    np_platinum_manual_override: Optional[bool] = None
    reason_manual_override: Optional[str] = None
    minimum_npp_eur: Optional[float] = None
    maximum_npp_eur: Optional[float] = None
    exception_flag: Optional[str] = None
    ps_action: Optional[str] = None
    comment_rrp: Optional[str] = None
    comment_np: Optional[str] = None
    comment_04_2026: Optional[str] = None
    hinweise_sms41: Optional[str] = None


class CalculationResult(BaseModel):
    material_10: str
    rrp_future_rounded: Optional[float] = None
    rrp_change_pct: Optional[float] = None
    ipp_current_rrp_based: Optional[float] = None
    ipp_current_np_based: Optional[float] = None
    ipp_final_current: Optional[float] = None
    ipp_future_rrp_based: Optional[float] = None
    ipp_future_np_based: Optional[float] = None
    ipp_final_future: Optional[float] = None
    ipp_change_pct: Optional[float] = None
    npp_current_de21: Optional[float] = None
    npp_future_de21: Optional[float] = None
    npp_change_pct: Optional[float] = None
    np_platinum_lc_future: Optional[float] = None
    np_gold_lc: Optional[float] = None
    np_silver_lc: Optional[float] = None
    np_bronze_lc: Optional[float] = None
    np_gold_lc_future: Optional[float] = None
    np_silver_lc_future: Optional[float] = None
    np_bronze_lc_future: Optional[float] = None
    deviation_intercars: Optional[float] = None
    deviation_autonet: Optional[float] = None
    deviation_truck: Optional[float] = None
    deviation_lkq: Optional[float] = None
    current_margin: Optional[float] = None
    new_margin: Optional[float] = None
    current_violation: str = "OK"
    future_violation: str = "OK"
    flag_ipp_change_above_10: bool = False
    flag_ipp_future_above_rrp: bool = False
    flag_minderrabatt: bool = False
    flag_min_npp_violation: bool = False
    flag_rotten_apple: bool = False
    ipp_volume_current: Optional[float] = None
    ipp_volume_future: Optional[float] = None
    rrp_at_alignment: Optional[float] = None
    rrp_ch_alignment: Optional[float] = None
    price_proposal_min_rrp: Optional[float] = None
    price_proposal_max_rrp: Optional[float] = None


class ProductWithCalc(ProductRead):
    calc: Optional[CalculationResult] = None


class ProductListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ProductWithCalc]


class SummaryStats(BaseModel):
    total_products: int
    active_products: int
    total_violations: int
    rotten_apples: int
    min_violations: int
    max_violations: int
    total_ipp_volume_current: float
    total_ipp_volume_future: float
    weighted_rrp_change_pct: Optional[float]
    weighted_ipp_change_pct: Optional[float]
