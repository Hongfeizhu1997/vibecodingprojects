"""
PyInstaller entry point for Stage 4 — GVE Validation.
Used instead of app.py when running as a compiled .exe.
"""
import sys
import os
import threading
import webbrowser

# ── Frozen-mode path fix ───────────────────────────────────────────────────────
if getattr(sys, "frozen", False):
    exe_dir = os.path.dirname(sys.executable)
    if not os.environ.get("GPS_DB_PATH"):
        os.environ["GPS_DB_PATH"] = os.path.join(exe_dir, "pricing.db")

# ── Import app (database path must be set before this line) ───────────────────
from app import app           # noqa: E402
from database import init_db  # noqa: E402

# ── Initialise DB & launch ─────────────────────────────────────────────────────
init_db()

port = int(os.environ.get("GPS_PORT", 5004))

print(f"\n  GPS Pricing Workbench — Stage 4: GVE Validation")
print(f"  Running at http://localhost:{port}")
print(f"  Close this window to stop the server.\n")


def _open_browser():
    webbrowser.open(f"http://localhost:{port}")


threading.Timer(1.5, _open_browser).start()
app.run(debug=False, host="127.0.0.1", port=port)
