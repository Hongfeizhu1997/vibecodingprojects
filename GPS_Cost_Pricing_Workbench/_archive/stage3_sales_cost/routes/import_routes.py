"""
SKU import routes.
Blueprint prefix: /api
"""

import os
import tempfile
from flask import Blueprint, request, jsonify, session
import database
from engine.excel_importer import import_from_excel, import_skus_from_csv

import_bp = Blueprint("import", __name__)


def _require_login():
    if not session.get("username"):
        return jsonify({"error": "Not logged in"}), 401
    return None


@import_bp.post("/api/cycles/<int:cycle_id>/import")
def import_data(cycle_id):
    """
    Accept multipart file upload (.xlsx or .csv)
    OR JSON body {csv_text: '...'}
    Returns {skus_imported, catalogs_imported, rules_imported, errors}
    """
    err = _require_login()
    if err:
        return err

    username = session["username"]
    conn = database.get_db()
    cycle = conn.execute("SELECT id FROM cycles WHERE id = ?", (cycle_id,)).fetchone()
    conn.close()
    if cycle is None:
        return jsonify({"error": "Cycle not found"}), 404

    # --- Multipart file upload ---
    if "file" in request.files:
        f = request.files["file"]
        fname = (f.filename or "").lower()

        if fname.endswith(".xlsx"):
            # Write to temp file and parse
            suffix = ".xlsx"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp_path = tmp.name
                f.save(tmp_path)
            try:
                result = import_from_excel(tmp_path, cycle_id, username)
            finally:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
            return jsonify(result)

        elif fname.endswith(".csv"):
            try:
                csv_text = f.read().decode("utf-8-sig")
            except Exception as exc:
                return jsonify({"error": f"Could not read CSV file: {exc}"}), 400
            result = import_skus_from_csv(csv_text, cycle_id, username)
            return jsonify(result)

        else:
            return jsonify({"error": "Unsupported file type. Use .xlsx or .csv"}), 400

    # --- JSON body with csv_text ---
    body = request.get_json(force=True, silent=True) or {}
    csv_text = body.get("csv_text", "").strip()
    if csv_text:
        result = import_skus_from_csv(csv_text, cycle_id, username)
        return jsonify(result)

    return jsonify({
        "error": "No data provided. Send a file upload or JSON {csv_text: '...'}"
    }), 400


@import_bp.get("/api/cycles/<int:cycle_id>/skus")
def list_skus(cycle_id):
    """
    Return paginated list of SKUs for a cycle.
    Filters: ?geo=&type_of_service=
    Pagination: ?page=1&per_page=50
    """
    err = _require_login()
    if err:
        return err

    geo = request.args.get("geo", "").strip()
    tos = request.args.get("type_of_service", "").strip()
    page = max(1, int(request.args.get("page", 1) or 1))
    per_page = max(1, min(500, int(request.args.get("per_page", 50) or 50)))

    conn = database.get_db()
    try:
        where = ["cycle_id = ?"]
        params = [cycle_id]
        if geo:
            where.append("geo = ?")
            params.append(geo)
        if tos:
            where.append("type_of_service = ?")
            params.append(tos)

        where_clause = " AND ".join(where)

        total = conn.execute(
            f"SELECT COUNT(*) FROM service_pns WHERE {where_clause}", params
        ).fetchone()[0]

        offset = (page - 1) * per_page
        rows = conn.execute(
            f"""SELECT id, service_pn, short_description, type_of_service, geo,
                       country, service_tier, service_term, service_delivery_type,
                       psc_value, sales_cost, sales_cost_source, currency,
                       uplift_ratio, uplift_formula
                FROM service_pns
                WHERE {where_clause}
                ORDER BY service_pn, country
                LIMIT ? OFFSET ?""",
            params + [per_page, offset],
        ).fetchall()

        return jsonify({
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
            "skus": [dict(r) for r in rows],
        })
    finally:
        conn.close()


@import_bp.get("/api/cycles/<int:cycle_id>/skus/summary")
def skus_summary(cycle_id):
    """
    Return counts of SKUs grouped by geo + type_of_service.
    """
    err = _require_login()
    if err:
        return err

    conn = database.get_db()
    try:
        rows = conn.execute(
            """SELECT geo, type_of_service, COUNT(*) as count
               FROM service_pns
               WHERE cycle_id = ?
               GROUP BY geo, type_of_service
               ORDER BY geo, type_of_service""",
            (cycle_id,),
        ).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) FROM service_pns WHERE cycle_id = ?", (cycle_id,)
        ).fetchone()[0]
        return jsonify({
            "total": total,
            "by_geo_tos": [dict(r) for r in rows],
        })
    finally:
        conn.close()
