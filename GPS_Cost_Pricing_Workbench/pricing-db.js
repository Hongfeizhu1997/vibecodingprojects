/**
 * pricing-db.js — Unified pricing history data layer
 * 
 * Loads pricing_master.csv via HTTP GET at startup, caches in memory,
 * and writes changes back via HTTP POST to server.py's /api/save-master.
 * 
 * API:
 *   PricingDB.init()              — load from server, call once on startup
 *   PricingDB.addRecord(data)     — upsert a record (key: cycle_name + service_pn)
 *   PricingDB.getCycles()         — list all unique cycle names with stats
 *   PricingDB.getCycleDetail(name)— all records in a given cycle
 *   PricingDB.getPNHistory(pn)    — all cycles for a given PN (chronological)
 *   PricingDB.getAll()            — raw array of all records
 *   PricingDB.downloadCSV()       — trigger browser download of current data
 */

const PricingDB = (() => {
  const RECORD_KEY_FIELDS = ['cycle_name', 'service_pn'];

  let _records = [];
  let _initialized = false;

  /** Load all records from server */
  async function init() {
    try {
      const resp = await fetch('/api/load-master');
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      _records = await resp.json();
      _initialized = true;
      console.log(`[PricingDB] Loaded ${_records.length} records from pricing_master.csv`);
      return _records;
    } catch (e) {
      console.warn('[PricingDB] Could not load from server, starting empty:', e.message);
      _records = [];
      _initialized = true;
      return [];
    }
  }

  /** Upsert a record: same (cycle_name, service_pn) = update, otherwise append. Posts to server. */
  async function addRecord(data) {
    if (!_initialized) await init();

    const record = { ...data };

    const idx = _records.findIndex(r =>
      RECORD_KEY_FIELDS.every(k => r[k] === record[k])
    );

    if (idx >= 0) {
      Object.assign(_records[idx], record);
    } else {
      _records.push(record);
    }

    try {
      const resp = await fetch('/api/save-master', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(record)
      });
      const result = await resp.json();
      console.log(`[PricingDB] ${result.action} record: ${record.service_pn} @ ${record.cycle_name}`);
    } catch (e) {
      console.error('[PricingDB] Failed to save to server:', e.message);
      throw e;
    }
    return record;
  }

  function getCycles() {
    if (!_initialized) return [];
    const cycles = {};
    for (const r of _records) {
      const cn = r.cycle_name;
      if (!cycles[cn]) {
        cycles[cn] = { name: cn, pn_count: 0, gp_sum: 0, gp_count: 0, completed_at: r.completed_at || '' };
      }
      cycles[cn].pn_count++;
      if (r.gp_percent) {
        cycles[cn].gp_sum += parseFloat(r.gp_percent);
        cycles[cn].gp_count++;
      }
      if (r.completed_at && r.completed_at > cycles[cn].completed_at) {
        cycles[cn].completed_at = r.completed_at;
      }
    }
    return Object.values(cycles).map(c => ({
      ...c,
      avg_gp: c.gp_count > 0 ? (c.gp_sum / c.gp_count).toFixed(1) + '%' : '—'
    }));
  }

  function getCycleDetail(name) {
    return _records.filter(r => r.cycle_name === name);
  }

  function getPNHistory(pn) {
    return _records
      .filter(r => r.service_pn === pn)
      .sort((a, b) => (b.completed_at || '').localeCompare(a.completed_at || ''));
  }

  function getAll() {
    return _records;
  }

  function downloadCSV() {
    if (_records.length === 0) { alert('No data to export.'); return; }
    const cols = [
      'cycle_name','completed_at','service_pn','country','service_tier',
      'upgrade_years','delivery_type','aipc','psc_value','sales_cost',
      'gve_status','list_price','channel_price','gp_percent','gradient_status'
    ];
    const header = cols.join(',');
    const rows = _records.map(r => cols.map(c => r[c] || '').join(','));
    const csv = [header, ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `pricing_master_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
  }

  return { init, addRecord, getCycles, getCycleDetail, getPNHistory, getAll, downloadCSV };
})();
