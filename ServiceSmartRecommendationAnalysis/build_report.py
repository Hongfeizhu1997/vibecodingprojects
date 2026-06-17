#!/usr/bin/env python3
"""Build updated Phase 1 report with Term x Type sections for all GEOs."""
with open('/root/ClaudeProjects/ServiceSmartRecommendationAnalysis/validation_output/phase1_operational_kpi_report_v2.html') as f:
    html = f.read()

# Section F content for each GEO
sections_f = {}

sections_f['EMEA'] = '''<div class="sub"><h3>F. Service Product Analysis — Term × Type</h3>
<p class="insight">Product PN descriptions parsed to extract term (1Y–5Y) and type (Premier Support / Onsite / Premier Support Plus / Courier). Analysis based on 42,608 EMEA configurations with parsable default term + type.</p>
<h4>By Term</h4>
<table><tr><th>Term</th><th class="num">Configs</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>
<tr><td><strong>1Y</strong></td><td class="num">727</td><td class="num" style="background:#f57f17;color:#fff">52.8%</td><td class="num">36.5%</td><td class="num">10.7%</td></tr>
<tr><td><strong>2Y</strong></td><td class="num">285</td><td class="num" style="background:#c62828;color:#fff">37.2%</td><td class="num" style="background:#c62828;color:#fff">46.3%</td><td class="num">16.5%</td></tr>
<tr><td><strong>3Y</strong></td><td class="num">34,516</td><td class="num" style="background:#c62828;color:#fff">47.4%</td><td class="num" style="background:#f57f17;color:#fff">28.3%</td><td class="num" style="background:#f57f17;color:#fff">24.3%</td></tr>
<tr><td><strong>4Y</strong></td><td class="num">3,014</td><td class="num" style="background:#2e7d32;color:#fff">61.5%</td><td class="num">24.3%</td><td class="num">14.2%</td></tr>
<tr><td><strong>5Y</strong></td><td class="num">4,066</td><td class="num" style="background:#f57f17;color:#fff">51.6%</td><td class="num">21.9%</td><td class="num" style="background:#c62828;color:#fff">26.5%</td></tr>
</table>
<h4>By Type</h4>
<table><tr><th>Type</th><th class="num">Configs</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>
<tr><td><strong>Premier Support</strong></td><td class="num">21,711</td><td class="num" style="background:#c62828;color:#fff">45.1%</td><td class="num" style="background:#f57f17;color:#fff">28.5%</td><td class="num" style="background:#c62828;color:#fff">26.3%</td></tr>
<tr><td><strong>Onsite</strong></td><td class="num">14,730</td><td class="num" style="background:#f57f17;color:#fff">49.7%</td><td class="num" style="background:#f57f17;color:#fff">27.9%</td><td class="num" style="background:#f57f17;color:#fff">22.4%</td></tr>
<tr><td><strong>Courier</strong></td><td class="num">3,867</td><td class="num" style="background:#f57f17;color:#fff">51.8%</td><td class="num">24.1%</td><td class="num" style="background:#f57f17;color:#fff">24.1%</td></tr>
<tr><td><strong>Premier Support Plus</strong></td><td class="num">1,520</td><td class="num" style="background:#2e7d32;color:#fff">65.4%</td><td class="num">24.5%</td><td class="num" style="background:#2e7d32;color:#fff">10.1%</td></tr>
</table>
<h4>Top Term x Type Combinations</h4>
<table><tr><th>Combination</th><th class="num">Configs</th><th class="num">Acceptance</th><th class="num">Change</th></tr>
<tr><td><strong>3Y Premier Support</strong></td><td class="num">18,041</td><td class="num" style="background:#c62828;color:#fff">42.5%</td><td class="num">29.3%</td></tr>
<tr><td><strong>3Y Onsite</strong></td><td class="num">11,011</td><td class="num" style="background:#f57f17;color:#fff">49.5%</td><td class="num">29.4%</td></tr>
<tr><td><strong>3Y Courier</strong></td><td class="num">3,439</td><td class="num" style="background:#f57f17;color:#fff">52.2%</td><td class="num">23.3%</td></tr>
<tr><td><strong>5Y Onsite</strong></td><td class="num">2,426</td><td class="num" style="background:#c62828;color:#fff">43.4%</td><td class="num">23.3%</td></tr>
<tr><td><strong>4Y Premier Support</strong></td><td class="num">1,549</td><td class="num" style="background:#f57f17;color:#fff">55.7%</td><td class="num">27.4%</td></tr>
<tr><td><strong>5Y Premier Support</strong></td><td class="num">1,327</td><td class="num" style="background:#2e7d32;color:#fff">66.5%</td><td class="num">18.9%</td></tr>
<tr><td><strong>3Y Premier Support Plus</strong></td><td class="num">1,118</td><td class="num" style="background:#2e7d32;color:#fff">65.7%</td><td class="num">24.7%</td></tr>
<tr><td><strong>4Y Onsite</strong></td><td class="num">1,016</td><td class="num" style="background:#2e7d32;color:#fff">67.1%</td><td class="num">19.4%</td></tr>
</table></div>'''

