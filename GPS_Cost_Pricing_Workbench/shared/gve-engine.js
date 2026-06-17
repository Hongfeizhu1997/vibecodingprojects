/* ═══════════════════════════════════════════════════════════════════════════
 * GPS Pricing Workbench — Shared GVE (Gradient Validation Engine)
 * Extracted from Stage 4 & Stage 6. Works with any numeric price/cost field.
 * 
 * Usage:
 *   const engine = new GVE.Engine({ settings, tierSequence });
 *   const violations = engine.validate(data, { valueField: 'sales_cost' });
 *   const violations = engine.validate(data, { valueField: 'list_price_calc', baseline });
 * ═══════════════════════════════════════════════════════════════════════════ */

var GVE = (function() {
  'use strict';

  // ── Defaults ────────────────────────────────────────────────────────────────

  var DEFAULT_SETTINGS = {
    ratio_band_3yr_1yr_min: '1.8',  ratio_band_3yr_1yr_max: '2.8',
    ratio_band_5yr_3yr_min: '1.3',  ratio_band_5yr_3yr_max: '1.7',
    ratio_band_4yr_2yr_min: '1.3',  ratio_band_4yr_2yr_max: '2.0',
    cross_geo_deviation_pct: '0.20', yoy_cell_change_pct: '0.25',
    yoy_ratio_change_pct: '0.15',   yoy_geo_avg_change_pct: '0.20',
  };

  var RATIO_PAIRS = [
    { hi: 3, lo: 1, minKey: 'ratio_band_3yr_1yr_min', maxKey: 'ratio_band_3yr_1yr_max', label: '3yr/1yr' },
    { hi: 5, lo: 3, minKey: 'ratio_band_5yr_3yr_min', maxKey: 'ratio_band_5yr_3yr_max', label: '5yr/3yr' },
    { hi: 4, lo: 2, minKey: 'ratio_band_4yr_2yr_min', maxKey: 'ratio_band_4yr_2yr_max', label: '4yr/2yr' },
  ];

  // ── Helpers ─────────────────────────────────────────────────────────────────

  function avg(arr) { return arr.length ? arr.reduce(function(a,b) { return a+b; }, 0) / arr.length : null; }

  function groupBy(items, keyFn) {
    var m = new Map();
    for (var i = 0; i < items.length; i++) {
      var k = keyFn(items[i]);
      if (!m.has(k)) m.set(k, []);
      m.get(k).push(items[i]);
    }
    return m;
  }

  function fmt(v) {
    if (v == null) return '—';
    return '$' + Number(v).toFixed(2);
  }

  function normTier(tier) {
    return String(tier || '').toLowerCase().replace(/[\s_-]+/g, '_').trim();
  }

  // ── Engine Constructor ──────────────────────────────────────────────────────

  function Engine(opts) {
    opts = opts || {};
    this.settings = Object.assign({}, DEFAULT_SETTINGS, opts.settings || {});
    this.tierSeq = opts.tierSequence || [];
  }

  Engine.prototype.updateSettings = function(newSettings) {
    Object.assign(this.settings, newSettings);
  };

  Engine.prototype.updateTierSequence = function(tierSeq) {
    this.tierSeq = tierSeq;
  };

  // ── Main validation entry ───────────────────────────────────────────────────

  Engine.prototype.validate = function(data, opts) {
    opts = opts || {};
    var valueField = opts.valueField || 'sales_cost';
    
    // Normalize data: ensure valueField is accessible as '.value' for engine
    var flatData = data.map(function(r) {
      return {
        sales_cost: r[valueField],
        tier: r.tier,
        delivery_type: r.delivery_type,
        upgrade_years: r.upgrade_years,
        region: r.region,
        part_number: r.part_number,
        prior_sales_cost: r.prior_sales_cost,
      };
    });

    var violations = [];
    
    // L1: Monotonicity
    var l1 = runLayer1(flatData, this.tierSeq);
    violations = violations.concat(l1);

    // L2: Ratio bands
    var l2 = runLayer2(flatData, this.settings);
    violations = violations.concat(l2);

    // L3: Cross-geo deviation
    var l3 = runLayer3(flatData, this.settings);
    violations = violations.concat(l3);

    // L4: YoY (only if baseline data provided)
    if (opts.baseline && opts.baseline.length) {
      var l4 = runLayer4(flatData, opts.baseline, this.settings);
      violations = violations.concat(l4);
    }

    return violations;
  };

  // ── L1: Monotonicity ────────────────────────────────────────────────────────

  function runLayer1(flatData, tierSeq) {
    if (!tierSeq.length) return [{
      layer: 1, severity: 'Warning', violation_type: 'NO_TIER_SEQUENCE',
      message: 'No tier sequence configured.', region: null, tier: null,
      upgrade_years: null, part_number: null
    }];

    var tierOrder = {};
    tierSeq.forEach(function(t) { tierOrder[normTier(t.tier_name || t.name)] = t.sort_order || t.order || 0; });

    var violations = [];
    var groups = groupBy(
      flatData.filter(function(r) { return r.sales_cost != null; }),
      function(r) { return (r.upgrade_years || '') + '|' + (r.delivery_type || '') + '|' + (r.region || ''); }
    );

    groups.forEach(function(items, key) {
      var parts = key.split('|');
      var years = parts[0], dtype = parts[1], region = parts[2];
      
      var tierCosts = {};
      for (var i = 0; i < items.length; i++) {
        var item = items[i];
        if (!item.tier) continue;
        var tk = normTier(item.tier);
        if (!tierCosts[tk]) tierCosts[tk] = [];
        tierCosts[tk].push(item.sales_cost);
      }

      var tiersInGroup = Object.keys(tierCosts)
        .filter(function(t) { return tierOrder[t] != null; })
        .sort(function(a,b) { return tierOrder[a] - tierOrder[b]; });

      for (var i = 0; i < tiersInGroup.length - 1; i++) {
        var tLow = tiersInGroup[i], tHigh = tiersInGroup[i+1];
        var costLow = avg(tierCosts[tLow]), costHigh = avg(tierCosts[tHigh]);
        if (costLow != null && costHigh != null && costLow > costHigh) {
          violations.push({
            layer: 1, severity: 'Critical', violation_type: 'MONOTONICITY_BREACH',
            region: region, tier: tLow + ' > ' + tHigh,
            upgrade_years: parseInt(years) || null, part_number: null,
            message: 'Monotonicity breach: ' + tLow + ' avg ' + fmt(costLow) + ' > ' + tHigh + ' avg ' + fmt(costHigh) + ' — ' + (dtype || 'all') + ' ' + years + 'yr in ' + region
          });
        }
      }
    });
    return violations;
  }

  // ── L2: Ratio bands ─────────────────────────────────────────────────────────

  function runLayer2(flatData, s) {
    var violations = [];
    for (var ri = 0; ri < RATIO_PAIRS.length; ri++) {
      var pair = RATIO_PAIRS[ri];
      var min = parseFloat(s[pair.minKey]) || 0;
      var max = parseFloat(s[pair.maxKey]) || 999;

      var groups = groupBy(
        flatData.filter(function(r) { return r.sales_cost != null; }),
        function(r) { return normTier(r.tier) + '|' + (r.delivery_type || '') + '|' + (r.region || ''); }
      );

      groups.forEach(function(items, key) {
        var parts = key.split('|');
        var tier = parts[0], dtype = parts[1], region = parts[2];

        var costsLo = items.filter(function(r) { return Math.round(r.upgrade_years) === pair.lo; }).map(function(r) { return r.sales_cost; });
        var costsHi = items.filter(function(r) { return Math.round(r.upgrade_years) === pair.hi; }).map(function(r) { return r.sales_cost; });

        if (!costsLo.length || !costsHi.length) return;
        var avgLo = avg(costsLo), avgHi = avg(costsHi);
        if (!avgLo || !avgHi || avgLo === 0) return;
        var ratio = avgHi / avgLo;

        if (ratio < min) {
          violations.push({
            layer: 2, severity: 'Critical', violation_type: 'RATIO_BELOW_FLOOR',
            region: region, tier: tier, upgrade_years: pair.hi, part_number: null,
            message: pair.label + ' ratio ' + ratio.toFixed(3) + ' < floor ' + min + ' for ' + tier + ' ' + (dtype || 'all') + ' in ' + region
          });
        } else if (ratio > max) {
          violations.push({
            layer: 2, severity: 'Warning', violation_type: 'RATIO_ABOVE_CEILING',
            region: region, tier: tier, upgrade_years: pair.hi, part_number: null,
            message: pair.label + ' ratio ' + ratio.toFixed(3) + ' > ceiling ' + max + ' for ' + tier + ' ' + (dtype || 'all') + ' in ' + region
          });
        }
      });
    }
    return violations;
  }

  // ── L3: Cross-geo deviation ─────────────────────────────────────────────────

  function runLayer3(flatData, s) {
    var threshold = parseFloat(s.cross_geo_deviation_pct) || 0.20;
    var violations = [];

    var groups = groupBy(
      flatData.filter(function(r) { return r.sales_cost != null; }),
      function(r) { return normTier(r.tier) + '|' + (r.delivery_type || '') + '|' + (r.upgrade_years || ''); }
    );

    groups.forEach(function(items, key) {
      var parts = key.split('|');
      var tier = parts[0], dtype = parts[1], yearsStr = parts[2];
      var years = parseInt(yearsStr) || null;

      var regionCosts = {};
      for (var i = 0; i < items.length; i++) {
        if (!items[i].region) continue;
        if (!regionCosts[items[i].region]) regionCosts[items[i].region] = [];
        regionCosts[items[i].region].push(items[i].sales_cost);
      }

      var regionAvgs = {};
      Object.keys(regionCosts).forEach(function(r) { regionAvgs[r] = avg(regionCosts[r]); });

      var allAvgs = Object.values(regionAvgs).filter(function(v) { return v != null; });
      if (allAvgs.length < 2) return;
      var crossMean = avg(allAvgs);
      if (!crossMean) return;

      var breaching = [];
      Object.keys(regionAvgs).forEach(function(region) {
        var ravg = regionAvgs[region];
        if (ravg == null) return;
        var dev = Math.abs(ravg - crossMean) / Math.abs(crossMean);
        if (dev > threshold) breaching.push({ region: region, ravg: ravg, dev: dev });
      });

      if (!breaching.length) return;

      var isSystemic = breaching.length >= 3;
      var severity = isSystemic ? 'Systemic' : 'Warning';
      var vtype = isSystemic ? 'SYSTEMIC_CROSS_GEO' : 'CROSS_GEO_DEVIATION';

      for (var b = 0; b < breaching.length; b++) {
        var br = breaching[b];
        violations.push({
          layer: 3, severity: severity, violation_type: vtype,
          region: br.region, tier: tier, upgrade_years: years, part_number: null,
          message: 'Cross-geo deviation ' + (br.dev * 100).toFixed(1) + '% for ' + tier + ' ' + (dtype || 'all') + ' ' + (years || '') + 'yr — region ' + br.region + ' avg ' + fmt(br.ravg) + ' vs cross-mean ' + fmt(crossMean) + (isSystemic ? ' (systemic: ' + breaching.length + ' regions)' : '')
        });
      }
    });
    return violations;
  }

  // ── L4: Year-over-Year ──────────────────────────────────────────────────────

  function runLayer4(flatData, baseline, s) {
    var cellThresh = parseFloat(s.yoy_cell_change_pct) || 0.25;
    var geoThresh = parseFloat(s.yoy_geo_avg_change_pct) || 0.20;
    var violations = [];

    // Current map: part_number + region → avg
    var currentMap = {};
    for (var i = 0; i < flatData.length; i++) {
      var r = flatData[i];
      if (r.sales_cost == null || !r.part_number || !r.region) continue;
      var k = r.part_number + '|' + r.region;
      if (!currentMap[k]) currentMap[k] = [];
      currentMap[k].push(r.sales_cost);
    }
    var currentAvg = {};
    Object.keys(currentMap).forEach(function(k) { currentAvg[k] = avg(currentMap[k]); });

    // Prior map
    var priorMap = {};
    for (var j = 0; j < baseline.length; j++) {
      priorMap[baseline[j].part_number + '|' + baseline[j].region] = baseline[j].prior_sales_cost || baseline[j].sales_cost;
    }

    // Cell-level check
    var regionChanges = {};
    Object.keys(currentAvg).forEach(function(k) {
      var curVal = currentAvg[k];
      var priorVal = priorMap[k];
      if (priorVal == null || priorVal === 0) return;
      var parts = k.split('|');
      var pn = parts[0], region = parts[1];
      var pctChange = (curVal - priorVal) / Math.abs(priorVal);

      if (!regionChanges[region]) regionChanges[region] = [];
      regionChanges[region].push(pctChange);

      if (Math.abs(pctChange) > cellThresh) {
        violations.push({
          layer: 4, severity: 'Critical', violation_type: 'YOY_CELL_DRIFT',
          region: region, tier: null, upgrade_years: null, part_number: pn,
          message: 'YoY cell drift ' + (pctChange * 100).toFixed(1) + '% for ' + pn + ' in ' + region + ' (current: ' + fmt(curVal) + ', prior: ' + fmt(priorVal) + ')'
        });
      }
    });

    // Geo-level average check
    Object.keys(regionChanges).forEach(function(region) {
      var changes = regionChanges[region];
      var avgChg = avg(changes);
      if (avgChg != null && Math.abs(avgChg) > geoThresh) {
        violations.push({
          layer: 4, severity: 'Warning', violation_type: 'YOY_GEO_AVG_DRIFT',
          region: region, tier: null, upgrade_years: null, part_number: null,
          message: 'YoY geo-avg drift ' + (avgChg * 100).toFixed(1) + '% for region ' + region + ' (avg across ' + changes.length + ' SKUs)'
        });
      }
    });

    return violations;
  }

  // ── Public API ──────────────────────────────────────────────────────────────

  return {
    Engine: Engine,
    RATIO_PAIRS: RATIO_PAIRS,
    DEFAULT_SETTINGS: DEFAULT_SETTINGS,
    // Utility: rank violations for display
    severityOrder: { 'Critical': 0, 'Systemic': 1, 'Warning': 2, 'OK': 3 },
    sortViolations: function(violations) {
      var sev = this.severityOrder;
      return violations.slice().sort(function(a, b) {
        return (sev[a.severity] || 99) - (sev[b.severity] || 99) || (a.layer || 0) - (b.layer || 0);
      });
    }
  };

})();

// Register globally for non-module stage scripts
if (typeof window !== 'undefined') window.GVE = GVE;
