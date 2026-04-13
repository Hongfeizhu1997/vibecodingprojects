from flask import Blueprint, request, jsonify, session
from database import get_db, log_audit
from engine.gve_engine import run_gve
from engine.list_price_engine import compute_list_prices

bp = Blueprint("gve", __name__)


@bp.post("/api/cycles/<int:cycle_id>/run-gve")
def trigger_gve(cycle_id):
    username = session.get("username", "unknown")
    conn = get_db()
    cycle = conn.execute("SELECT status FROM cycles WHERE id = ?", (cycle_id,)).fetchone()
    conn.close()
    if not cycle:
        return jsonify({"error": "Cycle not found"}), 404
    if cycle["status"] == "submitted":
        return jsonify({"error": "Cycle is already submitted"}), 400

    summary = run_gve(cycle_id)
    log_audit(cycle_id, "gve_results", None, "gve_run", None,
              f"status={summary['status']} total={summary['total']}", username)
    return jsonify(summary)


@bp.post("/api/cycles/<int:cycle_id>/run-list-price")
def trigger_list_price(cycle_id):
    username = session.get("username", "unknown")
    violations = compute_list_prices(cycle_id, username)
    return jsonify({"ok": True, "violations": violations})


@bp.get("/api/cycles/<int:cycle_id>/gve-results")
def get_gve_results(cycle_id):
    layer = request.args.get("layer", type=int)
    severity = request.args.get("severity")
    region = request.args.get("region")
    unresolved_only = request.args.get("unresolved_only", "false").lower() == "true"

    conn = get_db()
    sql = "SELECT * FROM gve_results WHERE cycle_id = ?"
    params = [cycle_id]
    if layer:
        sql += " AND layer = ?"
        params.append(layer)
    if severity:
        sql += " AND severity = ?"
        params.append(severity)
    if region:
        sql += " AND region = ?"
        params.append(region)
    if unresolved_only:
        sql += " AND is_resolved = 0"
    sql += " ORDER BY severity DESC, layer, region, tier"

    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@bp.get("/api/cycles/<int:cycle_id>/gve-summary")
def get_gve_summary(cycle_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT severity, is_resolved, COUNT(*) as cnt
        FROM gve_results WHERE cycle_id = ?
        GROUP BY severity, is_resolved
    """, (cycle_id,)).fetchall()
    conn.close()

    summary = {}
    for r in rows:
        key = r["severity"]
        if key not in summary:
            summary[key] = {"total": 0, "resolved": 0, "unresolved": 0}
        summary[key]["total"] += r["cnt"]
        if r["is_resolved"]:
            summary[key]["resolved"] += r["cnt"]
        else:
            summary[key]["unresolved"] += r["cnt"]
    return jsonify(summary)


@bp.post("/api/gve-results/<int:result_id>/resolve")
def resolve_violation(result_id):
    username = session.get("username", "unknown")
    data = request.json
    explanation = data.get("explanation", "").strip()
    if not explanation:
        return jsonify({"error": "Explanation is required to resolve a violation"}), 400

    conn = get_db()
    row = conn.execute("SELECT * FROM gve_results WHERE id = ?", (result_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Not found"}), 404

    conn.execute("""
        UPDATE gve_results
        SET is_resolved = 1, explanation = ?, resolved_by = ?, resolved_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (explanation, username, result_id))
    conn.commit()
    log_audit(row["cycle_id"], "gve_results", result_id, "resolved",
              "0", "1", username, explanation)
    conn.close()
    return jsonify({"ok": True})


@bp.post("/api/gve-results/<int:result_id>/unresolve")
def unresolve_violation(result_id):
    username = session.get("username", "unknown")
    conn = get_db()
    row = conn.execute("SELECT cycle_id FROM gve_results WHERE id = ?", (result_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Not found"}), 404

    conn.execute("""
        UPDATE gve_results
        SET is_resolved = 0, explanation = NULL, resolved_by = NULL, resolved_at = NULL
        WHERE id = ?
    """, (result_id,))
    conn.commit()
    log_audit(row["cycle_id"], "gve_results", result_id, "unresolved", "1", "0", username)
    conn.close()
    return jsonify({"ok": True})
