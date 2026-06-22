"""
Excel importer: reads the .xlsb price list and populates the SQLite database.
Works by first converting via LibreOffice to ODS/CSV, then parsing the XML.
"""
import zipfile
import xml.etree.ElementTree as ET
import subprocess
import os
import re
import logging
from pathlib import Path
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, text

from app.models.product import Product
from app.models.reference import NpClassDeviation, DiscountGroup, EuTargetIncrease

logger = logging.getLogger(__name__)

NS = {
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
}


def _convert_to_ods(xlsb_path: str) -> str:
    """Convert .xlsb to .ods using LibreOffice headless."""
    out_dir = str(Path(xlsb_path).parent)
    result = subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "ods", xlsb_path, "--outdir", out_dir],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")
    stem = Path(xlsb_path).stem
    ods_path = str(Path(out_dir) / f"{stem}.ods")
    if not os.path.exists(ods_path):
        raise FileNotFoundError(f"ODS output not found: {ods_path}")
    return ods_path


def _parse_ods(ods_path: str) -> dict[str, list[list[str]]]:
    """Parse ODS file and return dict of sheet_name → list of rows (list of cell strings)."""
    sheets: dict[str, list[list[str]]] = {}

    with zipfile.ZipFile(ods_path, "r") as z:
        content = z.read("content.xml").decode("utf-8", errors="replace")

    root = ET.fromstring(content)
    for sheet in root.findall(".//table:table", NS):
        name = sheet.get("{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name", "")
        rows_data: list[list[str]] = []
        for row_idx, row_el in enumerate(sheet.findall("table:table-row", NS)):
            row: list[str] = []
            # For header rows (rows 0-1), always use display text
            use_raw = row_idx > 1
            for cell in row_el.findall("table:table-cell", NS):
                repeat = cell.get(
                    "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}number-columns-repeated"
                )
                # Prefer raw numeric value for data rows (avoids currency/locale formatting)
                raw_val = cell.get("{urn:oasis:names:tc:opendocument:xmlns:office:1.0}value") if use_raw else None
                if raw_val is not None:
                    val = raw_val
                else:
                    texts = cell.findall(".//text:p", NS)
                    val = " ".join(t.text or "" for t in texts if t.text).strip()
                count = int(repeat) if repeat else 1
                # Only expand repeats up to reasonable limit to avoid memory bloat
                if val == "" and count > 50:
                    count = 1
                row.extend([val] * count)
            rows_data.append(row)
        sheets[name] = rows_data
    return sheets


