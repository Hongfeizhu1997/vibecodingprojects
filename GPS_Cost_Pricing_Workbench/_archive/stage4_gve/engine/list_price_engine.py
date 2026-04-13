"""
Stage 5 — List Price derivation.

B2C:  List Price = Sales Cost / (1 - GM%)
B2B:  Quoted Price Floor = Sales Cost * (1 + Markup%)

GM% and Markup% are configurable per tier in settings:
  gm_pct_<tier>     (fallback: gm_pct_default)
  markup_pct_<tier> (fallback: markup_pct_default)

Also checks:
  - Channel price floor: channel_price must be >= sales_cost
  - PFV benchmark: placeholder hook, fires if pfv_benchmarks data exists for the SKU+region

Returns per-sku-price updated values and a list of output violations.
"""

from database import get_db, get_setting


def _tier_setting(key_prefix, tier, default_key):
    """Get a tier-specific setting, falling back to default."""
    safe_tier = tier.lower().replace(" ", "_").replace("/", "_")
    val = get_setting(f"{key_prefix}_{safe_tier}")
    if val is None:
        val = get_setting(default_key, "0.30")
    return float(val)


def compute_list_prices(cycle_id, username):
    """
    Compute B2C and B2B list prices for all SKUs in a cycle.
    Writes results to sku_prices. Returns list of output violations.
    """
    conn = get_db()
    violations = []

    try:
        rows = conn.execute("""
            SELECT s.id as sku_id, s.tier, s.part_number,
                   p.id as price_id, p.region, p.sales_cost,
                   p.channel_price, p.list_price
            FROM skus s
            JOIN sku_prices p ON p.sku_id = s.id
            WHERE s.cycle_id = ? AND p.sales_cost IS NOT NULL AND p.sales_cost > 0
        """, (cycle_id,)).fetchall()

        for row in rows:
            tier = row["tier"]
            sales_cost = row["sales_cost"]
            channel_price = row["channel_price"]
            region = row["region"]
            part_number = row["part_number"]

            gm_pct = _tier_setting("gm_pct", tier, "gm_pct_default")
            markup_pct = _tier_setting("markup_pct", tier, "markup_pct_default")

            # B2C
            b2c = sales_cost / (1 - gm_pct) if gm_pct < 1 else None

            # B2B
            b2b = sales_cost * (1 + markup_pct)

            # Channel price check
            if channel_price is not None and channel_price < sales_cost:
                violations.append({
                    "type": "CHANNEL_BELOW_COST",
                    "severity": "Critical",
                    "region": region,
                    "part_number": part_number,
                    "message": (
                        f"[{region}] {part_number}: channel price ${channel_price:.2f} "
                        f"is below sales cost ${sales_cost:.2f}."
                    ),
                })

            # PFV check placeholder
            pfv_row = conn.execute(
                "SELECT pfv_price FROM pfv_benchmarks WHERE part_number = ? AND region = ?",
                (part_number, region)
            ).fetchone()
            if pfv_row and pfv_row["pfv_price"] and b2c and b2c > pfv_row["pfv_price"]:
                violations.append({
                    "type": "EXCEEDS_PFV",
                    "severity": "Warning",
                    "region": region,
                    "part_number": part_number,
                    "message": (
                        f"[{region}] {part_number}: computed B2C list price ${b2c:.2f} "
                        f"exceeds PFV benchmark ${pfv_row['pfv_price']:.2f}."
                    ),
                })

            conn.execute("""
                UPDATE sku_prices
                SET computed_list_price_b2c = ?,
                    computed_quoted_floor_b2b = ?
                WHERE id = ?
            """, (b2c, b2b, row["price_id"]))

        conn.commit()

    finally:
        conn.close()

    return violations
