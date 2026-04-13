"""
Sales Cost Calculation Engine
Formula: Sales Cost = PSC × (1 + Total Uplift Ratio)
Total Uplift Ratio = sum of uplift_ratio for all matching rule factors.
"""

import json
import database

# ---------------------------------------------------------------------------
# Factor → SKU field mapping
# ---------------------------------------------------------------------------

FACTOR_FIELD_MAP = {
    'TYPESRV':   'type_of_service',
    'SUBTYPESRV':'sub_type_of_service',
    'GEO':       'geo',
    'COUNTRY':   'country',
    'SRVTIER':   'service_tier',
    'SUBSRVTIER':'sub_service_tier',
    'MT':        'compatible_mt',
    'SRVTERM':   'service_term',
    'SABTIME':   'service_availability_time',
    'RSPTIME':   'service_response_time',
    'SDTYPE':    'service_delivery_type',
    'ICPS':      'included_premier_service',
    'PSTYPE':    'premier_service_type',
    'ICADP':     'included_adp',
    'ICKYD':     'included_kyd',
    'ICSBTY':    'included_sbty',
    'ICISE':     'included_ise',
    'ICTICRU':   'included_ticru',
}


def calculate_sku(sku_dict: dict, rule_factors: list) -> tuple:
    """
    Calculate sales cost for a single SKU against a list of rule factor dicts.

    rule_factors: list of dicts with keys:
        technical_id, factor_name, factor_values (comma-sep string), uplift_ratio (float)

    Returns:
        (sales_cost: float, total_uplift_ratio: float, formula_json: str)
    """
    psc = sku_dict.get("psc_value")
    if psc is None or psc == 0:
        return (None, 0.0, "[]")

    total_ratio = 0.0
    formula_parts = []

    for rf in rule_factors:
        technical_id = rf.get("technical_id", "")
        sku_field = FACTOR_FIELD_MAP.get(technical_id)
        if sku_field is None:
            continue

        sku_value = sku_dict.get(sku_field)
        if sku_value is None:
            continue

        sku_val_str = str(sku_value).strip()
        raw_values = rf.get("factor_values") or ""
        allowed = [v.strip() for v in raw_values.split(",") if v.strip()]

        if sku_val_str in allowed:
            ratio = float(rf.get("uplift_ratio") or 0.0)
            total_ratio += ratio
            formula_parts.append({
                "factor": rf.get("factor_name", technical_id),
                "technical_id": technical_id,
                "sku_value": sku_val_str,
                "uplift_ratio": ratio,
            })

    sales_cost = float(psc) * (1.0 + total_ratio)
    return (sales_cost, total_ratio, json.dumps(formula_parts))


def run_cycle_calculation(cycle_id: int, calculated_by: str) -> dict:
    """
    Calculate Sales Cost for every service_pn in the cycle that has a psc_value.

    For each SKU:
      1. Find the active Released uplift rule matching (type_of_service, geo).
      2. Load the rule's factors with their technical_ids.
      3. Call calculate_sku to get sales_cost, total_uplift_ratio, formula_json.
      4. Update the service_pns row.

    Returns:
        {"calculated": int, "skipped": int, "errors": [str]}
    """
    errors = []
    calculated = 0
    skipped = 0

    conn = database.get_db()
    try:
        # Load all SKUs with a PSC value
        skus = conn.execute(
            """SELECT * FROM service_pns
               WHERE cycle_id = ? AND psc_value IS NOT NULL""",
            (cycle_id,),
        ).fetchall()

        if not skus:
            return {
                "calculated": 0,
                "skipped": 0,
                "errors": ["No SKUs with PSC values found for this cycle."],
            }

        # Load all Released rules once, keyed by (type_of_service, geo)
        rules = conn.execute(
            """SELECT id, rule_id, type_of_service, geo
               FROM uplift_rules
               WHERE status = 'Released'""",
        ).fetchall()

        # Build a lookup: (type_of_service, geo) → rule row
        # If multiple Released rules match the same scope, use the first found.
        rule_map = {}
        for r in rules:
            key = (
                (r["type_of_service"] or "").strip().lower(),
                (r["geo"] or "").strip().lower(),
            )
            if key not in rule_map:
                rule_map[key] = r

        # Preload rule factors for each rule we have
        rule_factors_cache = {}  # rule DB id → list of factor dicts

        def get_rule_factors(rule_db_id):
            if rule_db_id in rule_factors_cache:
                return rule_factors_cache[rule_db_id]
            factors = conn.execute(
                """SELECT urf.factor_def_id, urf.factor_values, urf.uplift_ratio,
                          ufd.technical_id, ufd.factor_name
                   FROM uplift_rule_factors urf
                   JOIN uplift_factor_definitions ufd
                     ON ufd.id = urf.factor_def_id
                   WHERE urf.rule_id = ?""",
                (rule_db_id,),
            ).fetchall()
            result = [dict(f) for f in factors]
            rule_factors_cache[rule_db_id] = result
            return result

        for sku in skus:
            sku_dict = dict(sku)
            tos = (sku_dict.get("type_of_service") or "").strip().lower()
            geo = (sku_dict.get("geo") or "").strip().lower()

            rule_row = rule_map.get((tos, geo))
            if rule_row is None:
                # No matching rule — mark as no rule
                conn.execute(
                    """UPDATE service_pns
                       SET sales_cost_source = 'No Rule',
                           sales_cost = NULL,
                           uplift_formula = NULL,
                           uplift_ratio = NULL
                       WHERE id = ?""",
                    (sku_dict["id"],),
                )
                skipped += 1
                continue

            rule_factors = get_rule_factors(rule_row["id"])

            try:
                sales_cost, total_ratio, formula_json = calculate_sku(sku_dict, rule_factors)
            except Exception as exc:
                errors.append(
                    f"Calculation error for SKU {sku_dict.get('service_pn')}: {exc}"
                )
                skipped += 1
                continue

            conn.execute(
                """UPDATE service_pns
                   SET sales_cost = ?,
                       sales_cost_source = 'Auto-Calculation',
                       uplift_ratio = ?,
                       uplift_formula = ?
                   WHERE id = ?""",
                (sales_cost, total_ratio, formula_json, sku_dict["id"]),
            )
            calculated += 1

        conn.commit()

    except Exception as exc:
        errors.append(f"Fatal engine error: {exc}")
        try:
            conn.rollback()
        except Exception:
            pass
    finally:
        conn.close()

    return {"calculated": calculated, "skipped": skipped, "errors": errors}