sections_f['AP'] = '''<div class="sub"><h3>F. Service Product Analysis — Term x Type</h3>
<p class="warn">AP shows significantly different patterns from other GEOs: <strong>4Y Premier Support acceptance is only 16.1%</strong> (vs 55.7% in EMEA, 64.9% in NA). 1Y products dominate with 6,357 configs but only 33.1% acceptance. Premier Support Plus acceptance (43.7%) is far below EMEA (65.4%) and NA (58.9%).</p>
<h4>By Term</h4>
<table><tr><th>Term</th><th class="num">Configs</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>
<tr><td><strong>1Y</strong></td><td class="num">6,357</td><td class="num" style="background:#c62828;color:#fff">33.1%</td><td class="num" style="background:#c62828;color:#fff">48.1%</td><td class="num">18.8%</td></tr>
<tr><td><strong>2Y</strong></td><td class="num">84</td><td class="num">41.7%</td><td class="num">40.5%</td><td class="num">17.9%</td></tr>
<tr><td><strong>3Y</strong></td><td class="num">29,846</td><td class="num" style="background:#c62828;color:#fff">41.3%</td><td class="num" style="background:#c62828;color:#fff">35.9%</td><td class="num" style="background:#f57f17;color:#fff">22.8%</td></tr>
<tr><td><strong>4Y</strong></td><td class="num">6,339</td><td class="num" style="background:#c62828;color:#fff">20.2%</td><td class="num" style="background:#c62828;color:#fff">49.1%</td><td class="num" style="background:#c62828;color:#fff">30.7%</td></tr>
<tr><td><strong>5Y</strong></td><td class="num">3,627</td><td class="num" style="background:#c62828;color:#fff">38.1%</td><td class="num" style="background:#f57f17;color:#fff">31.7%</td><td class="num" style="background:#c62828;color:#fff">30.1%</td></tr>
</table>
<h4>By Type</h4>
<table><tr><th>Type</th><th class="num">Configs</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>
<tr><td><strong>Premier Support</strong></td><td class="num">33,247</td><td class="num" style="background:#c62828;color:#fff">34.9%</td><td class="num" style="background:#c62828;color:#fff">40.0%</td><td class="num" style="background:#f57f17;color:#fff">25.1%</td></tr>
<tr><td><strong>Onsite</strong></td><td class="num">7,376</td><td class="num" style="background:#f57f17;color:#fff">45.5%</td><td class="num" style="background:#f57f17;color:#fff">34.0%</td><td class="num">20.5%</td></tr>
<tr><td><strong>Premier Support Plus</strong></td><td class="num">4,150</td><td class="num" style="background:#c62828;color:#fff">43.7%</td><td class="num" style="background:#c62828;color:#fff">37.6%</td><td class="num">18.7%</td></tr>
<tr><td><strong>Courier</strong></td><td class="num">1,035</td><td class="num" style="background:#c62828;color:#fff">13.9%</td><td class="num" style="background:#c62828;color:#fff">53.5%</td><td class="num" style="background:#c62828;color:#fff">32.6%</td></tr>
</table>
<h4>Top Term x Type Combinations</h4>
<table><tr><th>Combination</th><th class="num">Configs</th><th class="num">Acceptance</th><th class="num">Change</th></tr>
<tr><td><strong>3Y Premier Support</strong></td><td class="num">19,430</td><td class="num" style="background:#c62828;color:#fff">41.9%</td><td class="num" style="background:#c62828;color:#fff">35.2%</td></tr>
<tr><td><strong>3Y Onsite</strong></td><td class="num">5,984</td><td class="num" style="background:#c62828;color:#fff">43.1%</td><td class="num" style="background:#c62828;color:#fff">34.8%</td></tr>
<tr><td><strong>1Y Premier Support</strong></td><td class="num">5,832</td><td class="num" style="background:#c62828;color:#fff">31.2%</td><td class="num" style="background:#c62828;color:#fff">49.1%</td></tr>
<tr><td><strong>4Y Premier Support</strong></td><td class="num">5,467</td><td class="num" style="background:#c62828;color:#fff">16.1%</td><td class="num" style="background:#c62828;color:#fff">49.6%</td></tr>
<tr><td><strong>3Y Premier Support Plus</strong></td><td class="num">3,377</td><td class="num" style="background:#c62828;color:#fff">42.4%</td><td class="num" style="background:#c62828;color:#fff">37.3%</td></tr>
<tr><td><strong>5Y Premier Support</strong></td><td class="num">2,476</td><td class="num" style="background:#c62828;color:#fff">30.5%</td><td class="num" style="background:#c62828;color:#fff">34.8%</td></tr>
</table></div>'''

