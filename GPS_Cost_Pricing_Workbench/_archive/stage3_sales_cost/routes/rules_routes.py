"""
Uplift Rules CRUD routes.
Blueprint prefix: /api
"""

from flask import Blueprint, jsonify, request, session
import database

rules_bp = Blueprint("rules", __name__)


def _require_login():
    if not session.get("username"):
        return jsonify({"error": "Not logged in"}), 401
    return None


def _rule_with_factors(conn, rule_row):
    """Return a rule dict enriched with its factors and total uplift ratio."""
    rule = dict(rule_row)

    # Attach catalog info
    if rule.get("catalog_id"):
        cat = conn.execute(
            "SELECT catalog_id, description, type_of_service, geo "
            "FROM uplift_catalogs WHERE id = ?",
            (rule["catalog_id"],),
        ).fetchone()
        rule["catalog"] = dict(cat) if cat else None
    else:
        rule["catalog"] = None

    factors = conn.execute(
        """SELECT urf.id, urf.factor_def_id, urf.factor_values, urf.uplift_ratio,
                  ufd.technical_id, ufd.factor_name, ufd.classification
           FROM uplift_rule_factors urf
           JOIN uplift_factor_definitions ufd ON ufd.id = urf.factor_def_id
           WHERE urf.rule_id = ?
           ORDER BY ufd.id""",
        (rule["id"],),
    ).fetchall()
    rule["factors"] = [dict(f) for f in factors]
    rule["total_uplift_ratio"] = sum(f["uplift_ratio"] for f in rule["factors"])
    return rule


@rules_bp.get("/api/rules")
def list_rules():
    err = _require_login()
    if err:
        return err

    catalog_id = request.args.get("catalog_id", "").strip()
    tos = request.args.get("type_of_service", "").strip()
    geo = request.args.get("geo", "").strip()

    conn = database.get_db()
    try:
        where = []
        params = []
        if catalog_id:
            where.append("r.catalog_id = ?")
            params.append(int(catalog_id))
        if tos:
            where.append("r.type_of_service = ?")
            params.append(tos)
        if geo:
            where.append("r.geo = ?")
            params.append(geo)

        where_clause = ("WHERE " + " AND ".join(where)) if where else ""
        rows = conn.execute(
            f"""SELECT r.id, r.rule_id, r.description, r.catalog_id,
                       r.type_of_service, r.geo, r.valid_from, r.valid_to,
                       r.status, r.created_by, r.created_at,
                       c.catalog_id as catalog_code
                FROM uplift_rules r
                LEFT JOIN uplift_catalogs c ON c.id = r.catalog_id
                {where_clause}
                ORDER BY r.rule_id""",
            params,
        ).fetchall()

        result = []
        for r in rows:
            rule = dict(r)
            # Factor count + total ratio
            agg = conn.execute(
                """SELECT COUNT(*) as cnt, SUM(uplift_ratio) as total
                   FROM uplift_rule_factors WHERE rule_id = ?""",
                (rule["id"],),
            ).fetchone()
            rule["factor_count"] = agg["cnt"] or 0
            rule["total_uplift_ratio"] = round(agg["total"] or 0.0, 6)
            result.append(rule)

        return jsonify(result)
    finally:
        conn.close()


