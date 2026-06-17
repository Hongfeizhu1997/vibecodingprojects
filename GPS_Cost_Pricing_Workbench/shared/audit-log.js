/* ═══════════════════════════════════════════════════════════════════════════
 * GPS Pricing Workbench — Audit Log
 * Tracks user actions across all stages. Stored in localStorage.
 *
 * Events logged:
 *   - Cycle create/release/retire
 *   - Data import (source, row count)
 *   - Calculation run (stage, count)
 *   - Export (format, row count)
 *   - Settings changed (key, old→new)
 *   - Stage bridge send/receive
 *
 * View with: Audit.log.getRecent(50)
 * Export with: Audit.log.exportCSV()
 * ═══════════════════════════════════════════════════════════════════════════ */

var Audit = (function() {
  'use strict';

  var STORAGE_KEY = 'gps_audit_log';
  var MAX_ENTRIES = 500;
  var stageNames = { 3: 'Sales Cost', 4: 'GVE Validation', 5: 'List Price', 6: 'Price Gradient' };

  // ── Internal ────────────────────────────────────────────────────────────────

  function _load() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    } catch (e) { return []; }
  }

  function _save(entries) {
    // Trim to max
    if (entries.length > MAX_ENTRIES) entries = entries.slice(entries.length - MAX_ENTRIES);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
    } catch (e) {
      // localStorage full — trim further
      var half = Math.floor(entries.length / 2);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(entries.slice(half)));
    }
  }

  function _entry(action, detail, user, stage) {
    return {
      timestamp: new Date().toISOString(),
      stage: stage || null,
      stageName: stageNames[stage] || null,
      user: user || 'unknown',
      action: action,
      detail: detail || '',
    };
  }

  // ── Public logging methods ──────────────────────────────────────────────────

  var log = {
    entries: _load(),

    _push: function(action, detail, user, stage) {
      this.entries.push(_entry(action, detail, user, stage));
      _save(this.entries);
    },

    // ── Stage lifecycle ───────────────────────────────────────────────────

    cycleCreate: function(name, fy, user, stage) {
      this._push('CYCLE_CREATE', 'Cycle "' + name + '" (FY: ' + (fy || '—') + ')', user, stage);
    },

    cycleRelease: function(name, user, stage) {
      this._push('CYCLE_RELEASE', 'Cycle "' + name + '" released', user, stage);
    },

    cycleRetire: function(name, user, stage) {
      this._push('CYCLE_RETIRE', 'Cycle "' + name + '" retired', user, stage);
    },

    // ── Data operations ───────────────────────────────────────────────────

    dataImport: function(source, rowCount, user, stage) {
      this._push('DATA_IMPORT', 'Imported ' + rowCount + ' rows from ' + source, user, stage);
    },

    dataExport: function(format, rowCount, user, stage) {
      this._push('DATA_EXPORT', 'Exported ' + rowCount + ' rows as ' + format, user, stage);
    },

    // ── Calculations ──────────────────────────────────────────────────────

    calcRun: function(calcCount, skipCount, user, stage) {
      this._push('CALC_RUN', 'Calculated ' + calcCount + ', skipped ' + skipCount, user, stage);
    },

    gveRun: function(critCount, warnCount, user, stage) {
      this._push('GVE_RUN', 'Validation: ' + critCount + ' Critical, ' + warnCount + ' Warning', user, stage);
    },

    // ── Settings ──────────────────────────────────────────────────────────

    settingChange: function(key, oldVal, newVal, user, stage) {
      this._push('SETTING_CHANGE', key + ': "' + oldVal + '" → "' + newVal + '"', user, stage);
    },

    // ── Bridge ────────────────────────────────────────────────────────────

    bridgeSend: function(toStage, rowCount, user, stage) {
      this._push('BRIDGE_SEND', 'Sent ' + rowCount + ' rows to Stage ' + toStage, user, stage);
    },

    bridgeReceive: function(fromStage, rowCount, user, stage) {
      this._push('BRIDGE_RECEIVE', 'Received ' + rowCount + ' rows from Stage ' + fromStage, user, stage);
    },

    // ── General ───────────────────────────────────────────────────────────

    generic: function(action, detail, user, stage) {
      this._push(action, detail, user, stage);
    },

    // ── Query ─────────────────────────────────────────────────────────────

    getRecent: function(n) {
      n = n || 50;
      var all = _load();
      return all.slice(Math.max(0, all.length - n)).reverse();
    },

    getByStage: function(stage) {
      return _load().filter(function(e) { return e.stage === stage; });
    },

    exportCSV: function() {
      var all = _load();
      var headers = ['Timestamp', 'Stage', 'User', 'Action', 'Detail'];
      var rows = [headers.join(',')];
      for (var i = 0; i < all.length; i++) {
        var e = all[i];
        rows.push([
          '"' + (e.timestamp || '') + '"',
          '"' + (e.stageName || '') + '"',
          '"' + (e.user || '') + '"',
          '"' + (e.action || '') + '"',
          '"' + (e.detail || '').replace(/"/g, '""') + '"',
        ].join(','));
      }
      var blob = new Blob([rows.join('\n')], { type: 'text/csv' });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'audit_log_' + new Date().toISOString().slice(0,10) + '.csv';
      a.click();
      URL.revokeObjectURL(url);
    },

    clear: function() {
      localStorage.removeItem(STORAGE_KEY);
      this.entries = [];
    },
  };

  return { log: log };
})();

if (typeof window !== 'undefined') window.Audit = Audit;
