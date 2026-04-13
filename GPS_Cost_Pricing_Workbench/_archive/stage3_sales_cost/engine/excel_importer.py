"""
Excel and CSV import engine for GPS Pricing Workbench Stage 3.

Supports:
  - parse_excel_file(filepath)  → {skus, catalogs, rules}
  - import_from_excel(filepath, cycle_id, imported_by)  → summary dict
  - import_skus_from_csv(csv_text_or_path, cycle_id, imported_by) → summary dict
"""

import csv
import io
import json
import os
import re
from datetime import datetime, date

import database

# ---------------------------------------------------------------------------
# Column name → SKU field mapping
# ---------------------------------------------------------------------------

SKU_COLUMN_MAP = {
    'Service PN':                           'service_pn',
    'Service PN Short Description':         'short_description',
    'Service PN Sales& Marketing Description': 'sm_description',
    'OH ID':                                'oh_id',
    'OH Name':                              'oh_name',
    'Type of Service':                      'type_of_service',
    'Sub-Type of Service':                  'sub_type_of_service',
    'Offering Type':                        'offering_type',
    'Standard Cost ( Base Cost )':          'psc_value',
    'Currency':                             'currency',
    'Sales Cost Source':                    'sales_cost_source',
    'GEO':                                  'geo',
    'Country':                              'country',
    'Service Tier':                         'service_tier',
    'Sub Service Tier':                     'sub_service_tier',
    'Compatible MT':                        'compatible_mt',
    'SDF Code':                             'sdf_code',
    'SDF Code Short Description':           'sdf_short_description',
    'SDF Code Long Description':            'sdf_long_description',
    'Service Term':                         'service_term',
    'Unit':                                 'unit',
    'Service Availability Time':            'service_availability_time',
    'Service Response Time':                'service_response_time',
    'Service Delivery Type':                'service_delivery_type',
    'Included Premier Service':             'included_premier_service',
    'Premier Service Type':                 'premier_service_type',
    'Included Protection Service':          'included_adp',
    'Included KYD Service':                 'included_kyd',
    'Included SBTY Service':                'included_sbty',
    'Included ISE Service':                 'included_ise',
    'Included TI CRU Service':              'included_ticru',
}

# Columns that should be skipped (not imported from Excel, will be calculated)
_SKIP_COLUMNS = {'Sales Cost'}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_str(val) -> str | None:
    """Convert any value to a stripped string or None."""
    if val is None:
        return None
    if isinstance(val, float):
        import math
        if math.isnan(val):
            return None
    if isinstance(val, (date, datetime)):
        return val.isoformat()
    s = str(val).strip()
    return s if s else None


def _safe_float(val) -> float | None:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        import math
        if isinstance(val, float) and math.isnan(val):
            return None
        return float(val)
    s = str(val).strip().replace('%', '').replace(',', '')
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _parse_date(val) -> str | None:
    if val is None:
        return None
    if isinstance(val, (date, datetime)):
        return val.strftime('%Y-%m-%d')
    s = str(val).strip()
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return s if s else None


def _parse_ratio(val) -> float:
    """Convert a ratio/percentage string to a decimal float (e.g. '20%' → 0.20)."""
    if val is None:
        return 0.0
    s = str(val).strip()
    if s.endswith('%'):
        try:
            return float(s[:-1]) / 100.0
        except ValueError:
            return 0.0
    try:
        f = float(s)
        # If it looks like a percentage (>1), divide by 100
        if abs(f) > 1.0:
            return f / 100.0
        return f
    except (ValueError, TypeError):
        return 0.0


def _normalize_service_term(val) -> str | None:
    """Keep service term as a string representation."""
    if val is None:
        return None
    if isinstance(val, float):
        import math
        if math.isnan(val):
            return None
        return str(int(val))
    if isinstance(val, int):
        return str(val)
    return str(val).strip() or None


# ---------------------------------------------------------------------------
# SKU row normalisation
# ---------------------------------------------------------------------------

