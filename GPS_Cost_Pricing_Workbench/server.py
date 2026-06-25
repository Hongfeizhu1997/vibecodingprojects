#!/usr/bin/env python3
"""
GPS Cost Pricing Workbench — Local HTTP Server (v5.0)
SQLite-backed with CSV bidirectional sync. Auto-migrates legacy CSV on first run.
Usage: python3 server.py [port]
"""
import http.server
import json
import csv
import sqlite3
import os
import io
import sys
from urllib.parse import urlparse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT, "pricing_master.db")
LEGACY_CSV = os.path.join(ROOT, "pricing_master.csv")

COLUMNS = [
    "cycle_name", "completed_at",
    "service_pn", "country", "service_tier", "upgrade_years", "delivery_type",
    "aipc", "psc_value", "sales_cost",
    "gve_status",
    "list_price", "channel_price", "gp_percent",
    "gradient_status"
]

# ── Database ──────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create tables if not exist. Migrate legacy CSV on first run."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS pricing_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cycle_name TEXT NOT NULL,
            service_pn TEXT NOT NULL,
            country TEXT, service_tier TEXT, upgrade_years TEXT,
            delivery_type TEXT, aipc TEXT,
            psc_value REAL, sales_cost REAL,
            gve_status TEXT,
            list_price REAL, channel_price REAL, gp_percent REAL,
            gradient_status TEXT,
            completed_at TEXT,
            updated_at TEXT DEFAULT (datetime('now')),
            UNIQUE(cycle_name, service_pn)
        );
        CREATE TABLE IF NOT EXISTS pricing_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cycle_name TEXT, service_pn TEXT,
            field_name TEXT, old_value TEXT, new_value TEXT,
            changed_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_pn ON pricing_records(service_pn);
        CREATE INDEX IF NOT EXISTS idx_cycle ON pricing_records(cycle_name);
        CREATE INDEX IF NOT EXISTS idx_hist_pn ON pricing_history(service_pn);
    """)
    conn.commit()

    # Auto-migrate legacy CSV if DB is empty and CSV exists
    count = conn.execute("SELECT COUNT(*) FROM pricing_records").fetchone()[0]
    if count == 0 and os.path.exists(LEGACY_CSV):
        migrated = _migrate_csv(conn)
        conn.commit()
        print(f"   ⚡ Migrated {migrated} records from pricing_master.csv → SQLite")
    conn.close()


def _migrate_csv(conn):
    """Import legacy CSV into SQLite."""
    count = 0
    with open(LEGACY_CSV, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("service_pn") or not row.get("cycle_name"):
                continue
            values = {k: (row.get(k) or None) for k in COLUMNS}
            placeholders = ", ".join(f":{k}" for k in COLUMNS)
            cols = ", ".join(COLUMNS)
            conn.execute(
                f"INSERT OR IGNORE INTO pricing_records ({cols}) VALUES ({placeholders})",
                values
            )
            count += 1
    return count


# ── Core Operations ───────────────────────────────────────

def load_all_records():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM pricing_records ORDER BY completed_at DESC, service_pn"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def upsert_record(data):
    """Upsert a record. Returns {status, action, changes: [...]}."""
    conn = get_db()
    cycle = data.get("cycle_name", "")
    pn = data.get("service_pn", "")
    if not cycle or not pn:
        conn.close()
        return {"status": "error", "message": "cycle_name and service_pn required"}

    existing = conn.execute(
        "SELECT * FROM pricing_records WHERE cycle_name=? AND service_pn=?",
        (cycle, pn)
    ).fetchone()

    changes = []
    if existing:
        # Record changed fields in history
        existing_d = dict(existing)
        for k in COLUMNS:
            if k in ("cycle_name", "service_pn", "completed_at"):
                continue
            old_val = existing_d.get(k)
            new_val = data.get(k)
            if new_val is not None and str(old_val) != str(new_val):
                conn.execute(
                    "INSERT INTO pricing_history (cycle_name, service_pn, field_name, old_value, new_value) VALUES (?,?,?,?,?)",
                    (cycle, pn, k, str(old_val) if old_val is not None else "", str(new_val))
                )
                changes.append({"field": k, "old": old_val, "new": new_val})

        # Update only fields that have values
        update_fields = {k: data[k] for k in COLUMNS
                        if k not in ("cycle_name", "service_pn") and k in data}
        if update_fields:
            set_clause = ", ".join(f"{k}=:{k}" for k in update_fields)
            update_fields["cycle_name"] = cycle
            update_fields["service_pn"] = pn
            conn.execute(
                f"UPDATE pricing_records SET {set_clause} WHERE cycle_name=:cycle_name AND service_pn=:service_pn",
                update_fields
            )
        action = "updated"
    else:
        values = {k: data.get(k) for k in COLUMNS}
        placeholders = ", ".join(f":{k}" for k in COLUMNS)
        cols = ", ".join(COLUMNS)
        conn.execute(
            f"INSERT INTO pricing_records ({cols}) VALUES ({placeholders})",
            values
        )
        action = "created"

    conn.commit()
    conn.close()
    return {"status": "ok", "action": action, "changes": changes}


def get_pn_history(service_pn):
    """Return all history for a given PN."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM pricing_history WHERE service_pn=? ORDER BY changed_at DESC",
        (service_pn,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def export_csv():
    """Export all records as CSV string."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=COLUMNS, extrasaction='ignore')
    writer.writeheader()
    conn = get_db()
    rows = conn.execute("SELECT * FROM pricing_records ORDER BY cycle_name, service_pn").fetchall()
    for r in rows:
        writer.writerow(dict(r))
    conn.close()
    return output.getvalue()


def import_csv(csv_text):
    """Import CSV text into SQLite. Returns {imported, skipped, errors}."""
    reader = csv.DictReader(io.StringIO(csv_text))
    imported = 0
    skipped = 0
    errors = []
    conn = get_db()
    for i, row in enumerate(reader):
        if not row.get("service_pn") or not row.get("cycle_name"):
            skipped += 1
            continue
        try:
            upsert_record(row)
            imported += 1
        except Exception as e:
            errors.append(f"Row {i+2}: {e}")
    conn.close()
    return {"status": "ok", "imported": imported, "skipped": skipped, "errors": errors}


# ── HTTP Handler ──────────────────────────────────────────

class Handler(http.server.SimpleHTTPRequestHandler):

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

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length else b""

    def _json_response(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def do_POST(self):
        parsed = urlparse(self.path)
        body = self._read_body()

        if parsed.path == "/api/save-master":
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                return
            result = upsert_record(data)
            self._json_response(result)

        elif parsed.path == "/api/import-csv":
            csv_text = body.decode("utf-8")
            result = import_csv(csv_text)
            self._json_response(result)

        else:
            self.send_error(404, "API endpoint not found")

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/load-master":
            records = load_all_records()
            self._json_response(records)

        elif parsed.path == "/api/pn-history":
            qs = urlparse(self.path).query if self.path else ""
            params = dict(p.split("=", 1) for p in qs.split("&") if "=" in p) if qs else {}
            pn = params.get("pn", "")
            if not pn:
                self.send_error(400, "Missing ?pn= parameter")
                return
            history = get_pn_history(pn)
            self._json_response(history)

        elif parsed.path == "/api/export-csv":
            csv_data = export_csv()
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=pricing_master.csv")
            self.end_headers()
            self.wfile.write(csv_data.encode("utf-8"))

        else:
            # Serve static files (existing behavior)
            super().do_GET()


# ── Main ──────────────────────────────────────────────────

print("📊 GPS Pricing Workbench Server v5.0 (SQLite)")
print(f"   Root:     {ROOT}")
print(f"   Database: {DB_PATH}")
print(f"   URL:      http://localhost:{PORT}")
print(f"   API:")
print(f"     GET  /api/load-master   — all records")
print(f"     POST /api/save-master   — upsert one record")
print(f"     GET  /api/pn-history?pn=xxx — change history")
print(f"     GET  /api/export-csv    — download CSV")
print(f"     POST /api/import-csv    — bulk import from CSV")
print()

init_db()
http.server.HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
