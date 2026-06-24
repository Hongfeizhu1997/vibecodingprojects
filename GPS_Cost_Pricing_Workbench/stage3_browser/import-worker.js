/**
 * GPS Cost Pricing Workbench — Phase 5: Streaming CSV Import Worker
 * No DOM or window access — pure JS for Web Worker context.
 */

// ── CSV line parser (identical to Stage 3 parseCSVLine) ──
function parseCSVLine(line) {
  const result = [];
  let cur = '', inQ = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (c === '"') { inQ = !inQ; }
    else if (c === ',' && !inQ) { result.push(cur); cur = ''; }
    else cur += c;
  }
  result.push(cur);
  return result;
}

// ── Worker state ──
let headers = null;      // extracted from first chunk
let carryover = '';      // incomplete last line from previous chunk
let totalRows = 0;

self.onmessage = function(e) {
  const msg = e.data;

  if (msg.type === 'chunk') {
    const text = msg.data;
    const isFirst = msg.isFirst;

    // Prepend any incomplete line from previous chunk
    const combined = carryover + text;
    const lines = combined.split('\n');

    // Last element may be incomplete — save for next chunk
    carryover = lines.pop() || '';

    if (isFirst && headers === null && lines.length > 0) {
      headers = parseCSVLine(lines.shift());
    }

    if (!headers) {
      self.postMessage({ type: 'rows', rows: [], done: false });
      return;
    }

    const rows = [];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;

      const vals = parseCSVLine(line);
      if (!vals.length) continue;

      const row = {};
      headers.forEach((h, j) => {
        row[h.trim()] = vals[j] || null;
      });
      rows.push(row);
    }

    totalRows += rows.length;
    self.postMessage({ type: 'rows', rows, done: false });

  } else if (msg.type === 'finish') {
    // Flush carryover (last incomplete line may actually be complete if
    // the file ended without a trailing newline)
    if (carryover.trim()) {
      const vals = parseCSVLine(carryover.trim());
      if (vals.length && headers) {
        const row = {};
        headers.forEach((h, j) => {
          row[h.trim()] = vals[j] || null;
        });
        self.postMessage({ type: 'rows', rows: [row], done: false });
        totalRows++;
      }
    }

    self.postMessage({
      type: 'done',
      totalRows,
      headers
    });
  }

  else if (msg.type === 'reset') {
    headers = null;
    carryover = '';
    totalRows = 0;
  }
};
