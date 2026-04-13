"""
Calculation and results routes.
Blueprint prefix: /api
"""

import csv
import io
from flask import Blueprint, jsonify, request, session, Response
import database
from engine.sales_cost_engine import run_cycle_calculation

calc_bp = Blueprint("calc", __name__)


def _require_login():
    if not session.get("username"):
        return jsonify({"error": "Not logged in"}), 401
    return None


@calc_bp.post("/api/cycles/<int:cycle_id>/calculate")
def calculate(cycle_id):
    err = _require_login()
    if err:
        return err

    conn = database.get_db()
    cycle = conn.execute("SELECT id FROM cycles WHERE id = ?", (cycle_id,)).fetchone()
    conn.close()
    if cycle is None:
        return jsonify({"error": "Cycle not found"}), 404

    username = session["username"]
    result = run_cycle_calculation(cycle_id, username)
    return jsonify(result)


@calc_bp.get("/api/cycles/<int:cycle_id>/results")
def get_results(cycle_id):
    err = _require_login()
    if err:
        return err

    geo = request.args.get("geo", "").strip()
    tos = request.args.get("type_of_service", "").strip()
    status_filter = request.args.get("status", "").strip()  # calculated | no_rule | no_psc
    page = max(1, int(request.args.get("page", 1) or 1))
    per_page = max(1, min(500, int(request.args.get("per_page", 50) or 50)))

    conn = database.get_db()
    try:
        cycle = conn.execute("SELECT id FROM cycles WHERE id = ?", (cycle_id,)).fetchone()
        if cycle is None:
            return jsonify({"error": "Cycle not found"}), 404

        where = ["cycle_id = ?"]
        params = [cycle_id]

        if geo:
            where.append("geo = ?")
            params.append(geo)
        if tos:
            where.append("type_of_service = ?")
            params.append(tos)
        if status_filter == "calculated":
            where.append("sales_cost IS NOT NULL AND sales_cost_source = 'Auto-Calculation'")
        elif status_filter == "no_rule":
            where.append("sales_cost_source = 'No Rule'")
        elif status_filter == "no_psc":
            where.append("psc_value IS NULL")

        where_clause = " AND ".join(where)
        total = conn.execute(
            f"SELECT COUNT(*) FROM service_pns WHERE {where_clause}", params
        ).fetchone()[0]

        offset = (page - 1) * per_page
        rows = conn.execute(
            f"""SELECT id, service_pn, short_description, type_of_service, geo, country,
                       service_tier, service_term, service_delivery_type,
                       psc_value, sales_cost, sales_cost_source,
                       uplift_ratio, uplift_formula, currency
                FROM service_pns
                WHERE {where_clause}
                ORDER BY geo, type_of_service, service_pn, country
                LIMIT ? OFFSET ?""",
            params + [per_page, offset],
        ).fetchall()

        # Summary aggregation
        summary_rows = conn.execute(
            f"""SELECT geo, type_of_service,
                       COUNT(*) as total,
                       SUM(CASE WHEN sales_cost IS NOT NULL AND sales_cost_source='Auto-Calculation' THEN 1 ELSE 0 END) as calculated,
                       SUM(CASE WHEN sales_cost_source='No Rule' THEN 1 ELSE 0 END) as no_rule,
                       SUM(CASE WHEN psc_value IS NULL THEN 1 ELSE 0 END) as no_psc,
                       AVG(CASE WHEN psc_value IS NOT NULL THEN psc_value END) as avg_psc,
                       AVG(CASE WHEN sales_cost IS NOT NULL THEN sales_cost END) as avg_sales_cost,
                       AVG(CASE WHEN uplift_ratio IS NOT NULL THEN uplift_ratio END) as avg_uplift
                FROM service_pns
                WHERE cycle_id = ?
                GROUP BY geo, type_of_service
                ORDER BY geo, type_of_service""",
            (cycle_id,),
        ).fetchall()

        return jsonify({
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
            "results": [dict(r) for r in rows],
            "summary": [dict(r) for r in summary_rows],
        })
    finally:
        conn.close()


@calc_bp.get("/api/cycles/<int:cycle_id>/results/export")
def export_results(cycle_id):
    err = _require_login()
    if err:
        return err

    conn = database.get_db()
    try:
        cycle = conn.execute(
            "SELECT id, name FROM cycles WHERE id = ?", (cycle_id,)
        ).fetchone()
        if cycle is None:
            return jsonify({"error": "Cycle not found"}), 404

        rows = conn.execute(
            """SELECT cycle_id, service_pn, short_description, sm_description,
                      oh_id, oh_name, type_of_service, sub_type_of_service,
                      offering_type, psc_value, currency, sales_cost,
                      sales_cost_source, uplift_formula, uplift_ratio,
                      geo, country, service_tier, sub_service_tier, compatible_mt,
                      sdf_code, sdf_short_description, sdf_long_description,
                      service_term, unit, service_availability_time,
                      service_response_time, service_delivery_type,
                      included_premier_service, premier_service_type,
                      included_adp, included_kyd, included_sbty, included_ise,
                      included_ticru, imported_at, imported_by
               FROM service_pns
               WHERE cycle_id = ?
               ORDER BY geo, type_of_service, service_pn, country""",
            (cycle_id,),
        ).fetchall()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "cycle_id", "service_pn", "short_description", "sm_description",
            "oh_id", "oh_name", "type_of_service", "sub_type_of_service",
            "offering_type", "psc_value", "currency", "sales_cost",
            "sales_cost_source", "uplift_formula", "uplift_ratio",
            "geo", "country", "service_tier", "sub_service_tier", "compatible_mt",
            "sdf_code", "sdf_short_description", "sdf_long_description",
            "service_term", "unit", "service_availability_time",
            "service_response_time", "service_delivery_type",
            "included_premier_service", "premier_service_type",
            "included_adp", "included_kyd", "included_sbty", "included_ise",
            "included_ticru", "imported_at", "imported_by",
        ])
        for r in rows:
            writer.writerow([
                r["cycle_id"], r["service_pn"], r["short_description"],
                r["sm_description"], r["oh_id"], r["oh_name"],
                r["type_of_service"], r["sub_type_of_service"], r["offering_type"],
                r["psc_value"], r["currency"], r["sales_cost"],
                r["sales_cost_source"], r["uplift_formula"], r["uplift_ratio"],
                r["geo"], r["country"], r["service_tier"], r["sub_service_tier"],
                r["compatible_mt"], r["sdf_code"], r["sdf_short_description"],
                r["sdf_long_description"], r["service_term"], r["unit"],
                r["service_availability_time"], r["service_response_time"],
                r["service_delivery_type"], r["included_premier_service"],
                r["premier_service_type"], r["included_adp"], r["included_kyd"],
                r["included_sbty"], r["included_ise"], r["included_ticru"],
                r["imported_at"], r["imported_by"],
            ])

        cycle_name = (cycle["name"] or "cycle").replace(" ", "_").replace("/", "-")
        filename = f"sales_cost_{cycle_name}.csv"

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    finally:
        conn.close()
