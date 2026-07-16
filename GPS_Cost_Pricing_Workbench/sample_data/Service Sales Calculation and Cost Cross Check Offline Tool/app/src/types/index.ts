// Types for Sales Cost Cross Check App

// Grouping and Compare Factor
export type GroupingFactor = 
  | 'POS or APOS' 
  | 'Service Tier' 
  | 'Sub Service Tier' 
  | 'Starting Point' 
  | 'Offering Type' 
  | 'Term' 
  | 'Country';

export const ALL_GROUPING_FACTORS: GroupingFactor[] = [
  'POS or APOS',
  'Service Tier',
  'Sub Service Tier',
  'Starting Point',
  'Offering Type',
  'Term',
  'Country'
];

// Sales Cost Check Rule
export interface SalesCostCheckRule {
  id: string;
  description: string;
  typeOfService: string;
  geo: string[];
  validFrom: string;
  validTo: string;
  createdBy: string;
  createdAt: string;
  status: 'Draft' | 'Released' | 'Retired';
  groupingFactors: GroupingFactor[];
  compareFactor: GroupingFactor;
  comparePriority: string[];
  checkLogic: string;
  summaryCheckLogic: string;
}

// Raw upload data
export interface SalesCostUploadRecord {
  servicePN: string;
  servicePNShortDescription: string;
  salesMarketingLongDescription: string;
  serviceTier: string;
  subServiceTier: string | null;
  ohCode: string;
  country: string;
  salesCost: number;
}

// Transformed display data
export interface SalesCostDisplayRecord {
  servicePN: string;
  servicePNShortDescription: string;
  salesMarketingLongDescription: string;
  posOrApos: 'POS' | 'APOS';
  serviceStartingPoint: string;
  term: string;
  serviceTier: string;
  subServiceTier: string | null;
  ohCode: string;
  ohName: string;
  typeOfService: string;
  subTypeOfService: string;
  offeringType: string;
  country: string;
  salesCost: number;
}

// OH Master Data
export interface OHMasterRecord {
  ohCode: string;
  ohName: string;
  group: string;
  bg: string;
  ohL1: string;
  typeOfService: string;
  subTypeOfService: string;
  offeringType: string;
  ohL5: string | null;
  ohL6: string | null;
}

// Check Result
export interface CheckResult {
  ruleId: string;
  ruleDescription: string;
  groupKey: string;
  compareFactor: string;
  lowPriorityValue: string;
  highPriorityValue: string;
  lowPrioritySalesCost: number;
  highPrioritySalesCost: number;
  status: 'PASS' | 'FAIL';
  difference: number;
  failReason?: string;
  records: SalesCostDisplayRecord[];
}

// Summary data
export interface CheckSummary {
  totalRules: number;
  totalGroups: number;
  totalChecks: number;
  passCount: number;
  failCount: number;
}

// Navigation item
export interface NavItem {
  id: string;
  label: string;
  icon: string;
}