def _build_sku_row(col_to_field: dict, row_dict: dict) -> dict | None:
    """
    Map a raw row dict (col_name → value) to a SKU field dict.
    Returns None if the row appears empty (no service_pn).
    currency_first_col_index tracks that the first 'Currency' column wins.
    """
    sku = {}
    currency_seen = False

    for col_name, raw_val in row_dict.items():
        col_name_stripped = str(col_name).strip()
        if col_name_stripped in _SKIP_COLUMNS:
            continue

        if col_name_stripped == 'Currency':
            if not currency_seen:
                sku['currency'] = _safe_str(raw_val)
                currency_seen = True
            continue

        field = SKU_COLUMN_MAP.get(col_name_stripped)
        if field is None:
            continue

        if field == 'psc_value':
            sku[field] = _safe_float(raw_val)
        elif field == 'service_term':
            sku[field] = _normalize_service_term(raw_val)
        else:
            sku[field] = _safe_str(raw_val)

    if not sku.get('service_pn'):
        return None
    return sku


# ---------------------------------------------------------------------------
# Excel parsing
# ---------------------------------------------------------------------------

def _parse_sku_sheet(ws) -> list:
    """
    Parse 'Maintenance and Search UI' sheet.
    Row 1 = instructions, Row 2 = headers, Row 3+ = data.
    openpyxl is 1-indexed.
    """
    skus = []
    headers = []

    for row_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if row_idx == 1:
            continue  # instructions row
        if row_idx == 2:
            headers = [str(c).strip() if c is not None else '' for c in row]
            continue
        # data rows
        if all(c is None for c in row):
            continue
        row_dict = {headers[i]: row[i] for i in range(min(len(headers), len(row)))}
        sku = _build_sku_row(SKU_COLUMN_MAP, row_dict)
        if sku:
            skus.append(sku)

    return skus


def _parse_catalog_sheet(ws) -> list:
    """
    Parse 'Custom Uplift Factors Catalog' sheet.
    Catalog blocks start at rows where col A (or B) contains 'Uplift Factors ID:'.
    """
    catalogs = []
    rows = list(ws.iter_rows(values_only=True))

    i = 0
    while i < len(rows):
        row = rows[i]
        # Detect block start: any cell in the row contains 'Uplift Factors ID'
        row_vals = [str(c).strip() if c is not None else '' for c in row]
        if any('Uplift Factors ID' in v for v in row_vals):
            catalog = {}
            # catalog_id in col B (index 1), description in col D (index 3)
            catalog['catalog_id'] = _safe_str(row[1] if len(row) > 1 else None)
            catalog['description'] = _safe_str(row[3] if len(row) > 3 else None)
            catalog['selected_factor_names'] = []

            i += 1
            factors_header_seen = False

            while i < len(rows):
                r = rows[i]
                rv = [str(c).strip() if c is not None else '' for c in r]

                # Blank row: end of block
                if all(v == '' for v in rv):
                    break

                a = rv[0] if rv else ''
                b = _safe_str(r[1] if len(r) > 1 else None)
                d = _safe_str(r[3] if len(r) > 3 else None)

                if 'Type of Service' in a:
                    catalog['type_of_service'] = b
                    catalog['geo'] = d
                elif 'Valid From' in a:
                    catalog['valid_from'] = _parse_date(b)
                    catalog['valid_to'] = _parse_date(d)
                elif 'Status' in a and 'status' not in catalog:
                    catalog['status'] = b or 'Draft'
                elif 'Available Uplift Factor List' in ' '.join(rv) or \
                     'Selected Uplift Factor List' in ' '.join(rv):
                    factors_header_seen = True
                elif factors_header_seen:
                    # Col C (index 2) contains selected factor names
                    c_val = _safe_str(r[2] if len(r) > 2 else None)
                    if c_val and c_val not in ('Selected Uplift Factor List',
                                               'Available Uplift Factor List',
                                               'Uplift Factor Name'):
                        catalog['selected_factor_names'].append(c_val)

                i += 1

            if catalog.get('catalog_id'):
                catalogs.append(catalog)
            continue

        i += 1

    return catalogs


