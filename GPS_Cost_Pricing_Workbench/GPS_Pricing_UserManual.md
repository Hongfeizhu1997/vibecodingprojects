# GPS Cost Pricing Workbench — User Manual

> **Version 5.0** | June 2026 | Lenovo Global Product Support (GPS) — SSGCDTO Division

---

## 1. Tool Overview

The **GPS Cost Pricing Workbench** is a browser-based offline pricing tool for Lenovo's GPS service pricing team. It guides you through a 6-stage pipeline from raw cost data to validated list prices, with a built-in pricing history database and dashboard.

```
Stage 1          Stage 2          Stage 3         Stage 4         Stage 5          Stage 6
Std Cost ──→ Forward Adj ──→ Sales Cost ──→ GVE Validation ──→ List Price ──→ Gradient Check
 (TBD)          (TBD)            ✅ ACTIVE        ✅ ACTIVE        ✅ ACTIVE         ✅ ACTIVE
                                              ↓
                                        Dashboard
                                   (History & Trends)
```

**Key features:**
- No installation — opens in Chrome/Edge
- All data stored locally (SQLite database + CSV export)
- Each stage is a self-contained page
- Full audit trail: every pricing change is recorded

---

## 2. Getting Started

### 2.1 Start the Server

```bash
cd GPS_Cost_Pricing_Workbench
python3 server.py 8080
```

Open your browser to **http://localhost:8080/GPS_Cost_Pricing_Workbench.html** — this is the launcher page with all stages.

> ⚠️ **Important**: Use `python3 server.py`, NOT `python3 -m http.server`. The custom server handles data persistence (SQLite + CSV import/export). The standard server will silently fail to save your data.

### 2.2 The Launcher

The launcher shows all 6 stages as cards. Click any **active stage** (3, 4, 5, or 6) to open it. The **Dashboard** card opens your pricing history.

### 2.3 Navigation

Every stage page has a top navigation bar with links to all other stages, so you can jump between them without going back to the launcher.

---

## 3. Workflow Overview (End-to-End)

A complete pricing cycle follows this flow:

```
1. Stage 3: Import raw SKU data → apply uplift rules → calculate Sales Cost
                                    ↓ (Bridge: auto-transfer to Stage 4)
2. Stage 4: Import from Stage 3 → run GVE 4-layer validation → fix violations
                                    ↓ (Bridge: auto-transfer to Stage 5)
3. Stage 5: Import from Stage 4 → import PFV benchmarks → derive List Price
                                    ↓ (Bridge: auto-transfer to Stage 6)
4. Stage 6: Import from Stage 5 → run 3-layer gradient validation
                                    ↓
5. Dashboard: View all cycles, track PN history, export CSV
```

---

## 4. Stage 3 — Sales Cost Calculation

**What it does**: Takes Standard Cost (PSC) data and applies uplift rules to calculate Sales Cost.

### Formula
```
Sales Cost = PSC × (1 + Σ Uplift %) + Σ Uplift $
```

### 4.1 Import SKU Data

1. Click the **Import** tab
2. Click **Choose File** and select your CSV or Excel file
3. Required columns: `Service PN`, `Standard Cost (Base Cost)`, `Country`, `Service Tier`, `GEO`

**Supported formats:**
- **CSV**: Simple flat format. Click **Download Template** to get a sample.
- **Excel (.xlsx)**: 3-sheet format from Wukong export.

**Large files** (50K+ rows): The tool automatically uses streaming import — you'll see a progress bar and the job completes in the background. Current limit: ~200K rows.

### 4.2 Uplift Rules

Uplift rules determine how much to add to the base cost based on product dimensions.

1. Go to **Uplift** tab → **Uplift Values**
2. Click **Import Uplift CSV** to load your uplift values file
3. Each rule has: `Factor Name`, `Factor Values` (dimension match), `Uplift Value` (%), `Status` (Released/Draft/Retired)

**How matching works**: The engine matches each SKU against all "Released" rules. If a SKU's attributes match a rule's factor values, that uplift percentage is applied.

### 4.3 AIPC Attribute

The **AIPC** column marks whether a Service PN is AIPC-enabled. Click the green/gray badge in the data grid to toggle Yes/No. AIPC is registered as an uplift factor — you can create rules like "AIPC=Yes → +10%".

### 4.4 Calculate & Send to Stage 4

