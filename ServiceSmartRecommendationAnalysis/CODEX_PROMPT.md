# Codex Prompt for SSR Analysis Project

You are taking over the **Service Smart Recommendation (SSR) Analysis** project — quantifying the business impact of Lenovo ISG's AI-powered service recommendation engine.

## WHAT THIS PROJECT IS

Lenovo ISG deployed an AI recommendation engine that suggests service products (warranty/support contracts) during hardware configuration. Sellers can accept, replace, or skip the AI's recommendation. The project ran from Aug 2025 (EMEA pilot) through Mar 2026.

**Your job**: Analyze real transaction data to determine how much incremental revenue this AI engine actually generated — stripping out organic growth, hardware price effects, and Windows 10 end-of-support cycle artifacts.

## THE TWO SUB-PROJECTS

### A. Post-hoc KPI Analysis (`ServiceSmartRecommendationAnalysis/`)
The completed quantitative analysis. Three phases:

**Phase 1 — Operational KPIs** (configuration-stage data):
- Metrics: Coverage, Acceptance Rate, Attach Rate
- Key stratification: New CTO vs Copied CTO (New CTO acceptance is 30-42pp lower — the biggest improvement lever)
- FY24 baseline: EMEA Coverage 74.4%, Acceptance 37.5%, Attach 53.1%
- Post-project: Coverage 94.4%, Acceptance 54.4%, Attach 73.6%

**Phase 2 V1 — Financial KPIs, conservative** ($13.6M):
- Method: Difference-in-Differences (DiD) + revenue decomposition
- Controls for: organic Lenovo growth (14.4%), HW ASP inflation, W10 EOS cycle
- DO NOT assume fixed 75% ASP pass-through — compute it from data (varies -3.9x to +10x)
- DO NOT apply subjective attribution rate on top of DiD (double-counting)

**Phase 2 V2 — Financial KPIs, optimistic** ($28.3M):
- Method: Constant service price framework (assume service prices unchanged YoY → all $/HW growth = project contribution)
- Simpler, management-friendly. $/HW growth rate × service revenue = contribution

**Phase 3 — Integration**: Cross-validate operational ↔ financial KPIs (correlation +0.87). True contribution: $14-28M.

### B. Forward-looking Architecture Design (`SSG_AI/ISG_SSR/`)
Design docs for SSR's next version: XGBoost recommendation model, LLM-generated explanations, Catalog integration API schema.

## DATA SOURCES

| File | Size | What's Inside |
|------|------|---------------|
| `Ai_Report_20250815~20260306.xlsx` | 68MB | 268K config transactions, 38 columns |
| `Ai_Report_2026-04-01(3.17-4.01).xlsx` | 8.6MB | Supplementary config data |
| `ESS Smart Recommendation Performance_Q4 analysis.xlsx` | 6.1MB | Q4 orders: Sheet1=70K rows, Sheet3=GEO×Quarter pivot |
| `ESS Smart Recommendation Performance_Q3 analysis.xlsx` | 7.0MB | Q3 orders, same structure |

**Always start from Sheet3 (pre-aggregated pivot)** before diving into raw data.

## CRITICAL DEFINITIONS
- **Fiscal year**: Q1=Apr-Jun, Q2=Jul-Sep, Q3=Oct-Dec, Q4=Jan-Mar
- **EMEA launch**: Pilot Aug 15 (Q2), Full Sep 28 (Q3)
- **WW launch**: Nov 28 (Q3)
- **Contract-to-revenue lag**: 1-2 months (→ NA/AP/LA Q3 revenue NOT affected by project)
- **$/HW** = Service Revenue ÷ Hardware Units (primary financial metric)

## KEY PITFALLS (DO NOT REPEAT)

1. **"Acceptance declining" ≠ system failure.** Check Mix Effect first: New CTO share growing → drags overall acceptance down, but New CTO acceptance itself may be improving
2. **NA negative growth (-1.6% $/HW) ≠ project failure.** NA has #1 absolute $/HW ($51.07), #1 ACV ($89K), but was on an unsustainable W10 EOS peak. The project provided defensive value ($3-6M)
3. **Establish FY24 baseline BEFORE judging any trend.** 37% was normal acceptance pre-project; 50%+ post-project is excellent
4. **Compute ASP pass-through from data, don't assume 75%.** Real values range from -3.9x to +10x
5. **DiD already controls for organic growth.** Don't layer another attribution rate on top

## YOUR FIRST STEPS

1. Read `CODEX_HANDOFF.md` for the complete project context
2. Read `background.txt` for the original task
3. Verify which data files are available
4. Read existing HTML analysis reports in `validation_output/`
5. If asked to run new analysis: reuse the methodology framework from existing scripts (`phase1_analysis.py`, `build_report.py`)
6. If data files are missing: ask me before guessing

## COMMUNICATION STYLE
- Present findings directly in Chinese
- Use structured tables over narrative paragraphs
- Flag contradictions with prior analysis immediately
- Ask for clarification when blocked — don't guess
