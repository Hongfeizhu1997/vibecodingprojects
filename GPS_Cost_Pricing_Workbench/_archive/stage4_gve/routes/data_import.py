import os
import tempfile
from flask import Blueprint, request, jsonify, session
from database import get_db, log_audit
from engine.excel_parser import parse_excel

bp = Blueprint("data_import", __name__)

ALLOWED_EXT = {".xlsx", ".xls"}


@bp.post("/api/cycles/<int:cycle_id>/import")
def import_excel(cycle_id):
    username = session.get("username", "unknown")
    conn = get_db()

    cycle = conn.execute("SELECT * FROM cycles WHERE id = ?", (cycle_id,)).fetchone()
    if not cycle:
        conn.close()
        return jsonify({"error": "Cycle not found"}), 404
    if cycle["status"] == "submitted":
        conn.close()
        return jsonify({"error": "Cannot import into a submitted cycle"}), 400

    if "file" not in request.files:
        conn.close()
        return jsonify({"error": "No file provided"}), 400

    f = request.files["file"]
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        conn.close()
        return jsonify({"error": "Only .xlsx files are supported"}), 400

    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    try:
        f.save(tmp.name)
        tmp.close()
        result = parse_excel(tmp.name)
    finally:
        os.unlink(tmp.name)

    if result["errors"]:
        conn.close()
        return jsonify({"error": " | ".join(result["errors"])}), 400

    if not result["rows"]:
        conn.close()
        return jsonify({"error": "No data rows found in file"}), 400

    # Sync tier sequence: add any new tiers not yet in tier_sequence
    existing_tiers = {
        r["tier_name"]: r["sort_order"]
        for r in conn.execute("SELECT tier_name, sort_order FROM tier_sequence").fetchall()
    }
    max_order = max(existing_tiers.values(), default=0)
    new_tiers = []
    for tier in result["tiers_found"]:
        if tier not in existing_tiers:
            max_order += 10
            conn.execute(
                "INSERT OR IGNORE INTO tier_sequence (tier_name, sort_order) VALUES (?, ?)",
                (tier, max_order),
            )
            new_tiers.append(tier)

    # Clear existing SKUs/prices for this cycle and re-import
    sku_ids = [r["id"] for r in conn.execute(
        "SELECT id FROM skus WHERE cycle_id = ?", (cycle_id,)
    ).fetchall()]
    if sku_ids:
        conn.execute(
            f"DELETE FROM sku_prices WHERE sku_id IN ({','.join('?' * len(sku_ids))})",
            sku_ids,
        )
    conn.execute("DELETE FROM skus WHERE cycle_id = ?", (cycle_id,))

    sku_count = 0
    price_count = 0
    for row in result["rows"]:
        cur = conn.execute("""
            INSERT INTO skus (cycle_id, part_number, tier, base_warranty,
                              upgrade_description, delivery_type, upgrade_years)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            cycle_id, row["part_number"], row["tier"], row["base_warranty"],
            row["upgrade_description"], row["delivery_type"], row["upgrade_years"],
        ))
        sku_id = cur.lastrowid
        sku_count += 1

        for region, prices in row["prices"].items():
            if prices["sales_cost"] is None and prices["channel_price"] is None and prices["list_price"] is None:
                continue
            conn.execute("""
                INSERT INTO sku_prices (sku_id, region, sales_cost, channel_price, list_price)
                VALUES (?, ?, ?, ?, ?)
            """, (
                sku_id, region,
                prices["sales_cost"], prices["channel_price"], prices["list_price"],
            ))
            price_count += 1

    conn.commit()
    log_audit(cycle_id, "skus", None, "import", None,
              f"{sku_count} SKUs / {price_count} price records", username,
              f"Imported from {f.filename}")
    conn.close()

    return jsonify({
        "ok": True,
        "skus_imported": sku_count,
        "price_records": price_count,
        "regions": result["regions"],
        "tiers_found": result["tiers_found"],
        "new_tiers": new_tiers,
        "warnings": (
            ["New tiers detected: " + ", ".join(new_tiers) + ". Please verify their order in Settings → Tier Sequence."]
            if new_tiers else []
        ),
    })


@bp.get("/api/cycles/<int:cycle_id>/prior-baseline")
def get_baseline(cycle_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM prior_baseline WHERE cycle_id = ? ORDER BY part_number, region",
        (cycle_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@bp.post("/api/cycles/<int:cycle_id>/prior-baseline")
def save_baseline(cycle_id):
    """
    Accept JSON: {"entries": [{"part_number": ..., "region": ..., "prior_sales_cost": ...}]}
    Replaces all baseline entries for this cycle.
    """
    username = session.get("username", "unknown")
    data = request.json
    entries = data.get("entries", [])

    conn = get_db()
    conn.execute("DELETE FROM prior_baseline WHERE cycle_id = ?", (cycle_id,))
    for e in entries:
        conn.execute("""
            INSERT INTO prior_baseline (cycle_id, part_number, region, prior_sales_cost, entered_by)
            VALUES (?, ?, ?, ?, ?)
        """, (cycle_id, e["part_number"], e["region"], e["prior_sales_cost"], username))

    conn.commit()
    log_audit(cycle_id, "prior_baseline", None, "bulk_save",
              None, f"{len(entries)} entries", username)
    conn.close()
    return jsonify({"ok": True, "entries_saved": len(entries)})