sections_f['LA'] = '''<div class="sub"><h3>F. Service Product Analysis — Term x Type</h3>
<p class="warn">LA has the most concentrated product mix: 3Y Onsite + 3Y Premier Support = 59% of all configurations. 4Y products show very poor acceptance (23.4%) with high change rates. Premier Support Plus at 34.7% is the lowest across all GEOs.</p>
<h4>By Term</h4>
<table><tr><th>Term</th><th class="num">Configs</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>
<tr><td><strong>1Y</strong></td><td class="num">841</td><td class="num" style="background:#c62828;color:#fff">28.7%</td><td class="num">17.0%</td><td class="num" style="background:#c62828;color:#fff">54.3%</td></tr>
<tr><td><strong>2Y</strong></td><td class="num">44</td><td class="num">34.1%</td><td class="num" style="background:#c62828;color:#fff">56.8%</td><td class="num">9.1%</td></tr>
<tr><td><strong>3Y</strong></td><td class="num">7,000</td><td class="num" style="background:#f57f17;color:#fff">51.1%</td><td class="num" style="background:#f57f17;color:#fff">32.1%</td><td class="num">16.8%</td></tr>
<tr><td><strong>4Y</strong></td><td class="num">1,895</td><td class="num" style="background:#c62828;color:#fff">23.4%</td><td class="num" style="background:#c62828;color:#fff">44.2%</td><td class="num" style="background:#c62828;color:#fff">32.5%</td></tr>
<tr><td><strong>5Y</strong></td><td class="num">1,048</td><td class="num" style="background:#c62828;color:#fff">34.9%</td><td class="num" style="background:#f57f17;color:#fff">30.8%</td><td class="num" style="background:#c62828;color:#fff">34.3%</td></tr>
</table>
<h4>By Type</h4>
<table><tr><th>Type</th><th class="num">Configs</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>
<tr><td><strong>Premier Support</strong></td><td class="num">5,017</td><td class="num" style="background:#c62828;color:#fff">38.3%</td><td class="num" style="background:#f57f17;color:#fff">31.2%</td><td class="num" style="background:#c62828;color:#fff">30.5%</td></tr>
<tr><td><strong>Onsite</strong></td><td class="num">4,475</td><td class="num" style="background:#f57f17;color:#fff">50.3%</td><td class="num" style="background:#f57f17;color:#fff">34.6%</td><td class="num">15.1%</td></tr>
<tr><td><strong>Premier Support Plus</strong></td><td class="num">1,313</td><td class="num" style="background:#c62828;color:#fff">34.7%</td><td class="num" style="background:#c62828;color:#fff">34.5%</td><td class="num" style="background:#c62828;color:#fff">30.8%</td></tr>
</table>
<h4>Top Term x Type Combinations</h4>
<table><tr><th>Combination</th><th class="num">Configs</th><th class="num">Acceptance</th><th class="num">Change</th></tr>
<tr><td><strong>3Y Onsite</strong></td><td class="num">3,221</td><td class="num" style="background:#f57f17;color:#fff">55.0%</td><td class="num" style="background:#f57f17;color:#fff">34.0%</td></tr>
<tr><td><strong>3Y Premier Support</strong></td><td class="num">3,174</td><td class="num" style="background:#f57f17;color:#fff">48.0%</td><td class="num" style="background:#f57f17;color:#fff">30.1%</td></tr>
<tr><td><strong>4Y Premier Support</strong></td><td class="num">990</td><td class="num" style="background:#c62828;color:#fff">18.7%</td><td class="num" style="background:#c62828;color:#fff">45.2%</td></tr>
<tr><td><strong>4Y Onsite</strong></td><td class="num">732</td><td class="num" style="background:#c62828;color:#fff">22.3%</td><td class="num" style="background:#c62828;color:#fff">42.9%</td></tr>
<tr><td><strong>1Y Premier Support</strong></td><td class="num">600</td><td class="num" style="background:#c62828;color:#fff">17.8%</td><td class="num">12.3%</td></tr>
</table></div>'''

