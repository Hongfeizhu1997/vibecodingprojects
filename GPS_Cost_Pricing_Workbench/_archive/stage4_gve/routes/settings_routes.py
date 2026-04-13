from flask import Blueprint, request, jsonify, session
from database import get_db, get_all_settings, log_audit

bp = Blueprint("settings_routes", __name__)


@bp.get("/api/settings")
def get_settings():
    return jsonify(get_all_settings())


@bp.post("/api/settings")
def save_settings():
    username = session.get("username", "unknown")
    data = request.json  # dict of key→value
    conn = get_db()
    for key, value in data.items():
        old = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        old_val = old["value"] if old else None
        conn.execute("""
            INSERT INTO settings (key, value, updated_by, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value,
              updated_by=excluded.updated_by, updated_at=excluded.updated_at
        """, (key, str(value), username))
        log_audit(None, "settings", None, key, old_val, str(value), username)
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@bp.get("/api/tier-sequence")
def get_tier_sequence():
    conn = get_db()
    rows = conn.execute(
        "SELECT tier_name, sort_order FROM tier_sequence ORDER BY sort_order"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@bp.post("/api/tier-sequence")
def save_tier_sequence():
    """Accept list of {tier_name, sort_order} and update the sequence."""
    username = session.get("username", "unknown")
    data = request.json  # list of {tier_name, sort_order}
    conn = get_db()
    for item in data:
        conn.execute("""
            INSERT INTO tier_sequence (tier_name, sort_order)
            VALUES (?, ?)
            ON CONFLICT(tier_name) DO UPDATE SET sort_order = excluded.sort_order
        """, (item["tier_name"], item["sort_order"]))
        log_audit(None, "tier_sequence", None, item["tier_name"],
                  None, str(item["sort_order"]), username, "Tier sequence updated")
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@bp.get("/api/cycle-maturity/<int:cycle_id>")
def get_cycle_maturity(cycle_id):
    """Get platform maturity settings for a specific cycle."""
    conn = get_db()
    rows = conn.execute(
        "SELECT key, value FROM settings WHERE key LIKE ?",
        (f"maturity_cycle_{cycle_id}_%",)
    ).fetchall()
    conn.close()
    result = {}
    prefix = f"maturity_cycle_{cycle_id}_"
    for r in rows:
        tier = r["key"][len(prefix):]
        result[tier] = r["value"]
    return jsonify(result)


@bp.post("/api/cycle-maturity/<int:cycle_id>")
def save_cycle_maturity(cycle_id):
    """Save {tier: maturity_level} for a cycle. maturity_level: new|mature_refresh|mature"""
    username = session.get("username", "unknown")
    data = request.json  # {tier: maturity_level}
    conn = get_db()
    for tier, maturity in data.items():
        key = f"maturity_cycle_{cycle_id}_{tier}"
        conn.execute("""
            INSERT INTO settings (key, value, updated_by, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value,
              updated_by=excluded.updated_by, updated_at=excluded.updated_at
        """, (key, maturity, username))
        log_audit(cycle_id, "settings", None, key, None, maturity, username)
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@bp.get("/api/tier-gm-markup")
def get_tier_gm_markup():
    """Return GM% and markup% per tier, plus defaults."""
    conn = get_db()
    rows = conn.execute(
        "SELECT key, value FROM settings WHERE key LIKE 'gm_pct_%' OR key LIKE 'markup_pct_%'"
    ).fetchall()
    conn.close()
    return jsonify({r["key"]: r["value"] for r in rows})


@bp.post("/api/tier-gm-markup")
def save_tier_gm_markup():
    username = session.get("username", "unknown")
    data = request.json
    conn = get_db()
    for key, value in data.items():
        if not (key.startswith("gm_pct_") or key.startswith("markup_pct_")):
            continue
        conn.execute("""
            INSERT INTO settings (key, value, updated_by, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value,
              updated_by=excluded.updated_by, updated_at=excluded.updated_at
        """, (key, str(value), username))
        log_audit(None, "settings", None, key, None, str(value), username)
    conn.commit()
    conn.close()
    return jsonify({"ok": True})
