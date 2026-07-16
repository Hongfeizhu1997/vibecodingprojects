import type { SalesCostUploadRecord, SalesCostDisplayRecord, OHMasterRecord } from '@/types';

// Transform raw upload data to display format
export function transformUploadData(
  uploadData: SalesCostUploadRecord[],
  ohMasterData: OHMasterRecord[]
): SalesCostDisplayRecord[] {
  return uploadData.map(record => {
    // Determine POS or APOS
    const posOrApos: 'POS' | 'APOS' = 
      record.salesMarketingLongDescription.toUpperCase().includes('APOS') ||
      record.salesMarketingLongDescription.toUpperCase().includes('POST') ||
      record.salesMarketingLongDescription.toUpperCase().includes('POST WARRANTY') ||
      record.salesMarketingLongDescription.toUpperCase().includes('PW')
        ? 'APOS'
        : 'POS';

    // Extract Starting Point from description (case-insensitive matching, preserve original format)
    let serviceStartingPoint = '';
    const originalDesc = record.salesMarketingLongDescription;
    
    // Create normalized version for matching (lowercase, single spaces)
    const normalizedDesc = originalDesc.toLowerCase().replace(/\s+/g, ' ').trim();
    
    // Try to find "upgrade from" position in normalized string
    const upgradeFromIndex = normalizedDesc.indexOf('upgrade from');
    if (upgradeFromIndex !== -1) {
      // Find the position in original string (accounting for potential extra spaces)
      let originalIndex = 0;
      let normalizedIndex = 0;
      for (let i = 0; i < originalDesc.length && normalizedIndex < upgradeFromIndex + 12; i++) {
        if (originalDesc[i].toLowerCase() === normalizedDesc[normalizedIndex]) {
          normalizedIndex++;
        }
        originalIndex = i;
      }
      
      // Extract from after "upgrade from" (12 chars)
      const afterUpgradeFrom = originalDesc.substring(originalIndex + 1);
      
      // Find the end marker (" for" or " upgrade" or end of string)
      const endMarkers = [' for', ' upgrade'];
      let endPos = afterUpgradeFrom.length;
      for (const marker of endMarkers) {
        const markerIndex = afterUpgradeFrom.toLowerCase().indexOf(marker);
        if (markerIndex !== -1 && markerIndex < endPos) {
          endPos = markerIndex;
        }
      }
      
      serviceStartingPoint = afterUpgradeFrom.substring(0, endPos).trim();
    }
    // If not found, leave blank (as per requirement)

    // Extract Term from Service PN Short Description (first 2 characters)
    const term = record.servicePNShortDescription.trim().substring(0, 2);

    // Lookup OH Master Data
    const ohRecord = ohMasterData.find(oh => oh.ohCode === record.ohCode);

    return {
      servicePN: record.servicePN,
      servicePNShortDescription: record.servicePNShortDescription,
      salesMarketingLongDescription: record.salesMarketingLongDescription,
      posOrApos,
      serviceStartingPoint,
      term,
      serviceTier: record.serviceTier,
      subServiceTier: record.subServiceTier,
      ohCode: record.ohCode,
      ohName: ohRecord?.ohName || '',
      typeOfService: ohRecord?.typeOfService || '',
      subTypeOfService: ohRecord?.subTypeOfService || '',
      offeringType: ohRecord?.offeringType || '',
      country: record.country,
      salesCost: record.salesCost
    };
  });
}

// Parse Excel file to JSON
export async function parseExcelFile(file: File): Promise<any[]> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = e.target?.result;
        if (!data) {
          reject(new Error('Failed to read file'));
          return;
        }
        // Use xlsx library to parse
        import('xlsx').then(XLSX => {
          const workbook = XLSX.read(data, { type: 'binary' });
          const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
          const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });
          resolve(jsonData);
        });
      } catch (error) {
        reject(error);
      }
    };
    reader.onerror = (error) => reject(error);
    reader.readAsBinaryString(file);
  });
}

// Convert parsed Excel data to SalesCostUploadRecord format
export function convertToUploadRecords(data: any[][]): SalesCostUploadRecord[] {
  if (data.length < 2) return [];
  
  // Skip header row (data[0])
  const records: SalesCostUploadRecord[] = [];
  
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    if (!row || row.length === 0) continue;
    
    const record: SalesCostUploadRecord = {
      servicePN: String(row[0] || ''),
      servicePNShortDescription: String(row[1] || ''),
      salesMarketingLongDescription: String(row[2] || ''),
      serviceTier: String(row[3] || ''),
      subServiceTier: row[4] ? String(row[4]) : null,
      ohCode: String(row[5] || ''),
      country: String(row[6] || ''),
      salesCost: parseFloat(row[7]) || 0
    };
    
    records.push(record);
  }
  
  return records;
}