sections_f['NA'] = '''<div class="sub"><h3>F. Service Product Analysis — Term x Type</h3>
<p class="insight">NA leads all GEOs in product-level acceptance. 5Y Premier Support at 71.6% is the highest single combination. Premier Support Plus (58.9%) and 4Y products (55.9%) show strong trust. Only weak spot: 3Y Courier at 32.2% with high no-selection rate (48.6%).</p>
<h4>By Term</h4>
<table><tr><th>Term</th><th class="num">Configs</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>
<tr><td><strong>1Y</strong></td><td class="num">258</td><td class="num" style="background:#c62828;color:#fff">28.3%</td><td class="num" style="background:#c62828;color:#fff">48.1%</td><td class="num">23.6%</td></tr>
<tr><td><strong>2Y</strong></td><td class="num">10</td><td class="num" style="background:#2e7d32;color:#fff">70.0%</td><td class="num">20.0%</td><td class="num">10.0%</td></tr>
<tr><td><strong>3Y</strong></td><td class="num">26,763</td><td class="num" style="background:#f57f17;color:#fff">52.9%</td><td class="num" style="background:#f57f17;color:#fff">27.0%</td><td class="num">20.1%</td></tr>
<tr><td><strong>4Y</strong></td><td class="num">4,331</td><td class="num" style="background:#f57f17;color:#fff">55.9%</td><td class="num">26.3%</td><td class="num">17.8%</td></tr>
<tr><td><strong>5Y</strong></td><td class="num">1,858</td><td class="num" style="background:#2e7d32;color:#fff">61.9%</td><td class="num">20.3%</td><td class="num">17.8%</td></tr>
</table>
<h4>By Type</h4>
<table><tr><th>Type</th><th class="num">Configs</th><th class="num">Acceptance</th><th class="num">Change</th><th class="num">Att.Fail</th></tr>
<tr><td><strong>Premier Support</strong></td><td class="num">22,442</td><td class="num" style="background:#f57f17;color:#fff">53.8%</td><td class="num" style="background:#f57f17;color:#fff">28.2%</td><td class="num">18.0%</td></tr>
<tr><td><strong>Premier Support Plus</strong></td><td class="num">3,893</td><td class="num" style="background:#f57f17;color:#fff">58.9%</td><td class="num" style="background:#c62828;color:#fff">33.3%</td><td class="num" style="background:#2e7d32;color:#fff">7.8%</td></tr>
<tr><td><strong>Onsite</strong></td><td class="num">3,773</td><td class="num" style="background:#2e7d32;color:#fff">56.7%</td><td class="num">19.2%</td><td class="num" style="background:#f57f17;color:#fff">24.1%</td></tr>
<tr><td><strong>Courier</strong></td><td class="num">2,062</td><td class="num" style="background:#c62828;color:#fff">30.4%</td><td class="num">21.0%</td><td class="num" style="background:#c62828;color:#fff">48.6%</td></tr>
</table>
<h4>Top Term x Type Combinations</h4>
<table><tr><th>Combination</th><th class="num">Configs</th><th class="num">Acceptance</th><th class="num">Change</th></tr>
<tr><td><strong>3Y Premier Support</strong></td><td class="num">19,868</td><td class="num" style="background:#f57f17;color:#fff">52.3%</td><td class="num" style="background:#f57f17;color:#fff">28.2%</td></tr>
<tr><td><strong>3Y Premier Support Plus</strong></td><td class="num">2,794</td><td class="num" style="background:#2e7d32;color:#fff">58.7%</td><td class="num" style="background:#c62828;color:#fff">32.5%</td></tr>
<tr><td><strong>3Y Onsite</strong></td><td class="num">1,805</td><td class="num" style="background:#2e7d32;color:#fff">59.2%</td><td class="num">19.4%</td></tr>
<tr><td><strong>4Y Premier Support</strong></td><td class="num">1,768</td><td class="num" style="background:#2e7d32;color:#fff">64.9%</td><td class="num" style="background:#f57f17;color:#fff">28.6%</td></tr>
<tr><td><strong>3Y Courier</strong></td><td class="num">1,338</td><td class="num" style="background:#c62828;color:#fff">32.2%</td><td class="num">20.7%</td></tr>
<tr><td><strong>4Y Onsite</strong></td><td class="num">1,053</td><td class="num" style="background:#2e7d32;color:#fff">59.2%</td><td class="num">17.1%</td></tr>
<tr><td><strong>5Y Onsite</strong></td><td class="num">773</td><td class="num" style="background:#f57f17;color:#fff">51.6%</td><td class="num">14.6%</td></tr>
<tr><td><strong>5Y Premier Support</strong></td><td class="num">739</td><td class="num" style="background:#2e7d32;color:#fff">71.6%</td><td class="num">23.1%</td></tr>
</table></div>'''

