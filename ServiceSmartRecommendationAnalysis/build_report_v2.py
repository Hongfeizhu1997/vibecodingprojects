#!/usr/bin/env python3
"""Regenerate complete Phase 1 V2 report with all sections including Term x Type analysis."""
import json

# Load metrics from earlier analysis
metrics = json.load(open('/tmp/phase1_new_data.json'))

# The complete HTML...
html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SSR Operational KPI Report — Phase 1 V2 (Q1 FY26/27)</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,sans-serif;background:#f0f2f5;color:#222;font-size:14px}
.navbar{background:#1a237e;color:#fff;padding:12px 24px;display:flex;align-items:center;
        gap:16px;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,.35);flex-wrap:wrap}
.navbar .brand{font-weight:700;font-size:15px}
.navbar a{color:#bbdefb;text-decoration:none;padding:4px 10px;border-radius:4px;font-size:12px}
.navbar a:hover{background:rgba(255,255,255,.15);color:#fff}
.page{max-width:1320px;margin:0 auto;padding:20px 24px}
.section{background:#fff;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.1);margin-bottom:24px;overflow:hidden}
.sec-hdr{background:#1a237e;color:#fff;padding:13px 20px}
.sec-hdr h2{font-size:17px;font-weight:600}
.sec-body{padding:18px 20px}
.sub{margin-bottom:22px}.sub:last-child{margin-bottom:0}
.sub h3{font-size:14px;font-weight:600;color:#37474f;margin-bottom:10px;border-left:4px solid #42a5f5;padding-left:10px}
.sub h4{font-size:13px;font-weight:600;color:#555;margin:14px 0 8px}
.insight{background:#e3f2fd;border-left:4px solid #1976d2;padding:9px 13px;border-radius:4px;font-size:13px;color:#0d47a1;margin-bottom:10px;line-height:1.5}
.warn{background:#fff3e0;border-left:4px solid #f57c00;padding:9px 13px;border-radius:4px;font-size:13px;color:#bf360c;margin-bottom:10px;line-height:1.5}
.critical{background:#ffebee;border-left:4px solid #c62828;padding:9px 13px;border-radius:4px;font-size:13px;color:#b71c1c;margin-bottom:10px;line-height:1.5}
table{border-collapse:collapse;width:100%;font-size:13px}
th{background:#37474f;color:#fff;padding:7px 10px;text-align:left;font-weight:600;white-space:nowrap}
td{padding:6px 10px;border-bottom:1px solid #eee;vertical-align:middle}
tr:last-child td{border-bottom:none}
.num{text-align:right;font-family:'Courier New',monospace;white-space:nowrap}
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}
.kpi-card{background:#f5f7ff;border:1px solid #e8eaf6;border-radius:8px;padding:14px}
.kpi-card .geo-tag{display:inline-block;background:#1a237e;color:#fff;border-radius:4px;padding:2px 8px;font-size:11px;font-weight:700;margin-bottom:6px}
.kpi-card .label{font-size:11px;color:#666;text-transform:uppercase;letter-spacing:.5px}
.kpi-card .big{font-size:24px;font-weight:700;margin:3px 0}
.kpi-card .sub{font-size:11px;color:#888;line-height:1.4}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.legend{display:flex;gap:10px;font-size:11px;margin-bottom:8px;align-items:center}
.legend span{padding:2px 8px;border-radius:10px;color:#fff;font-weight:600}
.tag{display:inline-block;padding:1px 6px;border-radius:3px;font-size:11px;font-weight:600}
.tag-new{background:#e3f2fd;color:#1565c0}
.tag-copied{background:#e8f5e9;color:#2e7d32}
.tag-mtm{background:#fff3e0;color:#e65100}
.trend-up{color:#2e7d32}
.trend-down{color:#c62828}
.period-tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;margin-right:6px}
.period-new{background:#e3f2fd;color:#1565c0;border:1px solid #90caf9}
.period-old{background:#f5f5f5;color:#666;border:1px solid #ddd}
</style>
</head>
<body>
<nav class="navbar"><span class="brand">SSR Operational KPI Report — Phase 1 V2</span><a href="#summary">Executive Summary</a><a href="#EMEA">EMEA</a><a href="#AP">AP</a><a href="#LA">LA</a><a href="#NA">NA</a><a href="#term-type-cross">Product Analysis</a><span style="margin-left:auto;font-size:11px;color:#90caf9">Data: 2026-04-01 to 2026-06-01 | Generated: 2026-06-09</span></nav>
<div class="page">
'''

# The rest will be split into sections and appended
# Using a build approach: write the HTML to file via terminal python script

print("Header written, length:", len(html))
with open('/tmp/report_header.html', 'w') as f:
    f.write(html)
print("Header saved to /tmp/report_header.html")
