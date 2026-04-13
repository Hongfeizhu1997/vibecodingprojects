import os
import urllib.request
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Stage registry — add Stage 1, 2, 5 here when ready
# ---------------------------------------------------------------------------
STAGES = [
    {
        "id": 1,
        "name": "Standard Cost",
        "description": "Import standard cost data as the base for PSC calculation.",
        "port": 5001,
        "status": "coming_soon",
    },
    {
        "id": 2,
        "name": "Forward Adjustment",
        "description": "PSC = Standard Cost × failure × parts × labor × mix factors.",
        "port": 5002,
        "status": "coming_soon",
    },
    {
        "id": 3,
        "name": "Sales Cost",
        "description": "Apply dimension-driven uplift rules to derive Sales Cost from PSC.",
        "port": 5003,
        "status": "active",
    },
    {
        "id": 4,
        "name": "GVE Validation",
        "description": "4-layer guardrail checks on the sales cost matrix before sign-off.",
        "port": 5004,
        "status": "active",
    },
    {
        "id": 5,
        "name": "List Price",
        "description": "Derive B2C / B2B list prices from validated sales cost.",
        "port": 5005,
        "status": "coming_soon",
    },
]


def ping_stage(port):
    """Return True if the stage is responding on its health endpoint."""
    try:
        url = f"http://127.0.0.1:{port}/health"
        with urllib.request.urlopen(url, timeout=1) as resp:
            return resp.status == 200
    except Exception:
        return False


@app.get("/")
def index():
    return render_template("index.html", stages=STAGES)


@app.get("/api/status")
def status():
    result = {}
    for stage in STAGES:
        if stage["status"] == "active":
            result[stage["id"]] = "running" if ping_stage(stage["port"]) else "offline"
        else:
            result[stage["id"]] = "coming_soon"
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("GPS_LAUNCHER_PORT", 5000))
    print(f"\n  GPS Pricing Workbench — Launcher")
    print(f"  Running at http://localhost:{port}\n")
    app.run(debug=False, host="127.0.0.1", port=port)
