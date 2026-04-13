from flask import Blueprint, request, jsonify, session
from database import get_db, log_audit

bp = Blueprint("cycles", __name__)


@bp.get("/api/cycles")
def list_cycles():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM cycles ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@bp.post("/api/cycles")
def create_cycle():
    data = request.json
    username = session.get("username", "unknown")
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO cycles (name, fiscal_year, created_by) VALUES (?, ?, ?)",
        (data["name"], data["fiscal_year"], username),
    )
    conn.commit()
    cycle_id = cur.lastrowid
    log_audit(cycle_id, "cycles", cycle_id, "status", None, "draft", username, "Cycle created")
    conn.close()
    return jsonify({"id": cycle_id}), 201


@bp.get("/api/cycles/<int:cycle_id>")
def get_cycle(cycle_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM cycles WHERE id = ?", (cycle_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Not found"}), 404
    return jsonify(dict(row))


@bp.post("/api/cycles/<int:cycle_id>/submit")
def submit_cycle(cycle_id):
    username = session.get("username", "unknown")
    conn = get_db()

    # Check no unresolved Critical GVE results
    unresolved = conn.execute("""
        SELECT COUNT(*) as cnt FROM gve_results
        WHERE cycle_id = ? AND severity = 'Critical' AND is_resolved = 0
    """, (cycle_id,)).fetchone()["cnt"]

    if unresolved > 0:
        conn.close()
        return jsonify({"error": f"{unresolved} unresolved Critical GVE violations must be resolved before submission."}), 400

    conn.execute("""
        UPDATE cycles SET status = 'submitted', submitted_at = CURRENT_TIMESTAMP, submitted_by = ?
        WHERE id = ?
    """, (username, cycle_id))
    conn.commit()
    log_audit(cycle_id, "cycles", cycle_id, "status", "draft", "submitted", username)
    conn.close()
    return jsonify({"ok": True})


@bp.get("/api/cycles/<int:cycle_id>/audit")
def get_audit(cycle_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM audit_log WHERE cycle_id = ? ORDER BY changed_at DESC",
        (cycle_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@bp.get("/api/cycles/<int:cycle_id>/matrix")
def get_matrix(cycle_id):
    """
    Return aggregated data for the matrix view.
    For each (tier, upgrade_years, delivery_type, region): avg sales_cost, avg channel_price, avg list_price, gve_status
    """
    conn = get_db()

    rows = conn.execute("""
        SELECT s.tier, s.upgrade_years, s.delivery_type,
               p.region, p.sales_cost, p.channel_price, p.list_price,
               p.computed_list_price_b2c, p.computed_quoted_floor_b2b
        FROM skus s JOIN sku_prices p ON p.sku_id = s.id
        WHERE s.cycle_id = ? AND p.sales_cost IS NOT NULL
        ORDER BY s.tier, s.upgrade_years, p.region
    """, (cycle_id,)).fetchall()

    gve_rows = conn.execute("""
        SELECT region, tier, upgrade_years, severity, is_resolved
        FROM gve_results WHERE cycle_id = ?
    """, (cycle_id,)).fetchall()

    tier_seq = conn.execute(
        "SELECT tier_name, sort_order FROM tier_sequence ORDER BY sort_order"
    ).fetchall()

    conn.close()

    # Build gve_status lookup: (region, tier, upgrade_years) → worst unresolved severity
    sev_rank = {"Critical": 3, "Systemic": 2, "Warning": 1}
    gve_status = {}
    for g in gve_rows:
        if g["is_resolved"]:
            continue
        key = (g["region"], g["tier"], g["upgrade_years"])
        current = gve_status.get(key, "")
        if sev_rank.get(g["severity"], 0) > sev_rank.get(current, 0):
            gve_status[key] = g["severity"]

    # Aggregate
    from collections import defaultdict
    buckets = defaultdict(lambda: {"sales_cost": [], "channel_price": [], "list_price": [],
                                    "b2c": [], "b2b": []})
    for r in rows:
        key = (r["tier"], r["upgrade_years"], r["delivery_type"], r["region"])
        if r["sales_cost"]:
            buckets[key]["sales_cost"].append(r["sales_cost"])
        if r["channel_price"]:
            buckets[key]["channel_price"].append(r["channel_price"])
        if r["list_price"]:
            buckets[key]["list_price"].append(r["list_price"])
        if r["computed_list_price_b2c"]:
            buckets[key]["b2c"].append(r["computed_list_price_b2c"])
        if r["computed_quoted_floor_b2b"]:
            buckets[key]["b2b"].append(r["computed_quoted_floor_b2b"])

    def avg(lst):
        return round(sum(lst) / len(lst), 2) if lst else None

    matrix = []
    for (tier, uyears, dtype, region), vals in buckets.items():
        status = gve_status.get((region, tier, uyears), "OK")
        matrix.append({
            "tier": tier,
            "upgrade_years": uyears,
            "delivery_type": dtype,
            "region": region,
            "avg_sales_cost": avg(vals["sales_cost"]),
            "avg_channel_price": avg(vals["channel_price"]),
            "avg_list_price": avg(vals["list_price"]),
            "avg_b2c": avg(vals["b2c"]),
            "avg_b2b": avg(vals["b2b"]),
            "sku_count": len(vals["sales_cost"]),
            "gve_status": status,
        })

    return jsonify({
        "matrix": matrix,
        "tier_sequence": [dict(r) for r in tier_seq],
    })


@bp.get("/api/cycles/<int:cycle_id>/skus")
def get_skus(cycle_id):
    """Return all SKUs with prices for a cycle, optionally filtered."""
    region = request.args.get("region")
    tier = request.args.get("tier")
    conn = get_db()

    sql = """
        SELECT s.id, s.part_number, s.tier, s.base_warranty,
               s.upgrade_description, s.delivery_type, s.upgrade_years,
               p.region, p.sales_cost, p.channel_price, p.list_price,
               p.computed_list_price_b2c, p.computed_quoted_floor_b2b
        FROM skus s JOIN sku_prices p ON p.sku_id = s.id
        WHERE s.cycle_id = ?
    """
    params = [cycle_id]
    if region:
        sql += " AND p.region = ?"
        params.append(region)
    if tier:
        sql += " AND s.tier = ?"
        params.append(tier)
    sql += " ORDER BY s.tier, s.upgrade_years, s.part_number, p.region"

    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])
