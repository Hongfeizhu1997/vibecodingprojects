import type { SalesCostCheckRule, SalesCostDisplayRecord, CheckResult, CheckSummary } from '@/types';

// Get group key from record based on grouping factors
export function getGroupKey(record: SalesCostDisplayRecord, groupingFactors: string[]): string {
  const keyParts: string[] = [];
  
  for (const factor of groupingFactors) {
    switch (factor) {
      case 'POS or APOS':
        keyParts.push(record.posOrApos);
        break;
      case 'Service Tier':
        keyParts.push(record.serviceTier);
        break;
      case 'Sub Service Tier':
        keyParts.push(record.subServiceTier || 'N/A');
        break;
      case 'Starting Point':
        keyParts.push(record.serviceStartingPoint);
        break;
      case 'Offering Type':
        keyParts.push(record.offeringType);
        break;
      case 'Term':
        keyParts.push(record.term);
        break;
      case 'Country':
        keyParts.push(record.country);
        break;
    }
  }
  
  return keyParts.join(' | ');
}

// Get compare value from record based on compare factor
export function getCompareValue(record: SalesCostDisplayRecord, compareFactor: string): string {
  switch (compareFactor) {
    case 'POS or APOS':
      return record.posOrApos;
    case 'Service Tier':
      return record.serviceTier;
    case 'Sub Service Tier':
      return record.subServiceTier || 'N/A';
    case 'Starting Point':
      return record.serviceStartingPoint;
    case 'Offering Type':
      return record.offeringType;
    case 'Term':
      return record.term;
    case 'Country':
      return record.country;
    default:
      return '';
  }
}

// Execute cross check for a single rule
// Logic: 
// 1. Group data by Grouping Factors
// 2. Filter records by Compare Priority values
// 3. Compare ALL pairs where high priority > low priority:
//    - Compare each individual record's sales cost (NOT average)
//    - High priority sales cost MUST BE STRICTLY GREATER than low priority
export function executeCrossCheck(
  rule: SalesCostCheckRule,
  data: SalesCostDisplayRecord[]
): CheckResult[] {
  const results: CheckResult[] = [];
  
  // Step 1: Group data by grouping factors
  const groups = new Map<string, SalesCostDisplayRecord[]>();
  
  for (const record of data) {
    const groupKey = getGroupKey(record, rule.groupingFactors);
    if (!groups.has(groupKey)) {
      groups.set(groupKey, []);
    }
    groups.get(groupKey)!.push(record);
  }
  
  // Step 2 & 3: For each group, filter and compare
  for (const [groupKey, groupRecords] of groups) {
    // Filter records that have compare factor values in the priority list
    const filteredRecords = groupRecords.filter(r => {
      const compareValue = getCompareValue(r, rule.compareFactor);
      return rule.comparePriority.includes(compareValue);
    });
    
    if (filteredRecords.length < 2) continue;
    
    // Group by compare factor value
    const compareGroups = new Map<string, SalesCostDisplayRecord[]>();
    for (const record of filteredRecords) {
      const compareValue = getCompareValue(record, rule.compareFactor);
      if (!compareGroups.has(compareValue)) {
        compareGroups.set(compareValue, []);
      }
      compareGroups.get(compareValue)!.push(record);
    }
    
    // Step 3: Compare all pairs where high priority > low priority
    // Compare each individual record (NOT average)
    for (let i = 0; i < rule.comparePriority.length; i++) {
      const lowPriorityValue = rule.comparePriority[i];
      const lowRecords = compareGroups.get(lowPriorityValue) || [];
      
      if (lowRecords.length === 0) continue;
      
      // Compare with all higher priority values
      for (let j = i + 1; j < rule.comparePriority.length; j++) {
        const highPriorityValue = rule.comparePriority[j];
        const highRecords = compareGroups.get(highPriorityValue) || [];
        
        if (highRecords.length === 0) continue;
        
        // Compare each high record against each low record
        for (const highRecord of highRecords) {
          for (const lowRecord of lowRecords) {
            const highSalesCost = highRecord.salesCost;
            const lowSalesCost = lowRecord.salesCost;
            
            // Check: high priority sales cost MUST BE STRICTLY GREATER than low priority
            const status = highSalesCost > lowSalesCost ? 'PASS' : 'FAIL';
            const difference = highSalesCost - lowSalesCost;
            
            // Generate fail reason if check fails
            const failReason = status === 'FAIL' 
              ? `${highPriorityValue} (${highRecord.servicePN}: $${highSalesCost.toFixed(4)}) must be > ${lowPriorityValue} (${lowRecord.servicePN}: $${lowSalesCost.toFixed(4)}), but difference is $${difference.toFixed(4)}`
              : undefined;
            
            results.push({
              ruleId: rule.id,
              ruleDescription: rule.description,
              groupKey,
              compareFactor: rule.compareFactor,
              lowPriorityValue,
              highPriorityValue,
              lowPrioritySalesCost: lowSalesCost,
              highPrioritySalesCost: highSalesCost,
              status,
              difference,
              failReason,
              records: [lowRecord, highRecord]
            });
          }
        }
      }
    }
  }
  
  return results;
}

// Execute all rules and return results
export function executeAllCrossChecks(
  rules: SalesCostCheckRule[],
  data: SalesCostDisplayRecord[]
): { results: CheckResult[]; summary: CheckSummary } {
  const allResults: CheckResult[] = [];
  
  for (const rule of rules) {
    const ruleResults = executeCrossCheck(rule, data);
    allResults.push(...ruleResults);
  }
  
  const passCount = allResults.filter(r => r.status === 'PASS').length;
  const failCount = allResults.filter(r => r.status === 'FAIL').length;
  
  const summary: CheckSummary = {
    totalRules: rules.length,
    totalGroups: new Set(allResults.map(r => r.groupKey)).size,
    totalChecks: allResults.length,
    passCount,
    failCount
  };
  
  return { results: allResults, summary };
}