def _parse_rules_sheet(ws) -> list:
    """
    Parse 'Customize Uplift Formula' sheet.
    Rule blocks start at rows containing 'Uplift Rule ID'.
    """
    rules = []
    rows = list(ws.iter_rows(values_only=True))

    # Load factor names for matching
    conn = database.get_db()
    try:
        factor_rows = conn.execute(
            "SELECT id, factor_name, technical_id FROM uplift_factor_definitions"
        ).fetchall()
    finally:
        conn.close()
    factor_name_map = {r['factor_name'].strip().lower(): dict(r) for r in factor_rows}

    i = 0
    while i < len(rows):
        row = rows[i]
        row_vals = [str(c).strip() if c is not None else '' for c in row]

        if any('Uplift Rule ID' in v for v in row_vals):
            rule = {}
            rule['rule_id'] = _safe_str(row[1] if len(row) > 1 else None)
            rule['description'] = _safe_str(row[3] if len(row) > 3 else None)
            rule['factors'] = []

            i += 1
            in_factor_rows = False
            current_factors = []

            while i < len(rows):
                r = rows[i]
                rv = [str(c).strip() if c is not None else '' for c in r]

                if all(v == '' for v in rv):
                    break

                a = rv[0] if rv else ''
                b = _safe_str(r[1] if len(r) > 1 else None)
                d = _safe_str(r[3] if len(r) > 3 else None)

                if 'Select Uplift Factor Catalog' in a:
                    rule['catalog_id_text'] = b
                elif 'Type of Service' in a:
                    rule['type_of_service'] = b
                    rule['geo'] = d
                elif 'Valid From' in a:
                    rule['valid_from'] = _parse_date(b)
                    rule['valid_to'] = _parse_date(d)
                elif 'Status' in a and 'status' not in rule:
                    rule['status'] = b or 'Draft'
                elif 'Uplift Factor Name' in a:
                    # Start of a factor grid — reset and collect
                    in_factor_rows = True
                    current_factors = []
                elif 'Uplift Formula' in a or 'Total Uplift' in a:
                    # End of factor rows for this section
                    if current_factors:
                        rule['factors'] = current_factors
                    in_factor_rows = False
                elif in_factor_rows:
                    factor_name_raw = a.strip()
                    if factor_name_raw:
                        fd = factor_name_map.get(factor_name_raw.lower())
                        if fd:
                            values_str = _safe_str(r[1] if len(r) > 1 else None) or ''
                            ratio_raw = _safe_str(r[2] if len(r) > 2 else None) or '0'
                            ratio = _parse_ratio(ratio_raw)
                            current_factors.append({
                                'factor_def_id': fd['id'],
                                'factor_name': fd['factor_name'],
                                'technical_id': fd['technical_id'],
                                'factor_values': values_str,
                                'uplift_ratio': ratio,
                            })

                i += 1

            # Finalise factors if we never hit an 'Uplift Formula' row
            if in_factor_rows and current_factors:
                rule['factors'] = current_factors

            if rule.get('rule_id'):
                rules.append(rule)
            continue

        i += 1

    return rules


def parse_excel_file(filepath: str) -> dict:
    """
    Parse the reference Excel file.
    Returns {"skus": [...], "catalogs": [...], "rules": [...], "errors": [...]}
    """
    try:
        import openpyxl
    except ImportError:
        return {"skus": [], "catalogs": [], "rules": [],
                "errors": ["openpyxl is not installed. Run: pip install openpyxl"]}

    errors = []
    skus = []
    catalogs = []
    rules = []

    try:
        wb = openpyxl.load_workbook(filepath, data_only=True)
    except Exception as exc:
        return {"skus": [], "catalogs": [], "rules": [],
                "errors": [f"Failed to open Excel file: {exc}"]}

    # Parse SKU sheet
    sku_sheet_names = ['Maintenance and Search UI', 'SKU Data', 'Service PNs']
    for sn in sku_sheet_names:
        if sn in wb.sheetnames:
            try:
                skus = _parse_sku_sheet(wb[sn])
            except Exception as exc:
                errors.append(f"Error parsing SKU sheet '{sn}': {exc}")
            break

    # Parse catalog sheet
    cat_sheet_names = ['Custom Uplift Factors Catalog', 'Uplift Catalogs', 'Catalogs']
    for sn in cat_sheet_names:
        if sn in wb.sheetnames:
            try:
                catalogs = _parse_catalog_sheet(wb[sn])
            except Exception as exc:
                errors.append(f"Error parsing catalog sheet '{sn}': {exc}")
            break

    # Parse rules sheet
    rule_sheet_names = ['Customize Uplift Formula', 'Uplift Rules', 'Rules']
    for sn in rule_sheet_names:
        if sn in wb.sheetnames:
            try:
                rules = _parse_rules_sheet(wb[sn])
            except Exception as exc:
                errors.append(f"Error parsing rules sheet '{sn}': {exc}")
            break

    return {"skus": skus, "catalogs": catalogs, "rules": rules, "errors": errors}