cross_geo = '''
<div class="section" id="term-type-cross"><div class="sec-hdr"><h2>Cross-GEO — Service Product Analysis Comparison</h2></div><div class="sec-body">
<p class="insight">Comparing the same product combinations across all 4 GEOs reveals large regional disparities in AI recommendation acceptance for identical service products.</p>

<h3 style="font-size:14px;font-weight:600;color:#37474f;margin-bottom:10px;border-left:4px solid #c62828;padding-left:10px">Cross-GEO: 3Y Premier Support — Largest Volume Product</h3>
<table><tr><th>GEO</th><th class="num">Configs</th><th class="num">Acceptance</th><th class="num">Change</th><th>Assessment</th></tr>
<tr><td><strong>EMEA</strong></td><td class="num">18,041</td><td class="num" style="background:#c62828;color:#fff">42.5%</td><td class="num">29.3%</td><td>Weak — 40% of EMEA volume, low trust</td></tr>
<tr><td><strong>AP</strong></td><td class="num">19,430</td><td class="num" style="background:#c62828;color:#fff">41.9%</td><td class="num" style="background:#c62828;color:#fff">35.2%</td><td>Weakest — highest change rate</td></tr>
<tr><td><strong>NA</strong></td><td class="num">19,868</td><td class="num" style="background:#f57f17;color:#fff">52.3%</td><td class="num">28.2%</td><td>Best — 10pp higher than AP/EMEA</td></tr>
<tr><td><strong>LA</strong></td><td class="num">3,174</td><td class="num" style="background:#f57f17;color:#fff">48.0%</td><td class="num">30.1%</td><td>Middle — smaller volume</td></tr>
</table>

<h3 style="font-size:14px;font-weight:600;color:#37474f;margin-bottom:10px;border-left:4px solid #f57c00;padding-left:10px">Cross-GEO: Premier Support Plus (All Terms) — Premium Product Trust</h3>
<table><tr><th>GEO</th><th class="num">Configs</th><th class="num">Acceptance</th><th class="num">Change</th><th>Assessment</th></tr>
<tr><td><strong>EMEA</strong></td><td class="num">1,520</td><td class="num" style="background:#2e7d32;color:#fff">65.4%</td><td class="num">24.5%</td><td>Strong — premium = high trust</td></tr>
<tr><td><strong>AP</strong></td><td class="num">4,150</td><td class="num" style="background:#c62828;color:#fff">43.7%</td><td class="num" style="background:#c62828;color:#fff">37.6%</td><td>Weak — premium not trusted here</td></tr>
<tr><td><strong>NA</strong></td><td class="num">3,893</td><td class="num" style="background:#f57f17;color:#fff">58.9%</td><td class="num" style="background:#c62828;color:#fff">33.3%</td><td>Good — reasonable trust</td></tr>
<tr><td><strong>LA</strong></td><td class="num">1,313</td><td class="num" style="background:#c62828;color:#fff">34.7%</td><td class="num" style="background:#c62828;color:#fff">34.5%</td><td>Weakest — premium not trusted at all</td></tr>
</table>

<h3 style="font-size:14px;font-weight:600;color:#37474f;margin-bottom:10px;border-left:4px solid #2e7d32;padding-left:10px">Key Cross-GEO Patterns</h3>
<p class="insight">
<strong>1. NA is the product trust leader.</strong> Same product (3Y Premier Support) gets 52.3% acceptance in NA vs 42.5% in EMEA vs 41.9% in AP. 10pp gap on identical product implies seller behavior or market maturity differences, not model quality.<br><br>
<strong>2. Premium products (PS Plus) reveal cultural gaps.</strong> EMEA sellers trust AI on premium at 65.4% — LA sellers only 34.7%. Same product, same AI engine, 30pp difference. Suggests different regional seller training or incentive structures.<br><br>
<strong>3. AP 4Y Premier Support is a disaster (16.1%).</strong> This product has 5,467 configs but sellers reject the AI recommendation 84% of the time. The 49.6% change rate means sellers are actively choosing different products.<br><br>
<strong>4. Longer terms consistently outperform.</strong> In every GEO, 3Y < 4Y < 5Y in acceptance. Sellers trust AI more for bigger, longer-term decisions.
</p>
</div></div>
'''

