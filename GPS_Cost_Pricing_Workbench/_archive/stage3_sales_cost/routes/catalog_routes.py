"""
Uplift Catalog CRUD routes.
Blueprint prefix: /api
"""

from flask import Blueprint, jsonify, request, session
import database

catalog_bp = Blueprint("catalog", __name__)


def _require_login():
    if not session.get("username"):
        return jsonify({"error": "Not logged in"}), 401
    return None


def _catalog_with_factors(conn, cat_row):
    """Return a catalog dict enriched with its selected factors."""
    cat = dict(cat_row)
    factors = conn.execute(
        """SELECT ucf.id, ucf.factor_def_id, ucf.sort_order,
                  ufd.technical_id, ufd.factor_name, ufd.classification
           FROM uplift_catalog_factors ucf
           JOIN uplift_factor_definitions ufd ON ufd.id = ucf.factor_def_id
           WHERE ucf.catalog_id = ?
           ORDER BY ucf.sort_order""",
        (cat["id"],),
    ).fetchall()
    cat["factors"] = [dict(f) for f in factors]
    return cat


@catalog_bp.get("/api/uplift-factors")
def list_factor_definitions():
    err = _require_login()
    if err:
        return err
    conn = database.get_db()
    try:
        rows = conn.execute(
            "SELECT id, technical_id, factor_name, classification, description "
            "FROM uplift_factor_definitions ORDER BY id"
        ).fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()


@catalog_bp.get("/api/catalogs")
def list_catalogs():
    err = _require_login()
    if err:
        return err

    tos = request.args.get("type_of_service", "").strip()
    geo = request.args.get("geo", "").strip()

    conn = database.get_db()
    try:
        where = []
        params = []
        if tos:
            where.append("type_of_service = ?")
            params.append(tos)
        if geo:
            where.append("geo = ?")
            params.append(geo)

        where_clause = ("WHERE " + " AND ".join(where)) if where else ""
        rows = conn.execute(
            f"SELECT id, catalog_id, description, type_of_service, geo, "
            f"valid_from, valid_to, status, created_by, created_at "
            f"FROM uplift_catalogs {where_clause} ORDER BY catalog_id",
            params,
        ).fetchall()

        result = []
        for r in rows:
            cat = dict(r)
            cnt = conn.execute(
                "SELECT COUNT(*) FROM uplift_catalog_factors WHERE catalog_id = ?",
                (cat["id"],),
            ).fetchone()[0]
            cat["factor_count"] = cnt
            result.append(cat)

        return jsonify(result)
    finally:
        conn.close()


@catalog_bp.post("/api/catalogs")
def create_catalog():
    err = _require_login()
    if err:
        return err

    username = session["username"]
    data = request.get_json(force=True, silent=True) or {}

    catalog_id = (data.get("catalog_id") or "").strip()
    if not catalog_id:
        return jsonify({"error": "catalog_id is required"}), 400

    conn = database.get_db()
    try:
        cur = conn.execute(
            """INSERT INTO uplift_catalogs
               (catalog_id, description, type_of_service, geo,
                valid_from, valid_to, status, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                catalog_id,
                data.get("description"),
                data.get("type_of_service"),
                data.get("geo"),
                data.get("valid_from"),
                data.get("valid_to"),
                data.get("status", "Draft"),
                username,
            ),
        )
        db_id = cur.lastrowid

        factor_def_ids = data.get("factor_def_ids") or []
        for sort_idx, fid in enumerate(factor_def_ids):
            conn.execute(
                """INSERT OR IGNORE INTO uplift_catalog_factors
                   (catalog_id, factor_def_id, sort_order) VALUES (?, ?, ?)""",
                (db_id, int(fid), sort_idx),
            )

        conn.commit()
        row = conn.execute(
            "SELECT * FROM uplift_catalogs WHERE id = ?", (db_id,)
        ).fetchone()
        return jsonify(_catalog_with_factors(conn, row)), 201

    except Exception as exc:
        try:
            conn.rollback()
        except Exception:
            pass
        if "UNIQUE" in str(exc):
            return jsonify({"error": f"Catalog '{catalog_id}' already exists."}), 409
        return jsonify({"error": str(exc)}), 500
    finally:
        conn.close()


@catalog_bp.get("/api/catalogs/<int:cat_id>")
def get_catalog(cat_id):
    err = _require_login()
    if err:
        return err

    conn = database.get_db()
    try:
        row = conn.execute(
            "SELECT * FROM uplift_catalogs WHERE id = ?", (cat_id,)
        ).fetchone()
        if row is None:
            return jsonify({"error": "Catalog not found"}), 404
        return jsonify(_catalog_with_factors(conn, row))
    finally:
        conn.close()


@catalog_bp.put("/api/catalogs/<int:cat_id>")
def update_catalog(cat_id):
    err = _require_login()
    if err:
        return err

    data = request.get_json(force=True, silent=True) or {}

    conn = database.get_db()
    try:
        row = conn.execute(
            "SELECT * FROM uplift_catalogs WHERE id = ?", (cat_id,)
        ).fetchone()
        if row is None:
            return jsonify({"error": "Catalog not found"}), 404

        conn.execute(
            """UPDATE uplift_catalogs SET
               description = ?, type_of_service = ?, geo = ?,
               valid_from = ?, valid_to = ?, status = ?
               WHERE id = ?""",
            (
                data.get("description", row["description"]),
                data.get("type_of_service", row["type_of_service"]),
                data.get("geo", row["geo"]),
                data.get("valid_from", row["valid_from"]),
                data.get("valid_to", row["valid_to"]),
                data.get("status", row["status"]),
                cat_id,
            ),
        )

        # Replace factor selection if provided
        if "factor_def_ids" in data:
            conn.execute(
                "DELETE FROM uplift_catalog_factors WHERE catalog_id = ?", (cat_id,)
            )
            for sort_idx, fid in enumerate(data["factor_def_ids"] or []):
                conn.execute(
                    """INSERT OR IGNORE INTO uplift_catalog_factors
                       (catalog_id, factor_def_id, sort_order) VALUES (?, ?, ?)""",
                    (cat_id, int(fid), sort_idx),
                )

        conn.commit()
        updated = conn.execute(
            "SELECT * FROM uplift_catalogs WHERE id = ?", (cat_id,)
        ).fetchone()
        return jsonify(_catalog_with_factors(conn, updated))

    except Exception as exc:
        try:
            conn.rollback()
        except Exception:
            pass
        return jsonify({"error": str(exc)}), 500
    finally:
        conn.close()


@catalog_bp.delete("/api/catalogs/<int:cat_id>")
def delete_catalog(cat_id):
    err = _require_login()
    if err:
        return err

    conn = database.get_db()
    try:
        row = conn.execute(
            "SELECT id, status FROM uplift_catalogs WHERE id = ?", (cat_id,)
        ).fetchone()
        if row is None:
            return jsonify({"error": "Catalog not found"}), 404
        if row["status"] != "Draft":
            return jsonify({"error": "Only Draft catalogs can be deleted."}), 409

        conn.execute("DELETE FROM uplift_catalogs WHERE id = ?", (cat_id,))
        conn.commit()
        return jsonify({"deleted": True})
    except Exception as exc:
        try:
            conn.rollback()
        except Exception:
            pass
        return jsonify({"error": str(exc)}), 500
    finally:
        conn.close()
