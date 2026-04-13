"""
GPS Cost Pricing Workbench — User Manual Generator
Generates GPS_Cost_Pricing_Workbench_UserManual.pptx in the same folder.
Run this script whenever the manual needs to be refreshed.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy

# ── Lenovo colour palette ──────────────────────────────────────────────────────
LENOVO_RED    = RGBColor(0xE6, 0x00, 0x12)   # #E60012
LENOVO_DARK   = RGBColor(0x1A, 0x1A, 0x2E)   # near-black navy
LENOVO_MID    = RGBColor(0x2E, 0x86, 0xAB)   # steel blue accent
LENOVO_LIGHT  = RGBColor(0xF4, 0xF4, 0xF4)   # off-white bg
WHITE         = RGBColor(0xFF, 0xFF, 0xFF)
BLACK         = RGBColor(0x00, 0x00, 0x00)
GREY_TEXT     = RGBColor(0x55, 0x55, 0x55)
AMBER         = RGBColor(0xFF, 0xA5, 0x00)
GREEN         = RGBColor(0x22, 0x8B, 0x22)
STAGE3_COLOR  = RGBColor(0x2E, 0x86, 0xAB)   # blue for Stage 3
STAGE4_COLOR  = RGBColor(0x8B, 0x45, 0x13)   # brown-orange for Stage 4
STAGE5_COLOR  = RGBColor(0x19, 0x6F, 0x3D)   # dark green for Stage 5
STAGE6_COLOR  = RGBColor(0x7D, 0x3C, 0x98)   # purple for Stage 6

# Slide dimensions: 13.33 x 7.5 inches (widescreen 16:9)
W = Inches(13.33)
H = Inches(7.5)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H

BLANK = prs.slide_layouts[6]   # completely blank layout


# ── helpers ───────────────────────────────────────────────────────────────────

def add_rect(slide, l, t, w, h, fill_rgb=None, line_rgb=None, line_width_pt=0):
    shape = slide.shapes.add_shape(1, l, t, w, h)
    shape.line.fill.background()
    if fill_rgb:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_rgb
    else:
        shape.fill.background()
    if line_rgb:
        shape.line.color.rgb = line_rgb
        shape.line.width = Pt(line_width_pt or 1)
    else:
        shape.line.fill.background()
    return shape


def add_text_box(slide, text, l, t, w, h,
                 font_size=14, bold=False, italic=False,
                 color=BLACK, align=PP_ALIGN.LEFT,
                 wrap=True, font_name="Calibri"):
    txb = slide.shapes.add_textbox(l, t, w, h)
    tf  = txb.text_frame
    tf.word_wrap = wrap
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(font_size)
    run.font.bold  = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name  = font_name
    return txb


def add_header_bar(slide, title, subtitle="", bg=LENOVO_DARK, bar_h=Inches(1.35)):
    add_rect(slide, 0, 0, W, bar_h, fill_rgb=bg)
    add_text_box(slide, title,
                 Inches(0.4), Inches(0.12), Inches(12.0), Inches(0.75),
                 font_size=28, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    if subtitle:
        add_text_box(slide, subtitle,
                     Inches(0.4), Inches(0.85), Inches(12.0), Inches(0.42),
                     font_size=15, color=RGBColor(0xCC, 0xCC, 0xCC), align=PP_ALIGN.LEFT)


def add_section_label(slide, label, color=LENOVO_MID):
    add_rect(slide, Inches(11.5), Inches(0.1), Inches(1.6), Inches(0.35), fill_rgb=color)
    add_text_box(slide, label,
                 Inches(11.5), Inches(0.12), Inches(1.6), Inches(0.35),
                 font_size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)


def bullet_block(slide, items, l, t, w, h,
                 font_size=13, title=None, title_size=15,
                 title_color=LENOVO_DARK, bullet_color=GREY_TEXT,
                 indent="  - "):
    txb = slide.shapes.add_textbox(l, t, w, h)
    tf  = txb.text_frame
    tf.word_wrap = True
    first = True
    if title:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        r = p.add_run()
        r.text = title
        r.font.bold = True
        r.font.size = Pt(title_size)
        r.font.color.rgb = title_color
        r.font.name = "Calibri"
    for item in items:
        p = tf.paragraphs[0] if (first and not title) else tf.add_paragraph()
        first = False
        r = p.add_run()
        r.text = f"{indent}{item}"
        r.font.size = Pt(font_size)
        r.font.color.rgb = bullet_color
        r.font.name = "Calibri"


def divider(slide, y=Inches(1.35)):
    add_rect(slide, 0, y, W, Pt(2), fill_rgb=LENOVO_RED)


def add_badge(slide, text, l, t, w=Inches(1.4), h=Inches(0.35), color=LENOVO_MID):
    add_rect(slide, l, t, w, h, fill_rgb=color)
    add_text_box(slide, text, l, t, w, h,
                 font_size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)


def new_slide(title, subtitle="", bg=LENOVO_DARK, label=None, label_color=LENOVO_MID):
    s = prs.slides.add_slide(BLANK)
    add_header_bar(s, title, subtitle, bg=bg)
    divider(s)
    if label:
        add_section_label(s, label, color=label_color)
    return s


# =============================================================================
# SLIDE 1 — Cover
# =============================================================================
s1 = prs.slides.add_slide(BLANK)

# Full dark background
add_rect(s1, 0, 0, W, H, fill_rgb=LENOVO_DARK)

# Red accent bar at bottom
add_rect(s1, 0, Inches(6.9), W, Inches(0.6), fill_rgb=LENOVO_RED)

# Top red accent line
add_rect(s1, 0, 0, W, Inches(0.08), fill_rgb=LENOVO_RED)

# Main title
add_text_box(s1, "GPS Cost Pricing Workbench",
             Inches(0.6), Inches(1.6), Inches(12.0), Inches(1.1),
             font_size=38, bold=True, color=WHITE, align=PP_ALIGN.LEFT)

# Subtitle
add_text_box(s1, "User Manual  |  Stage 3: Sales Cost  \u00b7  Stage 4: GVE Validation",
             Inches(0.6), Inches(2.75), Inches(12.0), Inches(0.55),
             font_size=20, bold=False, color=RGBColor(0xCC, 0xCC, 0xCC), align=PP_ALIGN.LEFT)

# Sub-subtitle
add_text_box(s1, "Lenovo Global Product Support (GPS) \u2014 SSGCDTO Division",
             Inches(0.6), Inches(3.35), Inches(12.0), Inches(0.45),
             font_size=15, italic=True, color=RGBColor(0x99, 0xBB, 0xCC), align=PP_ALIGN.LEFT)

# Horizontal divider line
add_rect(s1, Inches(0.6), Inches(4.0), Inches(10.0), Pt(1.5), fill_rgb=LENOVO_MID)

# Version bottom left
add_text_box(s1, "Version 2.0  \u00b7  March 2026",
             Inches(0.6), Inches(6.92), Inches(4.0), Inches(0.42),
             font_size=12, color=WHITE, align=PP_ALIGN.LEFT)

# Internal use only bottom right
add_text_box(s1, "INTERNAL USE ONLY",
             Inches(9.0), Inches(6.92), Inches(4.1), Inches(0.42),
             font_size=12, bold=True, color=AMBER, align=PP_ALIGN.RIGHT)

# Copyright very bottom
add_text_box(s1, "\u00a9 2026 HongfeiZhu \u00b7 SSGCDTO \u00b7 Lenovo. All rights reserved.",
             Inches(0.6), Inches(7.2), Inches(12.0), Inches(0.28),
             font_size=9, color=RGBColor(0x88, 0x88, 0x88), align=PP_ALIGN.CENTER)


# =============================================================================
# SLIDE 2 — Table of Contents
# =============================================================================
s2 = new_slide("Table of Contents", "GPS Cost Pricing Workbench — User Manual")

# Section background panels
add_rect(s2, Inches(0.3), Inches(1.5), Inches(6.2), Inches(5.7), fill_rgb=LENOVO_LIGHT,
         line_rgb=LENOVO_MID, line_width_pt=1)
add_rect(s2, Inches(6.8), Inches(1.5), Inches(6.2), Inches(5.7), fill_rgb=LENOVO_LIGHT,
         line_rgb=LENOVO_MID, line_width_pt=1)

# Left column header
add_text_box(s2, "Sections 1 \u2013 10",
             Inches(0.5), Inches(1.55), Inches(4.0), Inches(0.35),
             font_size=11, bold=True, color=LENOVO_DARK)

left_items = [
    "1.   Tool Overview & Pipeline",
    "2.   Architecture \u2014 Browser Edition",
    "3.   Getting Started",
    "4.   Stage 3 \u2014 Sales Cost Overview",
    "5.   Stage 3 \u2014 SKU Data Import",
    "6.   Stage 3 \u2014 Uplift Rules",
    "7.   Stage 3 \u2014 Uplift Values",
    "8.   Stage 3 \u2014 Run Calculation",
    "9.   Stage 3 \u2014 Export & Send to Stage 4",
    "10.  Stage 4 \u2014 GVE Validation Overview",
]

bullet_block(s2, left_items, Inches(0.5), Inches(1.95), Inches(5.8), Inches(5.0),
             font_size=12, bullet_color=LENOVO_DARK, indent="")

# Right column header
add_text_box(s2, "Sections 11 \u2013 25",
             Inches(7.0), Inches(1.55), Inches(4.0), Inches(0.35),
             font_size=11, bold=True, color=LENOVO_DARK)

right_items = [
    "11.  Stage 4 \u2014 Import Data & Settings",
    "12.  Stage 4 \u2014 Matrix View",
    "13.  Stage 4 \u2014 GVE Validation (4 Layers)",
    "14.  Stage 4 \u2014 List Price Computation",
    "15.  Stage 4 \u2014 Submit & Export",
    "16.  Stage 5 \u2014 List Price Calculator Overview",
    "17.  Stage 5 \u2014 Import & Settings",
    "18.  Stage 5 \u2014 Calculate & Results",
    "19.  Stage 6 \u2014 Price Gradient Validation",
    "20.  Stage 6 \u2014 Validation Layers",
    "21.  Pricing Pipeline Handoff Workflow",
    "22.  Offline Setup",
    "23.  Roadmap \u2014 Coming Next",
]

bullet_block(s2, right_items, Inches(7.0), Inches(1.95), Inches(5.8), Inches(5.0),
             font_size=12, bullet_color=LENOVO_DARK, indent="")


# =============================================================================
# SLIDE 3 — Tool Overview & Pipeline
# =============================================================================
s3 = new_slide("Tool Overview & Pipeline",
               "GPS Cost Pricing Workbench \u2014 6-Stage End-to-End Pricing Process")

GREY_STAGE = RGBColor(0xAA, 0xAA, 0xAA)
COMING_BG  = RGBColor(0xDD, 0xDD, 0xDD)

# Pipeline stage boxes — 6 stages across
stages = [
    ("Stage 1", "Standard Cost\nImport", COMING_BG, GREY_TEXT, "COMING SOON"),
    ("Stage 2", "Forward Adj.\n(PSC)", COMING_BG, GREY_TEXT, "COMING SOON"),
    ("Stage 3", "Sales Cost\nCalculator", STAGE3_COLOR, WHITE, "ACTIVE"),
    ("Stage 4", "GVE Validation\nEngine", STAGE4_COLOR, WHITE, "ACTIVE"),
    ("Stage 5", "List Price\nCalculator", STAGE5_COLOR, WHITE, "ACTIVE"),
    ("Stage 6", "Price Gradient\nValidation", STAGE6_COLOR, WHITE, "ACTIVE"),
]

box_w = Inches(1.8)
box_h = Inches(1.5)
box_t = Inches(1.6)
gap   = Inches(0.2)
arrow_w = Inches(0.15)
start_l = Inches(0.35)

for i, (stg_lbl, stg_name, bg, fg, status) in enumerate(stages):
    lpos = start_l + i * (box_w + gap + arrow_w)

    # Arrow between stages
    if i > 0:
        arrow_l = lpos - arrow_w - gap
        add_rect(s3, arrow_l + gap, box_t + Inches(0.6), arrow_w, Pt(3), fill_rgb=GREY_TEXT)

    # Stage box
    add_rect(s3, lpos, box_t, box_w, box_h, fill_rgb=bg,
             line_rgb=LENOVO_DARK, line_width_pt=1)

    # Stage label
    label_color = WHITE if bg not in [COMING_BG] else GREY_TEXT
    add_text_box(s3, stg_lbl,
                 lpos, box_t + Inches(0.1), box_w, Inches(0.3),
                 font_size=9, bold=True, color=label_color, align=PP_ALIGN.CENTER)

    # Stage name
    add_text_box(s3, stg_name,
                 lpos, box_t + Inches(0.35), box_w, Inches(0.75),
                 font_size=10, bold=True, color=fg, align=PP_ALIGN.CENTER)

    # Status badge at bottom of box
    status_color = GREEN if status == "ACTIVE" else GREY_STAGE
    add_rect(s3, lpos + Inches(0.3), box_t + box_h - Inches(0.32),
             box_w - Inches(0.6), Inches(0.28), fill_rgb=status_color)
    add_text_box(s3, status,
                 lpos + Inches(0.3), box_t + box_h - Inches(0.32),
                 box_w - Inches(0.6), Inches(0.28),
                 font_size=8, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# Two bullet columns below pipeline
add_rect(s3, Inches(0.35), Inches(3.35), Inches(6.0), Inches(3.85),
         fill_rgb=LENOVO_LIGHT, line_rgb=STAGE3_COLOR, line_width_pt=1)
add_rect(s3, Inches(6.7), Inches(3.35), Inches(6.3), Inches(3.85),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)

bullet_block(s3, [
    "Stage 3 (ACTIVE): Imports PSC SKU data, applies dimension-driven uplift rules",
    "  Sales Cost = PSC x (1 + Total Uplift Ratio)",
    "Stage 4 (ACTIVE): Validates sales cost matrix with 4 GVE layers",
    "  L1 Monotonicity  |  L2 Ratio Bands  |  L3 Cross-Geo  |  L4 YoY Drift",
    "Stage 5 (ACTIVE): Derives Channel Price and List Price from Sales Cost + PFV",
    "  C-Price model (C\u2192L) and L-Price model (L\u2192C) with geo-group regional factors",
    "Stage 6 (ACTIVE): Validates list price gradient across 3 structural layers",
    "  L1 Monotonicity  |  L2 Ratio Bands  |  L3 Cross-Geo Deviation",
    "Stage 1 / 2: Standard Cost import, PSC forward adjustment  (in development)",
],
    Inches(0.5), Inches(3.4), Inches(5.7), Inches(3.7),
    font_size=11, title="Active Stages", title_size=14,
    title_color=STAGE3_COLOR, bullet_color=GREY_TEXT)

bullet_block(s3, [
    "Standard Cost  (Stage 1 input)",
    "  |  x F_failure x F_parts x F_labor x F_mix",
    "Projected Service Cost / PSC  (Stage 2 output)",
    "  |  x (1 + Total Uplift Ratio)",
    "Sales Cost  (Stage 3 output)",
    "  |  GVE 4-layer validation",
    "Validated Sales Cost  (Stage 4 output)",
    "  |  x PFV factor + geo-group uplift",
    "Channel Price / List Price  (Stage 5 output)",
    "  |  3-layer gradient validation",
    "Validated List Price  (Stage 6 output)",
],
    Inches(6.85), Inches(3.4), Inches(6.0), Inches(3.7),
    font_size=11, title="Formula Chain", title_size=14,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT, indent="  ")


# =============================================================================
# SLIDE 4 — Architecture: Browser Edition
# =============================================================================
s4 = new_slide("Architecture \u2014 Browser Edition",
               "Pure HTML + JavaScript \u2014 No installation required")

# Left panel
add_rect(s4, Inches(0.3), Inches(1.5), Inches(5.8), Inches(5.7),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)

bullet_block(s4, [
    "No server, no Python, no installation required",
    "Opens directly in Chrome or Edge (double-click HTML file)",
    "Data stored in browser IndexedDB (Dexie.js)",
    "Excel import/export via SheetJS (xlsx.js)",
    "Works offline after running setup_offline_all.bat",
    "",
    "Each stage is a self-contained single-page app",
    "Cycles and data persist across browser sessions",
    "No login credentials \u2014 name entry for audit trail only",
],
    Inches(0.45), Inches(1.55), Inches(5.5), Inches(5.6),
    font_size=13, title="How It Works", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)

# Right panel — file structure
add_rect(s4, Inches(6.4), Inches(1.5), Inches(6.6), Inches(5.7),
         fill_rgb=RGBColor(0x1A, 0x1A, 0x2E), line_rgb=LENOVO_MID, line_width_pt=1)

add_text_box(s4, "File Structure",
             Inches(6.6), Inches(1.6), Inches(6.0), Inches(0.4),
             font_size=14, bold=True, color=WHITE)

structure_lines = [
    "GPS_Cost_Pricing_Workbench/",
    "  GPS_Cost_Pricing_Workbench.html    <- Launcher",
    "  setup_offline_all.bat              <- Offline setup",
    "  build_manual.py                    <- Manual generator",
    "",
    "  stage3_browser/   index.html  dexie.min.js  xlsx.full.min.js",
    "  stage4_browser/   index.html  dexie.min.js  xlsx.full.min.js",
    "  stage5_browser/   index.html  dexie.min.js  xlsx.full.min.js",
    "  stage6_browser/   index.html  dexie.min.js",
    "",
    "  Each stage is a self-contained single-page app.",
    "  Stage 5 & 6 share an IndexedDB: Stage 6 reads",
    "  list prices computed by Stage 5 directly from",
    "  the browser's local storage — no file export needed.",
]

bullet_block(s4, structure_lines,
             Inches(6.6), Inches(2.05), Inches(6.1), Inches(5.0),
             font_size=11, bullet_color=RGBColor(0xAA, 0xDD, 0xFF), indent="")


# =============================================================================
# SLIDE 5 — Getting Started
# =============================================================================
s5 = new_slide("Getting Started",
               "First-time setup and launching the tool")

steps = [
    ("1", "Offline Setup (IMPORTANT \u2014 First Time Only)",
     "Run setup_offline_all.bat from the GPS_Cost_Pricing_Workbench folder. "
     "Downloads Dexie.js and SheetJS locally. Required if your network blocks CDN scripts."),
    ("2", "Launch the Tool",
     "Double-click GPS_Cost_Pricing_Workbench.html. The launcher opens in your default "
     "browser showing all 6 stages (Stages 1 and 2 marked Coming Soon)."),
    ("3", "Open a Stage",
     "Click any active stage (3, 4, 5, or 6) from the launcher. "
     "Stages 1 and 2 are in development."),
    ("4", "Enter Your Name",
     "Each stage has a login screen. Enter your name \u2014 used for audit logging only, "
     "no password required."),
    ("5", "Create a Pricing Cycle",
     "From the dashboard, click '+ New Cycle' and enter the cycle name "
     "(e.g. FY26 Q2 EMEA) and fiscal year."),
]

step_h = Inches(1.0)
step_t = Inches(1.5)
step_gap = Inches(0.08)

for i, (num, title_txt, desc_txt) in enumerate(steps):
    t = step_t + i * (step_h + step_gap)

    # Number badge
    add_rect(s5, Inches(0.3), t, Inches(0.55), step_h,
             fill_rgb=LENOVO_DARK, line_rgb=LENOVO_RED, line_width_pt=2)
    add_text_box(s5, num, Inches(0.3), t + Inches(0.28), Inches(0.55), Inches(0.45),
                 font_size=18, bold=True, color=LENOVO_RED, align=PP_ALIGN.CENTER)

    # Step box
    box_color = RGBColor(0xEA, 0xF4, 0xF8) if i % 2 == 0 else LENOVO_LIGHT
    add_rect(s5, Inches(0.95), t, Inches(12.0), step_h,
             fill_rgb=box_color, line_rgb=LENOVO_MID, line_width_pt=1)

    add_text_box(s5, title_txt,
                 Inches(1.1), t + Inches(0.06), Inches(11.7), Inches(0.35),
                 font_size=13, bold=True, color=LENOVO_DARK)
    add_text_box(s5, desc_txt,
                 Inches(1.1), t + Inches(0.42), Inches(11.7), Inches(0.52),
                 font_size=11, color=GREY_TEXT)


# =============================================================================
# SLIDE 6 — Stage 3 Overview
# =============================================================================
s6 = new_slide("Stage 3 \u2014 Sales Cost Calculator",
               "Calculate Sales Cost from PSC using dimension-driven uplift rules",
               label="Stage 3", label_color=STAGE3_COLOR)

# Formula highlight box
add_rect(s6, Inches(0.3), Inches(1.5), Inches(12.7), Inches(0.65),
         fill_rgb=STAGE3_COLOR, line_rgb=LENOVO_DARK, line_width_pt=1)
add_text_box(s6, "Sales Cost  =  PSC  x  (1 + Total Uplift Ratio)",
             Inches(0.5), Inches(1.55), Inches(12.0), Inches(0.55),
             font_size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# Workflow tabs row
tab_labels = ["SKU Data", "Uplift", "Calculate", "Export"]
tab_w = Inches(2.1)
tab_gap = Inches(0.25)
tab_t = Inches(2.3)
tab_start = Inches(0.5)
for i, lbl in enumerate(tab_labels):
    tl = tab_start + i * (tab_w + tab_gap)
    add_rect(s6, tl, tab_t, tab_w, Inches(0.38),
             fill_rgb=LENOVO_DARK, line_rgb=STAGE3_COLOR, line_width_pt=1)
    add_text_box(s6, lbl, tl, tab_t, tab_w, Inches(0.38),
                 font_size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    if i < len(tab_labels) - 1:
        arrow_l = tl + tab_w + Inches(0.04)
        add_text_box(s6, ">", arrow_l, tab_t + Inches(0.05), Inches(0.18), Inches(0.3),
                     font_size=14, bold=True, color=STAGE3_COLOR, align=PP_ALIGN.CENTER)

# Left column
add_rect(s6, Inches(0.3), Inches(2.85), Inches(6.0), Inches(4.35),
         fill_rgb=LENOVO_LIGHT, line_rgb=STAGE3_COLOR, line_width_pt=1)

bullet_block(s6, [
    "Imports SKU data (Excel 3-sheet format or CSV)",
    "Matches each SKU to a Released uplift rule",
    "Applies factor-based uplift ratios per dimension",
    "Calculates Sales Cost per SKU",
    "Exports results to CSV/Excel or directly to Stage 4",
],
    Inches(0.45), Inches(2.9), Inches(5.7), Inches(4.2),
    font_size=13, title="What Stage 3 Does", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)

# Right column
add_rect(s6, Inches(6.7), Inches(2.85), Inches(6.3), Inches(4.35),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)

bullet_block(s6, [
    "Layer 1: 18 pre-defined uplift factor definitions",
    "  COUNTRY, SRVTIER, SDTYPE, GEO, WARRANTY, TERM...",
    "Layer 2: Uplift Rules",
    "  Scope = (Type of Service + GEO)",
    "  Specifies which factors apply to that segment",
    "Layer 3: Uplift Values",
    "  Released values with match values & ratios per factor",
    "  Total Uplift = sum of all matching factor ratios",
],
    Inches(6.85), Inches(2.9), Inches(6.0), Inches(4.2),
    font_size=13, title="The 3-Layer Uplift System", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)


# =============================================================================
# SLIDE 7 — Stage 3: SKU Data Import
# =============================================================================
s7 = new_slide("Stage 3 \u2014 SKU Data Import",
               "Importing your pricing SKU data",
               label="Stage 3", label_color=STAGE3_COLOR)

# Option A panel
add_rect(s7, Inches(0.3), Inches(1.5), Inches(6.0), Inches(4.45),
         fill_rgb=LENOVO_LIGHT, line_rgb=STAGE3_COLOR, line_width_pt=2)
add_rect(s7, Inches(0.3), Inches(1.5), Inches(6.0), Inches(0.4), fill_rgb=STAGE3_COLOR)
add_text_box(s7, "Option A \u2014 Excel Import (3-Sheet Format)",
             Inches(0.4), Inches(1.52), Inches(5.8), Inches(0.38),
             font_size=12, bold=True, color=WHITE)

bullet_block(s7, [
    "Sheet 1  'Maintenance and Search UI'",
    "  SKU data rows: Part#, Tier, PSC, GEO, Country, etc.",
    "Sheet 2  'Custom Uplift Factors Catalog'",
    "  Uplift Rule definitions exported from Stage 3",
    "Sheet 3  'Customize Uplift Formula'",
    "  Uplift Value definitions exported from Stage 3",
    "",
    "Use the 'Download Template' button for the correct format",
    "All 3 sheets are imported together in one operation",
],
    Inches(0.45), Inches(1.98), Inches(5.7), Inches(3.85),
    font_size=12, bullet_color=GREY_TEXT)

# Option B panel
add_rect(s7, Inches(6.7), Inches(1.5), Inches(6.3), Inches(4.45),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=2)
add_rect(s7, Inches(6.7), Inches(1.5), Inches(6.3), Inches(0.4), fill_rgb=LENOVO_MID)
add_text_box(s7, "Option B \u2014 CSV Paste",
             Inches(6.8), Inches(1.52), Inches(6.0), Inches(0.38),
             font_size=12, bold=True, color=WHITE)

bullet_block(s7, [
    "Copy-paste CSV text directly into the text area",
    "Headers must match the standard column names",
    "Only SKU data (no catalogs/rules in CSV mode)",
    "",
    "Use when you have data in a non-template spreadsheet",
    "Quick option for small updates",
],
    Inches(6.85), Inches(1.98), Inches(6.0), Inches(2.8),
    font_size=12, bullet_color=GREY_TEXT)

# Key SKU fields strip
add_rect(s7, Inches(6.7), Inches(4.1), Inches(6.3), Inches(1.85),
         fill_rgb=LENOVO_DARK, line_rgb=LENOVO_MID, line_width_pt=1)
add_text_box(s7, "Key SKU Fields",
             Inches(6.85), Inches(4.15), Inches(6.0), Inches(0.35),
             font_size=12, bold=True, color=WHITE)
bullet_block(s7, [
    "Service PN  |  Type of Service  |  Service Tier  |  GEO  |  Country",
    "Service Term  |  Service Delivery Type  |  Upgrade From Type  |  Upgrade From Term",
    "Standard Cost (PSC)  |  Currency",
],
    Inches(6.85), Inches(4.5), Inches(6.0), Inches(1.35),
    font_size=11, bullet_color=RGBColor(0xAA, 0xDD, 0xFF), indent="  ")

# Bottom note
add_rect(s7, Inches(0.3), Inches(6.08), Inches(6.0), Inches(0.62),
         fill_rgb=RGBColor(0xFF, 0xF3, 0xCD), line_rgb=AMBER, line_width_pt=1)
add_text_box(s7, "Note: Importing data does not overwrite existing uplift rules or values unless the "
             "Excel file includes those sheets. SKU data is appended to the current cycle.",
             Inches(0.45), Inches(6.1), Inches(5.7), Inches(0.58),
             font_size=10, color=RGBColor(0x66, 0x44, 0x00))


# =============================================================================
# SLIDE 8 — Stage 3: Uplift Catalogs
# =============================================================================
s8 = new_slide("Stage 3 \u2014 Uplift Rules",
               "Defining the scope and factors for each pricing segment",
               label="Stage 3", label_color=STAGE3_COLOR)

# What is a catalog explanation
add_rect(s8, Inches(0.3), Inches(1.5), Inches(12.7), Inches(0.85),
         fill_rgb=RGBColor(0xEA, 0xF4, 0xF8), line_rgb=STAGE3_COLOR, line_width_pt=1)
add_text_box(s8, "What is an Uplift Rule?",
             Inches(0.45), Inches(1.53), Inches(3.0), Inches(0.35),
             font_size=12, bold=True, color=LENOVO_DARK)
add_text_box(s8,
             "An Uplift Rule defines the scope (Type of Service + GEO) for a pricing segment and specifies which uplift "
             "factors apply. Uplift Rules are the bridge between factor definitions and Uplift Values.",
             Inches(0.45), Inches(1.85), Inches(12.3), Inches(0.42),
             font_size=12, color=GREY_TEXT)

# Left: Catalog fields
add_rect(s8, Inches(0.3), Inches(2.5), Inches(6.0), Inches(4.2),
         fill_rgb=LENOVO_LIGHT, line_rgb=STAGE3_COLOR, line_width_pt=1)
bullet_block(s8, [
    "Uplift Rule ID (unique identifier, e.g. UR-EMEA-SS)",
    "Type of Service (e.g. Support Services)",
    "GEO (e.g. EMEA)",
    "Status: Draft / Released / Retired",
    "Valid From / Valid To dates",
    "Selected Uplift Factors (chosen from 18 available)",
],
    Inches(0.45), Inches(2.55), Inches(5.7), Inches(4.0),
    font_size=13, title="Uplift Rule Fields", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)

# Right: factor classifications + workflow
add_rect(s8, Inches(6.7), Inches(2.5), Inches(6.3), Inches(4.2),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)
bullet_block(s8, [
    "Territory:      COUNTRY, GEO",
    "Hardware:       SRVTIER, SUBSRVTIER, MT",
    "Service Type:   TYPESRV, SUBTYPESRV",
    "Service Scope:  SDTYPE, ICPS, IPRT, IKYD, UPGFRMTYPE",
    "Service Period: SRVTERM, UPGFRMTERM",
    "SLA:            SABTIME, RSPTIME",
],
    Inches(6.85), Inches(2.55), Inches(6.0), Inches(2.5),
    font_size=12, title="Available Factor Classifications (18 total)", title_size=14,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)

bullet_block(s8, [
    "Create Uplift Rule \u2192 select factors \u2192 set status to Released",
    "Released Uplift Rules can be used by Uplift Values",
    "Retired Uplift Rules are excluded from matching",
    "Multiple Uplift Rules can cover different Type of Service / GEO combos",
],
    Inches(6.85), Inches(5.1), Inches(6.0), Inches(1.5),
    font_size=12, title="Workflow", title_size=14,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)


# =============================================================================
# SLIDE 9 — Stage 3: Uplift Rules
# =============================================================================
s9 = new_slide("Stage 3 \u2014 Uplift Values",
               "Assigning uplift ratios to dimension match values",
               label="Stage 3", label_color=STAGE3_COLOR)

# What is a rule explanation
add_rect(s9, Inches(0.3), Inches(1.5), Inches(12.7), Inches(0.85),
         fill_rgb=RGBColor(0xEA, 0xF4, 0xF8), line_rgb=STAGE3_COLOR, line_width_pt=1)
add_text_box(s9, "What is an Uplift Value?",
             Inches(0.45), Inches(1.53), Inches(3.0), Inches(0.35),
             font_size=12, bold=True, color=LENOVO_DARK)
add_text_box(s9,
             "A Released Uplift Value is matched to each SKU by (Type of Service + GEO). Each factor has match values "
             "and an uplift ratio. The total uplift is the sum of all matching factor ratios.",
             Inches(0.45), Inches(1.85), Inches(12.3), Inches(0.42),
             font_size=12, color=GREY_TEXT)

# Left: Rule fields
add_rect(s9, Inches(0.3), Inches(2.5), Inches(6.0), Inches(4.2),
         fill_rgb=LENOVO_LIGHT, line_rgb=STAGE3_COLOR, line_width_pt=1)
bullet_block(s9, [
    "Uplift Value ID (unique identifier)",
    "Linked Uplift Rule (scope reference)",
    "Type of Service + GEO (matching key)",
    "Status: Draft / Released / Retired",
    "Per-factor entries:",
    "  Match Values (comma-separated list)",
    "  Uplift % for this factor",
    "Total Uplift Ratio shown live as factors are entered",
],
    Inches(0.45), Inches(2.55), Inches(5.7), Inches(4.0),
    font_size=13, title="Uplift Value Fields", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)

# Right: Matching logic
add_rect(s9, Inches(6.7), Inches(2.5), Inches(6.3), Inches(4.2),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)
bullet_block(s9, [
    "SKU matched to an Uplift Value by exact (Type of Service + GEO)",
    "For each rule factor:",
    "  If SKU field value is in the match list \u2192 ratio is added",
    "  Unmatched factors contribute 0 uplift",
    "Total Uplift = sum of all contributing factor ratios",
    "",
    "If no Released rule matches \u2192 SKU flagged 'No Rule'",
    "If PSC is missing \u2192 SKU flagged 'No PSC'",
    "Only Released rules are used in calculation",
    "Multiple Uplift Values can exist per Uplift Rule (different GEOs)",
],
    Inches(6.85), Inches(2.55), Inches(6.0), Inches(4.0),
    font_size=13, title="Matching Logic", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)


# =============================================================================
# SLIDE 10 — Stage 3: Run Calculation
# =============================================================================
s10 = new_slide("Stage 3 \u2014 Run Calculation",
                "Executing the uplift calculation across all SKUs",
                label="Stage 3", label_color=STAGE3_COLOR)

# Formula box
add_rect(s10, Inches(0.3), Inches(1.5), Inches(12.7), Inches(0.65),
         fill_rgb=STAGE3_COLOR)
add_text_box(s10, "Sales Cost  =  PSC  x  (1 + Total Uplift Ratio)",
             Inches(0.5), Inches(1.55), Inches(12.3), Inches(0.55),
             font_size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# Steps
steps_calc = [
    ("1", "Go to Calculate tab and click 'Run Calculation'"),
    ("2", "Engine loads all Released rules and pre-caches their factor entries"),
    ("3", "Each SKU is matched to an Uplift Value by (Type of Service + GEO)"),
    ("4", "Matching factor ratios are summed \u2192 Total Uplift Ratio"),
    ("5", "Sales Cost = PSC x (1 + Total Uplift Ratio) is stored per SKU"),
]

for i, (num, desc) in enumerate(steps_calc):
    t = Inches(2.35) + i * Inches(0.62)
    add_rect(s10, Inches(0.3), t, Inches(0.5), Inches(0.5), fill_rgb=LENOVO_DARK)
    add_text_box(s10, num, Inches(0.3), t + Inches(0.1), Inches(0.5), Inches(0.35),
                 font_size=14, bold=True, color=LENOVO_RED, align=PP_ALIGN.CENTER)
    add_rect(s10, Inches(0.9), t, Inches(8.5), Inches(0.5),
             fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)
    add_text_box(s10, desc, Inches(1.05), t + Inches(0.1), Inches(8.2), Inches(0.38),
                 font_size=13, color=GREY_TEXT)

# Results summary panel
add_rect(s10, Inches(9.75), Inches(2.35), Inches(3.25), Inches(4.7),
         fill_rgb=LENOVO_DARK, line_rgb=STAGE3_COLOR, line_width_pt=2)
add_text_box(s10, "Results Summary Shows",
             Inches(9.9), Inches(2.42), Inches(3.0), Inches(0.38),
             font_size=13, bold=True, color=WHITE)
bullet_block(s10, [
    "Calculated count",
    "No Rule count",
    "No PSC count",
    "",
    "Breakdown by:",
    "  GEO",
    "  Service Tier",
    "",
    "Re-run at any time",
    "(results overwritten)",
],
    Inches(9.9), Inches(2.85), Inches(3.0), Inches(4.0),
    font_size=12, bullet_color=RGBColor(0xAA, 0xDD, 0xFF), indent="  ")


# =============================================================================
# SLIDE 11 — Stage 3: Export & Send to Stage 4
# =============================================================================
s11 = new_slide("Stage 3 \u2014 Export & Send to Stage 4",
                "Exporting results and handing off to GVE Validation",
                label="Stage 3", label_color=STAGE3_COLOR)

# Left: standard exports
add_rect(s11, Inches(0.3), Inches(1.5), Inches(5.8), Inches(5.7),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)
bullet_block(s11, [
    "Download CSV: full row-level results with all SKU fields",
    "Download Excel: same data in .xlsx format",
    "",
    "Fields included in export:",
    "  service_pn",
    "  psc_value",
    "  sales_cost",
    "  uplift_ratio",
    "  sales_cost_source",
    "  uplift_formula",
    "  service_tier, type_of_service, geo, country, term...",
    "",
    "Available from the Export tab after calculation is run",
],
    Inches(0.45), Inches(1.55), Inches(5.5), Inches(5.5),
    font_size=13, title="Standard Exports", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)

# Right: Send to Stage 4 (highlighted with purple border)
PURPLE = RGBColor(0x60, 0x20, 0xA0)
add_rect(s11, Inches(6.5), Inches(1.5), Inches(6.5), Inches(5.7),
         fill_rgb=RGBColor(0xF5, 0xEE, 0xFF), line_rgb=PURPLE, line_width_pt=2)
add_rect(s11, Inches(6.5), Inches(1.5), Inches(6.5), Inches(0.45), fill_rgb=PURPLE)
add_text_box(s11, "Send to Stage 4 \u2014 GVE Validation",
             Inches(6.6), Inches(1.53), Inches(6.2), Inches(0.4),
             font_size=13, bold=True, color=WHITE)

bullet_block(s11, [
    "Pivots flat SKU rows into the matrix format Stage 4 expects",
    "Each country becomes a region column block:",
    "  Cost  |  C-Price  |  L-Price",
    "Only SKUs with calculated Sales Cost are included",
    "",
    "Output file: Stage4_Input_<cycle_name>.xlsx",
    "",
    "How to use:",
    "  1. Click 'Download Stage 4 Input Excel' (purple button)",
    "  2. Open Stage 4 and create a new cycle",
    "  3. Go to Import Data tab",
    "  4. Import the Stage4_Input_<cycle>.xlsx file",
],
    Inches(6.65), Inches(2.02), Inches(6.1), Inches(5.0),
    font_size=12, bullet_color=GREY_TEXT)


# =============================================================================
# SLIDE 12 — Stage 4 Overview
# =============================================================================
s12 = new_slide("Stage 4 \u2014 GVE Validation Engine",
                "4-layer validation of the sales cost matrix + B2C/B2B list price computation",
                label="Stage 4", label_color=STAGE4_COLOR)

# GVE meaning callout
add_rect(s12, Inches(0.3), Inches(1.5), Inches(12.7), Inches(0.55),
         fill_rgb=STAGE4_COLOR)
add_text_box(s12, "GVE = Global Value Engine",
             Inches(0.5), Inches(1.55), Inches(6.0), Inches(0.42),
             font_size=14, bold=True, color=WHITE)

# Workflow tabs
tab_labels4 = ["Import Data", "Matrix View", "GVE Validation", "List Price", "Audit Log"]
tab_t4 = Inches(2.2)
for i, lbl in enumerate(tab_labels4):
    tl = Inches(0.5) + i * (Inches(2.3) + Inches(0.15))
    add_rect(s12, tl, tab_t4, Inches(2.3), Inches(0.38),
             fill_rgb=LENOVO_DARK, line_rgb=STAGE4_COLOR, line_width_pt=1)
    add_text_box(s12, lbl, tl, tab_t4, Inches(2.3), Inches(0.38),
                 font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    if i < len(tab_labels4) - 1:
        add_text_box(s12, ">", tl + Inches(2.3) + Inches(0.02), tab_t4 + Inches(0.06),
                     Inches(0.12), Inches(0.28),
                     font_size=12, bold=True, color=STAGE4_COLOR, align=PP_ALIGN.CENTER)

# Left: 4 validation layers
add_rect(s12, Inches(0.3), Inches(2.75), Inches(6.0), Inches(4.45),
         fill_rgb=LENOVO_LIGHT, line_rgb=STAGE4_COLOR, line_width_pt=1)
bullet_block(s12, [
    "L1 Monotonicity (Critical)",
    "  Tier cost must be non-decreasing",
    "L2 Ratio Bands (Critical / Warning)",
    "  3yr/1yr, 5yr/3yr, 4yr/2yr within floor/ceiling",
    "L3 Cross-Geo (Warning / Systemic)",
    "  Deviation from cross-region mean",
    "  3+ regions affected = Systemic flag",
    "L4 YoY Drift (Critical / Warning)",
    "  Cell-level and geo-level year-over-year change",
    "  Requires prior cycle baseline",
],
    Inches(0.45), Inches(2.8), Inches(5.7), Inches(4.2),
    font_size=12, title="The 4 Validation Layers", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)

# Right: List price computation
add_rect(s12, Inches(6.7), Inches(2.75), Inches(6.3), Inches(4.45),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)
bullet_block(s12, [
    "B2C List Price:    Sales Cost / (1 - GM%)",
    "B2B Floor Price:   Sales Cost x (1 + Markup%)",
    "",
    "Per-tier GM% and Markup% overrides supported",
    "Configuration set in Settings tab",
    "Results shown in List Price tab",
    "Included in CSV results export",
    "",
    "Cycle can be submitted only after all unresolved",
    "Critical violations are resolved with justification",
],
    Inches(6.85), Inches(2.8), Inches(6.0), Inches(4.2),
    font_size=12, title="List Price Computation", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)


# =============================================================================
# SLIDE 13 — Stage 4: Import Data & Settings
# =============================================================================
s13 = new_slide("Stage 4 \u2014 Import Data & Settings",
                "Loading the pricing matrix and configuring validation parameters",
                label="Stage 4", label_color=STAGE4_COLOR)

# Left: Import Data
add_rect(s13, Inches(0.3), Inches(1.5), Inches(6.0), Inches(5.7),
         fill_rgb=LENOVO_LIGHT, line_rgb=STAGE4_COLOR, line_width_pt=1)
bullet_block(s13, [
    "Import Excel file with matrix format:",
    "  Columns: Part#, Tier, Base Warranty, Upgrade, Type",
    "  Then geo blocks: Country_Cost | Country_C-Price | Country_L-Price",
    "",
    "Best practice: use 'Send to Stage 4' from Stage 3",
    "  Ensures correct column naming and structure",
    "",
    "Prior Cycle Baseline (for YoY Layer 4):",
    "  Paste CSV with columns:",
    "  part_number, region, prior_sales_cost",
    "  Used to compute year-over-year drift",
],
    Inches(0.45), Inches(1.55), Inches(5.7), Inches(5.5),
    font_size=12, title="Import Data Tab", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)

# Right: Settings
add_rect(s13, Inches(6.7), Inches(1.5), Inches(6.3), Inches(5.7),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)
bullet_block(s13, [
    "Contingency rates: by lifecycle (New / Mature Refresh / Mature)",
    "  and by term (1-3yr / 4-5yr)",
    "Overhead: total fixed cost and projected units",
    "Ratio Bands: min/max for 3yr/1yr, 5yr/3yr, 4yr/2yr",
    "Cross-Geo deviation threshold (%)",
    "YoY Drift thresholds: cell-level, ratio, geo average",
    "GM% and Markup% by tier for list price",
    "Tier sequence management (order for L1 monotonicity)",
],
    Inches(6.85), Inches(1.55), Inches(6.0), Inches(5.5),
    font_size=12, title="Settings Tab", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)


# =============================================================================
# SLIDE 14 — Stage 4: Matrix View
# =============================================================================
s14 = new_slide("Stage 4 \u2014 Matrix View",
                "Visualising the full pricing matrix before validation",
                label="Stage 4", label_color=STAGE4_COLOR)

# Left
add_rect(s14, Inches(0.3), Inches(1.5), Inches(6.0), Inches(5.7),
         fill_rgb=LENOVO_LIGHT, line_rgb=STAGE4_COLOR, line_width_pt=1)
bullet_block(s14, [
    "Pivot table: SKUs (rows) x Regions (columns)",
    "Shows Sales Cost per SKU per region in a grid",
    "Filter by Delivery Type to focus on a segment",
    "Color indicators for data completeness",
    "  Green: all regions populated",
    "  Amber: some regions missing",
    "  Red: no data for this SKU",
],
    Inches(0.45), Inches(1.55), Inches(5.7), Inches(5.5),
    font_size=13, title="What the Matrix View Shows", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)

# Right
add_rect(s14, Inches(6.7), Inches(1.5), Inches(6.3), Inches(5.7),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)
bullet_block(s14, [
    "Review data completeness before running GVE",
    "Verify region coverage and tier ordering",
    "Identify obvious outliers before formal validation",
    "Confirm that the Stage 3 handoff populated correctly",
    "",
    "Columns are grouped by region/country:",
    "  Each region shows: Cost | C-Price | L-Price",
    "",
    "Row grouping: by Part# and Tier sequence",
    "  Tier order matters for L1 Monotonicity check",
],
    Inches(6.85), Inches(1.55), Inches(6.0), Inches(5.5),
    font_size=13, title="How to Use", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)


# =============================================================================
# SLIDE 15 — Stage 4: GVE Validation (4 Layers)
# =============================================================================
s15 = new_slide("Stage 4 \u2014 GVE Validation",
                "Four-layer validation engine with severity classification",
                label="Stage 4", label_color=STAGE4_COLOR)

# Severity legend strip
add_rect(s15, Inches(0.3), Inches(1.5), Inches(12.7), Inches(0.45), fill_rgb=LENOVO_DARK)
for lbl, col, xpos in [
    ("Critical", LENOVO_RED, Inches(0.5)),
    ("Warning", AMBER, Inches(2.8)),
    ("Systemic", RGBColor(0xFF, 0x6B, 0x00), Inches(5.1)),
    ("OK", GREEN, Inches(7.4)),
]:
    add_rect(s15, xpos, Inches(1.56), Inches(0.7), Inches(0.3), fill_rgb=col)
    add_text_box(s15, lbl, xpos + Inches(0.75), Inches(1.57), Inches(1.4), Inches(0.3),
                 font_size=11, bold=True, color=WHITE)

# 4 layer boxes in 2x2 grid
layers = [
    ("L1", "Monotonicity", LENOVO_RED, "Critical",
     "For each SKU + Region, sales cost must not decrease as service tier increases.",
     "Violation = wrong tier ordering or data entry error.",
     "Affects: all SKU-region combinations."),
    ("L2", "Ratio Bands", AMBER, "Critical / Warning",
     "Ratio between higher and lower term tiers must fall within configured bands.",
     "Bands: 3yr/1yr, 5yr/3yr, 4yr/2yr (min and max thresholds in Settings).",
     "Critical if outside hard limits; Warning if outside soft limits."),
    ("L3", "Cross-Geo", RGBColor(0xFF, 0x6B, 0x00), "Warning / Systemic",
     "Sales cost must not deviate excessively from the cross-region mean for that SKU+Tier.",
     "Systemic flag if 3 or more regions are affected for the same SKU.",
     "Threshold configured in Settings (e.g. 30% deviation)."),
    ("L4", "YoY Drift", RGBColor(0x99, 0x33, 0xFF), "Critical / Warning",
     "Year-over-year change at cell level and geo level must not exceed configured thresholds.",
     "Requires prior cycle baseline (part_number, region, prior_sales_cost).",
     "Flags large price movements that may need business justification."),
]

positions = [
    (Inches(0.3), Inches(2.1)),
    (Inches(6.7), Inches(2.1)),
    (Inches(0.3), Inches(4.85)),
    (Inches(6.7), Inches(4.85)),
]

for (lbl_id, lbl_name, col, severity, line1, line2, line3), (lx, ly) in zip(layers, positions):
    bw = Inches(6.0)
    bh = Inches(2.55)
    add_rect(s15, lx, ly, bw, bh, fill_rgb=LENOVO_LIGHT, line_rgb=col, line_width_pt=2)
    # Header strip
    add_rect(s15, lx, ly, bw, Inches(0.42), fill_rgb=col)
    add_text_box(s15, f"{lbl_id}  {lbl_name}",
                 lx + Inches(0.12), ly + Inches(0.05), Inches(3.5), Inches(0.35),
                 font_size=14, bold=True, color=WHITE)
    add_text_box(s15, severity,
                 lx + bw - Inches(2.0), ly + Inches(0.07), Inches(1.85), Inches(0.3),
                 font_size=10, bold=True, color=WHITE, align=PP_ALIGN.RIGHT)
    bullet_block(s15, [line1, line2, line3],
                 lx + Inches(0.12), ly + Inches(0.5), bw - Inches(0.25), Inches(1.95),
                 font_size=11, bullet_color=GREY_TEXT)

# Bottom note
add_rect(s15, Inches(0.3), Inches(7.1), Inches(12.7), Inches(0.32),
         fill_rgb=LENOVO_DARK)
add_text_box(s15,
             "Violations can be Resolved with a justification comment. Resolved items are excluded "
             "from submit blocking. Full audit trail maintained.",
             Inches(0.5), Inches(7.12), Inches(12.3), Inches(0.28),
             font_size=10, color=RGBColor(0xCC, 0xCC, 0xCC), align=PP_ALIGN.CENTER)


# =============================================================================
# SLIDE 16 — Stage 4: List Price Computation
# =============================================================================
s16 = new_slide("Stage 4 \u2014 List Price Computation",
                "Deriving B2C and B2B floor prices from validated sales cost",
                label="Stage 4", label_color=STAGE4_COLOR)

# Two formula boxes
add_rect(s16, Inches(0.3), Inches(1.5), Inches(6.0), Inches(0.85),
         fill_rgb=STAGE3_COLOR, line_rgb=LENOVO_DARK, line_width_pt=1)
add_text_box(s16, "B2C List Price",
             Inches(0.45), Inches(1.55), Inches(3.0), Inches(0.35),
             font_size=12, bold=True, color=WHITE)
add_text_box(s16, "Sales Cost  /  (1 \u2212 GM%)",
             Inches(0.45), Inches(1.88), Inches(5.7), Inches(0.4),
             font_size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_rect(s16, Inches(6.7), Inches(1.5), Inches(6.3), Inches(0.85),
         fill_rgb=STAGE4_COLOR, line_rgb=LENOVO_DARK, line_width_pt=1)
add_text_box(s16, "B2B Quoted Floor",
             Inches(6.85), Inches(1.55), Inches(3.5), Inches(0.35),
             font_size=12, bold=True, color=WHITE)
add_text_box(s16, "Sales Cost  x  (1 + Markup%)",
             Inches(6.85), Inches(1.88), Inches(6.0), Inches(0.4),
             font_size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# Configuration panel
add_rect(s16, Inches(0.3), Inches(2.55), Inches(6.0), Inches(4.6),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)
bullet_block(s16, [
    "Default GM% and Markup% set in the Settings tab",
    "Per-tier overrides supported:",
    "  e.g. Premier tier at higher GM% than Base tier",
    "Override takes precedence over the default value",
    "",
    "Configuration applies cycle-wide",
    "Changes to Settings do not retroactively update",
    "already-submitted cycles",
],
    Inches(0.45), Inches(2.6), Inches(5.7), Inches(4.4),
    font_size=13, title="Configuration", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)

# Results and export panel
add_rect(s16, Inches(6.7), Inches(2.55), Inches(6.3), Inches(4.6),
         fill_rgb=LENOVO_LIGHT, line_rgb=STAGE4_COLOR, line_width_pt=1)
bullet_block(s16, [
    "Results shown in the List Price tab:",
    "  Alongside the cost matrix",
    "  B2C and B2B columns per region",
    "  Per-tier breakdown",
    "",
    "Export:",
    "  Included in CSV Results export from Export tab",
    "  Also included in the HTML GVE Report",
    "",
    "List price is informational \u2014 not used in GVE",
    "validation layers (which validate Sales Cost only)",
],
    Inches(6.85), Inches(2.6), Inches(6.0), Inches(4.4),
    font_size=13, title="Results & Export", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)


# =============================================================================
# SLIDE 17 — Stage 4: Submit & Export
# =============================================================================
s17 = new_slide("Stage 4 \u2014 Submit & Export",
                "Finalising the cycle and exporting deliverables",
                label="Stage 4", label_color=STAGE4_COLOR)

# Submit section
add_rect(s17, Inches(0.3), Inches(1.5), Inches(5.8), Inches(2.85),
         fill_rgb=LENOVO_DARK, line_rgb=STAGE4_COLOR, line_width_pt=2)
add_text_box(s17, "Submit Cycle",
             Inches(0.45), Inches(1.56), Inches(5.5), Inches(0.4),
             font_size=15, bold=True, color=STAGE4_COLOR)
bullet_block(s17, [
    "Submit is blocked if any unresolved Critical violations remain",
    "Resolve violations with a justification comment first",
    "Submission locks the cycle:",
    "  Import and edits are disabled",
    "  Submitted by + timestamp are recorded",
    "Locked cycles remain readable for audit/archive",
],
    Inches(0.45), Inches(2.0), Inches(5.5), Inches(2.2),
    font_size=12, bullet_color=RGBColor(0xCC, 0xCC, 0xCC), indent="  ")

# Audit log section
add_rect(s17, Inches(0.3), Inches(4.5), Inches(5.8), Inches(2.7),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)
bullet_block(s17, [
    "Full history of all actions with user + timestamp",
    "Records: data imports, validation runs, submissions",
    "Records: violation resolutions with justifications",
    "Non-deletable audit trail per cycle",
],
    Inches(0.45), Inches(4.55), Inches(5.5), Inches(2.5),
    font_size=13, title="Audit Log Tab", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)

# Exports section
add_rect(s17, Inches(6.5), Inches(1.5), Inches(6.5), Inches(5.7),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)
bullet_block(s17, [
    "CSV Results",
    "  Full SKU-level data per region:",
    "  sales cost, B2C list price, B2B floor price",
    "  GVE flags, uplift ratios, source fields",
    "  Available from the Export tab",
    "",
    "HTML GVE Report",
    "  Self-contained, single-file HTML report",
    "  Includes: all violation details and resolutions",
    "  Includes: list price summary and matrix snapshot",
    "  Shareable via email / suitable for archive",
    "  No external dependencies \u2014 opens in any browser",
    "",
    "Both exports available before and after submission",
],
    Inches(6.65), Inches(1.55), Inches(6.1), Inches(5.5),
    font_size=13, title="Export Options", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)


# =============================================================================
# SLIDE 16 — Stage 5 Overview
# =============================================================================
s_s5_overview = new_slide("Stage 5 \u2014 List Price Calculator",
                           "Derive Channel Price and List Price from Sales Cost + PFV benchmark",
                           label="Stage 5", label_color=STAGE5_COLOR)

# Header banner
add_rect(s_s5_overview, Inches(0.3), Inches(1.5), Inches(12.7), Inches(0.55),
         fill_rgb=STAGE5_COLOR)
add_text_box(s_s5_overview, "PFV = Price for Value — market benchmark anchor for list price derivation",
             Inches(0.5), Inches(1.57), Inches(12.3), Inches(0.42),
             font_size=13, bold=True, color=WHITE)

# Workflow tabs
tab_labels5 = ["Import SKU", "Import PFV", "Calculate", "Audit Log", "Export", "Settings"]
tab_t5 = Inches(2.2)
for i, lbl in enumerate(tab_labels5):
    tl = Inches(0.5) + i * (Inches(2.0) + Inches(0.08))
    add_rect(s_s5_overview, tl, tab_t5, Inches(2.0), Inches(0.38),
             fill_rgb=LENOVO_DARK, line_rgb=STAGE5_COLOR, line_width_pt=1)
    add_text_box(s_s5_overview, lbl, tl, tab_t5, Inches(2.0), Inches(0.38),
                 font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    if i < len(tab_labels5) - 1:
        add_text_box(s_s5_overview, ">", tl + Inches(2.0) + Inches(0.01), tab_t5 + Inches(0.06),
                     Inches(0.07), Inches(0.28),
                     font_size=10, bold=True, color=STAGE5_COLOR, align=PP_ALIGN.CENTER)

# Left: models
add_rect(s_s5_overview, Inches(0.3), Inches(2.75), Inches(6.0), Inches(4.45),
         fill_rgb=LENOVO_LIGHT, line_rgb=STAGE5_COLOR, line_width_pt=1)
bullet_block(s_s5_overview, [
    "C\u2192L Model (Channel Price first):",
    "  C-Price = Sales Cost \xd7 (1 + Add-On Adder)",
    "  List Price = C-Price \xf7 (1 \u2212 TopSeller Discount%)",
    "",
    "L\u2192C Model (List Price first):",
    "  List Price = Sales Cost \xd7 (1 + GP%)",
    "  C-Price = List Price \xd7 (1 \u2212 Channel Margin%)",
    "",
    "PFV Benchmark:",
    "  If PFV available: list price anchored to PFV",
    "  If no PFV: pfv_status = 'no_pfv', flagged",
    "  Geo-group factors adjust price regionally",
],
    Inches(0.45), Inches(2.8), Inches(5.7), Inches(4.2),
    font_size=12, title="Pricing Models", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)

# Right: key outputs
add_rect(s_s5_overview, Inches(6.7), Inches(2.75), Inches(6.3), Inches(4.45),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)
bullet_block(s_s5_overview, [
    "Per-SKU outputs stored in IndexedDB:",
    "  channel_price   \u2014 C-Price",
    "  list_price_calc \u2014 derived list price",
    "  pfv_status      \u2014 'pfv' | 'no_pfv'",
    "  gp_pct          \u2014 gross profit %",
    "",
    "Audit Log: tracks Import, Calculation, Clear events",
    "Export tab: downloads results as Excel/CSV",
    "",
    "Stage 6 reads 'list_price_calc' directly from",
    "Stage 5's IndexedDB \u2014 no file handoff needed",
    "Items with pfv_status='no_pfv' excluded from",
    "Stage 6 gradient validation checks",
],
    Inches(6.85), Inches(2.8), Inches(6.0), Inches(4.2),
    font_size=12, title="Outputs & Stage 6 Integration", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)


# =============================================================================
# SLIDE 17 — Stage 5: Import & Settings
# =============================================================================
s_s5_import = new_slide("Stage 5 \u2014 Import & Settings",
                         "Loading SKU data, PFV benchmark, and configuring calculation parameters",
                         label="Stage 5", label_color=STAGE5_COLOR)

# Left: Import
add_rect(s_s5_import, Inches(0.3), Inches(1.5), Inches(6.0), Inches(5.7),
         fill_rgb=LENOVO_LIGHT, line_rgb=STAGE5_COLOR, line_width_pt=1)
bullet_block(s_s5_import, [
    "Import SKU Data tab \u2014 required columns:",
    "  part_number  |  tier  |  upgrade_years",
    "  delivery_type  |  region  |  sales_cost",
    "",
    "Import PFV tab \u2014 PFV benchmark columns:",
    "  tier  |  upgrade_years  |  delivery_type",
    "  pfv_value  (market benchmark price)",
    "",
    "PFV is optional per SKU.",
    "  If matched: list_price_calc uses PFV anchor",
    "  If not matched: pfv_status = 'no_pfv'",
    "",
    "Best practice: export from Stage 4 cycle,",
    "  add sales_cost column before importing here",
],
    Inches(0.45), Inches(1.55), Inches(5.7), Inches(5.5),
    font_size=12, title="Import Data", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)

# Right: Settings
add_rect(s_s5_import, Inches(6.7), Inches(1.5), Inches(6.3), Inches(5.7),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)
bullet_block(s_s5_import, [
    "Pricing Model: C\u2192L (Channel first) or L\u2192C (List first)",
    "GP% by tier: Gross Profit percentage per tier",
    "Channel Margin%: used in L\u2192C model",
    "Add-On Adder: per-SKU uplift in C\u2192L model",
    "TopSeller Discount%: applied to Premier tier",
    "",
    "Geo-Group Regional Factors:",
    "  Groups of regions share a pricing premium/discount",
    "  Example: UKIR group = 1.10 (10% premium)",
    "  Configured per cycle in Settings tab",
    "",
    "Cycle can be re-run after adjusting settings",
    "  All results update in-place within same cycle",
],
    Inches(6.85), Inches(1.55), Inches(6.0), Inches(5.5),
    font_size=12, title="Settings", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)


# =============================================================================
# SLIDE 18 — Stage 5: Calculate & Results
# =============================================================================
s_s5_calc = new_slide("Stage 5 \u2014 Calculate & Results",
                       "Running the list price calculation and reviewing outputs",
                       label="Stage 5", label_color=STAGE5_COLOR)

# Left: How to run
add_rect(s_s5_calc, Inches(0.3), Inches(1.5), Inches(6.0), Inches(5.7),
         fill_rgb=LENOVO_LIGHT, line_rgb=STAGE5_COLOR, line_width_pt=1)
bullet_block(s_s5_calc, [
    "1. Import SKU Data (with sales_cost column)",
    "2. Import PFV benchmark file",
    "3. Configure Settings (GP%, model, geo factors)",
    "4. Click 'Run Calculation' in the Calculate tab",
    "",
    "Results table shows per-SKU:",
    "  Part #  |  Tier  |  Region  |  Upgrade Years",
    "  Sales Cost  \u2192  C-Price  \u2192  List Price",
    "  GP%  |  PFV Status  |  Geo-Group Factor",
    "",
    "Summary stats: calculated / no_pfv / error counts",
    "Re-run at any time after changing settings",
],
    Inches(0.45), Inches(1.55), Inches(5.7), Inches(5.5),
    font_size=12, title="Running the Calculation", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)

# Right: Export
add_rect(s_s5_calc, Inches(6.7), Inches(1.5), Inches(6.3), Inches(5.7),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)
bullet_block(s_s5_calc, [
    "Excel Export (Export tab):",
    "  Full results with all columns",
    "  One row per SKU / region / term combination",
    "  Suitable for commercial review and approval",
    "",
    "Stage 6 does NOT require a file export.",
    "  Stage 6 opens Stage 5's IndexedDB directly",
    "  Select same cycle in Stage 6 to validate",
    "  list_price_calc gradient automatically",
    "",
    "Audit Log tab records all significant events:",
    "  Cycle Created, Import SKU, Import PFV,",
    "  Calculation Run, Clear Data",
    "  Downloadable as CSV for compliance trail",
],
    Inches(6.85), Inches(1.55), Inches(6.0), Inches(5.5),
    font_size=12, title="Export & Audit", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)


# =============================================================================
# SLIDE 19 — Stage 6 Overview
# =============================================================================
s_s6_overview = new_slide("Stage 6 \u2014 Price Gradient Validation",
                            "3-layer structural validation of final list prices",
                            label="Stage 6", label_color=STAGE6_COLOR)

# Header banner
add_rect(s_s6_overview, Inches(0.3), Inches(1.5), Inches(12.7), Inches(0.55),
         fill_rgb=STAGE6_COLOR)
add_text_box(s_s6_overview,
             "Mirrors Stage 4 GVE — same structural logic, applied to list_price_calc instead of sales_cost",
             Inches(0.5), Inches(1.57), Inches(12.3), Inches(0.42),
             font_size=13, bold=True, color=WHITE)

# Workflow tabs
tab_labels6 = ["Summary", "L1 Monotonicity", "L2 Ratio Bands", "L3 Cross-Geo", "Export", "Settings"]
tab_t6 = Inches(2.2)
for i, lbl in enumerate(tab_labels6):
    tl = Inches(0.5) + i * (Inches(2.0) + Inches(0.08))
    add_rect(s_s6_overview, tl, tab_t6, Inches(2.0), Inches(0.38),
             fill_rgb=LENOVO_DARK, line_rgb=STAGE6_COLOR, line_width_pt=1)
    add_text_box(s_s6_overview, lbl, tl, tab_t6, Inches(2.0), Inches(0.38),
                 font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    if i < len(tab_labels6) - 1:
        add_text_box(s_s6_overview, ">", tl + Inches(2.0) + Inches(0.01), tab_t6 + Inches(0.06),
                     Inches(0.07), Inches(0.28),
                     font_size=10, bold=True, color=STAGE6_COLOR, align=PP_ALIGN.CENTER)

# Left: Why needed
add_rect(s_s6_overview, Inches(0.3), Inches(2.75), Inches(6.0), Inches(4.45),
         fill_rgb=LENOVO_LIGHT, line_rgb=STAGE6_COLOR, line_width_pt=1)
bullet_block(s_s6_overview, [
    "Stage 4 validates sales cost gradient.",
    "Stage 5 applies two further transformations:",
    "  1. PFV values differ per tier/year \u2014 can",
    "     invert tier ordering even if Stage 4 passed",
    "  2. Geo-group regional factors shift cross-geo",
    "     relationships independently",
    "",
    "Stage 6 checks the final list price gradient",
    "to ensure price integrity after Stage 5.",
    "",
    "Items with pfv_status = 'no_pfv' are excluded",
    "from all layer checks and flagged separately.",
],
    Inches(0.45), Inches(2.8), Inches(5.7), Inches(4.2),
    font_size=12, title="Why Stage 6?", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)

# Right: Data flow
add_rect(s_s6_overview, Inches(6.7), Inches(2.75), Inches(6.3), Inches(4.45),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)
bullet_block(s_s6_overview, [
    "Data source: Stage 5's IndexedDB (GPSPricingStage5V1)",
    "  Opens read-only \u2014 no import required",
    "  Select cycle in nav \u2192 prices load automatically",
    "",
    "Own DB: GPSPricingStage6V1",
    "  Stores settings and violation results",
    "  Violations persist across sessions",
    "",
    "Summary tab shows:",
    "  Total items checked  |  No-PFV excluded",
    "  L1 / L2 / L3 violation counts by severity",
    "  Overall PASS / BLOCKED status",
    "",
    "Export tab: full violations CSV",
],
    Inches(6.85), Inches(2.8), Inches(6.0), Inches(4.2),
    font_size=12, title="Data Flow & Summary", title_size=15,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)


# =============================================================================
# SLIDE 20 — Stage 6: Validation Layers Detail
# =============================================================================
s_s6_layers = new_slide("Stage 6 \u2014 Validation Layers",
                          "L1 Monotonicity  \u00b7  L2 Ratio Bands  \u00b7  L3 Cross-Geo",
                          label="Stage 6", label_color=STAGE6_COLOR)

# Three layer cards side by side
layer_cards = [
    ("L1", "Monotonicity", STAGE6_COLOR,
     [
         "Severity: Critical",
         "",
         "list_price_calc must be non-decreasing",
         "across tiers (by tier_sequence) within:",
         "  same region",
         "  same upgrade_years",
         "  same delivery_type",
         "",
         "Inversion = list price of higher tier is",
         "lower than preceding tier.",
         "",
         "Default tier order:",
         "  Education < Tablet < Classic",
         "  < Premium < Edge",
         "",
         "Configurable in Settings tab.",
     ]),
    ("L2", "Ratio Bands", RGBColor(0x5D, 0x2E, 0x76),
     [
         "Severity: Critical / Warning",
         "",
         "Term-length ratios must stay within",
         "configurable floor/ceiling bands:",
         "",
         "  3yr / 1yr  : 1.80 \u2013 2.80",
         "  5yr / 3yr  : 1.30 \u2013 1.70",
         "  4yr / 2yr  : 1.30 \u2013 2.00",
         "",
         "Checked within same:",
         "  tier  |  delivery_type  |  region",
         "",
         "Below floor = Critical",
         "Above ceiling = Warning",
     ]),
    ("L3", "Cross-Geo", RGBColor(0x4A, 0x23, 0x5E),
     [
         "Severity: Warning / Systemic",
         "",
         "list_price_calc deviation across regions",
         "for same (tier, delivery_type, upgrade_years)",
         "must stay within threshold (default: 20%).",
         "",
         "Deviation = (value - group_mean) / group_mean",
         "",
         "> threshold = Warning",
         "3+ regions flagged in same group = Systemic",
         "",
         "Excludes no_pfv items.",
         "Configurable threshold in Settings tab.",
     ]),
]

lcard_w = Inches(4.0)
lcard_h = Inches(5.5)
lcard_t = Inches(1.55)
lcard_start = Inches(0.45)
lcard_gap = Inches(0.27)

for i, (code, title_txt, col, bullets) in enumerate(layer_cards):
    lx = lcard_start + i * (lcard_w + lcard_gap)

    add_rect(s_s6_layers, lx, lcard_t, lcard_w, lcard_h,
             fill_rgb=LENOVO_LIGHT, line_rgb=col, line_width_pt=2)

    # Header
    add_rect(s_s6_layers, lx, lcard_t, lcard_w, Inches(0.75), fill_rgb=col)
    add_text_box(s_s6_layers, code,
                 lx + Inches(0.1), lcard_t + Inches(0.04), Inches(0.55), Inches(0.35),
                 font_size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text_box(s_s6_layers, title_txt,
                 lx + Inches(0.65), lcard_t + Inches(0.18), lcard_w - Inches(0.75), Inches(0.42),
                 font_size=15, bold=True, color=WHITE)

    bullet_block(s_s6_layers, bullets,
                 lx + Inches(0.1), lcard_t + Inches(0.82), lcard_w - Inches(0.2), Inches(4.55),
                 font_size=11, bullet_color=GREY_TEXT)


# =============================================================================
# SLIDE 18 — Pricing Pipeline Handoff Workflow
# =============================================================================
s18 = new_slide("Pricing Pipeline \u2014 Handoff Workflow",
                "End-to-end flow: Stage 3 \u2192 Stage 4 \u2192 Stage 5 \u2192 Stage 6")

handoff_steps = [
    ("1", "Stage 3: Run Sales Cost Calculation",
     STAGE3_COLOR,
     "Complete the uplift calculation in Stage 3. Verify results in the Calculate tab "
     "(Calculated / No Rule / No PSC counts). Then export via 'Send to Stage 4' button."),
    ("2", "Stage 4: Import & Run GVE Validation",
     STAGE4_COLOR,
     "Create a matching cycle in Stage 4, import Stage4_Input_<cycle>.xlsx. "
     "Run all 4 GVE layers, resolve Critical violations with justifications, then submit the cycle."),
    ("3", "Stage 5: Import SKU Data + PFV",
     STAGE5_COLOR,
     "Open Stage 5, create a cycle. Import the same SKU data (with sales_cost column) "
     "and the PFV benchmark file. Configure GP%, model type (C\u2192L or L\u2192C), and geo-group factors in Settings."),
    ("4", "Stage 5: Run List Price Calculation",
     STAGE5_COLOR,
     "Click 'Run Calculation'. Stage 5 derives Channel Price and List Price per SKU "
     "using the PFV benchmark and geo-group regional factors. Results stored in browser DB."),
    ("5", "Stage 6: Open same cycle, Run Gradient Validation",
     STAGE6_COLOR,
     "Open Stage 6, select the same cycle. Stage 6 reads list prices directly from Stage 5's "
     "IndexedDB \u2014 no file export needed. Run validation to check L1/L2/L3 gradient layers."),
    ("6", "Stage 6: Review Violations & Export",
     STAGE6_COLOR,
     "Review Critical violations (monotonicity inversions, ratio band breaches). "
     "Export all violations to CSV for audit trail. All-clear status = pricing cycle complete."),
]

step_h18 = Inches(0.83)
step_t18 = Inches(1.45)

for i, (num, title_txt, col, desc_txt) in enumerate(handoff_steps):
    t = step_t18 + i * (step_h18 + Inches(0.06))

    # Coloured number badge
    add_rect(s18, Inches(0.3), t, Inches(0.55), step_h18, fill_rgb=col)
    add_text_box(s18, num, Inches(0.3), t + Inches(0.28), Inches(0.55), Inches(0.42),
                 font_size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    # Step box
    add_rect(s18, Inches(0.95), t, Inches(12.1), step_h18,
             fill_rgb=LENOVO_LIGHT, line_rgb=col, line_width_pt=1)

    add_text_box(s18, title_txt,
                 Inches(1.1), t + Inches(0.06), Inches(11.8), Inches(0.35),
                 font_size=13, bold=True, color=LENOVO_DARK)
    add_text_box(s18, desc_txt,
                 Inches(1.1), t + Inches(0.44), Inches(11.8), Inches(0.5),
                 font_size=11, color=GREY_TEXT)


# =============================================================================
# SLIDE 19 — Offline Setup
# =============================================================================
s19 = new_slide("Offline Setup",
                "Making the tool work without internet access")

# Why needed
add_rect(s19, Inches(0.3), Inches(1.5), Inches(12.7), Inches(0.9),
         fill_rgb=RGBColor(0xFF, 0xF3, 0xCD), line_rgb=AMBER, line_width_pt=2)
add_text_box(s19, "Why is this needed?",
             Inches(0.45), Inches(1.53), Inches(4.0), Inches(0.35),
             font_size=12, bold=True, color=RGBColor(0x66, 0x44, 0x00))
add_text_box(s19,
             "Stages 3, 4, 5, and 6 load Dexie.js (IndexedDB wrapper) and SheetJS (Excel engine) from CDN URLs. "
             "Corporate networks often block CDN domains. Running the setup script downloads these libraries "
             "locally so the tool works permanently offline.",
             Inches(0.45), Inches(1.88), Inches(12.3), Inches(0.48),
             font_size=11, color=RGBColor(0x55, 0x44, 0x00))

# How to run
add_rect(s19, Inches(0.3), Inches(2.55), Inches(6.0), Inches(4.65),
         fill_rgb=LENOVO_DARK, line_rgb=LENOVO_MID, line_width_pt=1)
add_text_box(s19, "How to Run (One-Time Only)",
             Inches(0.45), Inches(2.6), Inches(5.7), Inches(0.4),
             font_size=14, bold=True, color=WHITE)

run_steps = [
    "Navigate to the GPS_Cost_Pricing_Workbench folder",
    "Double-click   setup_offline_all.bat",
    "Wait for downloads to complete",
    "  (requires internet at this one step only)",
    "HTML files are automatically patched to use local copies",
    "",
    "After this step, the tool works permanently offline.",
    "You do NOT need to re-run setup_offline_all.bat again.",
]
bullet_block(s19, run_steps,
             Inches(0.45), Inches(3.08), Inches(5.7), Inches(4.0),
             font_size=12, bullet_color=RGBColor(0xAA, 0xDD, 0xFF))

# What it does
add_rect(s19, Inches(6.7), Inches(2.55), Inches(6.3), Inches(4.65),
         fill_rgb=LENOVO_LIGHT, line_rgb=LENOVO_MID, line_width_pt=1)
bullet_block(s19, [
    "Downloads to stage3_browser\\:",
    "  dexie.min.js       \u2014 IndexedDB wrapper library",
    "  xlsx.full.min.js   \u2014 Excel read/write engine",
    "",
    "Downloads to stage4_browser\\:",
    "  dexie.min.js       \u2014 IndexedDB wrapper library",
    "  xlsx.full.min.js   \u2014 Excel read/write engine",
    "",
    "Patches index.html in each stage to reference",
    "  local file paths instead of CDN URLs",
    "",
    "Original CDN URLs are replaced with:",
    "  ./dexie.min.js",
    "  ./xlsx.full.min.js",
],
    Inches(6.85), Inches(2.6), Inches(6.0), Inches(4.5),
    font_size=12, title="What setup_offline_all.bat Does", title_size=14,
    title_color=LENOVO_DARK, bullet_color=GREY_TEXT)


# =============================================================================
# SLIDE 20 — Roadmap: Coming Next
# =============================================================================
s20 = new_slide("Roadmap \u2014 Coming Next",
                "Remaining stages to complete the full 6-stage pricing pipeline")

COMING_CARD_BG = RGBColor(0xEE, 0xEE, 0xEE)
COMING_HEADER_BG = RGBColor(0xAA, 0xAA, 0xAA)
COMING_TEXT = RGBColor(0x44, 0x44, 0x44)

road_stages = [
    ("Stage 1", "Standard Cost Import",
     [
         "Import and validate standard cost data from source systems.",
         "Supports multiple source formats and cost currencies.",
         "Includes data quality checks and mapping to SKU hierarchy.",
         "Output: cleaned standard cost table used as input to Stage 2.",
     ]),
    ("Stage 2", "Forward Adjustment (PSC)",
     [
         "Derives Projected Service Cost (PSC) from Standard Cost:",
         "  PSC = Standard Cost x F_failure x F_parts x F_labor x F_mix",
         "F_failure : field failure rate adjustment",
         "F_parts   : parts cost forward adjustment",
         "F_labor   : labor rate forward adjustment",
         "F_mix     : service mix (IOR / EMSR) weighting",
         "Output: PSC per SKU, which feeds Stage 3 as input.",
     ]),
]

card_w = Inches(6.0)
card_h = Inches(5.5)
card_t = Inches(1.55)
card_gap = Inches(0.35)
card_start = Inches(0.7)

for i, (stg, title_txt, bullets) in enumerate(road_stages):
    lx = card_start + i * (card_w + card_gap)

    add_rect(s20, lx, card_t, card_w, card_h,
             fill_rgb=COMING_CARD_BG, line_rgb=COMING_HEADER_BG, line_width_pt=2)

    # Header
    add_rect(s20, lx, card_t, card_w, Inches(0.75), fill_rgb=COMING_HEADER_BG)
    add_text_box(s20, stg,
                 lx + Inches(0.1), card_t + Inches(0.05), card_w - Inches(0.2), Inches(0.3),
                 font_size=10, bold=True, color=WHITE)
    add_text_box(s20, title_txt,
                 lx + Inches(0.1), card_t + Inches(0.33), card_w - Inches(0.2), Inches(0.38),
                 font_size=13, bold=True, color=WHITE)

    # Coming soon badge
    add_rect(s20, lx + card_w - Inches(1.35), card_t + Inches(0.78),
             Inches(1.25), Inches(0.28), fill_rgb=COMING_HEADER_BG)
    add_text_box(s20, "COMING SOON",
                 lx + card_w - Inches(1.35), card_t + Inches(0.78),
                 Inches(1.25), Inches(0.28),
                 font_size=8, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    bullet_block(s20, bullets,
                 lx + Inches(0.1), card_t + Inches(1.12), card_w - Inches(0.2), Inches(4.25),
                 font_size=11, bullet_color=COMING_TEXT)

# Footer
add_rect(s20, 0, Inches(7.18), W, Inches(0.32), fill_rgb=LENOVO_DARK)
add_text_box(s20, "\u00a9 2026 HongfeiZhu \u00b7 SSGCDTO \u00b7 Lenovo. All rights reserved.",
             Inches(0.4), Inches(7.2), Inches(12.5), Inches(0.28),
             font_size=10, color=RGBColor(0x88, 0x88, 0x88), align=PP_ALIGN.CENTER)


# =============================================================================
# SAVE
# =============================================================================
out = r"C:\Users\Administrator\ClaudeProjects\GPS_Cost_Pricing_Workbench\GPS_Cost_Pricing_Workbench_UserManual.pptx"
prs.save(out)
print(f"Saved: {out}")
