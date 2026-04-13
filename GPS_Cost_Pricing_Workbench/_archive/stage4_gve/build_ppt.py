"""
Build GPS Pricing Workbench — Solution Document PPT
Run: python build_ppt.py
Output: GPS_Pricing_Workbench_Solution.pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy

# ---------------------------------------------------------------------------
# Brand colours
# ---------------------------------------------------------------------------
NAVY      = RGBColor(0x1B, 0x2A, 0x4A)   # dark navy — primary bg / header
RED       = RGBColor(0xE2, 0x23, 0x1A)   # Lenovo red — accents
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BG  = RGBColor(0xF4, 0xF6, 0xFA)  # slide background
MID_GREY  = RGBColor(0x8A, 0x99, 0xAA)
DARK_TEXT = RGBColor(0x1B, 0x2A, 0x4A)
GREEN     = RGBColor(0x21, 0x96, 0x53)
AMBER     = RGBColor(0xF5, 0xA6, 0x23)
SLATE     = RGBColor(0x2C, 0x3E, 0x5A)   # slightly lighter navy

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width  = SLIDE_W
prs.slide_height = SLIDE_H

BLANK = prs.slide_layouts[6]   # completely blank


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def add_rect(slide, l, t, w, h, fill_rgb, alpha=None):
    shape = slide.shapes.add_shape(1, l, t, w, h)   # MSO_SHAPE_TYPE.RECTANGLE = 1
    shape.line.fill.background()
    shape.line.width = 0
    fill = shape.fill
    fill.solid()
    fill.fore_color.rgb = fill_rgb
    return shape


def add_text_box(slide, text, l, t, w, h,
                 font_size=18, bold=False, color=WHITE,
                 align=PP_ALIGN.LEFT, wrap=True, italic=False):
    txb = slide.shapes.add_textbox(l, t, w, h)
    tf  = txb.text_frame
    tf.word_wrap = wrap
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(font_size)
    run.font.bold  = bold
    run.font.color.rgb = color
    run.font.italic = italic
    return txb


def add_para(tf, text, font_size=14, bold=False, color=DARK_TEXT,
             align=PP_ALIGN.LEFT, space_before=0, indent_level=0, italic=False):
    p = tf.add_paragraph()
    p.alignment = align
    p.level = indent_level
    p.space_before = Pt(space_before)
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(font_size)
    run.font.bold  = bold
    run.font.color.rgb = color
    run.font.italic = italic
    return p


def slide_header(slide, title, subtitle=None):
    """Navy top bar with white title."""
    add_rect(slide, 0, 0, SLIDE_W, Inches(1.1), NAVY)
    # Red accent line
    add_rect(slide, 0, Inches(1.1), SLIDE_W, Inches(0.06), RED)
    add_text_box(slide, title,
                 Inches(0.4), Inches(0.18), Inches(12.5), Inches(0.72),
                 font_size=26, bold=True, color=WHITE)
    if subtitle:
        add_text_box(slide, subtitle,
                     Inches(0.4), Inches(0.78), Inches(12), Inches(0.38),
                     font_size=13, bold=False, color=RGBColor(0xB0, 0xC4, 0xDE),
                     italic=True)


def light_bg(slide):
    add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, LIGHT_BG)


def bullet_box(slide, items, l, t, w, h,
               font_size=14, color=DARK_TEXT, header=None, header_color=NAVY):
    """Render a list of bullet strings into a text box."""
    txb = slide.shapes.add_textbox(l, t, w, h)
    tf  = txb.text_frame
    tf.word_wrap = True
    first = True
    if header:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = header
        r.font.size  = Pt(font_size + 1)
        r.font.bold  = True
        r.font.color.rgb = header_color
    for item in items:
        p = tf.paragraphs[0] if (first and not header) else tf.add_paragraph()
        first = False
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = item
        r.font.size  = Pt(font_size)
        r.font.color.rgb = color
    return txb


def colored_card(slide, l, t, w, h, fill_rgb, title, body_lines,
                 title_size=15, body_size=13, title_color=WHITE, body_color=WHITE):
    add_rect(slide, l, t, w, h, fill_rgb)
    # title
    add_text_box(slide, title, l + Inches(0.12), t + Inches(0.1),
                 w - Inches(0.24), Inches(0.35),
                 font_size=title_size, bold=True, color=title_color)
    # body
    txb = slide.shapes.add_textbox(l + Inches(0.12), t + Inches(0.45),
                                   w - Inches(0.24), h - Inches(0.55))
    tf = txb.text_frame
    tf.word_wrap = True
    first = True
    for line in body_lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        r = p.add_run()
        r.text = line
        r.font.size = Pt(body_size)
        r.font.color.rgb = body_color


def number_badge(slide, number, l, t, size=Inches(0.48)):
    add_rect(slide, l, t, size, size, RED)
    add_text_box(slide, str(number),
                 l, t, size, size,
                 font_size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)


# ---------------------------------------------------------------------------
# SLIDE 1 — Title
# ---------------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
# Full navy background
add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, NAVY)
# Red accent stripe
add_rect(slide, 0, Inches(4.5), SLIDE_W, Inches(0.08), RED)
# Diagonal red accent block top-right
add_rect(slide, Inches(10.5), 0, Inches(2.83), Inches(2.2), RGBColor(0xC0, 0x1C, 0x14))

add_text_box(slide, "GPS Pricing Workbench",
             Inches(0.6), Inches(1.6), Inches(10), Inches(1.0),
             font_size=42, bold=True, color=WHITE)

add_text_box(slide, "Solution Design Document",
             Inches(0.6), Inches(2.7), Inches(9), Inches(0.55),
             font_size=22, bold=False, color=RGBColor(0xB0, 0xC4, 0xDE))

add_text_box(slide,
             "Lenovo Global Product Support  |  Service Pricing Automation",
             Inches(0.6), Inches(3.35), Inches(10), Inches(0.4),
             font_size=14, bold=False, color=RGBColor(0x80, 0xA0, 0xC0), italic=True)

add_text_box(slide, "March 2026",
             Inches(0.6), Inches(5.2), Inches(4), Inches(0.4),
             font_size=13, color=MID_GREY)


# ---------------------------------------------------------------------------
# SLIDE 2 — Agenda
# ---------------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
light_bg(slide)
slide_header(slide, "Agenda")

topics = [
    ("01", "Business Background",        "What GPS does and why pricing is complex"),
    ("02", "Current State & Pain Points", "The Excel-based manual process today"),
    ("03", "Objectives",                  "What the Pricing Workbench must achieve"),
    ("04", "High-Level Design",           "5-stage pipeline and system architecture"),
    ("05", "Detailed Solution",           "Stage-by-stage walkthrough + GVE deep dive"),
    ("06", "UI & User Experience",        "Matrix view, side panel, GVE issues panel"),
    ("07", "Data Governance & Audit",     "Versioning, audit log, access model"),
    ("08", "Tech Stack & Deployment",     "Technology choices and offline operation"),
    ("09", "Build Status & Roadmap",      "What is live today and what comes next"),
]

col_w = Inches(5.9)
for i, (num, title, desc) in enumerate(topics):
    col = i % 2
    row = i // 2
    lx = Inches(0.5) + col * (col_w + Inches(0.6))
    ty = Inches(1.35) + row * Inches(1.22)
    add_rect(slide, lx, ty, col_w, Inches(1.1), WHITE)
    # left red stripe
    add_rect(slide, lx, ty, Inches(0.07), Inches(1.1), RED)
    add_text_box(slide, num,
                 lx + Inches(0.15), ty + Inches(0.05),
                 Inches(0.5), Inches(0.4),
                 font_size=11, bold=True, color=RED)
    add_text_box(slide, title,
                 lx + Inches(0.15), ty + Inches(0.28),
                 col_w - Inches(0.3), Inches(0.38),
                 font_size=15, bold=True, color=NAVY)
    add_text_box(slide, desc,
                 lx + Inches(0.15), ty + Inches(0.67),
                 col_w - Inches(0.3), Inches(0.38),
                 font_size=12, color=MID_GREY, italic=True)


# ---------------------------------------------------------------------------
# SLIDE 3 — Business Background
# ---------------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
light_bg(slide)
slide_header(slide, "Business Background",
             "Lenovo GPS — Global Product Support, Service Pricing Division")

# Left column: what GPS sells
add_rect(slide, Inches(0.4), Inches(1.3), Inches(5.6), Inches(5.7), WHITE)
add_rect(slide, Inches(0.4), Inches(1.3), Inches(0.08), Inches(5.7), RED)

txb = slide.shapes.add_textbox(Inches(0.6), Inches(1.4), Inches(5.2), Inches(5.4))
tf = txb.text_frame
tf.word_wrap = True
first = True
items = [
    ("What GPS Sells", True, 16, NAVY),
    ("", False, 4, NAVY),
    ("Hardware platforms:", True, 13, SLATE),
    ("   ThinkPad, IdeaPad, Legion, Commercial (ThinkCentre / ThinkStation)", False, 12, DARK_TEXT),
    ("", False, 3, NAVY),
    ("Service products:", True, 13, SLATE),
    ("   Base Warranty (1yr / 3yr / 5yr)", False, 12, DARK_TEXT),
    ("   Accidental Damage Protection (ADP)", False, 12, DARK_TEXT),
    ("   Premier Support", False, 12, DARK_TEXT),
    ("", False, 3, NAVY),
    ("Geographies:", True, 13, SLATE),
    ("   NA  |  EMEA  |  APJ  |  China", False, 12, DARK_TEXT),
    ("", False, 3, NAVY),
    ("Annual pricing cycle (e.g. FY2025, FY2026)", False, 12, DARK_TEXT),
]
for text, bold, size, color in items:
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    first = False
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color

# Right column: why pricing is hard
add_rect(slide, Inches(6.4), Inches(1.3), Inches(6.5), Inches(5.7), WHITE)
add_rect(slide, Inches(6.4), Inches(1.3), Inches(0.08), Inches(5.7), RED)

txb2 = slide.shapes.add_textbox(Inches(6.6), Inches(1.4), Inches(6.1), Inches(5.4))
tf2 = txb2.text_frame
tf2.word_wrap = True
first2 = True
items2 = [
    ("Why Pricing is Complex", True, 16, NAVY),
    ("", False, 4, NAVY),
    ("Price set at point-of-sale; costs incurred over 3–5 years", False, 12, DARK_TEXT),
    ("  Prices must be forward-looking, not historical actuals", False, 11, MID_GREY),
    ("", False, 3, NAVY),
    ("Multiple compounding adjustment factors per SKU:", False, 12, DARK_TEXT),
    ("  Failure rate trends, parts cost indices, labor inflation,", False, 11, MID_GREY),
    ("  product mix shift, attach rate changes", False, 11, MID_GREY),
    ("", False, 3, NAVY),
    ("Sales Cost is an inviolable floor:", False, 12, DARK_TEXT),
    ("  No list price may be set below Sales Cost", False, 11, MID_GREY),
    ("", False, 3, NAVY),
    ("Cross-geo consistency must be enforced:", False, 12, DARK_TEXT),
    ("  Same structural ratios expected across NA / EMEA / APJ / China", False, 11, MID_GREY),
    ("", False, 3, NAVY),
    ("Regulatory & audit requirements:", False, 12, DARK_TEXT),
    ("  Every change must be traceable with owner, reason, timestamp", False, 11, MID_GREY),
]
for text, bold, size, color in items2:
    p = tf2.paragraphs[0] if first2 else tf2.add_paragraph()
    first2 = False
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color


# ---------------------------------------------------------------------------
# SLIDE 4 — Pain Points
# ---------------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
light_bg(slide)
slide_header(slide, "Current State & Pain Points",
             "Today the entire workflow is managed in Excel — manually")

pains = [
    ("No Pricing Floor Enforcement",
     "Sales Cost is computed in a separate sheet. There is no mechanism preventing list\nprices from being set below cost. Errors go undetected until Finance review."),
    ("No Structural Validation",
     "Ratio relationships between service tiers (e.g. 3yr/1yr) and product tiers\n(ThinkPad/IdeaPad) are checked manually — inconsistencies persist into published prices."),
    ("Zero Cross-Geography Consistency",
     "NA, EMEA, APJ and China pricing is managed in separate workbooks. Structural\ndeviations or methodology errors affecting all geos are invisible until escalation."),
    ("No Audit Trail",
     "Formula changes, rate overrides, and assumption edits leave no record. Answering\n'who changed this and why?' requires manual reconstruction from version history."),
    ("Error-Prone Manual Adjustments",
     "Forward adjustment factors (failure rate, parts, labor, mix) are applied by\ncopy-pasting values across rows/columns — transpose errors and stale values are common."),
    ("No Year-over-Year Guard",
     "Cells that drift >25% from the prior cycle are not flagged automatically. Large\nmovements pass unnoticed without a written explanation or committee review."),
]

col_w = Inches(5.9)
col_h = Inches(1.72)
for i, (title, body) in enumerate(pains):
    col = i % 2
    row = i // 2
    lx = Inches(0.4) + col * (col_w + Inches(0.63))
    ty = Inches(1.28) + row * (col_h + Inches(0.14))
    add_rect(slide, lx, ty, col_w, col_h, WHITE)
    # top red bar
    add_rect(slide, lx, ty, col_w, Inches(0.05), RED)
    add_text_box(slide, title,
                 lx + Inches(0.15), ty + Inches(0.1),
                 col_w - Inches(0.3), Inches(0.38),
                 font_size=14, bold=True, color=NAVY)
    add_text_box(slide, body,
                 lx + Inches(0.15), ty + Inches(0.48),
                 col_w - Inches(0.3), Inches(1.18),
                 font_size=11.5, color=DARK_TEXT)


# ---------------------------------------------------------------------------
# SLIDE 5 — Objectives
# ---------------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
light_bg(slide)
slide_header(slide, "Objectives",
             "What the GPS Pricing Workbench must deliver")

objs = [
    ("1", "Structured, Validated Pipeline",
     "Replace ad-hoc Excel with a 5-stage workflow: Standard Cost Import "
     "→ Forward Adjustment → Sales Cost → GVE Validation → List Price Derivation."),
    ("2", "Hard Sales Cost Floor",
     "Sales Cost is calculated by the system and enforced as an inviolable "
     "pricing floor. No list price or channel price may be set below it."),
    ("3", "Automated Gradient Validation",
     "Run 4-layer GVE on every submit: monotonicity, ratio bands, cross-geo "
     "consistency, and year-over-year drift. Block submission on Critical flags."),
    ("4", "Full Audit Traceability",
     "Every change — factor adjustment, rate override, assumption edit — "
     "is logged with timestamp, user, old value, new value, and reason."),
    ("5", "Versioned Pricing Cycles",
     "Each annual cycle is a sealed snapshot once submitted. Prior cycles "
     "are read-only and form the baseline for YoY comparison in future cycles."),
    ("6", "Offline Desktop Operation",
     "The tool runs entirely locally (no cloud dependency). Data stored in "
     "SQLite. Launchable by non-technical users via a single start.bat file."),
]

for i, (num, title, body) in enumerate(objs):
    ty = Inches(1.32) + i * Inches(0.97)
    # number badge
    add_rect(slide, Inches(0.4), ty, Inches(0.46), Inches(0.46), RED)
    add_text_box(slide, num, Inches(0.4), ty, Inches(0.46), Inches(0.46),
                 font_size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_rect(slide, Inches(1.0), ty, Inches(11.9), Inches(0.82), WHITE)
    add_text_box(slide, title,
                 Inches(1.15), ty + Inches(0.05),
                 Inches(11.5), Inches(0.32),
                 font_size=14, bold=True, color=NAVY)
    add_text_box(slide, body,
                 Inches(1.15), ty + Inches(0.36),
                 Inches(11.5), Inches(0.42),
                 font_size=12, color=DARK_TEXT)


# ---------------------------------------------------------------------------
# SLIDE 6 — High-Level Design: 5-Stage Pipeline
# ---------------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
light_bg(slide)
slide_header(slide, "High-Level Design — 5-Stage Pricing Pipeline")

stages = [
    ("Stage 1",  "Standard\nCost Import",    "Finance baseline\n(backward-looking\nactuals)"),
    ("Stage 2",  "Forward\nAdjustment",       "4 factors applied:\nFailure / Parts /\nLabor / Mix"),
    ("Stage 3",  "Sales Cost\nCalculation",   "PSC × (1+R_cont)\n× (1+R_overhead)\nPricing floor"),
    ("Stage 4",  "GVE\nValidation",           "4-layer automated\nvalidation engine\nBlocks on Critical"),
    ("Stage 5",  "List Price\nDerivation",    "B2C: Cost/(1-GM%)\nB2B: Cost×(1+Mkup%)\n+ PFV check"),
]

stage_w = Inches(2.18)
stage_h = Inches(3.2)
gap     = Inches(0.28)
total_w = len(stages) * stage_w + (len(stages) - 1) * gap
start_x = (SLIDE_W - total_w) / 2
ty      = Inches(1.6)

fills = [SLATE, SLATE, NAVY, RED, SLATE]

for i, (label, title, body) in enumerate(stages):
    lx = start_x + i * (stage_w + gap)
    add_rect(slide, lx, ty, stage_w, stage_h, fills[i])
    # stage label
    add_text_box(slide, label,
                 lx + Inches(0.1), ty + Inches(0.12),
                 stage_w - Inches(0.2), Inches(0.3),
                 font_size=10, bold=False, color=RGBColor(0xB0, 0xC4, 0xDE), italic=True)
    add_text_box(slide, title,
                 lx + Inches(0.1), ty + Inches(0.42),
                 stage_w - Inches(0.2), Inches(0.88),
                 font_size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text_box(slide, body,
                 lx + Inches(0.1), ty + Inches(1.38),
                 stage_w - Inches(0.2), Inches(1.65),
                 font_size=11.5, color=RGBColor(0xD0, 0xE0, 0xF0), align=PP_ALIGN.CENTER)
    # arrow (not after last)
    if i < len(stages) - 1:
        ax = lx + stage_w + Inches(0.05)
        ay = ty + stage_h / 2 - Inches(0.1)
        add_text_box(slide, ">",
                     ax, ay, gap - Inches(0.1), Inches(0.3),
                     font_size=18, bold=True, color=RED, align=PP_ALIGN.CENTER)

# Bottom note
add_text_box(slide,
             "Sales Cost (Stage 3 output) is the system-enforced pricing floor — "
             "it cannot be manually overridden to a lower value at any subsequent stage.",
             Inches(0.5), Inches(5.05), Inches(12.3), Inches(0.5),
             font_size=12, color=SLATE, italic=True)

# Architecture note
add_rect(slide, Inches(0.5), Inches(5.6), Inches(12.3), Inches(1.55), WHITE)
add_rect(slide, Inches(0.5), Inches(5.6), Inches(0.07), Inches(1.55), NAVY)
arch_lines = [
    ("Tech stack:  ", True),
    ("Python 3.12 + Flask 3.1  |  SQLite (local, no server)  |  "
     "Browser UI on localhost:5000  |  Starts via start.bat  |  "
     "Excel import via openpyxl", False),
]
txb = slide.shapes.add_textbox(Inches(0.7), Inches(5.72), Inches(11.9), Inches(1.3))
tf = txb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
for t, b in arch_lines:
    r = p.add_run()
    r.text = t
    r.font.size = Pt(12)
    r.font.bold = b
    r.font.color.rgb = NAVY if b else DARK_TEXT


# ---------------------------------------------------------------------------
# SLIDE 7 — Data Model & Dimensions
# ---------------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
light_bg(slide)
slide_header(slide, "Data Model — Core Dimensions & Schema")

# Left: dimensions
add_rect(slide, Inches(0.4), Inches(1.28), Inches(5.8), Inches(5.72), WHITE)
add_rect(slide, Inches(0.4), Inches(1.28), Inches(0.07), Inches(5.72), RED)
txb = slide.shapes.add_textbox(Inches(0.62), Inches(1.38), Inches(5.4), Inches(5.5))
tf = txb.text_frame
tf.word_wrap = True
items = [
    ("The 4 Core Dimensions", True, 15, NAVY),
    ("", False, 5, NAVY),
    ("Every cost and price record is identified by:", False, 12, DARK_TEXT),
    ("", False, 4, NAVY),
    ("  Product Tier (configurable sequence)", True, 13, SLATE),
    ("    TP Entry / TP Main / TP Halo / TP WS / TP WS Entry", False, 11, DARK_TEXT),
    ("    Auto-detected from imported Excel file", False, 11, MID_GREY),
    ("", False, 3, NAVY),
    ("  Service Type / Upgrade Window", True, 13, SLATE),
    ("    1yr / 3yr / 5yr base  |  ADP  |  Premier Support", False, 11, DARK_TEXT),
    ("    Encoded as upgrade_years + delivery_type", False, 11, MID_GREY),
    ("", False, 3, NAVY),
    ("  Geography (sub-region granularity)", True, 13, SLATE),
    ("    NA / EMEA sub-regions (BENELUX, NORDICS, etc.) / APJ / China", False, 11, DARK_TEXT),
    ("    User decides validation level — sub-region or rollup", False, 11, MID_GREY),
    ("", False, 3, NAVY),
    ("  Pricing Cycle Year", True, 13, SLATE),
    ("    FY2025, FY2026 ... — each cycle is an isolated snapshot", False, 11, DARK_TEXT),
    ("    Prior cycles are read-only once submitted", False, 11, MID_GREY),
]
first = True
for text, bold, size, color in items:
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    first = False
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color

# Right: key tables
add_rect(slide, Inches(6.55), Inches(1.28), Inches(6.35), Inches(5.72), WHITE)
add_rect(slide, Inches(6.55), Inches(1.28), Inches(0.07), Inches(5.72), RED)
txb2 = slide.shapes.add_textbox(Inches(6.77), Inches(1.38), Inches(5.95), Inches(5.5))
tf2 = txb2.text_frame
tf2.word_wrap = True
items2 = [
    ("Key SQLite Tables", True, 15, NAVY),
    ("", False, 5, NAVY),
    ("cycles", True, 13, SLATE),
    ("    id, name, geo, status, created_at", False, 11, DARK_TEXT),
    ("    status: draft | gve_clear | submitted (read-only once submitted)", False, 11, MID_GREY),
    ("", False, 3, NAVY),
    ("skus", True, 13, SLATE),
    ("    part_number, tier, base_warranty, upgrade_years,", False, 11, DARK_TEXT),
    ("    delivery_type, upgrade_description — linked to cycle_id", False, 11, DARK_TEXT),
    ("", False, 3, NAVY),
    ("sku_prices", True, 13, SLATE),
    ("    sku_id, region, sales_cost, channel_price", False, 11, DARK_TEXT),
    ("    computed_list_price_b2c, computed_quoted_floor_b2b", False, 11, DARK_TEXT),
    ("", False, 3, NAVY),
    ("gve_results", True, 13, SLATE),
    ("    layer, severity, violation_type, message", False, 11, DARK_TEXT),
    ("    region, tier, upgrade_years, part_number", False, 11, DARK_TEXT),
    ("", False, 3, NAVY),
    ("audit_log", True, 13, SLATE),
    ("    timestamp, username, table_name, record_id", False, 11, DARK_TEXT),
    ("    field_name, old_value, new_value, reason", False, 11, DARK_TEXT),
    ("", False, 3, NAVY),
    ("prior_baseline, pfv_benchmarks, tier_sequence, settings", False, 12, DARK_TEXT),
]
first2 = True
for text, bold, size, color in items2:
    p = tf2.paragraphs[0] if first2 else tf2.add_paragraph()
    first2 = False
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color


# ---------------------------------------------------------------------------
# SLIDE 8 — Stages 1-3: Cost Pipeline
# ---------------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
light_bg(slide)
slide_header(slide, "Detailed Solution — Stages 1–3: Cost Calculation Pipeline")

# Stage 1
add_rect(slide, Inches(0.4), Inches(1.28), Inches(3.9), Inches(5.65), WHITE)
add_rect(slide, Inches(0.4), Inches(1.28), Inches(0.07), Inches(5.65), NAVY)
txb = slide.shapes.add_textbox(Inches(0.62), Inches(1.38), Inches(3.6), Inches(5.4))
tf = txb.text_frame
tf.word_wrap = True
items = [
    ("Stage 1 — Standard Cost Import", True, 14, NAVY),
    ("", False, 5, NAVY),
    ("Excel file upload (openpyxl parser)", False, 12, DARK_TEXT),
    ("", False, 3, NAVY),
    ("Auto-detects:", True, 12, SLATE),
    ("  - Geographic columns (sub-regions)", False, 11, DARK_TEXT),
    ("  - Service tiers from header rows", False, 11, DARK_TEXT),
    ("  - Upgrade window (years)", False, 11, DARK_TEXT),
    ("", False, 3, NAVY),
    ("Tested with:", True, 12, SLATE),
    ("  EMEA ThinkNB — 145 SKUs,", False, 11, DARK_TEXT),
    ("  15 sub-regions, 5 tiers", False, 11, DARK_TEXT),
    ("", False, 3, NAVY),
    ("Standard Cost = Finance actuals baseline.", False, 11, MID_GREY),
    ("No calculation at this stage.", False, 11, MID_GREY),
    ("Input only.", False, 11, MID_GREY),
    ("", False, 3, NAVY),
    ("Prior cycle baseline for YoY (Layer 4)", True, 12, SLATE),
    ("entered here as CSV paste or", False, 11, DARK_TEXT),
    ("Excel import (roadmap).", False, 11, DARK_TEXT),
]
first = True
for text, bold, size, color in items:
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    first = False
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color

# Arrow
add_text_box(slide, ">", Inches(4.38), Inches(3.7), Inches(0.35), Inches(0.4),
             font_size=22, bold=True, color=RED, align=PP_ALIGN.CENTER)

# Stage 2
add_rect(slide, Inches(4.75), Inches(1.28), Inches(4.1), Inches(5.65), WHITE)
add_rect(slide, Inches(4.75), Inches(1.28), Inches(0.07), Inches(5.65), NAVY)
txb2 = slide.shapes.add_textbox(Inches(4.97), Inches(1.38), Inches(3.8), Inches(5.4))
tf2 = txb2.text_frame
tf2.word_wrap = True
items2 = [
    ("Stage 2 — Forward Adjustment", True, 14, NAVY),
    ("Projected Service Cost (PSC)", False, 12, RED),
    ("", False, 5, NAVY),
    ("PSC = Std Cost × F_failure × F_parts", False, 12, DARK_TEXT),
    ("              × F_labor × F_mix", False, 12, DARK_TEXT),
    ("", False, 4, NAVY),
    ("Each factor requires:", True, 12, SLATE),
    ("  - Numeric value", False, 11, DARK_TEXT),
    ("  - Source label (data origin)", False, 11, DARK_TEXT),
    ("  - Owner field (accountability)", False, 11, DARK_TEXT),
    ("", False, 4, NAVY),
    ("Factor scope hierarchy:", True, 12, SLATE),
    ("  Cell-level overrides row/col default", False, 11, DARK_TEXT),
    ("  Row = all service types for a product", False, 11, DARK_TEXT),
    ("  Column = all products for a service type", False, 11, DARK_TEXT),
    ("", False, 4, NAVY),
    ("F_failure — projected vs historical failure rate", False, 11, MID_GREY),
    ("F_parts   — NAND, panel, obsolescence index", False, 11, MID_GREY),
    ("F_labor   — regional labor / logistics inflation", False, 11, MID_GREY),
    ("F_mix     — product mix / attach rate correction", False, 11, MID_GREY),
]
first2 = True
for text, bold, size, color in items2:
    p = tf2.paragraphs[0] if first2 else tf2.add_paragraph()
    first2 = False
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color

# Arrow
add_text_box(slide, ">", Inches(8.93), Inches(3.7), Inches(0.35), Inches(0.4),
             font_size=22, bold=True, color=RED, align=PP_ALIGN.CENTER)

# Stage 3
add_rect(slide, Inches(9.3), Inches(1.28), Inches(3.6), Inches(5.65), WHITE)
add_rect(slide, Inches(9.3), Inches(1.28), Inches(0.07), Inches(5.65), RED)
txb3 = slide.shapes.add_textbox(Inches(9.52), Inches(1.38), Inches(3.3), Inches(5.4))
tf3 = txb3.text_frame
tf3.word_wrap = True
items3 = [
    ("Stage 3 — Sales Cost", True, 14, RED),
    ("The Pricing Floor", True, 12, NAVY),
    ("", False, 5, NAVY),
    ("Sales Cost =", False, 12, DARK_TEXT),
    ("  PSC", False, 12, DARK_TEXT),
    ("  × (1 + R_contingency)", False, 12, DARK_TEXT),
    ("  × (1 + R_overhead)", False, 12, DARK_TEXT),
    ("", False, 4, NAVY),
    ("R_contingency:", True, 12, SLATE),
    ("  Lookup by platform maturity", False, 11, DARK_TEXT),
    ("  × service window (1–3yr / 4–5yr)", False, 11, DARK_TEXT),
    ("  6 configurable rates in Settings", False, 11, DARK_TEXT),
    ("  Maturity: New / Mature Refresh /", False, 11, DARK_TEXT),
    ("  Mature — set per tier per cycle", False, 11, DARK_TEXT),
    ("", False, 4, NAVY),
    ("R_overhead:", True, 12, SLATE),
    ("  Total Fixed Cost / Projected Units", False, 11, DARK_TEXT),
    ("  Single global rate, set annually", False, 11, DARK_TEXT),
    ("  Auto-calculated from Settings input", False, 11, DARK_TEXT),
    ("", False, 4, NAVY),
    ("INVIOLABLE: Sales Cost cannot be", False, 11, RED),
    ("manually overridden downward.", False, 11, RED),
]
first3 = True
for text, bold, size, color in items3:
    p = tf3.paragraphs[0] if first3 else tf3.add_paragraph()
    first3 = False
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color


# ---------------------------------------------------------------------------
# SLIDE 9 — GVE Overview
# ---------------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
light_bg(slide)
slide_header(slide, "Stage 4 — Gradient Validation Engine (GVE)",
             "The most critical feature: automated 4-layer validation of the full pricing matrix")

# 4 layer cards
cards = [
    (NAVY,  "Layer 1 — Directional Monotonicity",
     ["Hard block (Critical severity)",
      "Avg cost per tier must follow configured",
      "tier sequence order.",
      "",
      "Within each (upgrade_years, delivery_type,",
      "region): tier[N] <= tier[N+1]",
      "",
      "Violation = Critical flag",
      "Blocks submission immediately."]),
    (SLATE, "Layer 2 — Ratio Bands",
     ["Critical below floor / Warning above ceiling",
      "",
      "3yr / 1yr ratio: expected 1.8x – 2.8x",
      "5yr / 3yr ratio: expected 1.3x – 1.7x",
      "4yr / 2yr ratio: configurable",
      "",
      "Checked per (tier, delivery_type, region)",
      "Thresholds fully configurable in Settings.",
      "Below floor = Critical; Above ceiling = Warning."]),
    (RGBColor(0x1A, 0x5C, 0x8A), "Layer 3 — Cross-Geo Consistency",
     ["Warning or Systemic severity",
      "",
      "For each (tier, delivery_type, upgrade_years):",
      "compare avg cost across all regions.",
      "",
      "Any region deviating >20% from",
      "cross-region mean → Warning.",
      "",
      "3+ regions with same violation → SYSTEMIC",
      "(indicates methodology error, not data error)"]),
    (RED,   "Layer 4 — Year-over-Year Drift",
     ["Requires prior cycle baseline input",
      "",
      "Individual cell change >25%:",
      "  Written explanation required,",
      "  blocks submission if unresolved.",
      "",
      "Geo-level average change >20%:",
      "  Flag for Supply Chain review.",
      "",
      "No baseline entered = layer skipped."]),
]

card_w = Inches(3.0)
card_h = Inches(5.35)
gap    = Inches(0.24)
total  = len(cards) * card_w + (len(cards) - 1) * gap
sx     = (SLIDE_W - total) / 2

for i, (fill, title, body) in enumerate(cards):
    lx = sx + i * (card_w + gap)
    ty = Inches(1.3)
    add_rect(slide, lx, ty, card_w, card_h, fill)
    add_text_box(slide, title,
                 lx + Inches(0.12), ty + Inches(0.1),
                 card_w - Inches(0.24), Inches(0.55),
                 font_size=12.5, bold=True, color=WHITE)
    txb = slide.shapes.add_textbox(lx + Inches(0.12), ty + Inches(0.7),
                                   card_w - Inches(0.24), card_h - Inches(0.82))
    tf = txb.text_frame
    tf.word_wrap = True
    first = True
    for line in body:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        r = p.add_run()
        r.text = line
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(0xD0, 0xE8, 0xFF) if line else WHITE

# Status row
add_rect(slide, Inches(0.4), Inches(6.78), Inches(12.5), Inches(0.48), WHITE)
statuses = [
    ("Clear", GREEN, "All layers passed — geo can proceed to List Price"),
    ("Warnings", AMBER, "Non-critical issues flagged — proceed with review"),
    ("Blocked", RED, "Unresolved Critical flags — submission blocked"),
    ("Systemic", NAVY, "Cross-geo methodology error — escalation required"),
]
for i, (label, color, desc) in enumerate(statuses):
    lx = Inches(0.6) + i * Inches(3.1)
    add_rect(slide, lx, Inches(6.82), Inches(0.9), Inches(0.32), color)
    add_text_box(slide, label, lx, Inches(6.82), Inches(0.9), Inches(0.32),
                 font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text_box(slide, desc,
                 lx + Inches(0.95), Inches(6.84), Inches(2.1), Inches(0.32),
                 font_size=11, color=DARK_TEXT)


# ---------------------------------------------------------------------------
# SLIDE 10 — Stage 5: List Price
# ---------------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
light_bg(slide)
slide_header(slide, "Stage 5 — List Price Derivation",
             "B2C and B2B pricing models with output validation checks")

# B2C
add_rect(slide, Inches(0.4), Inches(1.3), Inches(5.9), Inches(2.7), NAVY)
add_text_box(slide, "B2C — Consumer List Price",
             Inches(0.6), Inches(1.4), Inches(5.5), Inches(0.45),
             font_size=16, bold=True, color=WHITE)
add_text_box(slide, "List Price  =  Sales Cost  /  (1 - GM%)",
             Inches(0.6), Inches(1.92), Inches(5.5), Inches(0.45),
             font_size=14, bold=True, color=RGBColor(0xFF, 0xCC, 0x44))
add_text_box(slide,
             "GM% is configurable per tier in Settings.\n"
             "Fallback: gm_pct_default (default 30%).\n"
             "Ensures minimum gross margin on consumer sales.",
             Inches(0.6), Inches(2.45), Inches(5.5), Inches(1.4),
             font_size=12, color=RGBColor(0xC0, 0xD8, 0xF0))

# B2B
add_rect(slide, Inches(6.6), Inches(1.3), Inches(6.3), Inches(2.7), SLATE)
add_text_box(slide, "B2B — Commercial Quoted Floor",
             Inches(6.8), Inches(1.4), Inches(5.9), Inches(0.45),
             font_size=16, bold=True, color=WHITE)
add_text_box(slide, "Quoted Floor  =  Sales Cost  ×  (1 + Markup%)",
             Inches(6.8), Inches(1.92), Inches(5.9), Inches(0.45),
             font_size=14, bold=True, color=RGBColor(0xFF, 0xCC, 0x44))
add_text_box(slide,
             "Markup% is configurable per tier in Settings.\n"
             "System outputs a pricing band: floor to ceiling.\n"
             "Sales teams can negotiate within the band.",
             Inches(6.8), Inches(2.45), Inches(5.9), Inches(1.4),
             font_size=12, color=RGBColor(0xC0, 0xD8, 0xF0))

# Output validation checks
add_rect(slide, Inches(0.4), Inches(4.2), Inches(12.5), Inches(2.9), WHITE)
add_rect(slide, Inches(0.4), Inches(4.2), Inches(0.07), Inches(2.9), RED)
add_text_box(slide, "Output Validation Checks",
             Inches(0.65), Inches(4.28), Inches(12), Inches(0.38),
             font_size=15, bold=True, color=NAVY)

checks = [
    ("Channel Price Floor",
     "Channel price (C-Price = internal partner price) must be >= Sales Cost.\n"
     "CHANNEL_BELOW_COST violation = Critical — blocks output."),
    ("PFV Competitive Benchmark",
     "If competitive benchmark data exists (pfv_benchmarks table), B2C list price\n"
     "is compared. Exceeds benchmark → Warning (EXCEEDS_PFV). Import TBD."),
    ("Device Price Ratio (Roadmap)",
     "Service/device ratio checked against configurable threshold\n"
     "(default: 20% consumer, 15% commercial). Flags outlier pricing."),
]
for i, (title, body) in enumerate(checks):
    lx = Inches(0.65) + i * Inches(4.1)
    add_text_box(slide, title,
                 lx, Inches(4.74), Inches(3.9), Inches(0.35),
                 font_size=13, bold=True, color=SLATE)
    add_text_box(slide, body,
                 lx, Inches(5.12), Inches(3.9), Inches(0.9),
                 font_size=11, color=DARK_TEXT)


# ---------------------------------------------------------------------------
# SLIDE 11 — UI & User Experience
# ---------------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
light_bg(slide)
slide_header(slide, "UI & User Experience",
             "Browser-based local UI served by Flask on localhost:5000")

# Left: screen list
add_rect(slide, Inches(0.4), Inches(1.28), Inches(4.5), Inches(5.7), WHITE)
add_rect(slide, Inches(0.4), Inches(1.28), Inches(0.07), Inches(5.7), RED)
txb = slide.shapes.add_textbox(Inches(0.62), Inches(1.38), Inches(4.2), Inches(5.5))
tf = txb.text_frame
tf.word_wrap = True
screens = [
    ("Application Screens", True, 15, NAVY),
    ("", False, 5, NAVY),
    ("Login", True, 13, SLATE),
    ("  Simple name entry — no auth required.", False, 11, DARK_TEXT),
    ("  Username stamped on all audit entries.", False, 11, MID_GREY),
    ("", False, 4, NAVY),
    ("Dashboard", True, 13, SLATE),
    ("  All active pricing cycles + GVE status badges.", False, 11, DARK_TEXT),
    ("  Create new cycle or open existing.", False, 11, MID_GREY),
    ("", False, 4, NAVY),
    ("Cycle View  (central UI)", True, 13, SLATE),
    ("  Matrix table: rows = tiers, cols = service types.", False, 11, DARK_TEXT),
    ("  Geography tabs (EMEA sub-regions etc.).", False, 11, DARK_TEXT),
    ("  Cell color: green / amber / red from GVE.", False, 11, DARK_TEXT),
    ("  Side panel: all inputs, computed values,", False, 11, DARK_TEXT),
    ("  factor breakdown, and GVE flags for selection.", False, 11, DARK_TEXT),
    ("  GVE issues panel: all violations with filter by", False, 11, DARK_TEXT),
    ("  severity, geography, systemic flag.", False, 11, DARK_TEXT),
    ("", False, 4, NAVY),
    ("Settings", True, 13, SLATE),
    ("  R_overhead, R_contingency table, GM%/Markup%,", False, 11, DARK_TEXT),
    ("  tier sequence, ratio band thresholds.", False, 11, DARK_TEXT),
    ("", False, 4, NAVY),
    ("Export", True, 13, SLATE),
    ("  Full matrix CSV, GVE Health Report (HTML/PDF),", False, 11, DARK_TEXT),
    ("  List price output CSV.", False, 11, DARK_TEXT),
]
first = True
for text, bold, size, color in screens:
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    first = False
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color

# Right: matrix view mock
add_rect(slide, Inches(5.2), Inches(1.28), Inches(7.7), Inches(5.7), NAVY)
add_text_box(slide, "Matrix View — Cycle Screen Concept",
             Inches(5.4), Inches(1.35), Inches(7.3), Inches(0.38),
             font_size=13, bold=True, color=WHITE)

# Tab strip
tab_labels = ["EMEA — BENELUX", "NORDICS", "DACH", "UK&I", "FR"]
tab_colors = [RED, SLATE, SLATE, SLATE, SLATE]
for i, (lbl, clr) in enumerate(zip(tab_labels, tab_colors)):
    tx = Inches(5.25) + i * Inches(1.48)
    add_rect(slide, tx, Inches(1.78), Inches(1.42), Inches(0.3), clr)
    add_text_box(slide, lbl, tx, Inches(1.78), Inches(1.42), Inches(0.3),
                 font_size=9, bold=(i == 0), color=WHITE, align=PP_ALIGN.CENTER)

# Column headers
cols = ["", "1yr Base", "3yr Base", "5yr Base", "ADP", "Premier"]
row_h = Inches(0.48)
col_w2 = Inches(1.22)
start_x2 = Inches(5.25)
start_y  = Inches(2.12)
for j, col in enumerate(cols):
    cx = start_x2 + j * col_w2
    add_rect(slide, cx, start_y, col_w2, row_h, SLATE)
    add_text_box(slide, col, cx, start_y, col_w2, row_h,
                 font_size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# Data rows
tier_rows = [
    ("TP Entry",    ["$18.40", "$44.20", "$62.10", "$78.30", "$54.60"], [GREEN, GREEN, GREEN, AMBER, GREEN]),
    ("TP Main",     ["$22.10", "$52.80", "$75.40", "$91.20", "$64.80"], [GREEN, GREEN, GREEN, GREEN, GREEN]),
    ("TP Halo",     ["$28.60", "$67.30", "$96.50", "$112.40", "$84.20"], [GREEN, GREEN, RED, GREEN, GREEN]),
    ("TP WS Entry", ["$31.20", "$74.10", "$105.30", "$124.60", "$92.10"], [GREEN, GREEN, GREEN, GREEN, GREEN]),
    ("TP WS",       ["$38.80", "$92.40", "$131.20", "$155.80", "$114.30"], [GREEN, AMBER, GREEN, GREEN, GREEN]),
]
cell_colors_fill = {GREEN: RGBColor(0x1A, 0x6E, 0x3A), AMBER: RGBColor(0x8A, 0x5A, 0x00), RED: RGBColor(0x8A, 0x10, 0x10)}
for i, (tier_name, values, statuses) in enumerate(tier_rows):
    ry = start_y + (i + 1) * row_h
    row_bg = RGBColor(0x22, 0x38, 0x58) if i % 2 == 0 else RGBColor(0x1E, 0x30, 0x4E)
    add_rect(slide, start_x2, ry, col_w2, row_h, row_bg)
    add_text_box(slide, tier_name, start_x2, ry, col_w2, row_h,
                 font_size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    for j, (val, status) in enumerate(zip(values, statuses)):
        cx = start_x2 + (j + 1) * col_w2
        add_rect(slide, cx, ry, col_w2, row_h, row_bg)
        indicator_color = cell_colors_fill[status]
        add_rect(slide, cx + col_w2 - Inches(0.12), ry + Inches(0.1),
                 Inches(0.08), row_h - Inches(0.2), indicator_color)
        add_text_box(slide, val, cx, ry, col_w2 - Inches(0.15), row_h,
                     font_size=10, color=WHITE, align=PP_ALIGN.CENTER)

# Legend
add_text_box(slide,
             "  Green = GVE Clear   Amber = Warning   Red = Critical / Blocked",
             Inches(5.25), Inches(4.6), Inches(7.4), Inches(0.35),
             font_size=10, color=MID_GREY, italic=True)

# Side panel hint
add_rect(slide, Inches(5.25), Inches(5.0), Inches(7.4), Inches(0.9), SLATE)
add_text_box(slide,
             "Side Panel (shown on cell click): displays all inputs, PSC breakdown, "
             "Sales Cost floor, computed list prices, and any active GVE flags for "
             "the selected SKU × region combination.",
             Inches(5.4), Inches(5.05), Inches(7.1), Inches(0.82),
             font_size=11, color=RGBColor(0xC0, 0xD8, 0xF0))


# ---------------------------------------------------------------------------
# SLIDE 12 — Audit Trail & Data Governance
# ---------------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
light_bg(slide)
slide_header(slide, "Data Governance & Audit Trail")

items_l = [
    ("Audit Log — Every Change Recorded", True, 15, NAVY),
    ("", False, 5, NAVY),
    ("Every write operation logs:", False, 12, DARK_TEXT),
    ("  timestamp         — exact datetime of change", False, 11, DARK_TEXT),
    ("  username          — name entered at login", False, 11, DARK_TEXT),
    ("  table_name        — which entity was changed", False, 11, DARK_TEXT),
    ("  record_id         — which row was affected", False, 11, DARK_TEXT),
    ("  field_name        — which field changed", False, 11, DARK_TEXT),
    ("  old_value         — previous value", False, 11, DARK_TEXT),
    ("  new_value         — new value", False, 11, DARK_TEXT),
    ("  reason            — free-text justification (required for", False, 11, DARK_TEXT),
    ("                       YoY drift explanations)", False, 11, DARK_TEXT),
    ("", False, 5, NAVY),
    ("Answering 'who changed this and why?' is a single query.", False, 12, MID_GREY),
    ("No reconstruction from Excel version history required.", False, 12, MID_GREY),
]

add_rect(slide, Inches(0.4), Inches(1.28), Inches(5.9), Inches(5.7), WHITE)
add_rect(slide, Inches(0.4), Inches(1.28), Inches(0.07), Inches(5.7), RED)
txb = slide.shapes.add_textbox(Inches(0.62), Inches(1.38), Inches(5.6), Inches(5.5))
tf = txb.text_frame
tf.word_wrap = True
first = True
for text, bold, size, color in items_l:
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    first = False
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color

items_r = [
    ("Versioned Pricing Cycles", True, 15, NAVY),
    ("", False, 5, NAVY),
    ("Each cycle progresses through states:", True, 12, SLATE),
    ("  draft       — actively being worked on", False, 11, DARK_TEXT),
    ("  gve_clear   — all GVE layers passed", False, 11, DARK_TEXT),
    ("  submitted   — sealed, read-only", False, 11, DARK_TEXT),
    ("", False, 4, NAVY),
    ("Prior cycle = baseline for Layer 4 YoY comparison.", False, 12, DARK_TEXT),
    ("Prior costs entered as CSV paste at import time.", False, 12, DARK_TEXT),
    ("", False, 5, NAVY),
    ("Access Model", True, 15, NAVY),
    ("", False, 5, NAVY),
    ("Simple name-based identity — no auth server required.", False, 12, DARK_TEXT),
    ("Suitable for offline operation.", False, 12, DARK_TEXT),
    ("Username is set at login and stamped on all audit entries.", False, 12, DARK_TEXT),
    ("", False, 5, NAVY),
    ("Export Formats", True, 15, NAVY),
    ("", False, 5, NAVY),
    ("Full pricing matrix CSV (per cycle)", False, 12, DARK_TEXT),
    ("Gradient Health Report — HTML or PDF", False, 12, DARK_TEXT),
    ("List price output CSV (B2C + B2B floors)", False, 12, DARK_TEXT),
]

add_rect(slide, Inches(6.6), Inches(1.28), Inches(6.3), Inches(5.7), WHITE)
add_rect(slide, Inches(6.6), Inches(1.28), Inches(0.07), Inches(5.7), RED)
txb2 = slide.shapes.add_textbox(Inches(6.82), Inches(1.38), Inches(6.0), Inches(5.5))
tf2 = txb2.text_frame
tf2.word_wrap = True
first2 = True
for text, bold, size, color in items_r:
    p = tf2.paragraphs[0] if first2 else tf2.add_paragraph()
    first2 = False
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color


# ---------------------------------------------------------------------------
# SLIDE 13 — Tech Stack
# ---------------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
light_bg(slide)
slide_header(slide, "Tech Stack & Deployment")

components = [
    (NAVY,  "Runtime",
     "Python 3.12",
     "C:\\Users\\Administrator\\AppData\\Local\\\nPrograms\\Python\\Python312\\python.exe"),
    (SLATE, "Web Framework",
     "Flask 3.1",
     "Serves the browser UI on localhost:5000.\nHandles all routing and form logic."),
    (RGBColor(0x1A, 0x5C, 0x8A), "Database",
     "SQLite (built-in)",
     "Single file: pricing.db\nNo database server required.\nFull ACID transactions."),
    (RED,   "Excel Parser",
     "openpyxl 3.1",
     "Reads GPS pricing Excel files.\nAuto-detects geo columns, tiers,\nand upgrade windows."),
    (RGBColor(0x2A, 0x6A, 0x3A), "Frontend",
     "Jinja2 + HTML/CSS/JS",
     "Templates rendered by Flask.\nMatrix table, side panel, GVE panel,\nSettings and Export screens."),
    (RGBColor(0x6A, 0x3A, 0x2A), "Launcher",
     "start.bat",
     "Double-click to start the server\nand open the browser automatically.\nNo CLI required."),
]

cw = Inches(3.85)
ch = Inches(2.55)
gp = Inches(0.3)
for i, (fill, cat, name, desc) in enumerate(components):
    col = i % 3
    row = i // 3
    lx = Inches(0.5) + col * (cw + gp)
    ty = Inches(1.35) + row * (ch + gp)
    add_rect(slide, lx, ty, cw, ch, fill)
    add_text_box(slide, cat,
                 lx + Inches(0.15), ty + Inches(0.1),
                 cw - Inches(0.3), Inches(0.28),
                 font_size=10, bold=False, color=RGBColor(0xB0, 0xC4, 0xDE), italic=True)
    add_text_box(slide, name,
                 lx + Inches(0.15), ty + Inches(0.38),
                 cw - Inches(0.3), Inches(0.45),
                 font_size=18, bold=True, color=WHITE)
    add_text_box(slide, desc,
                 lx + Inches(0.15), ty + Inches(0.9),
                 cw - Inches(0.3), Inches(1.55),
                 font_size=11, color=RGBColor(0xC0, 0xD8, 0xF0))

# Deployment note
add_rect(slide, Inches(0.5), Inches(6.68), Inches(12.33), Inches(0.55), WHITE)
add_rect(slide, Inches(0.5), Inches(6.68), Inches(0.07), Inches(0.55), NAVY)
add_text_box(slide,
             "Deployment:  No installer, no cloud dependency. "
             "Copy folder to target machine, ensure Python 3.12 is present, double-click start.bat. "
             "PyInstaller standalone .exe packaging is on the roadmap to eliminate even the Python dependency.",
             Inches(0.7), Inches(6.72), Inches(12.0), Inches(0.48),
             font_size=11, color=DARK_TEXT)


# ---------------------------------------------------------------------------
# SLIDE 14 — Build Status & Roadmap
# ---------------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
light_bg(slide)
slide_header(slide, "Build Status & Roadmap")

# Built column
add_rect(slide, Inches(0.4), Inches(1.28), Inches(5.9), Inches(5.7), WHITE)
add_rect(slide, Inches(0.4), Inches(1.28), Inches(0.07), Inches(5.7), GREEN)
add_text_box(slide, "Built & Working",
             Inches(0.6), Inches(1.33), Inches(5.5), Inches(0.42),
             font_size=15, bold=True, color=GREEN)

built = [
    "app.py — Flask entry point, session management, login",
    "database.py — Full SQLite schema + audit log helpers",
    "engine/excel_parser.py — Auto-detects geo cols, tiers,",
    "  upgrade years from GPS pricing Excel files",
    "  (tested: 145 SKUs, 15 sub-regions, 5 tiers)",
    "engine/gve_engine.py — Full 4-layer GVE implementation",
    "  Layer 1: Monotonicity (Critical hard blocks)",
    "  Layer 2: Ratio bands (Critical / Warning)",
    "  Layer 3: Cross-geo deviation + Systemic detection",
    "  Layer 4: YoY drift (cell + geo-level)",
    "engine/list_price_engine.py — B2C and B2B computation",
    "  + channel price floor check + PFV hook",
    "routes/cycles.py — Cycle CRUD + GVE trigger",
    "routes/data_import.py — Excel + CSV baseline import",
    "routes/gve.py — GVE results API",
    "routes/settings_routes.py — All settings read/write",
    "routes/export.py — CSV and health report export",
    "templates — login, dashboard, cycle, settings (5 screens)",
    "start.bat — One-click launcher",
]

txb = slide.shapes.add_textbox(Inches(0.6), Inches(1.82), Inches(5.6), Inches(5.0))
tf = txb.text_frame
tf.word_wrap = True
first = True
for item in built:
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    first = False
    r = p.add_run()
    r.text = item
    r.font.size = Pt(11)
    r.font.color.rgb = DARK_TEXT

# Roadmap column
add_rect(slide, Inches(6.6), Inches(1.28), Inches(6.3), Inches(5.7), WHITE)
add_rect(slide, Inches(6.6), Inches(1.28), Inches(0.07), Inches(5.7), AMBER)
add_text_box(slide, "Roadmap — Next Steps",
             Inches(6.8), Inches(1.33), Inches(5.9), Inches(0.42),
             font_size=15, bold=True, color=RGBColor(0xB0, 0x70, 0x00))

roadmap = [
    ("Stage 1–3 UI", "Standard Cost entry form, Forward Adjustment\nfactor inputs per cell / row / column, Sales\nCost live computation display"),
    ("PFV Benchmark Import", "Upload Dell/HP benchmark price files into\npfv_benchmarks table. Hook in list_price_engine\nalready wired — needs import UI + file parser"),
    ("Maturity Assignment UI", "Backend (tier_maturity table) already exists.\nNeed a dedicated Settings section to set\nNew / Mature Refresh / Mature per tier per cycle"),
    ("Prior Baseline from Excel", "Currently: CSV paste only.\nRoadmap: parse prior cycle Excel export\ndirectly to populate prior_baseline table"),
    ("PyInstaller .exe Packaging", "Bundle Python + Flask + all dependencies into\na single .exe. Eliminates Python install\nrequirement for end users"),
    ("Attach Rate Sensitivity", "For a given price elasticity, show projected\nattach rate at base / +5% / -5% with net\nmargin per unit at each scenario"),
]

txb2 = slide.shapes.add_textbox(Inches(6.8), Inches(1.82), Inches(6.0), Inches(5.0))
tf2 = txb2.text_frame
tf2.word_wrap = True
first2 = True
for title, body in roadmap:
    p = tf2.paragraphs[0] if first2 else tf2.add_paragraph()
    first2 = False
    r = p.add_run()
    r.text = title
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = SLATE
    p2 = tf2.add_paragraph()
    r2 = p2.add_run()
    r2.text = body
    r2.font.size = Pt(11)
    r2.font.color.rgb = DARK_TEXT
    p3 = tf2.add_paragraph()
    r3 = p3.add_run()
    r3.text = ""
    r3.font.size = Pt(4)


# ---------------------------------------------------------------------------
# SLIDE 15 — Summary
# ---------------------------------------------------------------------------
slide = prs.slides.add_slide(BLANK)
add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, NAVY)
add_rect(slide, 0, Inches(4.8), SLIDE_W, Inches(0.07), RED)

add_text_box(slide, "GPS Pricing Workbench",
             Inches(0.6), Inches(1.0), Inches(10), Inches(0.8),
             font_size=36, bold=True, color=WHITE)
add_text_box(slide, "Replacing manual Excel pricing with a structured, validated, auditable workflow.",
             Inches(0.6), Inches(1.95), Inches(11.5), Inches(0.5),
             font_size=16, color=RGBColor(0xB0, 0xC4, 0xDE), italic=True)

bullets = [
    "5-stage pipeline from Standard Cost through to List Price",
    "4-layer GVE blocks submission on Critical violations — not after the fact",
    "Sales Cost is system-enforced as inviolable pricing floor",
    "Every change audited: who, when, what, why",
    "Fully offline — SQLite + Flask + start.bat, no cloud dependency",
    "Excel import tested on real GPS pricing files (145 SKUs, 15 sub-regions)",
]

for i, b in enumerate(bullets):
    ty = Inches(2.65) + i * Inches(0.36)
    add_rect(slide, Inches(0.6), ty + Inches(0.07), Inches(0.12), Inches(0.12), RED)
    add_text_box(slide, b, Inches(0.9), ty, Inches(11.5), Inches(0.34),
                 font_size=14, color=WHITE)

add_text_box(slide, "C:\\Users\\Administrator\\ClaudeProjects\\SalesCostValidator\\",
             Inches(0.6), Inches(5.25), Inches(11), Inches(0.35),
             font_size=12, color=MID_GREY, italic=True)

add_text_box(slide, "March 2026  |  Lenovo GPS Division",
             Inches(0.6), Inches(6.5), Inches(6), Inches(0.35),
             font_size=12, color=MID_GREY)


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
out_path = r"C:\Users\Administrator\ClaudeProjects\SalesCostValidator\GPS_Pricing_Workbench_Solution.pptx"
prs.save(out_path)
print(f"Saved: {out_path}")
print(f"Slides: {len(prs.slides)}")
