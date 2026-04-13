import os
from flask import Flask, render_template, session, request, jsonify, redirect, url_for
from database import init_db
from routes.cycles import cycles_bp
from routes.import_routes import import_bp
from routes.catalog_routes import catalog_bp
from routes.rules_routes import rules_bp
from routes.calc_routes import calc_bp

app = Flask(__name__)
app.secret_key = "gps-stage3-sales-cost-secret-2025"

app.register_blueprint(cycles_bp)
app.register_blueprint(import_bp)
app.register_blueprint(catalog_bp)
app.register_blueprint(rules_bp)
app.register_blueprint(calc_bp)


@app.before_request
def require_username():
    """Redirect to login if no username in session, except for the login route itself."""
    exempt = {"/login", "/static", "/health"}
    if not any(request.path.startswith(e) for e in exempt):
        if not session.get("username"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Not logged in"}), 401
            return redirect(url_for("login"))


@app.get("/health")
def health():
    return jsonify({"status": "ok", "stage": 3})


@app.get("/login")
def login():
    return render_template("login.html")


@app.post("/login")
def do_login():
    username = request.form.get("username", "").strip()
    if not username:
        return render_template("login.html", error="Please enter your name.")
    session["username"] = username
    return redirect(url_for("dashboard"))


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/")
def dashboard():
    return render_template("dashboard.html", username=session.get("username"))


@app.get("/cycle/<int:cycle_id>")
def cycle_view(cycle_id):
    return render_template("cycle.html", cycle_id=cycle_id, username=session.get("username"))


@app.get("/catalogs")
def catalogs_view():
    return render_template("catalogs.html", username=session.get("username"))


@app.get("/rules")
def rules_view():
    return render_template("rules.html", username=session.get("username"))


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("GPS_PORT", 5003))
    print(f"\n  GPS Pricing Workbench — Stage 3: Sales Cost")
    print(f"  Running at http://localhost:{port}\n")
    app.run(debug=False, host="127.0.0.1", port=port)
