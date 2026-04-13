"""
Gradient Validation Engine — 4 layers.

Input: cycle_id
Output: list of violation dicts, written to gve_results table.

Layer 1 — Directional monotonicity (hard blocks / Critical)
  For each (upgrade_years, delivery_type, region):
    avg sales_cost per tier must follow tier_sequence order.

Layer 2 — Ratio bands (Critical / Warning)
  For each (tier, delivery_type, region):
    ratios between avg costs at different upgrade_years must stay in configured bands.

Layer 3 — Cross-geo structural consistency (Warning / Systemic)
  For each (tier, delivery_type, upgrade_years) structural ratio:
    if any region deviates >threshold from cross-region mean → Warning.
    if 3+ regions share the same violation → Systemic.

Layer 4 — Year-over-year drift (requires prior_baseline)
  For each (part_number, region):
    compare current sales_cost to prior baseline.
    >threshold change → flag (unresolved = blocks submission).
"""

from database import get_db, get_setting


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_tier_order(conn):
    """Return {tier_name: sort_order} dict."""
    rows = conn.execute("SELECT tier_name, sort_order FROM tier_sequence ORDER BY sort_order").fetchall()
    return {r["tier_name"]: r["sort_order"] for r in rows}


def _get_skus_with_prices(conn, cycle_id):
    """
    Return list of dicts:
      part_number, tier, base_warranty, upgrade_description, delivery_type,
      upgrade_years, region, sales_cost, channel_price, list_price
    Only rows where sales_cost is not null.
    """
    rows = conn.execute("""
        SELECT s.id as sku_id, s.part_number, s.tier, s.base_warranty,
               s.upgrade_description, s.delivery_type, s.upgrade_years,
               p.region, p.sales_cost, p.channel_price, p.list_price
        FROM skus s
        JOIN sku_prices p ON p.sku_id = s.id
        WHERE s.cycle_id = ? AND p.sales_cost IS NOT NULL AND p.sales_cost > 0
    """, (cycle_id,)).fetchall()
    return [dict(r) for r in rows]


def _group_avg(records, group_keys, value_key="sales_cost"):
    """Compute average of value_key grouped by group_keys tuple."""
    from collections import defaultdict
    buckets = defaultdict(list)
    for r in records:
        key = tuple(r[k] for k in group_keys)
        v = r[value_key]
        if v is not None:
            buckets[key].append(v)
    return {k: sum(v) / len(v) for k, v in buckets.items() if v}


# ---------------------------------------------------------------------------
# Layer 1 — Monotonicity
# ---------------------------------------------------------------------------

def run_layer1(conn, cycle_id, tier_order):
    violations = []
    records = _get_skus_with_prices(conn, cycle_id)

    if not tier_order:
        return [{
            "layer": 1, "severity": "Warning",
            "region": None, "tier": None, "upgrade_years": None, "part_number": None,
            "violation_type": "NO_TIER_SEQUENCE",
            "message": "No tier sequence configured. Layer 1 monotonicity check skipped. Please configure tier order in Settings."
        }]

    # avg cost per (upgrade_years, delivery_type, region, tier)
    avgs = _group_avg(records, ["upgrade_years", "delivery_type", "region", "tier"])

    # collect all (upgrade_years, delivery_type, region) combos
    combos = set((k[0], k[1], k[2]) for k in avgs)

    for (uyears, dtype, region) in combos:
        # get all tiers present for this combo, sorted by tier_order
        tier_costs = {}
        for (uy, dt, reg, tier), avg in avgs.items():
            if uy == uyears and dt == dtype and reg == region:
                if tier in tier_order:
                    tier_costs[tier] = avg

        if len(tier_costs) < 2:
            continue  # need at least 2 tiers to check monotonicity

        sorted_tiers = sorted(tier_costs.keys(), key=lambda t: tier_order[t])

        for i in range(len(sorted_tiers) - 1):
            lo_tier = sorted_tiers[i]
            hi_tier = sorted_tiers[i + 1]
            lo_cost = tier_costs[lo_tier]
            hi_cost = tier_costs[hi_tier]
            if lo_cost > hi_cost:
                violations.append({
                    "layer": 1,
                    "severity": "Critical",
                    "region": region,
                    "tier": f"{lo_tier} / {hi_tier}",
                    "upgrade_years": uyears,
                    "part_number": None,
                    "violation_type": "MONOTONICITY_BREACH",
                    "message": (
                        f"[{region}] {uyears}Y {dtype}: avg {lo_tier} cost "
                        f"(${lo_cost:.2f}) > avg {hi_tier} cost (${hi_cost:.2f}). "
                        f"Expected {lo_tier} ≤ {hi_tier}."
                    ),
                })

    return violations


