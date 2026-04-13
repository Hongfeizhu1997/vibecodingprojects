"""
Cycle management routes.
Blueprint prefix: /api
"""

from flask import Blueprint, jsonify, request, session
import database

cycles_bp = Blueprint("cycles", __name__)


def _require_login():
    if not session.get("username"):
        return jsonify({"error": "Not logged in"}), 401
    return None


@cycles_bp.get("/api/cycles")
def list_cycles():
    err = _require_login()
    if err:
        return err
    conn = database.get_db()
    try:
        rows = conn.execute(
            "SELECT id, name, fiscal_year, status, created_by, created_at FROM cycles ORDER BY id DESC"
        ).fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()


@cycles_bp.post("/api/cycles")
def create_cycle():
    err = _require_login()
    if err:
        return err
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    fiscal_year = (data.get("fiscal_year") or "").strip()
    if not name:
        return jsonify({"error": "Cycle name is required"}), 400
    if not fiscal_year:
        return jsonify({"error": "Fiscal year is required"}), 400

    username = session["username"]
    conn = database.get_db()
    try:
        cur = conn.execute(
            "INSERT INTO cycles (name, fiscal_year, status, created_by) VALUES (?, ?, 'draft', ?)",
            (name, fiscal_year, username),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, name, fiscal_year, status, created_by, created_at FROM cycles WHERE id = ?",
            (cur.lastrowid,),
        ).fetchone()
        return jsonify(dict(row)), 201
    except Exception as exc:
        try:
            conn.rollback()
        except Exception:
            pass
        if "UNIQUE" in str(exc):
            return jsonify({"error": f"A cycle named '{name}' already exists."}), 409
        return jsonify({"error": str(exc)}), 500
    finally:
        conn.close()


@cycles_bp.get("/api/cycles/<int:cycle_id>")
def get_cycle(cycle_id):
    err = _require_login()
    if err:
        return err
    conn = database.get_db()
    try:
        row = conn.execute(
            "SELECT id, name, fiscal_year, status, created_by, created_at FROM cycles WHERE id = ?",
            (cycle_id,),
        ).fetchone()
        if row is None:
            return jsonify({"error": "Cycle not found"}), 404
        return jsonify(dict(row))
    finally:
        conn.close()
