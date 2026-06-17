/* ═══════════════════════════════════════════════════════════════════════════
 * GPS Pricing Workbench — Shared UI Components
 * Toast, Modal, Badges, Formatters, and helpers used across all stages.
 *
 * Depends on: DOM elements with IDs: 'toast-container', 'modal-overlay',
 *   'modal-header', 'modal-body', 'modal-footer', 'modal-box'.
 * If these don't exist yet, they are created on first use.
 * ═══════════════════════════════════════════════════════════════════════════ */

var UI = (function() {
  'use strict';

  // ── DOM shortcuts ───────────────────────────────────────────────────────────

  function $el(id) {
    var el = document.getElementById(id);
    if (!el && id === 'toast-container') {
      el = document.createElement('div');
      el.id = 'toast-container';
      el.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:2000;display:flex;flex-direction:column;gap:8px';
      document.body.appendChild(el);
    }
    if (!el && id === 'modal-overlay') {
      el = document.createElement('div');
      el.id = 'modal-overlay';
      el.className = 'modal-overlay hidden';
      el.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:1500;display:flex;align-items:center;justify-content:center';
      el.innerHTML = '<div id="modal-box" class="modal-box" style="background:#fff;border-radius:8px;max-width:700px;width:90%;max-height:85vh;overflow-y:auto;padding:0"><div id="modal-header" style="padding:16px 20px;border-bottom:1px solid #e5e7eb;font-weight:600;font-size:16px"></div><div id="modal-body" style="padding:20px"></div><div id="modal-footer" style="padding:12px 20px;border-top:1px solid #e5e7eb;display:flex;justify-content:flex-end;gap:8px"></div></div>';
      el.addEventListener('click', function(e) { if (e.target === el) hideModal(); });
      document.body.appendChild(el);
    }
    return el;
  }

  // ── Toast ───────────────────────────────────────────────────────────────────

  function toast(msg, type) {
    type = type || 'info';
    var container = $el('toast-container');
    var div = document.createElement('div');
    var colors = {
      info:    { bg: '#dbeafe', fg: '#1e40af', border: '#93c5fd' },
      success: { bg: '#d1fae5', fg: '#065f46', border: '#6ee7b7' },
      error:   { bg: '#fee2e2', fg: '#991b1b', border: '#fca5a5' },
      warn:    { bg: '#fef3c7', fg: '#92400e', border: '#fcd34d' },
    };
    var c = colors[type] || colors.info;
    div.style.cssText = 'padding:10px 16px;border-radius:6px;font-size:13px;max-width:400px;word-wrap:break-word;box-shadow:0 2px 8px rgba(0,0,0,0.15);animation:slideIn .25s ease;'
      + 'background:' + c.bg + ';color:' + c.fg + ';border:1px solid ' + c.border;
    div.textContent = msg;
    container.appendChild(div);
    setTimeout(function() { div.remove(); }, 4000);
  }

  // ── Modal ───────────────────────────────────────────────────────────────────

  function showModal(title, bodyHTML, footerHTML, wide) {
    $el('modal-header').textContent = title;
    $el('modal-body').innerHTML = bodyHTML;
    $el('modal-footer').innerHTML = footerHTML || '<button class="btn btn-secondary" onclick="UI.hideModal()">Close</button>';
    var box = $el('modal-box');
    if (wide) box.style.maxWidth = '1000px';
    else box.style.maxWidth = '700px';
    $el('modal-overlay').classList.remove('hidden');
  }

  function hideModal() {
    $el('modal-overlay').classList.add('hidden');
  }

  // ── Formatters ──────────────────────────────────────────────────────────────

  function fmtCurrency(v, d) {
    d = d === undefined ? 2 : d;
    if (v == null || isNaN(v)) return '—';
    return '$' + Number(v).toFixed(d);
  }

  function fmtPct(v, d) {
    d = d === undefined ? 1 : d;
    if (v == null || isNaN(v)) return '—';
    return (v * 100).toFixed(d) + '%';
  }

  function fmtDate(iso) {
    if (!iso) return '—';
    return iso.slice(0, 16).replace('T', ' ');
  }

  function safeFloat(v) {
    var s = String(v || '').replace(/[$,%,\s]/g, '');
    var f = parseFloat(s);
    return isNaN(f) ? null : f;
  }

  function safeStr(v) {
    return v == null ? '' : String(v).trim();
  }

  function escHtml(s) {
    return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // ── Badges ──────────────────────────────────────────────────────────────────

  function statusBadge(s) {
    var map = { Draft: 'badge-draft', Released: 'badge-released', Retired: 'badge-retired' };
    var cls = map[s] || 'badge-draft';
    return '<span class="badge ' + cls + '">' + (s || 'Draft') + '</span>';
  }

  function severityBadge(s) {
    var cls = { Critical: 'sev-critical', Systemic: 'sev-systemic', Warning: 'sev-warning', OK: 'sev-ok', Clear: 'sev-clear' };
    return '<span class="badge ' + (cls[s] || '') + '">' + (s || '') + '</span>';
  }

  function layerBadge(l) {
    return '<span class="layer-badge">L' + l + '</span>';
  }

  function sourceBadge(s) {
    if (!s) return '—';
    if (s === 'Auto-Calculation') return '<span class="badge badge-auto">Auto</span>';
    if (s === 'No Rule') return '<span class="badge badge-norule">No Rule</span>';
    return '<span class="badge badge-draft">' + s + '</span>';
  }

  // ── Export helpers ──────────────────────────────────────────────────────────

  function downloadCSV(data, filename) {
    var headers = Object.keys(data[0] || {});
    var rows = [headers.join(',')];
    for (var i = 0; i < data.length; i++) {
      rows.push(headers.map(function(h) {
        var v = data[i][h];
        return '"' + String(v == null ? '' : v).replace(/"/g, '""') + '"';
      }).join(','));
    }
    downloadBlob(rows.join('\n'), filename || 'export.csv', 'text/csv');
  }

  function downloadBlob(content, filename, mime) {
    var blob = new Blob([content], { type: mime || 'text/plain' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  // ── Init ────────────────────────────────────────────────────────────────────

  function init() {
    // Inject base CSS if not already present
    if (!document.getElementById('gps-shared-css')) {
      var style = document.createElement('style');
      style.id = 'gps-shared-css';
      style.textContent = [
        '.badge { display:inline-block; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600; }',
        '.badge-draft   { background:#f3f4f6; color:#6b7280; }',
        '.badge-released{ background:#d1fae5; color:#065f46; }',
        '.badge-retired { background:#fee2e2; color:#991b1b; }',
        '.badge-auto    { background:#dbeafe; color:#1e40af; }',
        '.badge-norule  { background:#fef3c7; color:#92400e; }',
        '.sev-critical  { background:#fee2e2; color:#991b1b; }',
        '.sev-systemic  { background:#ffedd5; color:#9a3412; }',
        '.sev-warning   { background:#fef9c3; color:#854d0e; }',
        '.sev-ok        { background:#d1fae5; color:#065f46; }',
        '.sev-clear     { background:#e0e7ff; color:#3730a3; }',
        '.layer-badge   { background:#e0e7ff; color:#3730a3; padding:1px 6px; border-radius:3px; font-size:11px; font-weight:600; }',
        '.modal-overlay.hidden { display:none; }',
        '@keyframes slideIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }',
        '.form-control { width:100%; padding:8px 12px; border:1px solid #d1d5db; border-radius:4px; font-size:13px; color:#1f2937; background:#fff; }',
        '.form-control:focus { outline:none; border-color:#E2232A; box-shadow:0 0 0 2px rgba(226,35,42,.15); }',
        '.form-control-sm { padding:5px 8px; font-size:12px; }',
        '.form-label { font-size:12px; font-weight:500; color:#374151; margin-bottom:2px; }',
        '.form-group { display:flex; flex-direction:column; gap:4px; }',
        '.form-row-2 { display:grid; grid-template-columns:1fr 1fr; gap:12px; }',
        '.form-row-3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; }',
        '.btn { padding:8px 16px; border:none; border-radius:4px; font-size:13px; font-weight:500; cursor:pointer; display:inline-flex; align-items:center; gap:6px; }',
        '.btn-primary { background:#E2232A; color:#fff; }',
        '.btn-primary:hover { background:#c41e24; }',
        '.btn-secondary { background:#f3f4f6; color:#374151; border:1px solid #d1d5db; }',
        '.btn-secondary:hover { background:#e5e7eb; }',
        '.btn-danger { background:#dc2626; color:#fff; }',
        '.btn-danger:hover { background:#b91c1c; }',
        '.btn-sm { padding:5px 10px; font-size:12px; }',
        '.btn:disabled { opacity:.5; cursor:not-allowed; }',
        '.card { background:#fff; border:1px solid #e5e7eb; border-radius:6px; padding:20px; margin-bottom:16px; }',
        '.card-title { font-size:16px; font-weight:600; color:#111827; margin-bottom:12px; }',
        '.text-muted { color:#6b7280; }',
        '.text-sm { font-size:12px; }',
        '.text-right { text-align:right; }',
        '.tbl { width:100%; border-collapse:collapse; font-size:13px; }',
        '.tbl th { text-align:left; padding:8px 12px; background:#f9fafb; font-weight:600; color:#374151; border-bottom:2px solid #e5e7eb; white-space:nowrap; }',
        '.tbl td { padding:7px 12px; border-bottom:1px solid #f3f4f6; color:#1f2937; }',
        '.tbl tr:hover td { background:#f9fafb; }',
        '.tbl-scroll { overflow-x:auto; }',
        '.hidden { display:none !important; }',
      ].join('\n');
      document.head.appendChild(style);
    }
    // Create toast container
    $el('toast-container');
  }

  // Auto-init on load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  return {
    toast: toast,
    showModal: showModal,
    hideModal: hideModal,
    fmtCurrency: fmtCurrency,
    fmtPct: fmtPct,
    fmtDate: fmtDate,
    safeFloat: safeFloat,
    safeStr: safeStr,
    escHtml: escHtml,
    statusBadge: statusBadge,
    severityBadge: severityBadge,
    layerBadge: layerBadge,
    sourceBadge: sourceBadge,
    downloadCSV: downloadCSV,
    downloadBlob: downloadBlob,
    $el: $el,
  };
})();

// Register globally
if (typeof window !== 'undefined') window.UI = UI;