# ---------------------------------------------------------------------------
# Layer 2 — Ratio bands
# ---------------------------------------------------------------------------

RATIO_PAIRS = [
    (3, 1, "ratio_band_3yr_1yr_min", "ratio_band_3yr_1yr_max"),
    (5, 3, "ratio_band_5yr_3yr_min", "ratio_band_5yr_3yr_max"),
    (4, 2, "ratio_band_4yr_2yr_min", "ratio_band_4yr_2yr_max"),
]


def run_layer2(conn, cycle_id):
    violations = []
    records = _get_skus_with_prices(conn, cycle_id)

    # avg cost per (tier, delivery_type, region, upgrade_years)
    avgs = _group_avg(records, ["tier", "delivery_type", "region", "upgrade_years"])

    for (hi_yr, lo_yr, min_key, max_key) in RATIO_PAIRS:
        band_min = float(get_setting(min_key, 1.0))
        band_max = float(get_setting(max_key, 9.0))

        # find all (tier, delivery_type, region) that have both years
        combos = set()
        for (tier, dtype, region, uy) in avgs:
            combos.add((tier, dtype, region))

        for (tier, dtype, region) in combos:
            hi_cost = avgs.get((tier, dtype, region, hi_yr))
            lo_cost = avgs.get((tier, dtype, region, lo_yr))

            if hi_cost is None or lo_cost is None or lo_cost == 0:
                continue

            ratio = hi_cost / lo_cost

            if ratio < band_min:
                violations.append({
                    "layer": 2,
                    "severity": "Critical",
                    "region": region,
                    "tier": tier,
                    "upgrade_years": hi_yr,
                    "part_number": None,
                    "violation_type": "RATIO_BELOW_FLOOR",
                    "message": (
                        f"[{region}] {tier} {dtype}: {hi_yr}yr/{lo_yr}yr ratio "
                        f"= {ratio:.2f}x — below floor of {band_min:.2f}x "
                        f"(avg {hi_yr}yr: ${hi_cost:.2f}, avg {lo_yr}yr: ${lo_cost:.2f})"
                    ),
                })
            elif ratio > band_max:
                violations.append({
                    "layer": 2,
                    "severity": "Warning",
                    "region": region,
                    "tier": tier,
                    "upgrade_years": hi_yr,
                    "part_number": None,
                    "violation_type": "RATIO_ABOVE_CEILING",
                    "message": (
                        f"[{region}] {tier} {dtype}: {hi_yr}yr/{lo_yr}yr ratio "
                        f"= {ratio:.2f}x — above ceiling of {band_max:.2f}x "
                        f"(avg {hi_yr}yr: ${hi_cost:.2f}, avg {lo_yr}yr: ${lo_cost:.2f})"
                    ),
                })

    return violations


# ---------------------------------------------------------------------------
# Layer 3 — Cross-geo consistency
# ---------------------------------------------------------------------------

def run_layer3(conn, cycle_id):
    violations = []
    records = _get_skus_with_prices(conn, cycle_id)
    threshold = float(get_setting("cross_geo_deviation_pct", 0.20))

    # For each (tier, delivery_type, upgrade_years) compute avg cost per region
    avgs = _group_avg(records, ["tier", "delivery_type", "upgrade_years", "region"])

    # Group into structural keys = (tier, delivery_type, upgrade_years)
    from collections import defaultdict
    struct_map = defaultdict(dict)  # struct_key → {region: avg_cost}
    for (tier, dtype, uyears, region), cost in avgs.items():
        struct_map[(tier, dtype, uyears)][region] = cost

    for struct_key, region_costs in struct_map.items():
        if len(region_costs) < 2:
            continue

        tier, dtype, uyears = struct_key
        mean_cost = sum(region_costs.values()) / len(region_costs)
        if mean_cost == 0:
            continue

        breaching_regions = []
        for region, cost in region_costs.items():
            deviation = abs(cost - mean_cost) / mean_cost
            if deviation > threshold:
                breaching_regions.append((region, cost, deviation))

        if not breaching_regions:
            continue

        is_systemic = len(breaching_regions) >= 3
        severity = "Systemic" if is_systemic else "Warning"

        for region, cost, deviation in breaching_regions:
            violations.append({
                "layer": 3,
                "severity": severity,
                "region": region,
                "tier": tier,
                "upgrade_years": uyears,
                "part_number": None,
                "violation_type": "SYSTEMIC_CROSS_GEO" if is_systemic else "CROSS_GEO_DEVIATION",
                "message": (
                    f"[{region}] {tier} {dtype} {uyears}Y: avg cost ${cost:.2f} deviates "
                    f"{deviation:.0%} from cross-region mean ${mean_cost:.2f}."
                    + (" SYSTEMIC — same issue in 3+ regions, may indicate methodology error." if is_systemic else "")
                ),
            })

    return violations