# ---------------------------------------------------------------------------
# Database import functions
# ---------------------------------------------------------------------------

def _upsert_skus(conn, cycle_id: int, skus: list, imported_by: str) -> tuple:
    """Insert/replace SKU rows. Returns (count, errors)."""
    count = 0
    errors = []
    now = datetime.utcnow().isoformat()

    for sku in skus:
        if not sku.get('service_pn'):
            continue
        try:
            conn.execute(
                """INSERT INTO service_pns
                   (cycle_id, service_pn, short_description, sm_description,
                    oh_id, oh_name, type_of_service, sub_type_of_service, offering_type,
                    psc_value, currency, sales_cost_source,
                    geo, country, service_tier, sub_service_tier, compatible_mt,
                    sdf_code, sdf_short_description, sdf_long_description,
                    service_term, unit, service_availability_time, service_response_time,
                    service_delivery_type, included_premier_service, premier_service_type,
                    included_adp, included_kyd, included_sbty, included_ise, included_ticru,
                    imported_at, imported_by)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(cycle_id, service_pn, country) DO UPDATE SET
                     short_description        = excluded.short_description,
                     sm_description           = excluded.sm_description,
                     oh_id                    = excluded.oh_id,
                     oh_name                  = excluded.oh_name,
                     type_of_service          = excluded.type_of_service,
                     sub_type_of_service      = excluded.sub_type_of_service,
                     offering_type            = excluded.offering_type,
                     psc_value                = excluded.psc_value,
                     currency                 = excluded.currency,
                     sales_cost_source        = excluded.sales_cost_source,
                     geo                      = excluded.geo,
                     service_tier             = excluded.service_tier,
                     sub_service_tier         = excluded.sub_service_tier,
                     compatible_mt            = excluded.compatible_mt,
                     sdf_code                 = excluded.sdf_code,
                     sdf_short_description    = excluded.sdf_short_description,
                     sdf_long_description     = excluded.sdf_long_description,
                     service_term             = excluded.service_term,
                     unit                     = excluded.unit,
                     service_availability_time = excluded.service_availability_time,
                     service_response_time    = excluded.service_response_time,
                     service_delivery_type    = excluded.service_delivery_type,
                     included_premier_service = excluded.included_premier_service,
                     premier_service_type     = excluded.premier_service_type,
                     included_adp             = excluded.included_adp,
                     included_kyd             = excluded.included_kyd,
                     included_sbty            = excluded.included_sbty,
                     included_ise             = excluded.included_ise,
                     included_ticru           = excluded.included_ticru,
                     imported_at              = excluded.imported_at,
                     imported_by              = excluded.imported_by""",
                (
                    cycle_id,
                    sku.get('service_pn'),
                    sku.get('short_description'),
                    sku.get('sm_description'),
                    sku.get('oh_id'),
                    sku.get('oh_name'),
                    sku.get('type_of_service'),
                    sku.get('sub_type_of_service'),
                    sku.get('offering_type'),
                    sku.get('psc_value'),
                    sku.get('currency'),
                    sku.get('sales_cost_source'),
                    sku.get('geo'),
                    sku.get('country'),
                    sku.get('service_tier'),
                    sku.get('sub_service_tier'),
                    sku.get('compatible_mt'),
                    sku.get('sdf_code'),
                    sku.get('sdf_short_description'),
                    sku.get('sdf_long_description'),
                    sku.get('service_term'),
                    sku.get('unit'),
                    sku.get('service_availability_time'),
                    sku.get('service_response_time'),
                    sku.get('service_delivery_type'),
                    sku.get('included_premier_service'),
                    sku.get('premier_service_type'),
                    sku.get('included_adp'),
                    sku.get('included_kyd'),
                    sku.get('included_sbty'),
                    sku.get('included_ise'),
                    sku.get('included_ticru'),
                    now,
                    imported_by,
                ),
            )
            count += 1
        except Exception as exc:
            errors.append(f"SKU {sku.get('service_pn')}: {exc}")

    return count, errors


