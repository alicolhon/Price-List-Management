"""
Core formula engine — replicates Excel calculation logic.

All prices are in local currency (EUR for DE21).
Discount rates are stored as percentages (e.g. 55.0 means 55%).
"""
from dataclasses import dataclass, field
from typing import Optional
import math


def _pct(val: Optional[float]) -> float:
    """Convert stored percentage (e.g. 55.0) to decimal (0.55)."""
    return (val or 0.0) / 100.0


def _safe(val: Optional[float], default: float = 0.0) -> float:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return default
    return float(val)


def _round2(val: Optional[float]) -> Optional[float]:
    if val is None:
        return None
    return round(val, 2)


@dataclass
class PriceInputs:
    """All editable + imported inputs needed for calculation."""
    # Product identity
    material_10: str = ""
    pg1_current: str = ""
    discount_group_current: str = ""
    discount_group_future: str = ""

    # Pre-computed values from Excel (SAP/IPT formula results)
    npp_current_imported: Optional[float] = None   # NPP Current DE21 from Excel
    npp_future_imported: Optional[float] = None    # NPP Future DE21 from Excel
    ipp_final_current_imported: Optional[float] = None
    ipp_final_future_imported: Optional[float] = None
    current_margin_imported: Optional[float] = None  # margin % as 0-1 (or raw %)
    new_margin_imported: Optional[float] = None
    current_violation_imported: Optional[str] = None  # raw text from Excel
    future_violation_imported: Optional[str] = None

    # Discount params
    max_basic_discount_current: Optional[float] = None   # %
    max_add_discount_current: Optional[float] = None     # %
    future_basic_discount: Optional[float] = None        # %
    future_add_discount: Optional[float] = None          # %
    bonus_sde: Optional[float] = None                    # %

    # Price inputs (editable by product specialist)
    rrp_current_01_2026: Optional[float] = None
    rrp_future_04_2026: Optional[float] = None
    np_platinum_lc: Optional[float] = None               # current NP Platinum
    np_platinum_manual_override: bool = False

    # Benchmark prices (imported)
    npp_pl_intercars: Optional[float] = None
    npp_autonet: Optional[float] = None
    npp_truck: Optional[float] = None
    npp_lkq: Optional[float] = None

    # Corridors
    minimum_npp_eur: Optional[float] = None
    maximum_npp_eur: Optional[float] = None

    # NP class deviation percentages (from Spruenge sheet, looked up by PG1+DGR)
    deviation_gold: Optional[float] = None    # %
    deviation_silver: Optional[float] = None  # %
    deviation_bronze: Optional[float] = None  # %

    # EU Target increase (from EU Target sheet)
    eu_target_price_increase: Optional[float] = None  # %


@dataclass
class PriceCalculation:
    """All calculated / formula results."""
    # RRP
    rrp_future_rounded: Optional[float] = None
    rrp_change_pct: Optional[float] = None

    # IPP Current
    ipp_current_rrp_based: Optional[float] = None
    ipp_current_np_based: Optional[float] = None
    ipp_final_current: Optional[float] = None

    # IPP Future
    ipp_future_rrp_based: Optional[float] = None
    ipp_future_np_based: Optional[float] = None
    ipp_final_future: Optional[float] = None
    ipp_change_pct: Optional[float] = None

    # NPP (net price point DE21)
    npp_current_de21: Optional[float] = None
    npp_future_de21: Optional[float] = None
    npp_change_pct: Optional[float] = None

    # NP future platinum (rounded)
    np_platinum_lc_future: Optional[float] = None
    np_platinum_lc_future_rounded: Optional[float] = None

    # NP tiers — current
    np_gold_lc: Optional[float] = None
    np_silver_lc: Optional[float] = None
    np_bronze_lc: Optional[float] = None

    # NP tiers — future
    np_gold_lc_future: Optional[float] = None
    np_silver_lc_future: Optional[float] = None
    np_bronze_lc_future: Optional[float] = None

    # Benchmark deviations
    deviation_intercars: Optional[float] = None
    deviation_autonet: Optional[float] = None
    deviation_truck: Optional[float] = None
    deviation_lkq: Optional[float] = None

    # Margin
    current_margin: Optional[float] = None
    new_margin: Optional[float] = None

    # Violation flags
    current_violation: str = "OK"   # "OK" | "MIN" | "MAX" | "ROTTEN_APPLE"
    future_violation: str = "OK"

    # Derived flags
    flag_ipp_change_above_10: bool = False
    flag_ipp_future_above_rrp: bool = False
    flag_minderrabatt: bool = False
    flag_min_npp_violation: bool = False
    flag_rotten_apple: bool = False

    # Volume impact
    ipp_volume_current: Optional[float] = None
    ipp_volume_future: Optional[float] = None
    rrp_volume_current: Optional[float] = None
    rrp_volume_future: Optional[float] = None

    # AT / CH alignment
    rrp_at_alignment: Optional[float] = None
    rrp_ch_alignment: Optional[float] = None

    # Price proposals (auto-suggestions)
    price_proposal_min_rrp: Optional[float] = None
    price_proposal_max_rrp: Optional[float] = None