# ---------------------------------------------------------------------------
# Layer 4 — Year-over-year drift
# ---------------------------------------------------------------------------

def run_layer4(conn, cycle_id):
    violations = []
    cell_threshold = float(get_setting("yoy_cell_change_pct", 0.25))
    geo_avg_threshold = float(get_setting("yoy_geo_avg_change_pct", 0.20))

    baseline_rows = conn.execute(
        "SELECT part_number, region, prior_sales_cost FROM prior_baseline WHERE cycle_id = ?",
        (cycle_id,)
    ).fetchall()

    if not baseline_rows:
        return []  # no baseline entered, skip

    # Build baseline dict: (part_number, region) → prior_cost
    baseline = {(r["part_number"], r["region"]): r["prior_sales_cost"] for r in baseline_rows}

    current_rows = conn.execute("""
        SELECT s.part_number, p.region, p.sales_cost
        FROM skus s JOIN sku_prices p ON p.sku_id = s.id
        WHERE s.cycle_id = ? AND p.sales_cost IS NOT NULL
    """, (cycle_id,)).fetchall()

    from collections import defaultdict
    geo_changes = defaultdict(list)  # region → list of pct changes

    for row in current_rows:
        key = (row["part_number"], row["region"])
        prior = baseline.get(key)
        if prior is None or prior == 0:
            continue

        current_cost = row["sales_cost"]
        pct_change = (current_cost - prior) / abs(prior)
        geo_changes[row["region"]].append(pct_change)

        if abs(pct_change) > cell_threshold:
            direction = "increased" if pct_change > 0 else "decreased"
            violations.append({
                "layer": 4,
                "severity": "Critical",
                "region": row["region"],
                "tier": None,
                "upgrade_years": None,
                "part_number": row["part_number"],
                "violation_type": "YOY_CELL_DRIFT",
                "message": (
                    f"[{row['region']}] {row['part_number']}: sales cost {direction} "
                    f"{abs(pct_change):.0%} vs prior cycle "
                    f"(${prior:.2f} → ${current_cost:.2f}). Written explanation required."
                ),
            })

    # Geo-level average check
    for region, changes in geo_changes.items():
        if not changes:
            continue
        avg_change = sum(changes) / len(changes)
        if abs(avg_change) > geo_avg_threshold:
            direction = "increased" if avg_change > 0 else "decreased"
            violations.append({
                "layer": 4,
                "severity": "Warning",
                "region": region,
                "tier": None,
                "upgrade_years": None,
                "part_number": None,
                "violation_type": "YOY_GEO_AVG_DRIFT",
                "message": (
                    f"[{region}] Geo-level average sales cost {direction} "
                    f"{abs(avg_change):.0%} vs prior cycle. Flag for Supply Chain review."
                ),
            })

    return violations


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_gve(cycle_id):
    """
    Run all 4 GVE layers for a cycle. Clears previous results, writes new ones.
    Returns summary dict.
    """
    conn = get_db()
    try:
        tier_order = _get_tier_order(conn)

        all_violations = []
        all_violations.extend(run_layer1(conn, cycle_id, tier_order))
        all_violations.extend(run_layer2(conn, cycle_id))
        all_violations.extend(run_layer3(conn, cycle_id))
        all_violations.extend(run_layer4(conn, cycle_id))

        # Clear previous GVE results for this cycle
        conn.execute("DELETE FROM gve_results WHERE cycle_id = ?", (cycle_id,))

        # Insert new results
        for v in all_violations:
            conn.execute("""
                INSERT INTO gve_results
                  (cycle_id, layer, severity, region, tier, upgrade_years,
                   part_number, violation_type, message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cycle_id, v["layer"], v["severity"], v.get("region"),
                v.get("tier"), v.get("upgrade_years"), v.get("part_number"),
                v["violation_type"], v["message"],
            ))

        conn.commit()

        counts = {"Critical": 0, "Warning": 0, "Systemic": 0}
        for v in all_violations:
            s = v["severity"]
            if s in counts:
                counts[s] += 1

        # Determine GVE status
        if counts["Critical"] > 0:
            status = "Blocked"
        elif counts["Systemic"] > 0:
            status = "Systemic"
        elif all_violations:
            status = "Warnings"
        else:
            status = "Clear"

        return {
            "status": status,
            "total": len(all_violations),
            "counts": counts,
        }
    finally:
        conn.close()
