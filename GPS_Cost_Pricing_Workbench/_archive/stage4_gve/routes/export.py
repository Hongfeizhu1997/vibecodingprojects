import csv
import io
from flask import Blueprint, Response, jsonify
from database import get_db

bp = Blueprint("export", __name__)


@bp.get("/api/cycles/<int:cycle_id>/export/skus.csv")
def export_skus_csv(cycle_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT s.part_number, s.tier, s.base_warranty, s.upgrade_description,
               s.delivery_type, s.upgrade_years,
               p.region, p.sales_cost, p.channel_price, p.list_price,
               p.computed_list_price_b2c, p.computed_quoted_floor_b2b
        FROM skus s JOIN sku_prices p ON p.sku_id = s.id
        WHERE s.cycle_id = ?
        ORDER BY s.tier, s.upgrade_years, s.part_number, p.region
    """, (cycle_id,)).fetchall()
    cycle = conn.execute("SELECT name FROM cycles WHERE id = ?", (cycle_id,)).fetchone()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Part Number", "Tier", "Base Warranty", "Upgrade", "Delivery Type",
        "Upgrade Years", "Region", "Sales Cost", "Channel Price", "List Price (Actual)",
        "Computed B2C List Price", "Computed B2B Floor Price"
    ])
    for r in rows:
        writer.writerow([
            r["part_number"], r["tier"], r["base_warranty"], r["upgrade_description"],
            r["delivery_type"], r["upgrade_years"], r["region"],
            r["sales_cost"], r["channel_price"], r["list_price"],
            r["computed_list_price_b2c"], r["computed_quoted_floor_b2b"]
        ])

    cycle_name = cycle["name"].replace(" ", "_") if cycle else str(cycle_id)
    filename = f"{cycle_name}_prices.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@bp.get("/api/cycles/<int:cycle_id>/export/gve-report.html")
def export_gve_html(cycle_id):
    conn = get_db()
    cycle = conn.execute("SELECT * FROM cycles WHERE id = ?", (cycle_id,)).fetchone()
    rows = conn.execute("""
        SELECT * FROM gve_results WHERE cycle_id = ?
        ORDER BY severity DESC, layer, region, tier
    """, (cycle_id,)).fetchall()
    conn.close()

    if not cycle:
        return jsonify({"error": "Not found"}), 404

    sev_color = {"Critical": "#dc3545", "Systemic": "#fd7e14", "Warning": "#ffc107"}

    html_rows = ""
    for r in rows:
        color = sev_color.get(r["severity"], "#6c757d")
        resolved_badge = (
            f'<span style="color:#198754">&#10003; Resolved by {r["resolved_by"]}</span>'
            if r["is_resolved"] else
            '<span style="color:#dc3545">Unresolved</span>'
        )
        explanation = r["explanation"] or ""
        html_rows += f"""
        <tr>
          <td>L{r['layer']}</td>
          <td style="color:{color};font-weight:600">{r['severity']}</td>
          <td>{r['region'] or ''}</td>
          <td>{r['tier'] or ''}</td>
          <td>{r['upgrade_years'] or ''}</td>
          <td>{r['part_number'] or ''}</td>
          <td>{r['message']}</td>
          <td>{resolved_badge}</td>
          <td>{explanation}</td>
        </tr>"""

    total = len(rows)
    unresolved = sum(1 for r in rows if not r["is_resolved"])
    status = "BLOCKED" if any(r["severity"] == "Critical" and not r["is_resolved"] for r in rows) else (
        "SYSTEMIC" if any(r["severity"] == "Systemic" and not r["is_resolved"] for r in rows) else (
            "WARNINGS" if unresolved else "CLEAR"
        )
    )
    status_color = {"BLOCKED": "#dc3545", "SYSTEMIC": "#fd7e14", "WARNINGS": "#ffc107", "CLEAR": "#198754"}

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>GVE Report — {cycle['name']}</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 30px; font-size: 13px; }}
  h1 {{ color: #333; }}
  .status {{ font-size: 1.4em; font-weight: bold; color: {status_color.get(status,'#333')}; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
  th {{ background: #343a40; color: #fff; padding: 8px 10px; text-align: left; }}
  td {{ padding: 7px 10px; border-bottom: 1px solid #dee2e6; vertical-align: top; }}
  tr:hover {{ background: #f8f9fa; }}
</style>
</head><body>
<h1>Gradient Validation Report</h1>
<p><b>Cycle:</b> {cycle['name']} &nbsp;|&nbsp; <b>Fiscal Year:</b> {cycle['fiscal_year']}
   &nbsp;|&nbsp; <b>Status:</b> <span class="status">{status}</span></p>
<p><b>Total violations:</b> {total} &nbsp;|&nbsp; <b>Unresolved:</b> {unresolved}</p>
<table>
<tr>
  <th>Layer</th><th>Severity</th><th>Region</th><th>Tier</th>
  <th>Yrs</th><th>Part #</th><th>Message</th><th>Status</th><th>Explanation</th>
</tr>
{html_rows}
</table>
</body></html>"""

    cycle_name = cycle["name"].replace(" ", "_")
    return Response(
        html,
        mimetype="text/html",
        headers={"Content-Disposition": f'attachment; filename="GVE_{cycle_name}.html"'}
    )
