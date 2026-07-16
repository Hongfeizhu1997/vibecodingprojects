import { useMemo } from 'react';

/**
 * Calculate column widths based on the maximum content length in each column.
 * Returns a map of column key -> width in pixels.
 * 
 * @param data - Array of data records
 * @param columnDefs - Array of column definitions with key and optional min/max width
 * @returns Record of column key -> CSS width string
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function useAutoColumnWidths(
  data: any[],
  columnDefs: { key: string; label: string; minWidth?: number; maxWidth?: number }[]
): Record<string, string> {
  return useMemo(() => {
    if (data.length === 0) {
      // Default widths when no data
      const defaults: Record<string, string> = {};
      columnDefs.forEach(col => {
        defaults[col.key] = `${col.minWidth || 120}px`;
      });
      return defaults;
    }

    const widths: Record<string, string> = {};
    
    columnDefs.forEach(col => {
      // Get the header (label) length
      const headerLength = col.label.length;
      
      // Find max content length in this column
      let maxContentLength = headerLength;
      
      // Sample up to 500 rows for performance
      const sampleSize = Math.min(data.length, 500);
      for (let i = 0; i < sampleSize; i++) {
        const value = data[i][col.key];
        if (value !== null && value !== undefined) {
          const str = String(value);
          if (str.length > maxContentLength) {
            maxContentLength = str.length;
          }
        }
      }
      
      // Calculate pixel width: ~8px per character for small text, with padding
      // Use a multiplier that accounts for font size and padding
      let pixelWidth = Math.max(maxContentLength * 8 + 24, col.minWidth || 80);
      
      // Apply max width cap if specified
      if (col.maxWidth && pixelWidth > col.maxWidth) {
        pixelWidth = col.maxWidth;
      }
      
      // Ensure minimum width for usability
      pixelWidth = Math.max(pixelWidth, col.minWidth || 80);
      
      widths[col.key] = `${pixelWidth}px`;
    });
    
    return widths;
  }, [data, columnDefs]);
}

/**
 * Simple version that returns a style object for table cells
 */
export function getColumnStyle(
  width: string,
  options?: { align?: 'left' | 'center' | 'right'; truncate?: boolean }
): React.CSSProperties {
  return {
    width,
    minWidth: width,
    textAlign: options?.align || 'left',
    whiteSpace: options?.truncate ? 'nowrap' : 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  };
}
