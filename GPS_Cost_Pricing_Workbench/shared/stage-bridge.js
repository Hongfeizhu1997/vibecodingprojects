/* ═══════════════════════════════════════════════════════════════════════════
 * GPS Pricing Workbench — Stage Bridge
 * Lightweight data passing between stages using localStorage.
 *
 * Pattern:
 *   Stage 3 exports:  Bridge.saveForNext(3, salesCostData, { cycleName: '...' })
 *   Stage 4 imports:  var data = Bridge.loadFromStage(3)
 *   Stage 4 exports:  Bridge.saveForNext(4, validatedData)
 *   etc.
 *
 * Data is stored as JSON under key: 'gps_bridge_stage{N}_to_{N+1}'
 * Metadata under:       'gps_bridge_meta_stage{N}'
 * ═══════════════════════════════════════════════════════════════════════════ */

var Bridge = (function() {
  'use strict';

  var PREFIX = 'gps_bridge_';

  // ── Save data for the next stage ────────────────────────────────────────────

  function saveForNext(fromStage, data, meta) {
    meta = meta || {};
    var toStage = fromStage + 1;
    var key = PREFIX + 'stage' + fromStage + '_to_' + toStage;
    var metaKey = PREFIX + 'meta_stage' + fromStage;

    var payload = {
      fromStage: fromStage,
      toStage: toStage,
      timestamp: new Date().toISOString(),
      rowCount: Array.isArray(data) ? data.length : 0,
      data: data,
    };

    try {
      localStorage.setItem(key, JSON.stringify(payload));
      localStorage.setItem(metaKey, JSON.stringify(Object.assign({}, meta, {
        savedAt: new Date().toISOString(),
        rowCount: payload.rowCount,
      })));
      return { success: true, key: key, rowCount: payload.rowCount };
    } catch (e) {
      return { success: false, error: 'localStorage full or unavailable: ' + e.message };
    }
  }

  // ── Load data from previous stage ───────────────────────────────────────────

  function loadFromStage(fromStage) {
    var key = PREFIX + 'stage' + fromStage + '_to_' + (fromStage + 1);
    var raw = localStorage.getItem(key);
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch (e) {
      return null;
    }
  }

  // ── Get metadata about a bridge entry ───────────────────────────────────────

  function getMeta(fromStage) {
    var metaKey = PREFIX + 'meta_stage' + fromStage;
    var raw = localStorage.getItem(metaKey);
    if (!raw) return null;
    try { return JSON.parse(raw); } catch (e) { return null; }
  }

  // ── Check if bridge data exists for import ──────────────────────────────────

  function hasDataFrom(fromStage) {
    return localStorage.getItem(PREFIX + 'stage' + fromStage + '_to_' + (fromStage + 1)) !== null;
  }

  // ── List all bridge entries ─────────────────────────────────────────────────

  function listAll() {
    var entries = [];
    for (var i = 0; i < localStorage.length; i++) {
      var key = localStorage.key(i);
      if (key && key.indexOf(PREFIX + 'stage') === 0 && key.indexOf('_to_') > 0) {
        try {
          var meta = JSON.parse(localStorage.getItem(key));
          entries.push({
            key: key,
            fromStage: meta.fromStage,
            toStage: meta.toStage,
            timestamp: meta.timestamp,
            rowCount: meta.rowCount,
          });
        } catch (e) {}
      }
    }
    return entries.sort(function(a, b) { return a.fromStage - b.fromStage; });
  }

  // ── Clear bridge data ───────────────────────────────────────────────────────

  function clear(fromStage) {
    if (fromStage != null) {
      localStorage.removeItem(PREFIX + 'stage' + fromStage + '_to_' + (fromStage + 1));
      localStorage.removeItem(PREFIX + 'meta_stage' + fromStage);
    } else {
      // Clear all bridge entries
      var keys = [];
      for (var i = 0; i < localStorage.length; i++) {
        var key = localStorage.key(i);
        if (key && key.indexOf(PREFIX) === 0) keys.push(key);
      }
      keys.forEach(function(k) { localStorage.removeItem(k); });
    }
  }

  // ── API ─────────────────────────────────────────────────────────────────────

  return {
    saveForNext: saveForNext,
    loadFromStage: loadFromStage,
    getMeta: getMeta,
    hasDataFrom: hasDataFrom,
    listAll: listAll,
    clear: clear,
  };
})();

if (typeof window !== 'undefined') window.Bridge = Bridge;
