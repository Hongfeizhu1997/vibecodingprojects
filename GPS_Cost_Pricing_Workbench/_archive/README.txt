GPS Pricing Workbench
=====================

A Lenovo GPS Division offline pricing tool structured as a multi-stage pipeline.
Each stage is a standalone Flask application that can run independently or integrate
with shared database infrastructure.

STAGES
------

Stage 1 — Standard Cost Import
  Imports standard cost data from source systems.
  Folder: stage1_standard_cost/

Stage 2 — Forward Adjustment
  Applies forward-looking adjustments to standard costs to derive PSC
  (Projected Service Cost).
  Folder: stage2_forward_adjustment/

Stage 3 — Sales Cost Calculation  [AVAILABLE]
  Calculates Sales Cost from PSC using the formula:
    Sales Cost = PSC × (1 + R_contingency) × (1 + R_overhead)
  Supports product categories: ThinkPad, IdeaPad, Legion, Commercial
  Supports service types: 1yr Base, 3yr Base, 5yr Base, 3yr ADP, Premier 3yr
  Supports geographies: NA, EMEA, APJ, China
  Folder: stage3_sales_cost/

Stage 4 — GVE Validation
  Gradient Validation Engine: checks Sales Costs and List Prices against
  monotonicity, ratio band, cross-geo, and year-over-year rules.
  Folder: stage4_gve_validation/

Stage 5 — List Price Derivation
  Derives List Prices from Sales Costs using channel markup rules.
  Folder: stage5_list_price/

STANDALONE USAGE
----------------

Each stage folder contains its own:
  - app.py          Flask application entry point
  - database.py     SQLite database layer
  - requirements.txt
  - start.bat       Windows launcher (double-click to run)

To run Stage 3 standalone:
  1. Open stage3_sales_cost/
  2. Double-click start.bat  (or run: python app.py)
  3. Open browser to http://localhost:5003

INTEGRATED USAGE
----------------

Set environment variable GPS_DB_PATH to a shared SQLite file location
(e.g. in the shared/ folder) so all stages read/write the same database.

  set GPS_DB_PATH=C:\Users\Administrator\ClaudeProjects\GPS_Pricing_Workbench\shared\pricing.db

Set GPS_PORT to override the default port for each stage:
  Stage 3 default port: 5003

FOLDER STRUCTURE
----------------

GPS_Pricing_Workbench/
├── README.txt                  This file
├── shared/                     Shared database location (for integrated mode)
├── stage3_sales_cost/          Stage 3 application (Sales Cost Calculation)
│   ├── app.py
│   ├── database.py
│   ├── requirements.txt
│   ├── start.bat
│   ├── engine/
│   │   └── sales_cost_engine.py
│   ├── routes/
│   │   ├── cycles.py
│   │   ├── import_routes.py
│   │   ├── settings_routes.py
│   │   └── calc_routes.py
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── dashboard.html
│       └── cycle.html