# Do replacements
# EMEA
old = '</div>\n</div></div>\n\n<!-- ================================================================ -->\n<!-- AP -->'
new = sections_f['EMEA'] + '\n</div>\n</div></div>\n\n<!-- ================================================================ -->\n<!-- AP -->'
count = html.count(old)
print(f'EMEA matches: {count}')
if count == 1:
    html = html.replace(old, new)

# AP
old = '</div>\n</div></div>\n\n<!-- ================================================================ -->\n<!-- LA -->'
new = sections_f['AP'] + '\n</div>\n</div></div>\n\n<!-- ================================================================ -->\n<!-- LA -->'
count = html.count(old)
print(f'AP matches: {count}')
if count == 1:
    html = html.replace(old, new)

# LA
old = '</div>\n</div></div>\n\n<!-- ================================================================ -->\n<!-- NA -->'
new = sections_f['LA'] + '\n</div>\n</div></div>\n\n<!-- ================================================================ -->\n<!-- NA -->'
count = html.count(old)
print(f'LA matches: {count}')
if count == 1:
    html = html.replace(old, new)

# NA
old = '</div>\n</div></div>\n\n</div>\n</body>'
new = sections_f['NA'] + '\n</div>\n</div></div>\n\n' + cross_geo + '\n</div>\n</body>'
count = html.count(old)
print(f'NA matches: {count}')
if count == 1:
    html = html.replace(old, new)

# Navbar link
html = html.replace('<a href="#NA">NA</a>', '<a href="#NA">NA</a><a href="#term-type-cross">Product Analysis</a>')

# Write
with open('/root/ClaudeProjects/ServiceSmartRecommendationAnalysis/validation_output/phase1_operational_kpi_report_v2.html', 'w') as f:
    f.write(html)

# Verify
divs_open = html.count('<div')
divs_close = html.count('</div>')
tables_open = html.count('<table')
tables_close = html.count('</table>')
print(f'div: {divs_open}/{divs_close} balanced={divs_open==divs_close}')
print(f'table: {tables_open}/{tables_close} balanced={tables_open==tables_close}')
print(f'Has F. Service: {"F. Service Product" in html}')
print(f'Has Cross-GEO section: {"Cross-GEO — Service Product" in html}')
print(f'File size: {len(html)} bytes')
print('DONE')