def _float(val: str) -> Optional[float]:
    if not val:
        return None
    # Strip currency symbols, spaces, and percentage signs
    cleaned = val.strip()
    cleaned = cleaned.replace("€", "").replace("$", "").replace("%", "").strip()
    # Handle German number format: "1.234,56" → "1234.56"
    # and English format: "1,234.56" → "1234.56"
    if "," in cleaned and "." in cleaned:
        # Determine which is thousands separator and which is decimal
        last_comma = cleaned.rfind(",")
        last_dot = cleaned.rfind(".")
        if last_comma > last_dot:
            # German: 1.234,56 → remove dots (thousands), comma is decimal
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            # English: 1,234.56 → remove commas (thousands)
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned and "." not in cleaned:
        # Could be German decimal: 6,70 → 6.70
        cleaned = cleaned.replace(",", ".")
    cleaned = cleaned.replace(" ", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _bool_flag(val: str) -> Optional[bool]:
    if not val:
        return None
    return val.strip().upper() in ("X", "TRUE", "1", "YES")


def _clean_text(val: str) -> Optional[str]:
    v = val.strip()
    return v if v else None


def _get(row: list[str], idx: int) -> str:
    if idx < len(row):
        return row[idx].strip()
    return ""


def _import_main_sheet(rows: list[list[str]]) -> list[Product]:
    """Parse main price list sheet (skip first 2 rows: summary + header)."""
    if len(rows) < 3:
        return []

    header_row = rows[1]

    # Build column index map from headers
    col_map: dict[str, int] = {}
    for i, h in enumerate(header_row):
        key = h.strip()
        if key:
            col_map[key] = i

    def col(row: list[str], name: str) -> str:
        idx = col_map.get(name)
        if idx is None:
            return ""
        return _get(row, idx)

    products = []
    for row in rows[2:]:
        mat10 = col(row, "Material 10")
        if not mat10 or mat10 == "Material 10":
            continue

        p = Product(
            material_10=mat10,
            material_13=_clean_text(col(row, "Material 13")),
            description_en=_clean_text(col(row, "Material Description EN")),
            description_de=_clean_text(col(row, "Material Description DE")),
            sales_org=_clean_text(col(row, "SalesOrg")),
            status=_clean_text(col(row, "Status")),

            # PG hierarchy
            pg3_current=_clean_text(col(row, "PG3 Current")),
            pg1_current=_clean_text(col(row, "PG1 Current")),
            pg2_current=_clean_text(col(row, "PG2 Current")),
            pg1_description=_clean_text(col(row, "PG1 Description")),
            pg2_description=_clean_text(col(row, "PG2 Description")),
            pg3_description=_clean_text(col(row, "PG3 Description")),
            pg1_2026=_clean_text(col(row, "PG1 2026")),
            pg2_2026=_clean_text(col(row, "PG2 2026")),
            pg3_2026=_clean_text(col(row, "PG3 2026")),
            pg1_description_2026_en=_clean_text(col(row, "PG1 Description 2026 EN")),
            pg2_description_2026_en=_clean_text(col(row, "PG2 Description 2026 EN")),
            pg3_description_2026_en=_clean_text(col(row, "PG3 Description 2026 EN")),
            pg_structure_change_2026=_clean_text(col(row, "Change 2026")),

            # Discounts
            discount_group_current=_clean_text(col(row, "Discount Group Current")),
            discount_group_future=_clean_text(col(row, "Discount Group Future")),
            max_basic_discount_current=_float(col(row, "Max Basic Discount Current")),
            max_add_discount_current=_float(col(row, "Max Add Discount Current")),
            future_basic_discount=_float(col(row, "Future Basic Discount")),
            future_add_discount=_float(col(row, "Future Add Discount")),
            bonus_sde=_float(col(row, "Bonus (SDE)")),

            # Predecessor / Successor
            predecessor=_clean_text(col(row, "Predecessor")),
            successor=_clean_text(col(row, "Final 10 digit replacement")),

            # Vehicle flags
            fg_pkw=_bool_flag(col(row, "FG_PKW")),
            fg_nkw=_bool_flag(col(row, "FG_NKW")),
            fg_krad=_bool_flag(col(row, "FG_KRAD")),
            fg_motor=_bool_flag(col(row, "FG_MOTOR")),
            nicht_tecdoc=_bool_flag(col(row, "NICHT_TECDOC")),
            eznrart=_clean_text(col(row, "EZNRART")),
            special_case=_clean_text(col(row, "special case")),
            product_key=_clean_text(col(row, "product key")),

            # ABC
            abc_sales=_clean_text(col(row, "ABC Sales")),
            abc_qty=_clean_text(col(row, "ABC Qty")),
            abc_vehicle_population=_clean_text(col(row, "ABC Vehicle Population")),

            # Volume
            qty_ly_total=_float(col(row, "Qty LY Total")),
            ipp_ly_total=_float(col(row, "IPP LY Total")),
            qty_12m=_float(col(row, "Qty 12M")),
            ipp_12m=_float(col(row, "IPP 12M")),

            # FEPAA / misc
            fepaa=_float(col(row, "FEPAA")),
            hinweise_sms41=_clean_text(col(row, "Hinweise SMS41-EU")),

            # Historical RRP
            rrp_01_2023=_float(col(row, "RRP Old LC 01-2023")),
            rrp_04_2023=_float(col(row, "RRP Old LC 04-2023")),
            rrp_07_2023=_float(col(row, "RRP Old LC 07-2023")),
            rrp_10_2023=_float(col(row, "RRP Old LC 10-2023")),
            rrp_01_2024=_float(col(row, "RRP Old LC 01-2024")),
            rrp_04_2024=_float(col(row, "RRP Old LC 04-2024")),
            rrp_07_2024=_float(col(row, "RRP Old LC 07-2024")),
            rrp_10_2024=_float(col(row, "RRP Old LC 10-2024")),
            rrp_01_2025=_float(col(row, "RRP Old LC 01-2025")),
            rrp_04_2025=_float(col(row, "RRP Old LC 04-2025")),
            rrp_07_2025=_float(col(row, "RRP Old LC 07-2025")),
            rrp_10_2025=_float(col(row, "RRP Old LC 10-2025")),
            rrp_current_01_2026=_float(col(row, "Current RRP 01-2026")),

            # EDITABLE price inputs
            rrp_future_04_2026=_float(col(row, "Future RRP 04-2026")),
            np_platinum_lc=_float(col(row, "NP Platinum LC")),
            np_platinum_manual_override=_bool_flag(col(row, "NP Platinum Manual Override")) or False,
            reason_manual_override=_clean_text(col(row, "Reason Manual Override")),
            minimum_npp_eur=_float(col(row, "Minimum NPP EUR")),
            maximum_npp_eur=_float(col(row, "Maximum NPP EUR")),
            exception_flag=_clean_text(col(row, "Exception")),
            ps_action=_clean_text(col(row, "PS")),
            comment_rrp=_clean_text(col(row, "Comment RRP")),
            comment_np=_clean_text(col(row, "Comment NP")),

            # NPP / IPP / Margin from Excel formula results (from SAP/IPT, pre-computed)
            npp_current_de21_imported=_float(col(row, "NPP Current DE21")),
            npp_future_de21_imported=_float(col(row, "NPP Future DE21")),
            ipp_final_current_imported=_float(col(row, "IPP FINAL Current")),
            ipp_final_future_imported=_float(col(row, "IPP FINAL Future")),
            current_margin_imported=_float(col(row, "Current Margin")),
            new_margin_imported=_float(col(row, "New Margin")),
            current_violation_imported=_clean_text(col(row, "Current Violation Check")),
            future_violation_imported=_clean_text(col(row, "Future Violation Check")),

            # Benchmarks
            npp_pl_intercars=_float(col(row, "NPP PL Intercars 072025")),
            npp_autonet=_float(col(row, "NPP Autonet 07-2025")),
            npp_truck=_float(col(row, "NPP Truck")),
            npp_lkq=_float(col(row, "NPP Tender/PEP/ZK76 LKQ")),
            zk76_truck=_clean_text(col(row, "ZK76 Truck")),

            # Historical comments
            comment_04_2023=_clean_text(col(row, "Kommentare aus der PL 042023")),
            comment_07_2023=_clean_text(col(row, "Kommentare aus der PL 072023")),
            comment_04_2024=_clean_text(col(row, "Comment 04-2024")),
            comment_07_2024=_clean_text(col(row, "Comment 07-2024")),
            comment_01_2025=_clean_text(col(row, "Comment 01-2025")),
            comment_04_2025=_clean_text(col(row, "Comment 04-2025")),
            comment_07_2025=_clean_text(col(row, "Comment 07-2025")),
            comment_10_2025=_clean_text(col(row, "Comment 10-2025")),
            comment_01_2026=_clean_text(col(row, "Comment 01-2026")),
            comment_04_2026=_clean_text(col(row, "Comment 04-2026")),

            # Volume adjusted
            ipp_volume_current_adj=_float(col(row, "IPP Volume Current Adjusted sales data 012025-122025")),
            ipp_volume_future_adj=_float(col(row, "IPP Volume Future Adjusted sales data 012025-122025")),
            rrp_volume_current_adj=_float(col(row, "RRP Volume Current Adjusted sales data 012025-122025")),
            rrp_volume_future_adj=_float(col(row, "RRP Volume Future Adjusted sales data 012025-122025")),
            tgs_product_gc=_float(col(row, "TGS Product (GC) 012025-122025")),
            qty_base_unit=_float(col(row, "QTY (Base Unit) 012025-122025")),
            bonus_lkq=_float(col(row, "Bonus LKQ")),
        )
        products.append(p)

    return products


def _import_np_deviations(rows: list[list[str]]) -> list[NpClassDeviation]:
    if len(rows) < 2:
        return []
    results = []
    # Headers: PG1 Code, NP Sprünge, Abweichung NP Bronze/Platinum, Silver/Platinum, Gold/Platinum, DGR, PG3 Des, Platinum, Gold...
    # Col 0: PG1 Code, Col 5: DGR, Col 2: Bronze deviation, Col 3: Silver deviation, Col 4: Gold deviation (all as %)
    for row in rows[1:]:
        pg1 = _get(row, 0)
        if not pg1:
            continue
        results.append(NpClassDeviation(
            pg1_code=pg1,
            dgr=_clean_text(_get(row, 5)),
            deviation_gold=_float(_get(row, 4)),
            deviation_silver=_float(_get(row, 3)),
            deviation_bronze=_float(_get(row, 2)),
        ))
    return results


def _import_discount_groups(rows: list[list[str]]) -> list[DiscountGroup]:
    if len(rows) < 2:
        return []
    results = []
    # Headers: ID, ID SRD, Rabattgr., CH1 Code, CH1 Desc, CH2 Code, CH2 Desc, CH3 Code, CH3 no-zero, CH3 Desc, ...
    # We need: discount group code (col 2), CH3 desc (col 9), max discounts (further right)
    header = rows[0]
    col_map: dict[str, int] = {h.strip(): i for i, h in enumerate(header) if h.strip()}

    for row in rows[1:]:
        dgr = _get(row, 2)
        if not dgr:
            continue
        results.append(DiscountGroup(
            discount_group_code=dgr,
            ch3_code=_clean_text(_get(row, 7)),
            ch3_description=_clean_text(_get(row, 9)),
            max_basic_discount=_float(col_map.get("Max Basic Discount") and _get(row, col_map["Max Basic Discount"]) or ""),
            max_add_discount=_float(col_map.get("Max Add Discount") and _get(row, col_map["Max Add Discount"]) or ""),
        ))
    return results


def _import_eu_targets(rows: list[list[str]], pg_level: str) -> list[EuTargetIncrease]:
    if len(rows) < 2:
        return []
    results = []
    for row in rows[1:]:
        pg_key = _get(row, 0)
        if not pg_key:
            continue
        results.append(EuTargetIncrease(
            pg_key=pg_key,
            pg_level=pg_level,
            pg_text=_clean_text(_get(row, 1)),
            sales_org=_clean_text(_get(row, 2)),
            pcr=_float(_get(row, 3)),
            par_04_2026=_float(_get(row, 4)),
        ))
    return results


async def import_excel(db: AsyncSession, xlsb_path: str, force: bool = False) -> dict:
    """Full import pipeline: convert → parse → insert into DB."""
    from sqlalchemy import select

    if not force:
        result = await db.execute(text("SELECT COUNT(*) FROM products"))
        count = result.scalar()
        if count and count > 0:
            return {"status": "skipped", "message": f"DB already has {count} products. Use force=true to reimport."}

    logger.info("Starting Excel import from %s", xlsb_path)

    # Convert to ODS
    ods_path = _convert_to_ods(xlsb_path)
    logger.info("Converted to ODS: %s", ods_path)

    # Parse all sheets
    sheets = _parse_ods(ods_path)
    logger.info("Parsed sheets: %s", list(sheets.keys()))

    # Clear existing data
    await db.execute(delete(Product))
    await db.execute(delete(NpClassDeviation))
    await db.execute(delete(DiscountGroup))
    await db.execute(delete(EuTargetIncrease))
    await db.commit()

    # Import main sheet
    main_sheet_name = next((k for k in sheets if "Lighting Technology" in k or "B_2" in k), None)
    if main_sheet_name:
        products = _import_main_sheet(sheets[main_sheet_name])
        db.add_all(products)
        await db.commit()
        logger.info("Imported %d products", len(products))
    else:
        logger.warning("Main sheet not found. Available: %s", list(sheets.keys()))
        products = []

    # Import reference sheets
    np_devs_sheet = next((k for k in sheets if "Spruenge" in k or "Spr" in k), None)
    if np_devs_sheet:
        np_devs = _import_np_deviations(sheets[np_devs_sheet])
        db.add_all(np_devs)
        await db.commit()

    disc_sheet = next((k for k in sheets if "Discount" in k or "MAX" in k), None)
    if disc_sheet:
        disc_groups = _import_discount_groups(sheets[disc_sheet])
        db.add_all(disc_groups)
        await db.commit()

    target_pg1 = next((k for k in sheets if "PG1" in k and "Target" in k), None)
    if target_pg1:
        targets = _import_eu_targets(sheets[target_pg1], "PG1")
        db.add_all(targets)
        await db.commit()

    target_pg2 = next((k for k in sheets if "PG2" in k and "Target" in k), None)
    if target_pg2:
        targets = _import_eu_targets(sheets[target_pg2], "PG2")
        db.add_all(targets)
        await db.commit()

    return {"status": "ok", "products_imported": len(products)}