def _upsert_catalogs(conn, catalogs: list, created_by: str) -> tuple:
    """Insert/update catalog rows and their factor links. Returns (count, errors)."""
    count = 0
    errors = []

    # Load factor definitions for name lookup
    factor_rows = conn.execute(
        "SELECT id, factor_name FROM uplift_factor_definitions"
    ).fetchall()
    factor_name_to_id = {r['factor_name'].strip().lower(): r['id'] for r in factor_rows}

    for cat in catalogs:
        cid = cat.get('catalog_id')
        if not cid:
            continue
        try:
            conn.execute(
                """INSERT INTO uplift_catalogs
                   (catalog_id, description, type_of_service, geo,
                    valid_from, valid_to, status, created_by)
                   VALUES (?,?,?,?,?,?,?,?)
                   ON CONFLICT(catalog_id) DO UPDATE SET
                     description     = excluded.description,
                     type_of_service = excluded.type_of_service,
                     geo             = excluded.geo,
                     valid_from      = excluded.valid_from,
                     valid_to        = excluded.valid_to,
                     status          = excluded.status""",
                (
                    cid,
                    cat.get('description'),
                    cat.get('type_of_service'),
                    cat.get('geo'),
                    cat.get('valid_from'),
                    cat.get('valid_to'),
                    cat.get('status', 'Draft'),
                    created_by,
                ),
            )
            # Get the DB id
            cat_row = conn.execute(
                "SELECT id FROM uplift_catalogs WHERE catalog_id = ?", (cid,)
            ).fetchone()
            if cat_row is None:
                continue
            cat_db_id = cat_row['id']

            # Insert selected factors
            for sort_idx, fname in enumerate(cat.get('selected_factor_names', [])):
                fid = factor_name_to_id.get(fname.strip().lower())
                if fid is None:
                    continue
                conn.execute(
                    """INSERT OR IGNORE INTO uplift_catalog_factors
                       (catalog_id, factor_def_id, sort_order)
                       VALUES (?, ?, ?)""",
                    (cat_db_id, fid, sort_idx),
                )

            count += 1
        except Exception as exc:
            errors.append(f"Catalog {cid}: {exc}")

    return count, errors


def _upsert_rules(conn, rules: list, created_by: str) -> tuple:
    """Insert/update rule rows and their factor lines. Returns (count, errors)."""
    count = 0
    errors = []

    for rule in rules:
        rid = rule.get('rule_id')
        if not rid:
            continue
        try:
            # Resolve catalog_id_text → catalog DB id
            cat_db_id = None
            cat_text = rule.get('catalog_id_text')
            if cat_text:
                cat_row = conn.execute(
                    "SELECT id FROM uplift_catalogs WHERE catalog_id = ?",
                    (cat_text.strip(),),
                ).fetchone()
                if cat_row:
                    cat_db_id = cat_row['id']

            conn.execute(
                """INSERT INTO uplift_rules
                   (rule_id, description, catalog_id, type_of_service, geo,
                    valid_from, valid_to, status, created_by)
                   VALUES (?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(rule_id) DO UPDATE SET
                     description     = excluded.description,
                     catalog_id      = excluded.catalog_id,
                     type_of_service = excluded.type_of_service,
                     geo             = excluded.geo,
                     valid_from      = excluded.valid_from,
                     valid_to        = excluded.valid_to,
                     status          = excluded.status""",
                (
                    rid,
                    rule.get('description'),
                    cat_db_id,
                    rule.get('type_of_service'),
                    rule.get('geo'),
                    rule.get('valid_from'),
                    rule.get('valid_to'),
                    rule.get('status', 'Draft'),
                    created_by,
                ),
            )
            rule_row = conn.execute(
                "SELECT id FROM uplift_rules WHERE rule_id = ?", (rid,)
            ).fetchone()
            if rule_row is None:
                continue
            rule_db_id = rule_row['id']

            # Clear existing factors and re-insert
            conn.execute(
                "DELETE FROM uplift_rule_factors WHERE rule_id = ?", (rule_db_id,)
            )
            for factor in rule.get('factors', []):
                fdef_id = factor.get('factor_def_id')
                if fdef_id is None:
                    continue
                conn.execute(
                    """INSERT OR IGNORE INTO uplift_rule_factors
                       (rule_id, factor_def_id, factor_values, uplift_ratio)
                       VALUES (?, ?, ?, ?)""",
                    (rule_db_id, fdef_id,
                     factor.get('factor_values', ''),
                     float(factor.get('uplift_ratio', 0.0))),
                )

            count += 1
        except Exception as exc:
            errors.append(f"Rule {rid}: {exc}")

    return count, errors