# Constants for AT/CH alignment
AT_ALIGNMENT_FACTOR = 1.0      # identical to DE (can be parameterised)
CH_ALIGNMENT_FACTOR = 1.10     # NPP DE + 10%


def calculate(inputs: PriceInputs, qty_12m: Optional[float] = None) -> PriceCalculation:
    out = PriceCalculation()

    rrp_cur = _safe(inputs.rrp_current_01_2026)
    rrp_fut = _safe(inputs.rrp_future_04_2026, rrp_cur)

    # --- RRP ---
    out.rrp_future_rounded = _round2(rrp_fut)
    if rrp_cur and rrp_cur != 0:
        out.rrp_change_pct = (rrp_fut / rrp_cur) - 1.0
    else:
        out.rrp_change_pct = None

    # Effective discount rates
    basic_cur = _pct(inputs.max_basic_discount_current)
    add_cur = _pct(inputs.max_add_discount_current)
    basic_fut = _pct(inputs.future_basic_discount)
    add_fut = _pct(inputs.future_add_discount)
    bonus = _pct(inputs.bonus_sde)

    # --- IPP Current ---
    # Method 1: RRP × (1 - basic - add - bonus)  → worst case discount
    if rrp_cur:
        out.ipp_current_rrp_based = _round2(rrp_cur * (1 - basic_cur - add_cur - bonus))
    # Method 2: from NP Platinum (current)
    np_plat_cur = _safe(inputs.np_platinum_lc)
    if np_plat_cur:
        # NP Platinum is the floor — add back distribution margin factor
        # IPP based on NP = NP Platinum / (1 - bonus)  if bonus applies
        # Simplified: IPP_NP = NP_platinum (as-is — worst case means we use the higher)
        out.ipp_current_np_based = _round2(np_plat_cur)

    # FINAL = MAX(RRP-based, NP-based) — worst case for customer payment
    candidates_cur = [x for x in [out.ipp_current_rrp_based, out.ipp_current_np_based] if x is not None]
    out.ipp_final_current = max(candidates_cur) if candidates_cur else None

    # --- IPP Future ---
    if rrp_fut:
        out.ipp_future_rrp_based = _round2(rrp_fut * (1 - basic_fut - add_fut - bonus))

    # NP Platinum future = NP_platinum_lc × (1 + RRP_change_pct) unless manual override
    if np_plat_cur and not inputs.np_platinum_manual_override:
        if out.rrp_change_pct is not None:
            np_plat_fut = np_plat_cur * (1 + out.rrp_change_pct)
        else:
            np_plat_fut = np_plat_cur
        out.np_platinum_lc_future = _round2(np_plat_fut)
    elif inputs.np_platinum_manual_override and np_plat_cur:
        # Manual override: keep current NP value, don't scale with RRP
        out.np_platinum_lc_future = _round2(np_plat_cur)
    else:
        out.np_platinum_lc_future = None

    out.np_platinum_lc_future_rounded = _round2(out.np_platinum_lc_future)

    if out.np_platinum_lc_future:
        out.ipp_future_np_based = _round2(out.np_platinum_lc_future)

    candidates_fut = [x for x in [out.ipp_future_rrp_based, out.ipp_future_np_based] if x is not None]
    out.ipp_final_future = max(candidates_fut) if candidates_fut else None

    if out.ipp_final_current and out.ipp_final_current != 0 and out.ipp_final_future is not None:
        out.ipp_change_pct = (out.ipp_final_future / out.ipp_final_current) - 1.0
    else:
        out.ipp_change_pct = None

    # --- NPP DE21 ---
    # Current NPP: use imported SAP value (authoritative, can't derive without SAP conditions).
    if inputs.npp_current_imported is not None:
        out.npp_current_de21 = _round2(inputs.npp_current_imported)
    elif np_plat_cur and basic_cur:
        out.npp_current_de21 = _round2(np_plat_cur * (1 - basic_cur))

    # Future NPP: scale current NPP by RRP change ratio so user edits to RRP are reflected.
    # NPP scales proportionally with NP Platinum, which scales with RRP.
    if inputs.npp_current_imported is not None and out.rrp_change_pct is not None:
        out.npp_future_de21 = _round2(inputs.npp_current_imported * (1 + out.rrp_change_pct))
    elif inputs.npp_future_imported is not None:
        out.npp_future_de21 = _round2(inputs.npp_future_imported)
    elif out.np_platinum_lc_future and basic_fut:
        out.npp_future_de21 = _round2(out.np_platinum_lc_future * (1 - basic_fut))

    # Override IPP with imported values if our formula differs
    if inputs.ipp_final_current_imported is not None and out.ipp_final_current is None:
        out.ipp_final_current = _round2(inputs.ipp_final_current_imported)
    if inputs.ipp_final_future_imported is not None and out.ipp_final_future is None:
        out.ipp_final_future = _round2(inputs.ipp_final_future_imported)

    if out.npp_current_de21 and out.npp_current_de21 != 0 and out.npp_future_de21 is not None:
        out.npp_change_pct = (out.npp_future_de21 / out.npp_current_de21) - 1.0

    # --- NP Tiers (current) ---
    if np_plat_cur:
        dev_g = _pct(inputs.deviation_gold)
        dev_s = _pct(inputs.deviation_silver)
        dev_b = _pct(inputs.deviation_bronze)
        out.np_gold_lc = _round2(np_plat_cur * (1 + dev_g))
        out.np_silver_lc = _round2(np_plat_cur * (1 + dev_s))
        out.np_bronze_lc = _round2(np_plat_cur * (1 + dev_b))

    # --- NP Tiers (future) ---
    if out.np_platinum_lc_future:
        dev_g = _pct(inputs.deviation_gold)
        dev_s = _pct(inputs.deviation_silver)
        dev_b = _pct(inputs.deviation_bronze)
        out.np_gold_lc_future = _round2(out.np_platinum_lc_future * (1 + dev_g))
        out.np_silver_lc_future = _round2(out.np_platinum_lc_future * (1 + dev_s))
        out.np_bronze_lc_future = _round2(out.np_platinum_lc_future * (1 + dev_b))

    # --- Benchmark Deviations ---
    npp_de = out.npp_future_de21 or out.npp_current_de21
    if npp_de and npp_de != 0:
        if inputs.npp_pl_intercars:
            out.deviation_intercars = (inputs.npp_pl_intercars / npp_de) - 1.0
        if inputs.npp_autonet:
            out.deviation_autonet = (inputs.npp_autonet / npp_de) - 1.0
        if inputs.npp_truck:
            out.deviation_truck = (inputs.npp_truck / npp_de) - 1.0
        if inputs.npp_lkq:
            out.deviation_lkq = (inputs.npp_lkq / npp_de) - 1.0

    # --- Margin ---
    # Use imported margin from Excel (calculated from SAP purchase cost) when available.
    # The margin % in Excel is stored as a decimal (0.677 = 67.7%).
    if inputs.current_margin_imported is not None:
        m = inputs.current_margin_imported
        # Handle if stored as percentage (>1) vs decimal
        out.current_margin = m / 100.0 if m > 1.5 else m
    elif out.ipp_final_current and out.npp_current_de21 and out.npp_current_de21 != 0:
        out.current_margin = 1 - (out.ipp_final_current / out.npp_current_de21)

    if inputs.new_margin_imported is not None:
        m = inputs.new_margin_imported
        out.new_margin = m / 100.0 if m > 1.5 else m
    elif out.ipp_final_future and out.npp_future_de21 and out.npp_future_de21 != 0:
        out.new_margin = 1 - (out.ipp_final_future / out.npp_future_de21)

    # --- Violations ---
    # Use imported violation flags from Excel when available (pre-computed from SAP corridors).
    # Parse Excel violation strings to our enum values.
    def _parse_excel_violation(raw: Optional[str]) -> str:
        if not raw:
            return "OK"
        r = raw.strip().lower()
        if "rotten" in r or "apple" in r or "0%" in r:
            return "ROTTEN_APPLE"
        if "min" in r and "verletz" in r.lower():
            return "MIN"
        if "min" in r:
            return "MIN"
        if "max" in r:
            return "MAX"
        # "Keine Verletzung" = no violation
        if "keine" in r or "ok" in r or "no" in r:
            return "OK"
        return "OK"

    min_npp = _safe(inputs.minimum_npp_eur)
    max_npp = _safe(inputs.maximum_npp_eur)

    def _check_violation(npp: Optional[float], margin: Optional[float]) -> str:
        if npp is None:
            return "OK"
        if margin is not None and margin < 0:
            return "ROTTEN_APPLE"
        if min_npp and npp < min_npp:
            return "MIN"
        if max_npp and npp > max_npp:
            return "MAX"
        return "OK"

    # Always calculate violations dynamically using imported NPP/margin values.
    # The imported violation fields (cols 77/78 in Excel) contain numeric check values
    # (not violation text), so we derive violations from NPP corridor checks instead.
    out.current_violation = _check_violation(out.npp_current_de21, out.current_margin)
    out.future_violation = _check_violation(out.npp_future_de21, out.new_margin)

    # --- Derived flags ---
    if out.ipp_change_pct is not None:
        out.flag_ipp_change_above_10 = abs(out.ipp_change_pct) > 0.10
    if out.ipp_final_future and rrp_fut and rrp_fut != 0:
        out.flag_ipp_future_above_rrp = out.ipp_final_future > rrp_fut
    out.flag_min_npp_violation = out.future_violation in ("MIN", "ROTTEN_APPLE")
    out.flag_rotten_apple = out.future_violation == "ROTTEN_APPLE"

    # Minderrabatt: when net price pushes IPP above standard RRP-discount calc
    if out.ipp_future_np_based and out.ipp_future_rrp_based:
        out.flag_minderrabatt = out.ipp_future_np_based > out.ipp_future_rrp_based

    # --- Volume Impact ---
    qty = _safe(qty_12m)
    if out.ipp_final_current and qty:
        out.ipp_volume_current = _round2(out.ipp_final_current * qty)
    if out.ipp_final_future and qty:
        out.ipp_volume_future = _round2(out.ipp_final_future * qty)
    if rrp_cur and qty:
        out.rrp_volume_current = _round2(rrp_cur * qty)
    if rrp_fut and qty:
        out.rrp_volume_future = _round2(rrp_fut * qty)

    # --- AT / CH Alignment ---
    if npp_de:
        out.rrp_at_alignment = _round2(npp_de * AT_ALIGNMENT_FACTOR)
        out.rrp_ch_alignment = _round2(npp_de * CH_ALIGNMENT_FACTOR)

    # --- Price Proposals (auto-suggestions to fix violations) ---
    if min_npp and basic_fut:
        out.price_proposal_min_rrp = _round2(min_npp / (1 - basic_fut - add_fut - bonus))
    if max_npp and basic_fut:
        out.price_proposal_max_rrp = _round2(max_npp / (1 - basic_fut - add_fut - bonus))

    return out
