#!/usr/bin/env python3
"""
GPS Cost Pricing Workbench — Local HTTP Server
Serves static files + handles CSV master data persistence via POST API.
Usage: python3 server.py [port]
"""
import http.server
import json
import csv
import os
import io
import sys
from urllib.parse import urlparse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
ROOT = os.path.dirname(os.path.abspath(__file__))
MASTER_CSV = os.path.join(ROOT, "pricing_master.csv")

# ── CSV columns (in order) ──
COLUMNS = [
    "cycle_name", "completed_at",
    "service_pn", "country", "service_tier", "upgrade_years", "delivery_type",
    "aipc", "psc_value", "sales_cost",
    "gve_status",
    "list_price", "channel_price", "gp_percent",
    "gradient_status"
]


def ensure_master_csv():
    """Create master CSV with header if it doesn't exist."""
    if not os.path.exists(MASTER_CSV):
        with open(MASTER_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNS)


def read_master_csv():
    """Read all records from master CSV."""
    ensure_master_csv()
    records = []
    with open(MASTER_CSV, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records


def write_master_csv(records, fieldnames=None):
    """Write records to master CSV."""
    if fieldnames is None:
        fieldnames = COLUMNS
    with open(MASTER_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def upsert_record(new_record):
    """
    Upsert a record into master CSV.
    Key: (cycle_name, service_pn) — same PN in same cycle is an update.
    """
    records = read_master_csv()
    key_fields = ("cycle_name", "service_pn")

    # Find existing
    found = False
    for i, r in enumerate(records):
        if all(r.get(k) == new_record.get(k) for k in key_fields):
            # Merge: new fields overwrite old, keep old fields not in new
            r.update(new_record)
            found = True
            break

    if not found:
        records.append(new_record)

    write_master_csv(records, COLUMNS)
    return {"status": "ok", "action": "updated" if found else "created"}


class Handler(http.server.SimpleHTTPRequestHandler):
    """Custom handler: GET serves static files, POST /api/* handles data."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/save-master":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                return

            result = upsert_record(data)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            return

        elif parsed.path == "/api/load-master":
            records = read_master_csv()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(records).encode())
            return

        self.send_error(404, "API endpoint not found")


print(f"📊 GPS Pricing Workbench Server")
print(f"   Root: {ROOT}")
print(f"   URL:  http://localhost:{PORT}")
print(f"   API:  POST /api/save-master  |  GET /api/load-master")
print()

ensure_master_csv()
http.server.HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