1. Go to **Calculate** tab → click **Run Calculation**
2. Review results in the data grid
3. Go to **Export** tab → click **Send to Stage 4**

This automatically opens Stage 4 in a new tab with the data pre-loaded.

---

## 5. Stage 4 — GVE Validation

**What it does**: Validates the Sales Cost matrix against pricing rules (GVE = Global Value Engine).

### 5.1 Import from Stage 3

When Stage 4 opens from Stage 3's "Send to Stage 4", data is automatically imported. Otherwise:
1. Click **Create Cycle**, name it
2. Click **Import from Stage 3** (Bridge) on the dashboard

### 5.2 GVE Validation (4 Layers)

| Layer | Rule | Example |
|-------|------|---------|
| **L1** | Monotonicity | 1YR < 3YR < 5YR for same tier |
| **L2** | Ratio Bands | 3YR ÷ 1YR must be 1.8–2.8 |
| **L3** | Cross-Geo Deviation | Same tier/term across countries: max deviation < 20% |
| **L4** | YoY Drift | Current vs. last year: max change 25%/20% |

**How to run**: Click **Run GVE** on the dashboard. Results show PASS/BLOCKED/WARNINGS status per PN.

### 5.3 CrossCheck Engine

Additional rule-based validation:
- **Priority rules**: e.g., TP Halo ≥ TP Workstation (price hierarchy)
- **Term rules**: 1YR < 3YR < 5YR
- **GEO-scoped rules**: country-specific constraints
- **Custom rules**: Create your own via the Rule Designer

### 5.4 Rule Designer

1. Go to **CrossCheck** tab → **Rule Designer**
2. Define: factor, operator (≤ / ≥ / =), comparison factor, scope
3. Save → rule appears in CrossCheck engine

### 5.5 Export

- **Export GVE Results**: Excel with all violations
- **Export CC Results**: CrossCheck results
- **Batch Acknowledge**: Group violations by root cause, acknowledge all at once

---

## 6. Stage 5 — List Price Derivation

**What it does**: Derives Channel Price and List Price from Sales Cost using PFV (Price Floor Value) benchmarks.

### Formula
```
PFV = Base PFV + Σ Add-on PFV (ADP + KYD + SBTY + TICRU + Priority)
Adj PFV = PFV × Regional Factor
List Price / Channel Price = Adj PFV × TopSeller Factor × (1 ± Ratio)
GP% = (Channel Price − Sales Cost) / Channel Price
```

### 6.1 Import Data

1. Click **Import from Stage 4** (Bridge) — brings in Sales Cost data
2. Go to **PFV** tab → import PFV benchmark file

**PFV file format (CSV)**:
```
tier,term_years,delivery_type,geo,base,adp,kyd,sbty,ticru,priority
TP Premium,3,Onsite,DE,318,50,30,20,15,10
```

### 6.2 Pricing Models

Two calculation models available:

| Model | Direction | Use Case |
|-------|-----------|----------|
| **C→L** | Cost → List | Start from Sales Cost, derive List Price |
| **L→C** | List → Cost | Start from target List Price, back-calculate required cost |

### 6.3 GP Floor Rules

GP Floor ensures minimum profitability. Now supports **multi-dimensional rules**:

| Dimension | Example Values |
|-----------|---------------|
| **Country** | GB, DE, FR, US, AR... |
| **SLA Type** | Onsite, Offsite, Premier... |
| **Term** | 1YR, 2YR, 3YR, 4YR, 5YR |
| **GP Floor %** | e.g., 30% |

**Matching priority**: Exact match (Country + SLA + Term) → Country + SLA → Country only → Global default (30%)

**How to configure**: Settings → GP Floor Rules → Add Rule. Rules with higher specificity override generic ones.

### 6.4 Calculate & Send to Stage 6

1. Click **Calculate** → review results (List Price, Channel Price, GP%)
2. Click **Send to Stage 6** — auto-opens Stage 6 with data pre-loaded

---

## 7. Stage 6 — Price Gradient Validation

**What it does**: Validates final List Prices across 3 structural layers to ensure pricing integrity.

### 7.1 Import from Stage 5

Data is auto-imported via Bridge when opened from Stage 5.

### 7.2 Validation Layers

| Layer | Rule | What It Checks |
|-------|------|---------------|
| **L1** | Monotonicity | Higher tier → higher price |
| **L2** | Ratio Bands | Price ratios between tiers/terms are reasonable |
| **L3** | Cross-Geo | Same product across countries has consistent pricing |

