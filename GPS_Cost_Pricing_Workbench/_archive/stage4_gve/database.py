import sqlite3
import os

DB_PATH = os.environ.get("GPS_DB_PATH", os.path.join(os.path.dirname(__file__), "pricing.db"))


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS cycles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        fiscal_year TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'draft',
        created_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        submitted_at TIMESTAMP,
        submitted_by TEXT
    );

    CREATE TABLE IF NOT EXISTS tier_sequence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tier_name TEXT UNIQUE NOT NULL,
        sort_order INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS skus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cycle_id INTEGER NOT NULL REFERENCES cycles(id),
        part_number TEXT NOT NULL,
        tier TEXT NOT NULL,
        base_warranty TEXT NOT NULL,
        upgrade_description TEXT NOT NULL,
        delivery_type TEXT NOT NULL,
        upgrade_years INTEGER
    );

    CREATE TABLE IF NOT EXISTS sku_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku_id INTEGER NOT NULL REFERENCES skus(id),
        region TEXT NOT NULL,
        sales_cost REAL,
        channel_price REAL,
        list_price REAL,
        computed_list_price_b2c REAL,
        computed_quoted_floor_b2b REAL
    );

    CREATE TABLE IF NOT EXISTS prior_baseline (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cycle_id INTEGER NOT NULL REFERENCES cycles(id),
        part_number TEXT NOT NULL,
        region TEXT NOT NULL,
        prior_sales_cost REAL NOT NULL,
        entered_by TEXT,
        entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS gve_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cycle_id INTEGER NOT NULL REFERENCES cycles(id),
        layer INTEGER NOT NULL,
        severity TEXT NOT NULL,
        region TEXT,
        tier TEXT,
        upgrade_years INTEGER,
        part_number TEXT,
        violation_type TEXT NOT NULL,
        message TEXT NOT NULL,
        is_resolved INTEGER NOT NULL DEFAULT 0,
        explanation TEXT,
        resolved_by TEXT,
        resolved_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cycle_id INTEGER,
        table_name TEXT NOT NULL,
        record_id INTEGER,
        field_name TEXT NOT NULL,
        old_value TEXT,
        new_value TEXT,
        changed_by TEXT NOT NULL,
        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reason TEXT
    );

    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_by TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS pfv_benchmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        part_number TEXT NOT NULL,
        region TEXT NOT NULL,
        pfv_price REAL,
        source TEXT,
        effective_cycle TEXT,
        entered_by TEXT,
        entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Insert default settings if not present
    defaults = {
        "contingency_new_1_3yr": "0.12",
        "contingency_new_4_5yr": "0.18",
        "contingency_mature_refresh_1_3yr": "0.08",
        "contingency_mature_refresh_4_5yr": "0.13",
        "contingency_mature_1_3yr": "0.05",
        "contingency_mature_4_5yr": "0.09",
        "overhead_total_fixed_cost": "0",
        "overhead_projected_units": "0",
        "ratio_band_3yr_1yr_min": "1.8",
        "ratio_band_3yr_1yr_max": "2.8",
        "ratio_band_5yr_3yr_min": "1.3",
        "ratio_band_5yr_3yr_max": "1.7",
        "ratio_band_4yr_2yr_min": "1.3",
        "ratio_band_4yr_2yr_max": "2.0",
        "cross_geo_deviation_pct": "0.20",
        "yoy_cell_change_pct": "0.25",
        "yoy_ratio_change_pct": "0.15",
        "yoy_geo_avg_change_pct": "0.20",
    }
    for key, value in defaults.items():
        c.execute(
            "INSERT OR IGNORE INTO settings (key, value, updated_by) VALUES (?, ?, 'system')",
            (key, value),
        )

    conn.commit()
    conn.close()


def log_audit(cycle_id, table_name, record_id, field_name, old_value, new_value, changed_by, reason=None):
    conn = get_db()
    conn.execute(
        """INSERT INTO audit_log
           (cycle_id, table_name, record_id, field_name, old_value, new_value, changed_by, reason)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (cycle_id, table_name, record_id, field_name,
         str(old_value) if old_value is not None else None,
         str(new_value) if new_value is not None else None,
         changed_by, reason),
    )
    conn.commit()
    conn.close()


def get_setting(key, default=None):
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def get_all_settings():
    conn = get_db()
    rows = conn.execute("SELECT key, value FROM settings ORDER BY key").fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}
