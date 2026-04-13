# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Stage 3 — Sales Cost
# Run from the GPS_Pricing_Workbench\ root:
#   pyinstaller build\stage3.spec

import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_data_files

STAGE_DIR = os.path.join(os.path.dirname(SPECPATH), 'stage3_sales_cost')

# ── Data files ────────────────────────────────────────────────────────────────
datas = [
    (os.path.join(STAGE_DIR, 'templates'), 'templates'),
]

# Collect all Flask / Werkzeug / Jinja2 package data
for pkg in ('flask', 'werkzeug', 'jinja2'):
    pkg_datas, pkg_bins, pkg_hidden = collect_all(pkg)
    datas += pkg_datas

# ── Hidden imports ────────────────────────────────────────────────────────────
hiddenimports = [
    # App modules
    'database',
    'engine', 'engine.sales_cost_engine', 'engine.excel_importer',
    'routes', 'routes.cycles', 'routes.import_routes',
    'routes.catalog_routes', 'routes.rules_routes', 'routes.calc_routes',
    # Flask internals
    'flask', 'flask.helpers', 'flask.templating', 'flask.sessions',
    'flask.json', 'flask.logging', 'flask.signals',
    # Werkzeug
    'werkzeug', 'werkzeug.routing', 'werkzeug.routing.rules',
    'werkzeug.routing.matcher', 'werkzeug.routing.converters',
    'werkzeug.sansio.routing', 'werkzeug.exceptions',
    'werkzeug.serving', 'werkzeug.utils', 'werkzeug.wrappers',
    # Jinja2
    'jinja2', 'jinja2.ext', 'jinja2.defaults',
    # openpyxl
    'openpyxl', 'openpyxl.styles', 'openpyxl.utils', 'openpyxl.utils.dataframe',
    'openpyxl.reader.excel', 'openpyxl.writer.excel',
    'et_xmlfile',
    # stdlib
    'sqlite3', 'click', 'csv', 'io',
]

# ── Analysis ──────────────────────────────────────────────────────────────────
a = Analysis(
    [os.path.join(STAGE_DIR, 'run.py')],
    pathex=[STAGE_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'PIL', 'tkinter', 'PyQt5'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Stage3_SalesCost',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,           # keep console window — shows server status & errors
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Stage3_SalesCost',
)
