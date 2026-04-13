import os
from flask import Flask, render_template, session, request, jsonify, redirect, url_for
from database import init_db
from routes.cycles import bp as cycles_bp
from routes.data_import import bp as import_bp
from routes.gve import bp as gve_bp
from routes.settings_routes import bp as settings_bp
from routes.export import bp as export_bp

app = Flask(__name__)
app.secret_key = "gps-pricing-workbench-secret-2025"

app.register_blueprint(cycles_bp)
app.register_blueprint(import_bp)
app.register_blueprint(gve_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(export_bp)


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
    return jsonify({"status": "ok", "stage": 4})


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


@app.get("/settings")
def settings_view():
    return render_template("settings.html", username=session.get("username"))


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("GPS_PORT", 5004))
    print(f"\n  GPS Pricing Workbench — Stage 4: GVE Validation running at http://localhost:{port}\n")
    app.run(debug=False, host="127.0.0.1", port=port)