def import_from_excel(filepath: str, cycle_id: int, imported_by: str) -> dict:
    """
    Parse and import Excel file into the database.
    Returns summary: {skus_imported, catalogs_imported, rules_imported, errors}
    """
    parsed = parse_excel_file(filepath)
    errors = list(parsed.get('errors', []))

    conn = database.get_db()
    skus_imported = 0
    catalogs_imported = 0
    rules_imported = 0

    try:
        if parsed.get('catalogs'):
            ci, ce = _upsert_catalogs(conn, parsed['catalogs'], imported_by)
            catalogs_imported = ci
            errors.extend(ce)

        if parsed.get('rules'):
            ri, re_ = _upsert_rules(conn, parsed['rules'], imported_by)
            rules_imported = ri
            errors.extend(re_)

        if parsed.get('skus'):
            si, se = _upsert_skus(conn, cycle_id, parsed['skus'], imported_by)
            skus_imported = si
            errors.extend(se)

        conn.commit()
    except Exception as exc:
        errors.append(f"Import error: {exc}")
        try:
            conn.rollback()
        except Exception:
            pass
    finally:
        conn.close()

    return {
        "skus_imported": skus_imported,
        "catalogs_imported": catalogs_imported,
        "rules_imported": rules_imported,
        "errors": errors,
    }


def import_skus_from_csv(csv_text_or_path: str, cycle_id: int, imported_by: str) -> dict:
    """
    Import SKUs from CSV text or a CSV file path.
    Returns {skus_imported, catalogs_imported: 0, rules_imported: 0, errors}
    """
    errors = []

    # Determine if it's a file path or raw CSV text
    if os.path.isfile(csv_text_or_path):
        with open(csv_text_or_path, 'r', encoding='utf-8-sig') as f:
            csv_text = f.read()
    else:
        csv_text = csv_text_or_path

    try:
        reader = csv.DictReader(io.StringIO(csv_text))
        skus = []
        for row in reader:
            sku = _build_sku_row(SKU_COLUMN_MAP, row)
            if sku:
                skus.append(sku)
    except Exception as exc:
        return {
            "skus_imported": 0,
            "catalogs_imported": 0,
            "rules_imported": 0,
            "errors": [f"CSV parse error: {exc}"],
        }

    if not skus:
        return {
            "skus_imported": 0,
            "catalogs_imported": 0,
            "rules_imported": 0,
            "errors": ["No valid SKU rows found in CSV."],
        }

    conn = database.get_db()
    try:
        count, errs = _upsert_skus(conn, cycle_id, skus, imported_by)
        errors.extend(errs)
        conn.commit()
    except Exception as exc:
        errors.append(f"DB error: {exc}")
        count = 0
        try:
            conn.rollback()
        except Exception:
            pass
    finally:
        conn.close()

    return {
        "skus_imported": count,
        "catalogs_imported": 0,
        "rules_imported": 0,
        "errors": errors,
    }