@rules_bp.post("/api/rules")
def create_rule():
    err = _require_login()
    if err:
        return err

    username = session["username"]
    data = request.get_json(force=True, silent=True) or {}

    rule_id = (data.get("rule_id") or "").strip()
    if not rule_id:
        return jsonify({"error": "rule_id is required"}), 400

    conn = database.get_db()
    try:
        catalog_db_id = data.get("catalog_id")
        if catalog_db_id is not None:
            catalog_db_id = int(catalog_db_id)

        cur = conn.execute(
            """INSERT INTO uplift_rules
               (rule_id, description, catalog_id, type_of_service, geo,
                valid_from, valid_to, status, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                rule_id,
                data.get("description"),
                catalog_db_id,
                data.get("type_of_service"),
                data.get("geo"),
                data.get("valid_from"),
                data.get("valid_to"),
                data.get("status", "Draft"),
                username,
            ),
        )
        db_id = cur.lastrowid

        for factor in (data.get("factors") or []):
            fdef_id = factor.get("factor_def_id")
            if fdef_id is None:
                continue
            conn.execute(
                """INSERT OR IGNORE INTO uplift_rule_factors
                   (rule_id, factor_def_id, factor_values, uplift_ratio)
                   VALUES (?, ?, ?, ?)""",
                (
                    db_id,
                    int(fdef_id),
                    factor.get("factor_values", ""),
                    float(factor.get("uplift_ratio", 0.0)),
                ),
            )

        conn.commit()
        row = conn.execute(
            "SELECT * FROM uplift_rules WHERE id = ?", (db_id,)
        ).fetchone()
        return jsonify(_rule_with_factors(conn, row)), 201

    except Exception as exc:
        try:
            conn.rollback()
        except Exception:
            pass
        if "UNIQUE" in str(exc):
            return jsonify({"error": f"Rule '{rule_id}' already exists."}), 409
        return jsonify({"error": str(exc)}), 500
    finally:
        conn.close()


@rules_bp.get("/api/rules/<int:rule_id>")
def get_rule(rule_id):
    err = _require_login()
    if err:
        return err

    conn = database.get_db()
    try:
        row = conn.execute(
            "SELECT * FROM uplift_rules WHERE id = ?", (rule_id,)
        ).fetchone()
        if row is None:
            return jsonify({"error": "Rule not found"}), 404
        return jsonify(_rule_with_factors(conn, row))
    finally:
        conn.close()


@rules_bp.put("/api/rules/<int:rule_id>")
def update_rule(rule_id):
    err = _require_login()
    if err:
        return err

    data = request.get_json(force=True, silent=True) or {}

    conn = database.get_db()
    try:
        row = conn.execute(
            "SELECT * FROM uplift_rules WHERE id = ?", (rule_id,)
        ).fetchone()
        if row is None:
            return jsonify({"error": "Rule not found"}), 404

        catalog_db_id = data.get("catalog_id", row["catalog_id"])
        if catalog_db_id is not None:
            catalog_db_id = int(catalog_db_id)

        conn.execute(
            """UPDATE uplift_rules SET
               description = ?, catalog_id = ?, type_of_service = ?, geo = ?,
               valid_from = ?, valid_to = ?, status = ?
               WHERE id = ?""",
            (
                data.get("description", row["description"]),
                catalog_db_id,
                data.get("type_of_service", row["type_of_service"]),
                data.get("geo", row["geo"]),
                data.get("valid_from", row["valid_from"]),
                data.get("valid_to", row["valid_to"]),
                data.get("status", row["status"]),
                rule_id,
            ),
        )

        if "factors" in data:
            conn.execute(
                "DELETE FROM uplift_rule_factors WHERE rule_id = ?", (rule_id,)
            )
            for factor in (data["factors"] or []):
                fdef_id = factor.get("factor_def_id")
                if fdef_id is None:
                    continue
                conn.execute(
                    """INSERT OR IGNORE INTO uplift_rule_factors
                       (rule_id, factor_def_id, factor_values, uplift_ratio)
                       VALUES (?, ?, ?, ?)""",
                    (
                        rule_id,
                        int(fdef_id),
                        factor.get("factor_values", ""),
                        float(factor.get("uplift_ratio", 0.0)),
                    ),
                )

        conn.commit()
        updated = conn.execute(
            "SELECT * FROM uplift_rules WHERE id = ?", (rule_id,)
        ).fetchone()
        return jsonify(_rule_with_factors(conn, updated))

    except Exception as exc:
        try:
            conn.rollback()
        except Exception:
            pass
        return jsonify({"error": str(exc)}), 500
    finally:
        conn.close()


@rules_bp.delete("/api/rules/<int:rule_id>")
def delete_rule(rule_id):
    err = _require_login()
    if err:
        return err

    conn = database.get_db()
    try:
        row = conn.execute(
            "SELECT id, status FROM uplift_rules WHERE id = ?", (rule_id,)
        ).fetchone()
        if row is None:
            return jsonify({"error": "Rule not found"}), 404
        if row["status"] != "Draft":
            return jsonify({"error": "Only Draft rules can be deleted."}), 409

        conn.execute("DELETE FROM uplift_rules WHERE id = ?", (rule_id,))
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
