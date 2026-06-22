from sqlalchemy import String, Float, Integer, Boolean, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class Product(Base):
    __tablename__ = "products"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # --- Product Identity (static, from SAP/KP1) ---
    material_10: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    material_13: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description_en: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description_de: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sales_org: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # --- Product Group Hierarchy ---
    pg3_current: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pg1_current: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pg2_current: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pg1_description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    pg2_description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    pg3_description: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # PG 2026 structure (may change)
    pg1_2026: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pg2_2026: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pg3_2026: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pg1_description_2026_en: Mapped[str | None] = mapped_column(String(200), nullable=True)
    pg2_description_2026_en: Mapped[str | None] = mapped_column(String(200), nullable=True)
    pg3_description_2026_en: Mapped[str | None] = mapped_column(String(200), nullable=True)
    pg_structure_change_2026: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # --- Discount Groups ---
    discount_group_current: Mapped[str | None] = mapped_column(String(20), nullable=True)
    discount_group_future: Mapped[str | None] = mapped_column(String(20), nullable=True)
    max_basic_discount_current: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_add_discount_current: Mapped[float | None] = mapped_column(Float, nullable=True)
    future_basic_discount: Mapped[float | None] = mapped_column(Float, nullable=True)
    future_add_discount: Mapped[float | None] = mapped_column(Float, nullable=True)
    bonus_sde: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Predecessor / Successor ---
    predecessor: Mapped[str | None] = mapped_column(String(20), nullable=True)
    successor: Mapped[str | None] = mapped_column(String(20), nullable=True)  # final_10_digit_replacement

    # --- Vehicle / Application Flags ---
    fg_pkw: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    fg_nkw: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    fg_krad: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    fg_motor: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    nicht_tecdoc: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    eznrart: Mapped[str | None] = mapped_column(String(10), nullable=True)
    special_case: Mapped[str | None] = mapped_column(String(200), nullable=True)
    product_key: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # --- ABC Classifications (imported from SAP/IPT) ---
    abc_sales: Mapped[str | None] = mapped_column(String(5), nullable=True)
    abc_qty: Mapped[str | None] = mapped_column(String(5), nullable=True)
    abc_vehicle_population: Mapped[str | None] = mapped_column(String(5), nullable=True)
    abc_vehicle_age: Mapped[str | None] = mapped_column(String(5), nullable=True)

    # --- Volume Data (imported from SAP) ---
    qty_ly_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    ipp_ly_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    qty_12m: Mapped[float | None] = mapped_column(Float, nullable=True)
    ipp_12m: Mapped[float | None] = mapped_column(Float, nullable=True)
    tgs_product_gc: Mapped[float | None] = mapped_column(Float, nullable=True)
    qty_base_unit: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- FEPAA & misc reference ---
    fepaa: Mapped[float | None] = mapped_column(Float, nullable=True)
    artikelstamm_nicht_relevant: Mapped[str | None] = mapped_column(String(10), nullable=True)
    hinweise_sms41: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Historical RRP prices (locked) ---
    rrp_01_2023: Mapped[float | None] = mapped_column(Float, nullable=True)
    rrp_04_2023: Mapped[float | None] = mapped_column(Float, nullable=True)
    rrp_07_2023: Mapped[float | None] = mapped_column(Float, nullable=True)
    rrp_10_2023: Mapped[float | None] = mapped_column(Float, nullable=True)
    rrp_01_2024: Mapped[float | None] = mapped_column(Float, nullable=True)
    rrp_04_2024: Mapped[float | None] = mapped_column(Float, nullable=True)
    rrp_07_2024: Mapped[float | None] = mapped_column(Float, nullable=True)
    rrp_10_2024: Mapped[float | None] = mapped_column(Float, nullable=True)
    rrp_01_2025: Mapped[float | None] = mapped_column(Float, nullable=True)
    rrp_04_2025: Mapped[float | None] = mapped_column(Float, nullable=True)
    rrp_07_2025: Mapped[float | None] = mapped_column(Float, nullable=True)
    rrp_10_2025: Mapped[float | None] = mapped_column(Float, nullable=True)
    rrp_current_01_2026: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- EDITABLE: Inputs set by product specialist ---
    rrp_future_04_2026: Mapped[float | None] = mapped_column(Float, nullable=True)
    np_platinum_lc: Mapped[float | None] = mapped_column(Float, nullable=True)  # current NP Platinum
    np_platinum_manual_override: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    reason_manual_override: Mapped[str | None] = mapped_column(Text, nullable=True)
    minimum_npp_eur: Mapped[float | None] = mapped_column(Float, nullable=True)
    maximum_npp_eur: Mapped[float | None] = mapped_column(Float, nullable=True)
    exception_flag: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ps_action: Mapped[str | None] = mapped_column(String(50), nullable=True)
    comment_rrp: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_np: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- NPP / IPP / Margin from Excel (imported formula results from SAP/IPT) ---
    npp_current_de21_imported: Mapped[float | None] = mapped_column(Float, nullable=True)
    npp_future_de21_imported: Mapped[float | None] = mapped_column(Float, nullable=True)
    ipp_final_current_imported: Mapped[float | None] = mapped_column(Float, nullable=True)
    ipp_final_future_imported: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_margin_imported: Mapped[float | None] = mapped_column(Float, nullable=True)
    new_margin_imported: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_violation_imported: Mapped[str | None] = mapped_column(String(50), nullable=True)
    future_violation_imported: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # --- Benchmark NPP (imported from external systems) ---
    npp_pl_intercars: Mapped[float | None] = mapped_column(Float, nullable=True)
    npp_autonet: Mapped[float | None] = mapped_column(Float, nullable=True)
    zk76_truck: Mapped[str | None] = mapped_column(String(20), nullable=True)
    npp_truck: Mapped[float | None] = mapped_column(Float, nullable=True)
    tender_pep_zk76_lkq: Mapped[str | None] = mapped_column(String(20), nullable=True)
    npp_lkq: Mapped[float | None] = mapped_column(Float, nullable=True)
    bonus_lkq: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Historical comments per price round (editable) ---
    comment_04_2023: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_07_2023: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_10_2023: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_01_2024: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_04_2024: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_07_2024: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_01_2025: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_04_2025: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_07_2025: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_10_2025: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_01_2026: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_04_2026: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- EU Target / PG corrections (reference, calculated) ---
    eu_target_price_increase: Mapped[float | None] = mapped_column(Float, nullable=True)
    change_of_discount_group: Mapped[str | None] = mapped_column(String(50), nullable=True)
    new_discount: Mapped[float | None] = mapped_column(Float, nullable=True)
    new_add_discount: Mapped[float | None] = mapped_column(Float, nullable=True)
    comment_pg_correction: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Adjusted volume (imported, 2025 data) ---
    ipp_volume_current_adj: Mapped[float | None] = mapped_column(Float, nullable=True)
    ipp_volume_future_adj: Mapped[float | None] = mapped_column(Float, nullable=True)
    rrp_volume_current_adj: Mapped[float | None] = mapped_column(Float, nullable=True)
    rrp_volume_future_adj: Mapped[float | None] = mapped_column(Float, nullable=True)