> **Note**: Stage 6 uses the same GVE engine as Stage 4, but L4 (YoY Drift) is disabled for standalone mode.

### 7.3 Results & Export

- Pass/Fail/Warn status per PN
- Export results to Excel with detailed violation info
- Each violation shows: which layer, expected range, actual value

---

## 8. Dashboard — Pricing History

**What it does**: Your personal pricing database. View all cycles, track PN pricing over time, export/import data.

### 8.1 Main View

The dashboard landing page shows:
- **Stats cards**: Total Cycles, Unique PNs, Total Records, Latest Activity
- **Cycle table**: All pricing cycles with PN count, average GP%, last updated

### 8.2 View a Cycle

Click any **cycle name** → shows all PNs in that cycle with:
- Service PN, Country, Tier, Term
- Sales Cost, List Price, Channel Price, GP%
- GVE status, Gradient status
- **Trend** button for each PN

**Search**: Use the search box to filter by PN.

### 8.3 PN History & Trends

Click **Trend** on any PN → shows:
1. **Pricing History table**: All cycles this PN appeared in, with prices/GP% per cycle
2. **GP% Trend**: Shows ▲+Xpp or ▼-Xpp between oldest and newest cycle
3. **Change Log**: Field-level audit trail — every time a value was changed, who changed it, old→new values

### 8.4 CSV Export

Click **Export CSV** → downloads the complete pricing database as a CSV file. You can:
- Open in Excel for analysis
- Share with colleagues
- Archive as backup

### 8.5 CSV Import

Click **Import CSV** → select a CSV file → records are upserted into the database:
- **New records** (PN + Cycle not in DB) → added
- **Existing records** → updated (field changes are logged)

The CSV format matches the export format, so you can export → edit in Excel → import back.

---

## 9. Data Persistence & Backup

### Where is my data?

All pricing data is stored in a **SQLite database** (`pricing_master.db`) in the project folder. This is the primary store. CSV is an export/import format.

### Backup strategy

1. **Daily**: Export CSV from Dashboard → save to a safe location
2. **Before major changes**: Export CSV as snapshot
3. **Automatic**: Every field change is logged in the audit trail

### Restore

If you need to restore from a CSV backup:
1. Dashboard → **Import CSV** → select your backup file
2. Records are upserted — existing data is updated, new data is added

---

## 10. Tips & Best Practices

### Cycle Naming
Use a consistent naming convention: `FY26_Q3_EMEA`, `FY26_Q3_AP`, etc. This makes Dashboard filtering and PN history tracking more useful.

### GP Floor
Start with a global 30% threshold, then add country/SLA-specific rules as you discover regional differences. The more specific rules automatically override the global default.

### Large Data Sets
- **10K rows**: Instant import
- **50K rows**: ~20-40 seconds, streaming progress bar
- **100K+ rows**: Use streaming import (automatic for files > 500KB)

### Cross-Stage Workflow
Always use the **Bridge** (Send to Stage N+1) buttons — they auto-transfer data and open the next stage with everything pre-loaded. Don't export CSV from one stage and import to the next manually.

### Audit Trail
The Change Log in Dashboard tracks every field-level change. Use it to:
- Review who changed what
- Understand pricing decisions over time
- Revert to previous values if needed

---

## Appendix: Quick Reference

### Startup
```bash
python3 server.py 8080
# Open: http://localhost:8080/GPS_Cost_Pricing_Workbench.html
```

### Key URLs
| Page | URL |
|------|-----|
| Launcher | `/GPS_Cost_Pricing_Workbench.html` |
| Stage 3 | `/stage3_browser/index.html` |
| Stage 4 | `/stage4_browser/index.html` |
| Stage 5 | `/stage5_browser/index.html` |
| Stage 6 | `/stage6_browser/index.html` |
| Dashboard | `/dashboard_browser/index.html` |

### API Endpoints (for reference)
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/load-master` | Load all records |
| POST | `/api/save-master` | Upsert one record |
| GET | `/api/pn-history?pn=xxx` | Get change log for a PN |
| GET | `/api/export-csv` | Download full CSV |
| POST | `/api/import-csv` | Bulk import CSV |

---

*© 2026 HongfeiZhu · SSGCDTO · Lenovo. All rights reserved.*
