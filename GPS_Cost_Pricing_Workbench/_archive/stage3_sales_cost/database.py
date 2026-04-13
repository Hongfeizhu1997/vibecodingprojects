import os
import sqlite3

# ---------------------------------------------------------------------------
# Path configuration
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("GPS_DB_PATH", os.path.join(_HERE, "pricing.db"))

# ---------------------------------------------------------------------------
# Uplift Factor Definitions seed data
# ---------------------------------------------------------------------------

UPLIFT_FACTOR_DEFINITIONS = [
    ("TYPESRV",   "Type of Service",              "Service Type"),
    ("SUBTYPESRV","Sub-Type of Service",           "Service Type"),
    ("GEO",       "GEO",                           "Territory"),
    ("COUNTRY",   "Country",                       "Territory"),
    ("SRVTIER",   "Service Tier",                  "Hardware"),
    ("SUBSRVTIER","Sub Service Tier",               "Hardware"),
    ("MT",        "Compatible MT",                 "Hardware"),
    ("SRVTERM",   "Service Term",                  "Service Period"),
    ("SABTIME",   "Service Availability Time",     "SLA"),
    ("RSPTIME",   "Service Response Time",         "SLA"),
    ("SDTYPE",    "Service Delivery Type",         "Service Scope"),
    ("ICPS",      "Included Premier Service",      "Service Scope"),
    ("PSTYPE",    "Premier Service Type",          "Service Scope"),
    ("ICADP",     "Included ADP or ADI Service",   "Service Scope"),
    ("ICKYD",     "Included KYD Service",          "Service Scope"),
    ("ICSBTY",    "Included SBTY Service",         "Service Scope"),
    ("ICISE",     "Included ISE Service",          "Service Scope"),
    ("ICTICRU",   "Included TI CRU Service",       "Service Scope"),
]

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------


def get_db():
    """Return a sqlite3 connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------------------------------------------------------------------------
# Schema initialisation
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS cycles (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL UNIQUE,
    fiscal_year  TEXT    NOT NULL,
    status       TEXT    NOT NULL DEFAULT 'draft',
    created_by   TEXT    NOT NULL,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS uplift_factor_definitions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    technical_id   TEXT    NOT NULL UNIQUE,
    factor_name    TEXT    NOT NULL,
    classification TEXT    NOT NULL,
    description    TEXT
);

CREATE TABLE IF NOT EXISTS uplift_catalogs (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    catalog_id       TEXT    NOT NULL UNIQUE,
    description      TEXT,
    type_of_service  TEXT,
    geo              TEXT,
    valid_from       TEXT,
    valid_to         TEXT,
    status           TEXT    NOT NULL DEFAULT 'Draft',
    created_by       TEXT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS uplift_catalog_factors (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    catalog_id     INTEGER NOT NULL REFERENCES uplift_catalogs(id) ON DELETE CASCADE,
    factor_def_id  INTEGER NOT NULL REFERENCES uplift_factor_definitions(id) ON DELETE CASCADE,
    sort_order     INTEGER NOT NULL DEFAULT 0,
    UNIQUE(catalog_id, factor_def_id)
);

CREATE TABLE IF NOT EXISTS uplift_rules (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id          TEXT    NOT NULL UNIQUE,
    description      TEXT,
    catalog_id       INTEGER REFERENCES uplift_catalogs(id) ON DELETE SET NULL,
    type_of_service  TEXT,
    geo              TEXT,
    valid_from       TEXT,
    valid_to         TEXT,
    status           TEXT    NOT NULL DEFAULT 'Draft',
    created_by       TEXT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS uplift_rule_factors (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id        INTEGER NOT NULL REFERENCES uplift_rules(id) ON DELETE CASCADE,
    factor_def_id  INTEGER NOT NULL REFERENCES uplift_factor_definitions(id) ON DELETE CASCADE,
    factor_values  TEXT,
    uplift_ratio   REAL    NOT NULL DEFAULT 0.0,
    UNIQUE(rule_id, factor_def_id)
);

CREATE TABLE IF NOT EXISTS service_pns (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_id                 INTEGER NOT NULL REFERENCES cycles(id) ON DELETE CASCADE,
    service_pn               TEXT    NOT NULL,
    short_description        TEXT,
    sm_description           TEXT,
    oh_id                    TEXT,
    oh_name                  TEXT,
    type_of_service          TEXT,
    sub_type_of_service      TEXT,
    offering_type            TEXT,
    psc_value                REAL,
    currency                 TEXT,
    sales_cost               REAL,
    sales_cost_source        TEXT,
    uplift_formula           TEXT,
    uplift_ratio             REAL,
    geo                      TEXT,
    country                  TEXT,
    service_tier             TEXT,
    sub_service_tier         TEXT,
    compatible_mt            TEXT,
    sdf_code                 TEXT,
    sdf_short_description    TEXT,
    sdf_long_description     TEXT,
    service_term             TEXT,
    unit                     TEXT,
    service_availability_time TEXT,
    service_response_time    TEXT,
    service_delivery_type    TEXT,
    included_premier_service TEXT,
    premier_service_type     TEXT,
    included_adp             TEXT,
    included_kyd             TEXT,
    included_sbty            TEXT,
    included_ise             TEXT,
    included_ticru           TEXT,
    imported_at              TEXT    NOT NULL DEFAULT (datetime('now')),
    imported_by              TEXT,
    UNIQUE(cycle_id, service_pn, country)
);

CREATE TABLE IF NOT EXISTS audit_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_id     INTEGER,
    table_name   TEXT NOT NULL,
    record_key   TEXT NOT NULL,
    field_name   TEXT NOT NULL,
    old_value    TEXT,
    new_value    TEXT,
    changed_by   TEXT NOT NULL,
    changed_at   TEXT NOT NULL DEFAULT (datetime('now')),
    reason       TEXT
);
"""


def init_db():
    """Create all tables and seed uplift_factor_definitions if empty."""
    conn = get_db()
    try:
        conn.executescript(_SCHEMA)
        for (tid, fname, cls) in UPLIFT_FACTOR_DEFINITIONS:
            conn.execute(
                """INSERT OR IGNORE INTO uplift_factor_definitions
                   (technical_id, factor_name, classification)
                   VALUES (?, ?, ?)""",
                (tid, fname, cls),
            )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Audit log helper
# ---------------------------------------------------------------------------


def log_audit(cycle_id, table_name, record_key, field_name,
              old_value, new_value, changed_by, reason=None):
    """Insert a row into audit_log."""
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO audit_log
               (cycle_id, table_name, record_key, field_name,
                old_value, new_value, changed_by, reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (cycle_id, table_name, record_key, field_name,
             str(old_value) if old_value is not None else None,
             str(new_value) if new_value is not None else None,
             changed_by, reason),
        )
        conn.commit()
    finally:
        conn.close()
