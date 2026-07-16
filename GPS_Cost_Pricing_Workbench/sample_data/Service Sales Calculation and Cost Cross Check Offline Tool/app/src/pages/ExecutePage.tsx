import { useState, useMemo, useEffect } from 'react';
import { useApp } from '@/store/AppContext';
import { useAutoColumnWidths } from '@/hooks/useColumnWidths';
import * as XLSX from 'xlsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { 
  Play, 
  CheckCircle, 
  XCircle, 
  BarChart3,
  PieChart,
  Filter,
  Download,
  RotateCcw,
  AlertTriangle,
  Search,
  Eye,
  Layers,
  Target,
  ChevronRight,
  ArrowLeft,
  FolderOpen,
  FileText,
  Columns,
  ArrowUp,
  ArrowDown,
  ChevronsUp,
  ChevronsDown,
  ChevronLeft,
  ChevronsLeft,
  ChevronsRight,
  GripVertical,
  X,
  Globe
} from 'lucide-react';
import type { CheckResult, SalesCostDisplayRecord } from '@/types';

interface FilterState {
  ruleId: string;
  status: 'all' | 'PASS' | 'FAIL';
  compareFactor: string;
  groupKey: string;
  minDifference: string;
  maxDifference: string;
  posOrApos: string;
  country: string;
  serviceTier: string;
  subServiceTier: string;
  offeringType: string;
  term: string;
  startingPoint: string;
}

// Drill-down view types
type DrillView = 'rules' | 'groups' | 'records' | 'detail';

export function ExecutePage() {
  const { rules, displayData, checkResults, checkSummary, executeChecks } = useApp();
  const [isExecuting, setIsExecuting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Drill-down state
  const [drillView, setDrillView] = useState<DrillView>('rules');
  const [selectedRuleId, setSelectedRuleId] = useState<string | null>(null);
  const [selectedGroupKey, setSelectedGroupKey] = useState<string | null>(null);
  const [selectedResult, setSelectedResult] = useState<CheckResult | null>(null);

  // Drill-down filters
  const [drillFilters, setDrillFilters] = useState({
    status: 'all' as 'all' | 'PASS' | 'FAIL',
    search: '',
  });

  // Grouped Check Results tab state
  const [groupedFilters, setGroupedFilters] = useState({
    rule: 'all',
    serviceTier: 'all',
    subServiceTier: 'all',
    startingPoint: 'all',
    offeringType: 'all',
    country: 'all',
    status: 'all' as 'all' | 'PASS' | 'FAIL',
  });
  const [groupedDrillRule, setGroupedDrillRule] = useState<string | null>(null);
  const [groupedDrillGroup, setGroupedDrillGroup] = useState<string | null>(null);

  // Missing Check Rules tab state
  const [missingFilters, setMissingFilters] = useState({
    serviceTier: 'all',
    subServiceTier: 'all',
    startingPoint: 'all',
    offeringType: 'all',
    country: 'all',
    posOrApos: 'all',
  });

  // Filters
  const [filters, setFilters] = useState<FilterState>({
    ruleId: 'all',
    status: 'all',
    compareFactor: 'all',
    groupKey: '',
    minDifference: '',
    maxDifference: '',
    posOrApos: 'all',
    country: 'all',
    serviceTier: 'all',
    subServiceTier: 'all',
    offeringType: 'all',
    term: 'all',
    startingPoint: 'all'
  });

  // Details tab pagination
  const [detailsPage, setDetailsPage] = useState(1);
  const DETAILS_PAGE_SIZE = 100;

  // Column visibility configuration for detail table
  const ALL_COLUMNS = [
    { key: 'servicePN', label: 'Service PN', default: true },
    { key: 'servicePNShortDescription', label: 'Service PN Short Description', default: true },
    { key: 'salesMarketingLongDescription', label: 'Sales&Marketing Long Description', default: false },
    { key: 'posOrApos', label: 'POS or APOS', default: true },
    { key: 'serviceStartingPoint', label: 'Starting Point', default: true },
    { key: 'term', label: 'Term', default: true },
    { key: 'serviceTier', label: 'Service Tier', default: true },
    { key: 'subServiceTier', label: 'Sub Service Tier', default: true },
    { key: 'ohCode', label: 'OH Code', default: false },
    { key: 'ohName', label: 'OH Name', default: true },
    { key: 'typeOfService', label: 'Type of Service', default: false },
    { key: 'subTypeOfService', label: 'Sub Type of Service', default: false },
    { key: 'offeringType', label: 'Offering Type', default: true },
    { key: 'country', label: 'Country', default: true },
    { key: 'salesCost', label: 'Sales Cost', default: true },
  ] as const;

  type ColumnKey = typeof ALL_COLUMNS[number]['key'];

  const [visibleColumns, setVisibleColumns] = useState<Set<ColumnKey>>(() => {
    const saved = localStorage.getItem('executePageVisibleColumns');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        return new Set(parsed as ColumnKey[]);
      } catch {
        // fallback to defaults
      }
    }
    return new Set(ALL_COLUMNS.filter(c => c.default).map(c => c.key));
  });

  // Persist column visibility to localStorage
  useEffect(() => {
    localStorage.setItem('executePageVisibleColumns', JSON.stringify([...visibleColumns]));
  }, [visibleColumns]);

  const toggleColumn = (key: ColumnKey) => {
    setVisibleColumns(prev => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const resetColumns = () => {
    setVisibleColumns(new Set(ALL_COLUMNS.filter(c => c.default).map(c => c.key)));
  };

  const showAllColumns = () => {
    setVisibleColumns(new Set(ALL_COLUMNS.map(c => c.key)));
  };

  // Column visibility for Details tab table - V9 Style
  const DETAILS_COLUMNS = [
    { key: 'ruleId', label: 'Rule ID', default: true },
    { key: 'servicePN', label: 'Service PN', default: true },
    { key: 'serviceTier', label: 'Service Tier', default: true },
    { key: 'subServiceTier', label: 'Sub Tier', default: true },
    { key: 'term', label: 'Term', default: true },
    { key: 'country', label: 'Country', default: true },
    { key: 'offeringType', label: 'Offering Type', default: true },
    { key: 'lowCost', label: 'Low Cost', default: true },
    { key: 'highCost', label: 'High Cost', default: true },
    { key: 'status', label: 'Status', default: true },
    { key: 'validationError', label: 'Validation Errors', default: true },
    { key: 'groupKey', label: 'Group Key', default: false },
    { key: 'compare', label: 'Compare', default: false },
    { key: 'posOrApos', label: 'POS or APOS', default: false },
    { key: 'servicePNShortDescription', label: 'Service PN Short Description', default: false },
    { key: 'salesMarketingLongDescription', label: 'Sales&Marketing Long Description', default: false },
    { key: 'startingPoint', label: 'Starting Point', default: false },
    { key: 'ohName', label: 'OH Name', default: false },
    { key: 'typeOfService', label: 'Type of Service', default: false },
    { key: 'subTypeOfService', label: 'Sub Type of Service', default: false },
    { key: 'difference', label: 'Difference', default: false },
    { key: 'failReason', label: 'Fail Reason (Legacy)', default: false },
  ] as const;

  type DetailsColumnKey = typeof DETAILS_COLUMNS[number]['key'];

  const [detailsVisibleColumns, setDetailsVisibleColumns] = useState<Set<DetailsColumnKey>>(() => {
    const saved = localStorage.getItem('detailsTabVisibleColumns');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        return new Set(parsed as DetailsColumnKey[]);
      } catch {
        // fallback to defaults
      }
    }
    return new Set(DETAILS_COLUMNS.filter(c => c.default).map(c => c.key));
  });

  // Column order state for Details tab
  const [detailsColumnOrder, setDetailsColumnOrder] = useState<DetailsColumnKey[]>(() => {
    const saved = localStorage.getItem('detailsTabColumnOrder');
    if (saved) {
      try {
        const parsed = JSON.parse(saved) as DetailsColumnKey[];
        // Validate that all saved columns still exist in DETAILS_COLUMNS
        const validColumns = parsed.filter(col => DETAILS_COLUMNS.some(c => c.key === col));
        // Add any new columns that aren't in the saved order
        const newColumns = DETAILS_COLUMNS.filter(c => !parsed.includes(c.key)).map(c => c.key);
        return [...validColumns, ...newColumns];
      } catch {
        // fallback to default order
      }
    }
    return DETAILS_COLUMNS.map(c => c.key);
  });

  useEffect(() => {
    localStorage.setItem('detailsTabVisibleColumns', JSON.stringify([...detailsVisibleColumns]));
  }, [detailsVisibleColumns]);

  useEffect(() => {
    localStorage.setItem('detailsTabColumnOrder', JSON.stringify(detailsColumnOrder));
  }, [detailsColumnOrder]);

  const toggleDetailsColumn = (key: DetailsColumnKey) => {
    setDetailsVisibleColumns(prev => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const resetDetailsColumns = () => {
    setDetailsVisibleColumns(new Set(DETAILS_COLUMNS.filter(c => c.default).map(c => c.key)));
    setDetailsColumnOrder(DETAILS_COLUMNS.map(c => c.key));
  };

  const showAllDetailsColumns = () => {
    setDetailsVisibleColumns(new Set(DETAILS_COLUMNS.map(c => c.key)));
  };

  // Column reordering functions
  const moveColumnUp = (key: DetailsColumnKey) => {
    setDetailsColumnOrder(prev => {
      const index = prev.indexOf(key);
      if (index <= 0) return prev;
      const newOrder = [...prev];
      [newOrder[index - 1], newOrder[index]] = [newOrder[index], newOrder[index - 1]];
      return newOrder;
    });
  };

  const moveColumnDown = (key: DetailsColumnKey) => {
    setDetailsColumnOrder(prev => {
      const index = prev.indexOf(key);
      if (index >= prev.length - 1) return prev;
      const newOrder = [...prev];
      [newOrder[index], newOrder[index + 1]] = [newOrder[index + 1], newOrder[index]];
      return newOrder;
    });
  };

  const moveColumnToTop = (key: DetailsColumnKey) => {
    setDetailsColumnOrder(prev => {
      const index = prev.indexOf(key);
      if (index <= 0) return prev;
      const newOrder = [...prev];
      newOrder.splice(index, 1);
      newOrder.unshift(key);
      return newOrder;
    });
  };

  const moveColumnToBottom = (key: DetailsColumnKey) => {
    setDetailsColumnOrder(prev => {
      const index = prev.indexOf(key);
      if (index >= prev.length - 1) return prev;
      const newOrder = [...prev];
      newOrder.splice(index, 1);
      newOrder.push(key);
      return newOrder;
    });
  };

  // Get unique values for filters
  const uniqueRules = useMemo(() => [...new Set(checkResults.map(r => r.ruleId))], [checkResults]);
  const uniqueCompareFactors = useMemo(() => [...new Set(checkResults.map(r => r.compareFactor))], [checkResults]);
  
  const uniquePosOrApos = useMemo(() => {
    const values = new Set<string>();
    checkResults.forEach(r => r.records.forEach(rec => values.add(rec.posOrApos)));
    return [...values].sort();
  }, [checkResults]);
  
  const uniqueCountries = useMemo(() => {
    const values = new Set<string>();
    checkResults.forEach(r => r.records.forEach(rec => values.add(rec.country)));
    return [...values].sort();
  }, [checkResults]);
  
  const uniqueServiceTiers = useMemo(() => {
    const values = new Set<string>();
    checkResults.forEach(r => r.records.forEach(rec => values.add(rec.serviceTier)));
    return [...values].sort();
  }, [checkResults]);
  
  const uniqueSubServiceTiers = useMemo(() => {
    const values = new Set<string>();
    checkResults.forEach(r => r.records.forEach(rec => {
      if (rec.subServiceTier) values.add(rec.subServiceTier);
    }));
    return [...values].sort();
  }, [checkResults]);
  
  const uniqueOfferingTypes = useMemo(() => {
    const values = new Set<string>();
    checkResults.forEach(r => r.records.forEach(rec => values.add(rec.offeringType)));
    return [...values].sort();
  }, [checkResults]);
  
  const uniqueTerms = useMemo(() => {
    const values = new Set<string>();
    checkResults.forEach(r => r.records.forEach(rec => values.add(rec.term)));
    return [...values].sort();
  }, [checkResults]);
  
  const uniqueStartingPoints = useMemo(() => {
    const values = new Set<string>();
    checkResults.forEach(r => r.records.forEach(rec => values.add(rec.serviceStartingPoint)));
    return [...values].sort();
  }, [checkResults]);

  // Get rule description map
  const ruleDescriptionMap = useMemo(() => {
    const map = new Map<string, string>();
    rules.forEach(r => map.set(r.id, r.description));
    return map;
  }, [rules]);

  // Apply filters
  const filteredResults = useMemo(() => {
    return checkResults.filter(result => {
      if (filters.ruleId !== 'all' && result.ruleId !== filters.ruleId) return false;
      if (filters.status !== 'all' && result.status !== filters.status) return false;
      if (filters.compareFactor !== 'all' && result.compareFactor !== filters.compareFactor) return false;
      if (filters.groupKey && !result.groupKey.toLowerCase().includes(filters.groupKey.toLowerCase())) return false;
      if (filters.minDifference && result.difference < parseFloat(filters.minDifference)) return false;
      if (filters.maxDifference && result.difference > parseFloat(filters.maxDifference)) return false;
      
      if (filters.posOrApos !== 'all' && !result.records.some(r => r.posOrApos === filters.posOrApos)) return false;
      if (filters.country !== 'all' && !result.records.some(r => r.country === filters.country)) return false;
      if (filters.serviceTier !== 'all' && !result.records.some(r => r.serviceTier === filters.serviceTier)) return false;
      if (filters.subServiceTier !== 'all' && !result.records.some(r => r.subServiceTier === filters.subServiceTier)) return false;
      if (filters.offeringType !== 'all' && !result.records.some(r => r.offeringType === filters.offeringType)) return false;
      if (filters.term !== 'all' && !result.records.some(r => r.term === filters.term)) return false;
      if (filters.startingPoint !== 'all' && !result.records.some(r => r.serviceStartingPoint === filters.startingPoint)) return false;
      
      return true;
    });
  }, [checkResults, filters]);

  // ===== Grouped Check Results computation =====
  const groupedData = useMemo(() => {
    const groupMap = new Map<string, {
      ruleId: string;
      groupKey: string;
      records: CheckResult[];
      hasFail: boolean;
      allPass: boolean;
      errorCount: number;
      totalCount: number;
      firstRecord: SalesCostDisplayRecord | null;
    }>();
    checkResults.forEach(cr => {
      const key = `${cr.ruleId}::${cr.groupKey}`;
      const existing = groupMap.get(key);
      if (existing) {
        existing.records.push(cr);
        existing.totalCount++;
        if (cr.status === 'FAIL') { existing.hasFail = true; existing.errorCount++; }
      } else {
        groupMap.set(key, {
          ruleId: cr.ruleId, groupKey: cr.groupKey, records: [cr],
          hasFail: cr.status === 'FAIL', allPass: cr.status === 'PASS',
          errorCount: cr.status === 'FAIL' ? 1 : 0, totalCount: 1,
          firstRecord: cr.records[0] || null,
        });
      }
    });
    return [...groupMap.values()];
  }, [checkResults]);

  const filteredGroupedData = useMemo(() => {
    return groupedData.filter(g => {
      if (groupedFilters.rule !== 'all' && g.ruleId !== groupedFilters.rule) return false;
      if (groupedFilters.status !== 'all') {
        if (groupedFilters.status === 'PASS' && g.hasFail) return false;
        if (groupedFilters.status === 'FAIL' && !g.hasFail) return false;
      }
      if (groupedFilters.serviceTier !== 'all' && g.firstRecord?.serviceTier !== groupedFilters.serviceTier) return false;
      if (groupedFilters.subServiceTier !== 'all' && g.firstRecord?.subServiceTier !== groupedFilters.subServiceTier) return false;
      if (groupedFilters.startingPoint !== 'all' && g.firstRecord?.serviceStartingPoint !== groupedFilters.startingPoint) return false;
      if (groupedFilters.offeringType !== 'all' && g.firstRecord?.offeringType !== groupedFilters.offeringType) return false;
      if (groupedFilters.country !== 'all' && g.firstRecord?.country !== groupedFilters.country) return false;
      return true;
    });
  }, [groupedData, groupedFilters]);

  const groupedSummary = useMemo(() => {
    const totalGroups = filteredGroupedData.length;
    const groupsPassed = filteredGroupedData.filter(g => !g.hasFail).length;
    const groupsWithErrors = filteredGroupedData.filter(g => g.hasFail).length;
    const totalErrors = filteredGroupedData.reduce((sum, g) => sum + g.errorCount, 0);
    return { totalGroups, groupsPassed, groupsWithErrors, totalErrors };
  }, [filteredGroupedData]);

  const groupedFilterOptions = useMemo(() => ({
    rules: [...new Set(groupedData.map(g => g.ruleId))].sort(),
    serviceTiers: [...new Set(groupedData.map(g => g.firstRecord?.serviceTier).filter(Boolean))].sort() as string[],
    subServiceTiers: [...new Set(groupedData.map(g => g.firstRecord?.subServiceTier).filter(Boolean))].sort() as string[],
    startingPoints: [...new Set(groupedData.map(g => g.firstRecord?.serviceStartingPoint).filter(Boolean))].sort() as string[],
    offeringTypes: [...new Set(groupedData.map(g => g.firstRecord?.offeringType).filter(Boolean))].sort() as string[],
    countries: [...new Set(groupedData.map(g => g.firstRecord?.country).filter(Boolean))].sort() as string[],
  }), [groupedData]);

  // Missing Check Rules - records not covered by any released rule
  const missingRecords = useMemo(() => {
    const checkedKeys = new Set<string>();
    checkResults.forEach(cr => {
      cr.records.forEach(rec => {
        checkedKeys.add(`${rec.servicePN}|${rec.country}|${rec.term}|${rec.posOrApos}`);
      });
    });
    return displayData.filter(rec => {
      const key = `${rec.servicePN}|${rec.country}|${rec.term}|${rec.posOrApos}`;
      return !checkedKeys.has(key);
    });
  }, [checkResults, displayData]);

  const filteredMissingRecords = useMemo(() => {
    return missingRecords.filter(rec => {
      if (missingFilters.serviceTier !== 'all' && rec.serviceTier !== missingFilters.serviceTier) return false;
      if (missingFilters.subServiceTier !== 'all' && rec.subServiceTier !== missingFilters.subServiceTier) return false;
      if (missingFilters.startingPoint !== 'all' && rec.serviceStartingPoint !== missingFilters.startingPoint) return false;
      if (missingFilters.offeringType !== 'all' && rec.offeringType !== missingFilters.offeringType) return false;
      if (missingFilters.country !== 'all' && rec.country !== missingFilters.country) return false;
      if (missingFilters.posOrApos !== 'all' && rec.posOrApos !== missingFilters.posOrApos) return false;
      return true;
    });
  }, [missingRecords, missingFilters]);

  const missingFilterOptions = useMemo(() => ({
    serviceTiers: [...new Set(missingRecords.map(r => r.serviceTier).filter((v): v is string => !!v))].sort(),
    subServiceTiers: [...new Set(missingRecords.map(r => r.subServiceTier).filter((v): v is string => !!v))].sort(),
    startingPoints: [...new Set(missingRecords.map(r => r.serviceStartingPoint).filter((v): v is string => !!v))].sort(),
    offeringTypes: [...new Set(missingRecords.map(r => r.offeringType).filter((v): v is string => !!v))].sort(),
    countries: [...new Set(missingRecords.map(r => r.country).filter((v): v is string => !!v))].sort(),
    posOrApos: [...new Set(missingRecords.map(r => r.posOrApos).filter((v): v is 'POS' | 'APOS' => !!v))].sort(),
  }), [missingRecords]);

  // Grouped drill-down: Rule -> Group -> Results
  const groupedRuleGroups = useMemo(() => {
    if (!groupedDrillRule) return [];
    return filteredGroupedData.filter(g => g.ruleId === groupedDrillRule);
  }, [filteredGroupedData, groupedDrillRule]);

  const groupedGroupResults = useMemo(() => {
    if (!groupedDrillRule || !groupedDrillGroup) return [];
    return checkResults.filter(cr => cr.ruleId === groupedDrillRule && cr.groupKey === groupedDrillGroup);
  }, [checkResults, groupedDrillRule, groupedDrillGroup]);

  // Column width calculation for Details tab - V9 Style
  const detailsColumnDefs = useMemo(() => [
    { key: 'ruleId', label: 'Rule ID', minWidth: 80, maxWidth: 110 },
    { key: 'servicePN', label: 'Service PN', minWidth: 120, maxWidth: 160 },
    { key: 'serviceTier', label: 'Service Tier', minWidth: 130, maxWidth: 200 },
    { key: 'subServiceTier', label: 'Sub Tier', minWidth: 80, maxWidth: 130 },
    { key: 'term', label: 'Term', minWidth: 50, maxWidth: 70 },
    { key: 'country', label: 'Country', minWidth: 60, maxWidth: 80 },
    { key: 'offeringType', label: 'Offering Type', minWidth: 160, maxWidth: 260 },
    { key: 'lowCost', label: 'Low Cost', minWidth: 90, maxWidth: 120 },
    { key: 'highCost', label: 'High Cost', minWidth: 90, maxWidth: 120 },
    { key: 'status', label: 'Status', minWidth: 70, maxWidth: 90 },
    { key: 'validationError', label: 'Validation Errors', minWidth: 350, maxWidth: 600 },
    { key: 'groupKey', label: 'Group Key', minWidth: 150, maxWidth: 300 },
    { key: 'compare', label: 'Compare', minWidth: 110, maxWidth: 150 },
    { key: 'posOrApos', label: 'POS or APOS', minWidth: 90, maxWidth: 100 },
    { key: 'servicePNShortDescription', label: 'Service PN Desc', minWidth: 140, maxWidth: 220 },
    { key: 'salesMarketingLongDescription', label: 'Sales&Marketing Desc', minWidth: 180, maxWidth: 350 },
    { key: 'startingPoint', label: 'Starting Point', minWidth: 120, maxWidth: 200 },
    { key: 'ohName', label: 'OH Name', minWidth: 120, maxWidth: 200 },
    { key: 'typeOfService', label: 'Type of Service', minWidth: 120, maxWidth: 200 },
    { key: 'subTypeOfService', label: 'Sub Type of Service', minWidth: 120, maxWidth: 200 },
    { key: 'difference', label: 'Difference', minWidth: 90, maxWidth: 120 },
    { key: 'failReason', label: 'Fail Reason', minWidth: 180, maxWidth: 350 },
  ], []);

  const detailsColWidths = useAutoColumnWidths(filteredResults, detailsColumnDefs);

  // Pre-compute Details tab row data to avoid expensive per-render .find() operations
  const detailsRowData = useMemo(() => {
    return filteredResults.map((result) => {
      const getCompareValue = (r: SalesCostDisplayRecord) => {
        switch (result.compareFactor) {
          case 'POS or APOS': return r.posOrApos;
          case 'Service Tier': return r.serviceTier;
          case 'Sub Service Tier': return r.subServiceTier || '';
          case 'Starting Point': return r.serviceStartingPoint;
          case 'Offering Type': return r.offeringType;
          case 'Term': return r.term;
          case 'Country': return r.country;
          default: return '';
        }
      };
      const lowRecord = result.records.find(r => getCompareValue(r) === result.lowPriorityValue);
      const highRecord = result.records.find(r => getCompareValue(r) === result.highPriorityValue);
      const firstRecord = result.records[0];
      const isFail = result.status === 'FAIL';
      const ruleDesc = ruleDescriptionMap.get(result.ruleId) || result.ruleId;
      const validationError = isFail
        ? `${result.ruleId}${ruleDesc !== result.ruleId ? ` (${ruleDesc})` : ''}: ${result.highPriorityValue} cost ($${result.highPrioritySalesCost.toFixed(4)}) should be > ${result.lowPriorityValue} cost ($${result.lowPrioritySalesCost.toFixed(4)})`
        : '-';
      return { result, lowRecord, highRecord, firstRecord, isFail, ruleDesc, validationError };
    });
  }, [filteredResults, ruleDescriptionMap]);

  // Paginated details data
  const detailsTotalPages = Math.max(1, Math.ceil(detailsRowData.length / DETAILS_PAGE_SIZE));
  const paginatedDetails = useMemo(() => {
    const start = (detailsPage - 1) * DETAILS_PAGE_SIZE;
    return detailsRowData.slice(start, start + DETAILS_PAGE_SIZE);
  }, [detailsRowData, detailsPage]);

  // Reset details page when filters change
  useEffect(() => {
    setDetailsPage(1);
  }, [filters]);

  // Group results by rule for drill-down
  const resultsByRule = useMemo(() => {
    const grouped = new Map<string, CheckResult[]>();
    filteredResults.forEach(r => {
      if (!grouped.has(r.ruleId)) {
        grouped.set(r.ruleId, []);
      }
      grouped.get(r.ruleId)!.push(r);
    });
    return grouped;
  }, [filteredResults]);

  // Group results by groupKey for a specific rule
  const resultsByGroupKey = useMemo(() => {
    if (!selectedRuleId) return new Map<string, CheckResult[]>();
    const ruleResults = filteredResults.filter(r => r.ruleId === selectedRuleId);
    const grouped = new Map<string, CheckResult[]>();
    ruleResults.forEach(r => {
      if (!grouped.has(r.groupKey)) {
        grouped.set(r.groupKey, []);
      }
      grouped.get(r.groupKey)!.push(r);
    });
    return grouped;
  }, [filteredResults, selectedRuleId]);

  // Insights calculations
  const insights = useMemo(() => {
    if (checkResults.length === 0) return null;

    const passCount = checkResults.filter(r => r.status === 'PASS').length;
    const failCount = checkResults.filter(r => r.status === 'FAIL').length;
    const passRate = (passCount / checkResults.length) * 100;
    
    const byRule = uniqueRules.map(ruleId => {
      const ruleResults = checkResults.filter(r => r.ruleId === ruleId);
      const pass = ruleResults.filter(r => r.status === 'PASS').length;
      const fail = ruleResults.filter(r => r.status === 'FAIL').length;
      const avgDiff = ruleResults.length > 0 ? ruleResults.reduce((s, r) => s + r.difference, 0) / ruleResults.length : 0;
      const largestDiff = [...ruleResults].sort((a, b) => Math.abs(b.difference) - Math.abs(a.difference))[0];
      return { ruleId, total: ruleResults.length, pass, fail, passRate: (pass / ruleResults.length) * 100, avgDiff, largestDiff };
    });

    const byCompareFactor = uniqueCompareFactors.map(factor => {
      const factorResults = checkResults.filter(r => r.compareFactor === factor);
      const pass = factorResults.filter(r => r.status === 'PASS').length;
      const fail = factorResults.filter(r => r.status === 'FAIL').length;
      const descriptions: Record<string, string> = {
        'POS or APOS': 'Point of Service vs After Point of Service',
        'Service Tier': 'Service level tier comparison',
        'Sub Service Tier': 'Sub-tier classification comparison',
        'Starting Point': 'Service starting point comparison',
        'Offering Type': 'Type of offering comparison',
        'Term': 'Contract term comparison',
        'Country': 'Country-level comparison',
      };
      return { factor, description: descriptions[factor] || `${factor} comparison`, total: factorResults.length, pass, fail, passRate: (pass / factorResults.length) * 100 };
    });

    const uniqueGroupKeys = [...new Set(checkResults.map(r => r.groupKey))];
    const byGroup = uniqueGroupKeys.map(groupKey => {
      const groupResults = checkResults.filter(r => r.groupKey === groupKey);
      const pass = groupResults.filter(r => r.status === 'PASS').length;
      const fail = groupResults.filter(r => r.status === 'FAIL').length;
      return { groupKey, total: groupResults.length, pass, fail, passRate: (pass / groupResults.length) * 100 };
    }).sort((a, b) => b.fail - a.fail);

    const avgPassDifference = checkResults
      .filter(r => r.status === 'PASS')
      .reduce((sum, r) => sum + r.difference, 0) / (passCount || 1);
    
    const avgFailDifference = checkResults
      .filter(r => r.status === 'FAIL')
      .reduce((sum, r) => sum + r.difference, 0) / (failCount || 1);

    const largestPass = checkResults
      .filter(r => r.status === 'PASS')
      .sort((a, b) => b.difference - a.difference)[0];
    
    const largestFail = checkResults
      .filter(r => r.status === 'FAIL')
      .sort((a, b) => a.difference - b.difference)[0];

    // Records hit vs not hit by any check
    const checkedRecordKeys = new Set<string>();
    checkResults.forEach(r => {
      r.records.forEach(rec => {
        checkedRecordKeys.add(`${rec.servicePN}|${rec.country}|${rec.term}|${rec.posOrApos}`);
      });
    });
    
    // Use all displayData records to determine coverage
    const allRecordKeys = new Set<string>();
    displayData.forEach(rec => {
      allRecordKeys.add(`${rec.servicePN}|${rec.country}|${rec.term}|${rec.posOrApos}`);
    });
    
    const performedCheckCount = checkedRecordKeys.size;
    const missingCheckCount = displayData.length > 0 ? displayData.length - performedCheckCount : 0;

    // ===== Record-based summaries =====
    // 1. Sales Cost Records Summary
    const totalSalesCostAmount = displayData.reduce((sum, r) => sum + r.salesCost, 0);
    const avgSalesCost = displayData.length > 0 ? totalSalesCostAmount / displayData.length : 0;
    const posCount = displayData.filter(r => r.posOrApos === 'POS').length;
    const aposCount = displayData.filter(r => r.posOrApos === 'APOS').length;

    // 2. Validation Status by actual records
    // For each record, track if it was checked and the outcome
    const recordValidationMap = new Map<string, { checked: boolean; passedAll: boolean; failedAny: boolean }>();
    displayData.forEach(rec => {
      const key = `${rec.servicePN}|${rec.country}|${rec.term}|${rec.posOrApos}`;
      recordValidationMap.set(key, { checked: false, passedAll: true, failedAny: false });
    });
    checkResults.forEach(cr => {
      cr.records.forEach(rec => {
        const key = `${rec.servicePN}|${rec.country}|${rec.term}|${rec.posOrApos}`;
        const existing = recordValidationMap.get(key);
        if (existing) {
          existing.checked = true;
          if (cr.status === 'FAIL') {
            existing.failedAny = true;
            existing.passedAll = false;
          }
        }
      });
    });
    const recordValidationSummary = {
      totalRecords: displayData.length,
      checkedRecords: 0,
      passedRecords: 0,
      failedRecords: 0,
      uncheckedRecords: 0,
    };
    recordValidationMap.forEach(v => {
      if (!v.checked) {
        recordValidationSummary.uncheckedRecords++;
      } else if (v.failedAny) {
        recordValidationSummary.failedRecords++;
      } else if (v.passedAll) {
        recordValidationSummary.passedRecords++;
      }
      if (v.checked) recordValidationSummary.checkedRecords++;
    });

    // 3. Missing Check Rules Summary - records not covered by any released rule
    // Group unchecked records by key dimensions to show patterns
    const missingByCountry = new Map<string, number>();
    const missingByServiceTier = new Map<string, number>();
    recordValidationMap.forEach((v, key) => {
      if (!v.checked) {
        // Find the record to get its attributes
        const rec = displayData.find(d => `${d.servicePN}|${d.country}|${d.term}|${d.posOrApos}` === key);
        if (rec) {
          missingByCountry.set(rec.country, (missingByCountry.get(rec.country) || 0) + 1);
          missingByServiceTier.set(rec.serviceTier, (missingByServiceTier.get(rec.serviceTier) || 0) + 1);
        }
      }
    });
    const missingCheckSummary = {
      totalMissing: missingCheckCount,
      byCountry: [...missingByCountry.entries()].map(([country, count]) => ({ country, count })).sort((a, b) => b.count - a.count),
      byServiceTier: [...missingByServiceTier.entries()].map(([tier, count]) => ({ serviceTier: tier, count })).sort((a, b) => b.count - a.count),
    };

    // New breakdown insights
    // By Country - aggregate from records
    const countryMap = new Map<string, { pass: number; fail: number; total: number }>();
    checkResults.forEach(r => {
      r.records.forEach(rec => {
        const existing = countryMap.get(rec.country) || { pass: 0, fail: 0, total: 0 };
        if (r.status === 'PASS') existing.pass++;
        else existing.fail++;
        existing.total++;
        countryMap.set(rec.country, existing);
      });
    });
    const byCountry = [...countryMap.entries()].map(([country, data]) => ({
      country,
      ...data,
      passRate: data.total > 0 ? (data.pass / data.total) * 100 : 0
    })).sort((a, b) => b.total - a.total);

    // By POS or APOS
    const posMap = new Map<string, { pass: number; fail: number; total: number }>();
    checkResults.forEach(r => {
      r.records.forEach(rec => {
        const existing = posMap.get(rec.posOrApos) || { pass: 0, fail: 0, total: 0 };
        if (r.status === 'PASS') existing.pass++;
        else existing.fail++;
        existing.total++;
        posMap.set(rec.posOrApos, existing);
      });
    });
    const byPosOrApos = [...posMap.entries()].map(([pos, data]) => ({
      posOrApos: pos,
      ...data,
      passRate: data.total > 0 ? (data.pass / data.total) * 100 : 0
    })).sort((a, b) => b.total - a.total);

    // By Term
    const termMap = new Map<string, { pass: number; fail: number; total: number }>();
    checkResults.forEach(r => {
      r.records.forEach(rec => {
        const existing = termMap.get(rec.term) || { pass: 0, fail: 0, total: 0 };
        if (r.status === 'PASS') existing.pass++;
        else existing.fail++;
        existing.total++;
        termMap.set(rec.term, existing);
      });
    });
    const byTerm = [...termMap.entries()].map(([term, data]) => ({
      term,
      ...data,
      passRate: data.total > 0 ? (data.pass / data.total) * 100 : 0
    })).sort((a, b) => b.total - a.total);

    // By Service Tier
    const tierMap = new Map<string, { pass: number; fail: number; total: number }>();
    checkResults.forEach(r => {
      r.records.forEach(rec => {
        const existing = tierMap.get(rec.serviceTier) || { pass: 0, fail: 0, total: 0 };
        if (r.status === 'PASS') existing.pass++;
        else existing.fail++;
        existing.total++;
        tierMap.set(rec.serviceTier, existing);
      });
    });
    const byServiceTier = [...tierMap.entries()].map(([tier, data]) => ({
      serviceTier: tier,
      ...data,
      passRate: data.total > 0 ? (data.pass / data.total) * 100 : 0
    })).sort((a, b) => b.total - a.total);

    // By Offering Type
    const offeringMap = new Map<string, { pass: number; fail: number; total: number }>();
    checkResults.forEach(r => {
      r.records.forEach(rec => {
        const existing = offeringMap.get(rec.offeringType) || { pass: 0, fail: 0, total: 0 };
        if (r.status === 'PASS') existing.pass++;
        else existing.fail++;
        existing.total++;
        offeringMap.set(rec.offeringType, existing);
      });
    });
    const byOfferingType = [...offeringMap.entries()].map(([offering, data]) => ({
      offeringType: offering,
      ...data,
      passRate: data.total > 0 ? (data.pass / data.total) * 100 : 0
    })).sort((a, b) => b.total - a.total);

    return {
      total: checkResults.length,
      passCount,
      failCount,
      passRate,
      byRule,
      byCompareFactor,
      byGroup,
      avgPassDifference,
      avgFailDifference,
      largestPass,
      largestFail,
      byCountry,
      byPosOrApos,
      byTerm,
      byServiceTier,
      byOfferingType,
      performedCheckCount,
      missingCheckCount,
      // Record-based summaries
      recordSummary: {
        totalRecords: displayData.length,
        totalSalesCostAmount,
        avgSalesCost,
        posCount,
        aposCount,
      },
      recordValidationSummary,
      missingCheckSummary,
    };
  }, [checkResults, uniqueRules, uniqueCompareFactors, displayData]);

  const handleExecute = async () => {
    if (rules.length === 0 || displayData.length === 0) {
      alert('Please ensure you have rules and data loaded before executing checks.');
      return;
    }

    setIsExecuting(true);
    setProgress(0);
    setDrillView('rules');
    setSelectedRuleId(null);
    setSelectedGroupKey(null);
    setSelectedResult(null);

    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) {
          clearInterval(interval);
          return 90;
        }
        return prev + 10;
      });
    }, 200);

    setTimeout(() => {
      executeChecks();
      setProgress(100);
      setTimeout(() => {
        setIsExecuting(false);
        setProgress(0);
        setActiveTab('dashboard');
      }, 500);
    }, 2000);
  };

  const handleExport = () => {
    const exportData = filteredResults.map(r => {
      const firstRecord = r.records[0];
      return {
        'Rule ID': r.ruleId,
        'Rule Description': ruleDescriptionMap.get(r.ruleId) || '',
        'Group Key': r.groupKey,
        'Compare Factor': r.compareFactor,
        'Low Priority Value': r.lowPriorityValue,
        'High Priority Value': r.highPriorityValue,
        'Low Priority Sales Cost': r.lowPrioritySalesCost,
        'High Priority Sales Cost': r.highPrioritySalesCost,
        'Difference': r.difference,
        'Status': r.status,
        'Fail Reason': r.failReason || '',
        'Service PN': firstRecord?.servicePN || '',
        'Service Tier': firstRecord?.serviceTier || '',
        'Sub Service Tier': firstRecord?.subServiceTier || '',
        'Term': firstRecord?.term || '',
        'POS/APOS': firstRecord?.posOrApos || '',
        'Starting Point': firstRecord?.serviceStartingPoint || '',
        'Offering Type': firstRecord?.offeringType || '',
        'Country': firstRecord?.country || '',
        'OH Name': firstRecord?.ohName || '',
        'Type of Service': firstRecord?.typeOfService || '',
        'Sub Type of Service': firstRecord?.subTypeOfService || '',
      };
    });

    const ws = XLSX.utils.json_to_sheet(exportData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Check Results');
    XLSX.writeFile(wb, `check-results-${new Date().toISOString().split('T')[0]}.xlsx`);
  };

  const clearFilters = () => {
    setFilters({
      ruleId: 'all',
      status: 'all',
      compareFactor: 'all',
      groupKey: '',
      minDifference: '',
      maxDifference: '',
      posOrApos: 'all',
      country: 'all',
      serviceTier: 'all',
      subServiceTier: 'all',
      offeringType: 'all',
      term: 'all',
      startingPoint: 'all'
    });
  };

  const navigateToRuleGroups = (ruleId: string) => {
    setSelectedRuleId(ruleId);
    setDrillView('groups');
  };

  const navigateToGroupRecords = (groupKey: string) => {
    setSelectedGroupKey(groupKey);
    setDrillView('records');
  };

  const navigateToDetail = (result: CheckResult) => {
    setSelectedResult(result);
    setDrillView('detail');
  };

  const navigateBack = () => {
    if (drillView === 'detail') {
      setDrillView('records');
      setSelectedResult(null);
    } else if (drillView === 'records') {
      setDrillView('groups');
      setSelectedGroupKey(null);
    } else if (drillView === 'groups') {
      setDrillView('rules');
      setSelectedRuleId(null);
    }
  };

  // Dashboard section ordering with drag-and-drop
  const DASHBOARD_SECTIONS = [
    'summary-cards',
    'sales-cost-records',
    'validation-status-records',
    'missing-check-rules',
    'errors-by-rule',
    'check-rule-summary',
    'compare-factors',
    'country-breakdown',
    'pos-apos-tier-breakdown',
  ] as const;
  type DashboardSection = typeof DASHBOARD_SECTIONS[number];

  const [dashboardOrder, setDashboardOrder] = useState<DashboardSection[]>(() => {
    const saved = localStorage.getItem('dashboardSectionOrder');
    if (saved) {
      try {
        const parsed = JSON.parse(saved) as DashboardSection[];
        // Validate all sections exist
        const valid = parsed.filter(s => DASHBOARD_SECTIONS.includes(s));
        const missing = DASHBOARD_SECTIONS.filter(s => !parsed.includes(s));
        return [...valid, ...missing];
      } catch { /* fallback */ }
    }
    return [...DASHBOARD_SECTIONS];
  });

  const [dragOverSection, setDragOverSection] = useState<string | null>(null);

  useEffect(() => {
    localStorage.setItem('dashboardSectionOrder', JSON.stringify(dashboardOrder));
  }, [dashboardOrder]);

  const handleDragStart = (e: React.DragEvent, section: DashboardSection) => {
    e.dataTransfer.setData('text/plain', section);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent, section: DashboardSection) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverSection(section);
  };

  const handleDragLeave = () => {
    setDragOverSection(null);
  };

  const handleDrop = (e: React.DragEvent, targetSection: DashboardSection) => {
    e.preventDefault();
    const sourceSection = e.dataTransfer.getData('text/plain') as DashboardSection;
    setDragOverSection(null);
    if (sourceSection === targetSection) return;
    if (!DASHBOARD_SECTIONS.includes(sourceSection)) return;

    setDashboardOrder(prev => {
      const newOrder = [...prev];
      const sourceIdx = newOrder.indexOf(sourceSection);
      const targetIdx = newOrder.indexOf(targetSection);
      if (sourceIdx === -1 || targetIdx === -1) return prev;
      newOrder.splice(sourceIdx, 1);
      newOrder.splice(targetIdx, 0, sourceSection);
      return newOrder;
    });
  };

  const resetDashboardOrder = () => {
    setDashboardOrder([
      'summary-cards',
      'sales-cost-records',
      'validation-status-records',
      'missing-check-rules',
      'errors-by-rule',
      'check-rule-summary',
      'compare-factors',
      'country-breakdown',
      'pos-apos-tier-breakdown',
    ]);
  };

  const activeFilterCount = Object.values(filters).filter(v => v !== 'all' && v !== '').length;

  // Filtered drill-down data
  const filteredResultsByRule = useMemo(() => {
    const filtered = new Map<string, CheckResult[]>();
    resultsByRule.forEach((results, ruleId) => {
      let filteredResults = results;
      if (drillFilters.status !== 'all') {
        filteredResults = filteredResults.filter(r => r.status === drillFilters.status);
      }
      if (drillFilters.search) {
        const search = drillFilters.search.toLowerCase();
        filteredResults = filteredResults.filter(r =>
          r.groupKey.toLowerCase().includes(search) ||
          r.lowPriorityValue.toLowerCase().includes(search) ||
          r.highPriorityValue.toLowerCase().includes(search)
        );
      }
      if (filteredResults.length > 0) {
        filtered.set(ruleId, filteredResults);
      }
    });
    return filtered;
  }, [resultsByRule, drillFilters]);

  const filteredResultsByGroupKey = useMemo(() => {
    const filtered = new Map<string, CheckResult[]>();
    resultsByGroupKey.forEach((results, groupKey) => {
      let filteredResults = results;
      if (drillFilters.status !== 'all') {
        filteredResults = filteredResults.filter(r => r.status === drillFilters.status);
      }
      if (drillFilters.search) {
        const search = drillFilters.search.toLowerCase();
        filteredResults = filteredResults.filter(r =>
          r.lowPriorityValue.toLowerCase().includes(search) ||
          r.highPriorityValue.toLowerCase().includes(search) ||
          r.compareFactor.toLowerCase().includes(search)
        );
      }
      if (filteredResults.length > 0) {
        filtered.set(groupKey, filteredResults);
      }
    });
    return filtered;
  }, [resultsByGroupKey, drillFilters]);

  // Column width calculation for Drill Down detail table
  const drillDownColumns = useMemo(() => [
    { key: 'servicePN', label: 'Service PN', minWidth: 120, maxWidth: 180 },
    { key: 'servicePNShortDescription', label: 'Service PN Desc', minWidth: 140, maxWidth: 220 },
    { key: 'salesMarketingLongDescription', label: 'Sales&Marketing Desc', minWidth: 180, maxWidth: 350 },
    { key: 'posOrApos', label: 'POS or APOS', minWidth: 90, maxWidth: 100 },
    { key: 'serviceStartingPoint', label: 'Starting Point', minWidth: 120, maxWidth: 200 },
    { key: 'term', label: 'Term', minWidth: 60, maxWidth: 80 },
    { key: 'serviceTier', label: 'Service Tier', minWidth: 120, maxWidth: 200 },
    { key: 'subServiceTier', label: 'Sub Service Tier', minWidth: 120, maxWidth: 200 },
    { key: 'ohCode', label: 'OH Code', minWidth: 100, maxWidth: 140 },
    { key: 'ohName', label: 'OH Name', minWidth: 120, maxWidth: 200 },
    { key: 'typeOfService', label: 'Type of Service', minWidth: 120, maxWidth: 200 },
    { key: 'subTypeOfService', label: 'Sub Type of Service', minWidth: 120, maxWidth: 200 },
    { key: 'offeringType', label: 'Offering Type', minWidth: 130, maxWidth: 220 },
    { key: 'country', label: 'Country', minWidth: 70, maxWidth: 90 },
    { key: 'salesCost', label: 'Sales Cost', minWidth: 110, maxWidth: 140 },
  ], []);

  const drillDownColWidths = useAutoColumnWidths(
    selectedResult?.records || [],
    drillDownColumns
  );

  const filteredGroupResults = useMemo(() => {
    const results = resultsByGroupKey.get(selectedGroupKey || '') || [];
    let filtered = results;
    if (drillFilters.status !== 'all') {
      filtered = filtered.filter(r => r.status === drillFilters.status);
    }
    if (drillFilters.search) {
      const search = drillFilters.search.toLowerCase();
      filtered = filtered.filter(r =>
        r.lowPriorityValue.toLowerCase().includes(search) ||
        r.highPriorityValue.toLowerCase().includes(search)
      );
    }
    return filtered;
  }, [resultsByGroupKey, selectedGroupKey, drillFilters]);

  const clearDrillFilters = () => {
    setDrillFilters({ status: 'all', search: '' });
  };

  // Get released rules count for display
  const releasedRulesCount = rules.filter(r => r.status === 'Released').length;

  return (
    <TooltipProvider>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Execute Cross Check</h2>
            <p className="text-gray-500 mt-1">
              Run sales cost validation checks using <span className="font-medium text-green-600">{releasedRulesCount} Released rules</span>
            </p>
          </div>
          <Button 
            onClick={handleExecute}
            disabled={isExecuting || releasedRulesCount === 0 || displayData.length === 0}
            className="bg-green-600 hover:bg-green-700"
          >
            {isExecuting ? (
              <>
                <RotateCcw className="w-4 h-4 mr-2 animate-spin" />
                Executing...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Execute Checks
              </>
            )}
          </Button>
        </div>

        {/* Progress */}
        {isExecuting && (
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="p-6">
              <p className="text-sm text-blue-700 mb-2">Executing cross-checks with {releasedRulesCount} released rules...</p>
              <Progress value={progress} className="h-2" />
              <p className="text-xs text-blue-600 mt-2">{progress}% complete</p>
            </CardContent>
          </Card>
        )}

        {/* Pre-check Status */}
        {!checkSummary && !isExecuting && (
          <Card className="bg-yellow-50 border-yellow-200">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <AlertTriangle className="w-5 h-5 text-yellow-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-yellow-900">Ready to Execute</h3>
                  <p className="text-sm text-yellow-700 mt-1">
                    Only <span className="font-medium">{releasedRulesCount} Released rules</span> will be used for validation.
                  </p>
                  <div className="flex gap-6 mt-3">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-yellow-900">{releasedRulesCount}</p>
                      <p className="text-xs text-yellow-700">Released Rules</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-gray-400">{rules.filter(r => r.status !== 'Released').length}</p>
                      <p className="text-xs text-gray-500">Draft/Retired (excluded)</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-yellow-900">{displayData.length}</p>
                      <p className="text-xs text-yellow-700">Records</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results Dashboard */}
        {checkSummary && insights && (
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <div className="flex items-center gap-4 flex-wrap">
              <TabsList className="grid grid-cols-4 w-full max-w-4xl h-auto">
                <TabsTrigger value="dashboard" className="text-[11px] px-2 py-2 h-auto">Dashboard</TabsTrigger>
                <TabsTrigger value="grouped" className="text-[11px] px-2 py-2 h-auto">Grouped Check Results</TabsTrigger>
                <TabsTrigger value="missing" className="text-[11px] px-2 py-2 h-auto">Missing Rules</TabsTrigger>
                <TabsTrigger value="drilldown" className="text-[11px] px-2 py-2 h-auto">Check Results Drill Down</TabsTrigger>
              </TabsList>
              <Button onClick={handleExport} variant="outline" size="sm" className="shrink-0 gap-1.5 h-9">
                <Download className="w-4 h-4" />
                Export Excel
              </Button>
            </div>

            {/* Dashboard Tab - V9 Style with Drag-to-Reorder */}
            <TabsContent value="dashboard" className="space-y-4">
              {/* Drag hint */}
              <div className="flex items-center justify-between">
                <p className="text-xs text-gray-400 flex items-center gap-1">
                  <GripVertical className="w-3 h-3" />
                  Drag sections by the handle to reorder the dashboard
                </p>
                <Button variant="ghost" size="sm" onClick={resetDashboardOrder} className="text-xs text-gray-400 hover:text-gray-600">
                  Reset Layout
                </Button>
              </div>

              {dashboardOrder.map((sectionId) => {
                const isDragOver = dragOverSection === sectionId;
                const dragClass = isDragOver ? 'ring-2 ring-blue-400 ring-offset-2 bg-blue-50/30' : '';

                switch (sectionId) {
                  // ===== 1. Summary Cards Row =====
                  case 'summary-cards':
                    return (
                      <div
                        key={sectionId}
                        draggable
                        onDragStart={(e) => handleDragStart(e, sectionId)}
                        onDragOver={(e) => handleDragOver(e, sectionId)}
                        onDragLeave={handleDragLeave}
                        onDrop={(e) => handleDrop(e, sectionId)}
                        className={`rounded-lg transition-all ${dragClass}`}
                      >
                        <div className="flex items-center gap-1 mb-2 px-1">
                          <GripVertical className="w-4 h-4 text-gray-300 cursor-grab active:cursor-grabbing" />
                          <span className="text-[10px] text-gray-400 uppercase tracking-wider">Summary Overview</span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <Card className="border shadow-sm">
                            <CardContent className="p-5">
                              <div className="flex items-start justify-between">
                                <div>
                                  <p className="text-sm text-gray-500 font-medium">Total Records</p>
                                  <p className="text-3xl font-bold text-gray-900 mt-2">{insights.total.toLocaleString()}</p>
                                  <p className="text-xs text-gray-400 mt-1">Across {insights.byCountry.length} countries</p>
                                </div>
                                <div className="w-9 h-9 bg-blue-50 rounded-lg flex items-center justify-center">
                                  <FileText className="w-4 h-4 text-blue-500" />
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                          <Card className="border shadow-sm">
                            <CardContent className="p-5">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <p className="text-sm text-gray-500 font-medium">Validation Status</p>
                                  <div className="flex items-center gap-2 mt-2">
                                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-green-100 text-green-700">
                                      <CheckCircle className="w-3 h-3" />{insights.passCount}
                                    </span>
                                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-red-100 text-red-700">
                                      <XCircle className="w-3 h-3" />{insights.failCount}
                                    </span>
                                  </div>
                                  <p className="text-xs text-gray-400 mt-2">{insights.passRate.toFixed(1)}% validation rate</p>
                                </div>
                                <div className="w-9 h-9 bg-purple-50 rounded-lg flex items-center justify-center">
                                  <BarChart3 className="w-4 h-4 text-purple-500" />
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                          <Card className="border shadow-sm">
                            <CardContent className="p-5">
                              <div className="flex items-start justify-between">
                                <div>
                                  <p className="text-sm text-gray-500 font-medium">Check Rules</p>
                                  <p className="text-3xl font-bold text-gray-900 mt-2">{releasedRulesCount}</p>
                                  <p className="text-xs text-gray-400 mt-1">Active validation rules</p>
                                </div>
                                <div className="w-9 h-9 bg-orange-50 rounded-lg flex items-center justify-center">
                                  <Layers className="w-4 h-4 text-orange-500" />
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </div>
                      </div>
                    );

                  // ===== 2. Sales Cost Records Summary (NEW) =====
                  case 'sales-cost-records':
                    return (
                      <div
                        key={sectionId}
                        draggable
                        onDragStart={(e) => handleDragStart(e, sectionId)}
                        onDragOver={(e) => handleDragOver(e, sectionId)}
                        onDragLeave={handleDragLeave}
                        onDrop={(e) => handleDrop(e, sectionId)}
                        className={`rounded-lg transition-all ${dragClass}`}
                      >
                        <div className="flex items-center gap-1 mb-2 px-1">
                          <GripVertical className="w-4 h-4 text-gray-300 cursor-grab active:cursor-grabbing" />
                          <span className="text-[10px] text-gray-400 uppercase tracking-wider">Sales Cost Records Summary</span>
                        </div>
                        <Card className="border shadow-sm">
                          <CardContent className="p-5">
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                              <div className="text-center p-3 bg-blue-50/50 rounded-lg">
                                <p className="text-xs text-gray-500">Total Records</p>
                                <p className="text-2xl font-bold text-gray-900 mt-1">{insights.recordSummary.totalRecords.toLocaleString()}</p>
                              </div>
                              <div className="text-center p-3 bg-green-50/50 rounded-lg">
                                <p className="text-xs text-gray-500">POS Records</p>
                                <p className="text-2xl font-bold text-gray-900 mt-1">{insights.recordSummary.posCount.toLocaleString()}</p>
                              </div>
                              <div className="text-center p-3 bg-purple-50/50 rounded-lg">
                                <p className="text-xs text-gray-500">APOS Records</p>
                                <p className="text-2xl font-bold text-gray-900 mt-1">{insights.recordSummary.aposCount.toLocaleString()}</p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    );

                  // ===== 3. Validation Status by Records (NEW) =====
                  case 'validation-status-records':
                    return (
                      <div
                        key={sectionId}
                        draggable
                        onDragStart={(e) => handleDragStart(e, sectionId)}
                        onDragOver={(e) => handleDragOver(e, sectionId)}
                        onDragLeave={handleDragLeave}
                        onDrop={(e) => handleDrop(e, sectionId)}
                        className={`rounded-lg transition-all ${dragClass}`}
                      >
                        <div className="flex items-center gap-1 mb-2 px-1">
                          <GripVertical className="w-4 h-4 text-gray-300 cursor-grab active:cursor-grabbing" />
                          <span className="text-[10px] text-gray-400 uppercase tracking-wider">Validation Status (by Records)</span>
                        </div>
                        <Card className="border shadow-sm">
                          <CardContent className="p-5">
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                              <div className="text-center p-3 bg-gray-50 rounded-lg">
                                <p className="text-xs text-gray-500">Total Records</p>
                                <p className="text-2xl font-bold text-gray-900 mt-1">{insights.recordValidationSummary.totalRecords.toLocaleString()}</p>
                              </div>
                              <div className="text-center p-3 bg-green-50 rounded-lg">
                                <p className="text-xs text-green-600">Passed All Checks</p>
                                <p className="text-2xl font-bold text-green-700 mt-1">{insights.recordValidationSummary.passedRecords.toLocaleString()}</p>
                                <p className="text-[10px] text-green-500 mt-0.5">
                                  {insights.recordValidationSummary.totalRecords > 0
                                    ? ((insights.recordValidationSummary.passedRecords / insights.recordValidationSummary.totalRecords) * 100).toFixed(1)
                                    : 0}%
                                </p>
                              </div>
                              <div className="text-center p-3 bg-red-50 rounded-lg">
                                <p className="text-xs text-red-500">Failed Any Check</p>
                                <p className="text-2xl font-bold text-red-600 mt-1">{insights.recordValidationSummary.failedRecords.toLocaleString()}</p>
                                <p className="text-[10px] text-red-400 mt-0.5">
                                  {insights.recordValidationSummary.totalRecords > 0
                                    ? ((insights.recordValidationSummary.failedRecords / insights.recordValidationSummary.totalRecords) * 100).toFixed(1)
                                    : 0}%
                                </p>
                              </div>
                              <div className="text-center p-3 bg-orange-50 rounded-lg">
                                <p className="text-xs text-orange-500">Unchecked</p>
                                <p className="text-2xl font-bold text-orange-600 mt-1">{insights.recordValidationSummary.uncheckedRecords.toLocaleString()}</p>
                                <p className="text-[10px] text-orange-400 mt-0.5">
                                  {insights.recordValidationSummary.totalRecords > 0
                                    ? ((insights.recordValidationSummary.uncheckedRecords / insights.recordValidationSummary.totalRecords) * 100).toFixed(1)
                                    : 0}%
                                </p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    );

                  // ===== 4. Missing Check Rules Summary (NEW) =====
                  case 'missing-check-rules':
                    return (
                      <div
                        key={sectionId}
                        draggable
                        onDragStart={(e) => handleDragStart(e, sectionId)}
                        onDragOver={(e) => handleDragOver(e, sectionId)}
                        onDragLeave={handleDragLeave}
                        onDrop={(e) => handleDrop(e, sectionId)}
                        className={`rounded-lg transition-all ${dragClass}`}
                      >
                        <div className="flex items-center gap-1 mb-2 px-1">
                          <GripVertical className="w-4 h-4 text-gray-300 cursor-grab active:cursor-grabbing" />
                          <span className="text-[10px] text-gray-400 uppercase tracking-wider">Missing Check Rules Summary</span>
                        </div>
                        <Card className="border shadow-sm">
                          <CardContent className="p-5">
                            <div className="mb-4 p-3 bg-orange-50 rounded-lg border border-orange-100">
                              <p className="text-xs text-orange-600 font-medium">
                                {insights.missingCheckSummary.totalMissing.toLocaleString()} records are not covered by any released check rule
                                {insights.recordValidationSummary.totalRecords > 0 && (
                                  <span className="text-orange-400 ml-1">
                                    ({((insights.missingCheckSummary.totalMissing / insights.recordValidationSummary.totalRecords) * 100).toFixed(1)}% of total)
                                  </span>
                                )}
                              </p>
                            </div>
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                              <div>
                                <p className="text-xs font-medium text-gray-500 mb-2">Missing by Country</p>
                                <ScrollArea className="h-[200px]">
                                  <div className="space-y-2">
                                    {insights.missingCheckSummary.byCountry.map((item) => (
                                      <div key={item.country} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                                        <span className="text-xs font-medium text-gray-600">{item.country}</span>
                                        <span className="text-xs text-red-600 font-semibold">{item.count} records</span>
                                      </div>
                                    ))}
                                    {insights.missingCheckSummary.byCountry.length === 0 && (
                                      <p className="text-xs text-gray-400 text-center py-4">All records covered</p>
                                    )}
                                  </div>
                                </ScrollArea>
                              </div>
                              <div>
                                <p className="text-xs font-medium text-gray-500 mb-2">Missing by Service Tier</p>
                                <ScrollArea className="h-[200px]">
                                  <div className="space-y-2">
                                    {insights.missingCheckSummary.byServiceTier.map((item) => (
                                      <div key={item.serviceTier} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                                        <span className="text-xs font-medium text-gray-600">{item.serviceTier}</span>
                                        <span className="text-xs text-red-600 font-semibold">{item.count} records</span>
                                      </div>
                                    ))}
                                    {insights.missingCheckSummary.byServiceTier.length === 0 && (
                                      <p className="text-xs text-gray-400 text-center py-4">All records covered</p>
                                    )}
                                  </div>
                                </ScrollArea>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    );

                  // ===== 5. Errors by Check Rule (integrated with By Rule data) =====
                  case 'errors-by-rule':
                    return (
                      <div
                        key={sectionId}
                        draggable
                        onDragStart={(e) => handleDragStart(e, sectionId)}
                        onDragOver={(e) => handleDragOver(e, sectionId)}
                        onDragLeave={handleDragLeave}
                        onDrop={(e) => handleDrop(e, sectionId)}
                        className={`rounded-lg transition-all ${dragClass}`}
                      >
                        <div className="flex items-center gap-1 mb-2 px-1">
                          <GripVertical className="w-4 h-4 text-gray-300 cursor-grab active:cursor-grabbing" />
                          <span className="text-[10px] text-gray-400 uppercase tracking-wider">Errors by Check Rule</span>
                        </div>
                        <Card className="border shadow-sm">
                          <CardHeader className="pb-3">
                            <CardTitle className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                              <AlertTriangle className="w-4 h-4 text-red-500" />
                              Errors by Check Rule
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                              {insights.byRule.map((item) => {
                                const hasErrors = item.fail > 0;
                                const ruleDesc = ruleDescriptionMap.get(item.ruleId) || '';
                                return (
                                  <div key={item.ruleId} className={`rounded-lg p-4 border ${hasErrors ? 'bg-red-50/50 border-red-100' : 'bg-green-50/50 border-green-100'}`}>
                                    <div className="flex items-start justify-between mb-2">
                                      <div>
                                        <p className={`text-sm font-semibold ${hasErrors ? 'text-red-700' : 'text-green-700'}`}>{item.ruleId}</p>
                                        {ruleDesc && <p className="text-[10px] text-gray-400 mt-0.5">{ruleDesc}</p>}
                                      </div>
                                      <span className={`text-2xl font-bold ${hasErrors ? 'text-red-600' : 'text-green-600'}`}>{item.fail}</span>
                                    </div>
                                    <div className="flex items-center gap-3 mt-3 pt-2 border-t border-gray-200/50">
                                      <div className="text-center flex-1">
                                        <p className="text-[10px] text-gray-400">Total</p>
                                        <p className="text-sm font-semibold text-gray-700">{item.total}</p>
                                      </div>
                                      <div className="text-center flex-1">
                                        <p className="text-[10px] text-green-500">Pass</p>
                                        <p className="text-sm font-semibold text-green-600">{item.pass}</p>
                                      </div>
                                      <div className="text-center flex-1">
                                        <p className="text-[10px] text-red-500">Fail</p>
                                        <p className="text-sm font-semibold text-red-600">{item.fail}</p>
                                      </div>
                                      <div className="text-center flex-1">
                                        <p className="text-[10px] text-gray-400">Avg Diff</p>
                                        <p className="text-sm font-semibold text-gray-700">{item.avgDiff.toFixed(2)}</p>
                                      </div>
                                    </div>
                                    {item.largestDiff && (
                                      <div className="mt-2 pt-2 border-t border-gray-200/50">
                                        <p className="text-[10px] text-gray-400">
                                          Largest diff: <span className={item.largestDiff.difference >= 0 ? 'text-green-600' : 'text-red-600'}>
                                            {item.largestDiff.difference >= 0 ? '+' : ''}{item.largestDiff.difference.toFixed(4)}
                                          </span> ({item.largestDiff.lowPriorityValue} vs {item.largestDiff.highPriorityValue})
                                        </p>
                                      </div>
                                    )}
                                  </div>
                                );
                              })}
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    );

                  // ===== 6. Check Rule Summary (from By Rule tab) =====
                  case 'check-rule-summary':
                    return (
                      <div
                        key={sectionId}
                        draggable
                        onDragStart={(e) => handleDragStart(e, sectionId)}
                        onDragOver={(e) => handleDragOver(e, sectionId)}
                        onDragLeave={handleDragLeave}
                        onDrop={(e) => handleDrop(e, sectionId)}
                        className={`rounded-lg transition-all ${dragClass}`}
                      >
                        <div className="flex items-center gap-1 mb-2 px-1">
                          <GripVertical className="w-4 h-4 text-gray-300 cursor-grab active:cursor-grabbing" />
                          <span className="text-[10px] text-gray-400 uppercase tracking-wider">Check Rule Summary</span>
                        </div>
                        <Card className="border shadow-sm">
                          <CardHeader className="pb-3">
                            <CardTitle className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                              <Layers className="w-4 h-4 text-blue-500" />
                              Check Rule Summary
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="overflow-auto border rounded-md" style={{ maxHeight: '400px' }}>
                              <Table>
                                <TableHeader className="sticky top-0 z-10 bg-gray-50">
                                  <TableRow className="bg-gray-50">
                                    <TableHead className="text-xs font-medium text-gray-500">Rule ID</TableHead>
                                    <TableHead className="text-xs font-medium text-gray-500">Description</TableHead>
                                    <TableHead className="text-xs font-medium text-gray-500">Compare Factor</TableHead>
                                    <TableHead className="text-xs font-medium text-gray-500 text-center">Total</TableHead>
                                    <TableHead className="text-xs font-medium text-gray-500 text-center">Pass</TableHead>
                                    <TableHead className="text-xs font-medium text-gray-500 text-center">Fail</TableHead>
                                    <TableHead className="text-xs font-medium text-gray-500 text-center">Pass Rate</TableHead>
                                    <TableHead className="text-xs font-medium text-gray-500 text-right">Avg Diff</TableHead>
                                    <TableHead className="text-xs font-medium text-gray-500">Largest Diff</TableHead>
                                  </TableRow>
                                </TableHeader>
                                <TableBody>
                                  {insights.byRule.map((item) => (
                                    <TableRow key={item.ruleId} className={item.fail > 0 ? 'hover:bg-red-50/30' : 'hover:bg-green-50/20'}>
                                      <TableCell className="py-2 text-xs font-mono font-medium">{item.ruleId}</TableCell>
                                      <TableCell className="py-2 text-xs text-gray-500 max-w-[200px] truncate" title={ruleDescriptionMap.get(item.ruleId) || ''}>
                                        {ruleDescriptionMap.get(item.ruleId) || '-'}
                                      </TableCell>
                                      <TableCell className="py-2 text-xs">{item.ruleId.split('-').pop()?.toUpperCase() || '-'}</TableCell>
                                      <TableCell className="py-2 text-xs text-center font-medium">{item.total}</TableCell>
                                      <TableCell className="py-2 text-xs text-center text-green-600">{item.pass}</TableCell>
                                      <TableCell className="py-2 text-xs text-center">
                                        {item.fail > 0 ? <span className="text-red-600 font-semibold">{item.fail}</span> : <span className="text-gray-300">0</span>}
                                      </TableCell>
                                      <TableCell className="py-2 text-xs text-center">
                                        <span className={`text-xs font-medium ${item.passRate >= 80 ? 'text-green-600' : item.passRate >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
                                          {item.passRate.toFixed(1)}%
                                        </span>
                                      </TableCell>
                                      <TableCell className="py-2 text-xs text-right font-mono">
                                        <span className={item.avgDiff >= 0 ? 'text-green-600' : 'text-red-600'}>
                                          {item.avgDiff >= 0 ? '+' : ''}{item.avgDiff.toFixed(4)}
                                        </span>
                                      </TableCell>
                                      <TableCell className="py-2 text-xs">
                                        {item.largestDiff ? (
                                          <span className={`text-xs font-mono ${item.largestDiff.difference >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                            {item.largestDiff.difference >= 0 ? '+' : ''}{item.largestDiff.difference.toFixed(4)}
                                          </span>
                                        ) : (
                                          <span className="text-gray-300">-</span>
                                        )}
                                      </TableCell>
                                    </TableRow>
                                  ))}
                                </TableBody>
                              </Table>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    );

                  // ===== 7. Compare Factors (from By Dimension tab) =====
                  case 'compare-factors':
                    return (
                      <div
                        key={sectionId}
                        draggable
                        onDragStart={(e) => handleDragStart(e, sectionId)}
                        onDragOver={(e) => handleDragOver(e, sectionId)}
                        onDragLeave={handleDragLeave}
                        onDrop={(e) => handleDrop(e, sectionId)}
                        className={`rounded-lg transition-all ${dragClass}`}
                      >
                        <div className="flex items-center gap-1 mb-2 px-1">
                          <GripVertical className="w-4 h-4 text-gray-300 cursor-grab active:cursor-grabbing" />
                          <span className="text-[10px] text-gray-400 uppercase tracking-wider">Compare Factors</span>
                        </div>
                        <Card className="border shadow-sm">
                          <CardHeader className="pb-3">
                            <CardTitle className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                              <BarChart3 className="w-4 h-4 text-purple-500" />
                              Compare Factors
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-4">
                              {insights.byCompareFactor.map((cf) => (
                                <div key={cf.factor} className="border rounded-lg p-4">
                                  <div className="flex items-center justify-between mb-3">
                                    <div>
                                      <h4 className="text-sm font-semibold text-gray-700">{cf.factor}</h4>
                                      <p className="text-xs text-gray-400 mt-0.5">{cf.description}</p>
                                    </div>
                                    <div className="flex items-center gap-3">
                                      <span className="text-xs text-gray-500">{cf.total} checks</span>
                                      <span className={`text-xs font-semibold ${cf.passRate >= 80 ? 'text-green-600' : cf.passRate >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
                                        {cf.passRate.toFixed(1)}%
                                      </span>
                                    </div>
                                  </div>
                                  {/* Pass/Fail bar */}
                                  <div className="h-4 bg-gray-100 rounded-full overflow-hidden flex mb-2">
                                    <div className="h-full bg-green-400 transition-all" style={{ width: `${cf.total > 0 ? (cf.pass / cf.total) * 100 : 0}%` }} />
                                    <div className="h-full bg-red-400 transition-all" style={{ width: `${cf.total > 0 ? (cf.fail / cf.total) * 100 : 0}%` }} />
                                  </div>
                                  <div className="flex justify-between text-xs">
                                    <span className="text-green-600">{cf.pass} Pass</span>
                                    <span className="text-red-600">{cf.fail} Fail</span>
                                  </div>
                                </div>
                              ))}
                              {/* Comparison distribution */}
                              <div className="border rounded-lg p-4 mt-4">
                                <h4 className="text-sm font-semibold text-gray-700 mb-3">Pass vs Fail Distribution</h4>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                  {/* Pass distribution */}
                                  <div>
                                    <p className="text-xs text-green-600 font-medium mb-2">Passed Checks ({insights.passCount})</p>
                                    <div className="space-y-1">
                                      {checkResults.filter(r => r.status === 'PASS').slice(0, 10).map((r, i) => (
                                        <div key={i} className="flex items-center justify-between p-1.5 bg-green-50 rounded text-xs">
                                          <span className="text-gray-600 truncate max-w-[200px]" title={r.groupKey}>{r.groupKey}</span>
                                          <span className="text-green-600 font-mono">+{r.difference.toFixed(2)}</span>
                                        </div>
                                      ))}
                                      {insights.passCount > 10 && (
                                        <p className="text-[10px] text-gray-400 text-center">...and {insights.passCount - 10} more</p>
                                      )}
                                    </div>
                                  </div>
                                  {/* Fail distribution */}
                                  <div>
                                    <p className="text-xs text-red-600 font-medium mb-2">Failed Checks ({insights.failCount})</p>
                                    <div className="space-y-1">
                                      {checkResults.filter(r => r.status === 'FAIL').slice(0, 10).map((r, i) => (
                                        <div key={i} className="flex items-center justify-between p-1.5 bg-red-50 rounded text-xs">
                                          <span className="text-gray-600 truncate max-w-[200px]" title={r.groupKey}>{r.groupKey}</span>
                                          <span className="text-red-600 font-mono">{r.difference.toFixed(2)}</span>
                                        </div>
                                      ))}
                                      {insights.failCount > 10 && (
                                        <p className="text-[10px] text-gray-400 text-center">...and {insights.failCount - 10} more</p>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    );

                  // ===== 8. Country Breakdown =====
                  case 'country-breakdown':
                    return (
                      <div
                        key={sectionId}
                        draggable
                        onDragStart={(e) => handleDragStart(e, sectionId)}
                        onDragOver={(e) => handleDragOver(e, sectionId)}
                        onDragLeave={handleDragLeave}
                        onDrop={(e) => handleDrop(e, sectionId)}
                        className={`rounded-lg transition-all ${dragClass}`}
                      >
                        <div className="flex items-center gap-1 mb-2 px-1">
                          <GripVertical className="w-4 h-4 text-gray-300 cursor-grab active:cursor-grabbing" />
                          <span className="text-[10px] text-gray-400 uppercase tracking-wider">Country Breakdown</span>
                        </div>
                        <Card className="border shadow-sm">
                          <CardHeader className="pb-3">
                            <CardTitle className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                              <Globe className="w-4 h-4 text-blue-500" />
                              Country Breakdown
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-3">
                              {insights.byCountry.map((item) => (
                                <div key={item.country} className="flex items-center gap-4">
                                  <span className="text-sm font-medium text-gray-600 w-20">{item.country}</span>
                                  <div className="flex-1">
                                    <div className="h-6 bg-gray-100 rounded-full overflow-hidden flex">
                                      <div className="h-full bg-green-400 flex items-center justify-end pr-1 transition-all" style={{ width: `${item.total > 0 ? (item.pass / item.total) * 100 : 0}%` }}>
                                        {item.pass > 0 && <span className="text-[10px] text-white font-medium">{item.pass}</span>}
                                      </div>
                                      <div className="h-full bg-red-400 flex items-center pl-1 transition-all" style={{ width: `${item.total > 0 ? (item.fail / item.total) * 100 : 0}%` }}>
                                        {item.fail > 0 && <span className="text-[10px] text-white font-medium">{item.fail}</span>}
                                      </div>
                                    </div>
                                  </div>
                                  <span className="text-xs text-gray-500 w-12 text-right">{item.total}</span>
                                </div>
                              ))}
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    );

                  // ===== 7. POS/APOS + Service Tier Breakdowns =====
                  case 'pos-apos-tier-breakdown':
                    return (
                      <div
                        key={sectionId}
                        draggable
                        onDragStart={(e) => handleDragStart(e, sectionId)}
                        onDragOver={(e) => handleDragOver(e, sectionId)}
                        onDragLeave={handleDragLeave}
                        onDrop={(e) => handleDrop(e, sectionId)}
                        className={`rounded-lg transition-all ${dragClass}`}
                      >
                        <div className="flex items-center gap-1 mb-2 px-1">
                          <GripVertical className="w-4 h-4 text-gray-300 cursor-grab active:cursor-grabbing" />
                          <span className="text-[10px] text-gray-400 uppercase tracking-wider">Dimension Breakdowns</span>
                        </div>
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                          {/* By POS or APOS */}
                          <Card className="border shadow-sm">
                            <CardHeader className="pb-3">
                              <CardTitle className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                                <PieChart className="w-4 h-4 text-purple-500" />
                                By POS or APOS
                              </CardTitle>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-3">
                                {insights.byPosOrApos.map((item) => (
                                  <div key={item.posOrApos} className="flex items-center gap-4">
                                    <span className="text-sm font-medium text-gray-600 w-16">{item.posOrApos}</span>
                                    <div className="flex-1">
                                      <div className="h-6 bg-gray-100 rounded-full overflow-hidden flex">
                                        <div className="h-full bg-green-400 flex items-center justify-end pr-1 transition-all" style={{ width: `${item.total > 0 ? (item.pass / item.total) * 100 : 0}%` }}>
                                          {item.pass > 0 && <span className="text-[10px] text-white font-medium">{item.pass}</span>}
                                        </div>
                                        <div className="h-full bg-red-400 flex items-center pl-1 transition-all" style={{ width: `${item.total > 0 ? (item.fail / item.total) * 100 : 0}%` }}>
                                          {item.fail > 0 && <span className="text-[10px] text-white font-medium">{item.fail}</span>}
                                        </div>
                                      </div>
                                    </div>
                                    <span className="text-xs text-gray-500 w-12 text-right">{item.total}</span>
                                  </div>
                                ))}
                              </div>
                            </CardContent>
                          </Card>
                          {/* By Service Tier */}
                          <Card className="border shadow-sm">
                            <CardHeader className="pb-3">
                              <CardTitle className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                                <Target className="w-4 h-4 text-teal-500" />
                                By Service Tier
                              </CardTitle>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-3">
                                {insights.byServiceTier.map((item) => (
                                  <div key={item.serviceTier} className="flex items-center gap-4">
                                    <span className="text-sm font-medium text-gray-600 w-24 truncate" title={item.serviceTier}>{item.serviceTier}</span>
                                    <div className="flex-1">
                                      <div className="h-6 bg-gray-100 rounded-full overflow-hidden flex">
                                        <div className="h-full bg-green-400 flex items-center justify-end pr-1 transition-all" style={{ width: `${item.total > 0 ? (item.pass / item.total) * 100 : 0}%` }}>
                                          {item.pass > 0 && <span className="text-[10px] text-white font-medium">{item.pass}</span>}
                                        </div>
                                        <div className="h-full bg-red-400 flex items-center pl-1 transition-all" style={{ width: `${item.total > 0 ? (item.fail / item.total) * 100 : 0}%` }}>
                                          {item.fail > 0 && <span className="text-[10px] text-white font-medium">{item.fail}</span>}
                                        </div>
                                      </div>
                                    </div>
                                    <span className="text-xs text-gray-500 w-12 text-right">{item.total}</span>
                                  </div>
                                ))}
                              </div>
                            </CardContent>
                          </Card>
                        </div>
                      </div>
                    );

                  default:
                    return null;
                }
              })}
            </TabsContent>

            {/* Grouped Check Results Tab */}
            <TabsContent value="grouped" className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card className="border shadow-sm">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                        <Layers className="w-5 h-5 text-blue-500" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-gray-900">{groupedSummary.totalGroups}</p>
                        <p className="text-xs text-gray-500">Total Groups</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card className="border shadow-sm">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-green-50 rounded-lg flex items-center justify-center">
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-gray-900">{groupedSummary.groupsPassed}</p>
                        <p className="text-xs text-gray-500">Groups Passed</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card className="border shadow-sm">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-red-50 rounded-lg flex items-center justify-center">
                        <AlertTriangle className="w-5 h-5 text-red-500" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-gray-900">{groupedSummary.groupsWithErrors}</p>
                        <p className="text-xs text-gray-500">Groups With Errors</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card className="border shadow-sm">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-orange-50 rounded-lg flex items-center justify-center">
                        <XCircle className="w-5 h-5 text-orange-500" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-gray-900">{groupedSummary.totalErrors}</p>
                        <p className="text-xs text-gray-500">Total Errors</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Filters */}
              <Card className="border shadow-sm">
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                    <Filter className="w-4 h-4 text-blue-500" />
                    Filters
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-4">
                    <div className="space-y-1">
                      <Label className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Rule</Label>
                      <Select value={groupedFilters.rule} onValueChange={(v) => setGroupedFilters(prev => ({ ...prev, rule: v }))}>
                        <SelectTrigger className="text-xs h-8"><SelectValue placeholder="All Rules" /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Rules</SelectItem>
                          {groupedFilterOptions.rules.map(r => <SelectItem key={r} value={r}>{r}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Service Tier</Label>
                      <Select value={groupedFilters.serviceTier} onValueChange={(v) => setGroupedFilters(prev => ({ ...prev, serviceTier: v }))}>
                        <SelectTrigger className="text-xs h-8"><SelectValue placeholder="All Tiers" /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Tiers</SelectItem>
                          {groupedFilterOptions.serviceTiers.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Sub Service Tier</Label>
                      <Select value={groupedFilters.subServiceTier} onValueChange={(v) => setGroupedFilters(prev => ({ ...prev, subServiceTier: v }))}>
                        <SelectTrigger className="text-xs h-8"><SelectValue placeholder="All Sub Tiers" /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Sub Tiers</SelectItem>
                          {groupedFilterOptions.subServiceTiers.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Starting Point</Label>
                      <Select value={groupedFilters.startingPoint} onValueChange={(v) => setGroupedFilters(prev => ({ ...prev, startingPoint: v }))}>
                        <SelectTrigger className="text-xs h-8"><SelectValue placeholder="All" /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All</SelectItem>
                          {groupedFilterOptions.startingPoints.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Offering Type</Label>
                      <Select value={groupedFilters.offeringType} onValueChange={(v) => setGroupedFilters(prev => ({ ...prev, offeringType: v }))}>
                        <SelectTrigger className="text-xs h-8"><SelectValue placeholder="All" /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All</SelectItem>
                          {groupedFilterOptions.offeringTypes.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Country</Label>
                      <Select value={groupedFilters.country} onValueChange={(v) => setGroupedFilters(prev => ({ ...prev, country: v }))}>
                        <SelectTrigger className="text-xs h-8"><SelectValue placeholder="All" /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All</SelectItem>
                          {groupedFilterOptions.countries.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Status</Label>
                      <Select value={groupedFilters.status} onValueChange={(v) => setGroupedFilters(prev => ({ ...prev, status: v as 'all' | 'PASS' | 'FAIL' }))}>
                        <SelectTrigger className="text-xs h-8"><SelectValue placeholder="All" /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All</SelectItem>
                          <SelectItem value="PASS">Pass</SelectItem>
                          <SelectItem value="FAIL">Fail</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Grouped Results Table with Drill-Down */}
              {!groupedDrillRule ? (
                /* Level 1: Show all groups aggregated by Rule */
                <Card className="border shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                      <FolderOpen className="w-4 h-4 text-blue-500" />
                      Check Result Groups
                      <Badge variant="secondary" className="ml-2">{filteredGroupedData.length} groups</Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-auto border rounded-md" style={{ maxHeight: '600px' }}>
                      <Table>
                        <TableHeader className="sticky top-0 z-10 bg-gray-50">
                          <TableRow className="bg-gray-50">
                            <TableHead className="text-xs font-medium text-gray-500">Rule ID</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Rule Description</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Group Key</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Service PN</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Service PN Desc</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Sales&Marketing Desc</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Service Tier</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Sub Tier</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Starting Point</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Offering Type</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Country</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500 text-center">Checks</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500 text-center">Errors</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Status</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500"></TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {filteredGroupedData.map((group, idx) => (
                            <TableRow key={idx} className={group.hasFail ? 'hover:bg-red-50/50' : 'hover:bg-green-50/30'}>
                              <TableCell className="py-2 text-xs font-mono">{group.ruleId}</TableCell>
                              <TableCell className="py-2 text-xs text-gray-500 max-w-[150px] truncate" title={ruleDescriptionMap.get(group.ruleId) || ''}>
                                {ruleDescriptionMap.get(group.ruleId) || '-'}
                              </TableCell>
                              <TableCell className="py-2 text-xs max-w-[200px] truncate" title={group.groupKey}>{group.groupKey}</TableCell>
                              <TableCell className="py-2 text-xs font-mono max-w-[120px] truncate" title={group.firstRecord?.servicePN}>{group.firstRecord?.servicePN || '-'}</TableCell>
                              <TableCell className="py-2 text-xs max-w-[150px] truncate" title={group.firstRecord?.servicePNShortDescription}>{group.firstRecord?.servicePNShortDescription || '-'}</TableCell>
                              <TableCell className="py-2 text-xs max-w-[200px] truncate" title={group.firstRecord?.salesMarketingLongDescription}>{group.firstRecord?.salesMarketingLongDescription || '-'}</TableCell>
                              <TableCell className="py-2 text-xs">{group.firstRecord?.serviceTier || '-'}</TableCell>
                              <TableCell className="py-2 text-xs">{group.firstRecord?.subServiceTier || '-'}</TableCell>
                              <TableCell className="py-2 text-xs">{group.firstRecord?.serviceStartingPoint || '-'}</TableCell>
                              <TableCell className="py-2 text-xs max-w-[120px] truncate" title={group.firstRecord?.offeringType}>{group.firstRecord?.offeringType || '-'}</TableCell>
                              <TableCell className="py-2 text-xs">
                                <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-gray-100 text-gray-600">
                                  {group.firstRecord?.country || '-'}
                                </span>
                              </TableCell>
                              <TableCell className="py-2 text-xs text-center font-medium">{group.totalCount}</TableCell>
                              <TableCell className="py-2 text-center">
                                {group.errorCount > 0 ? (
                                  <span className="text-xs font-bold text-red-600">{group.errorCount}</span>
                                ) : (
                                  <span className="text-xs text-gray-300">0</span>
                                )}
                              </TableCell>
                              <TableCell className="py-2">
                                {group.hasFail ? (
                                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-red-100 text-red-700 border border-red-200">Error</span>
                                ) : (
                                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-green-100 text-green-700 border border-green-200">Valid</span>
                                )}
                              </TableCell>
                              <TableCell className="py-2">
                                <Button variant="ghost" size="sm" className="h-7 text-xs gap-1" onClick={() => { setGroupedDrillRule(group.ruleId); setGroupedDrillGroup(group.groupKey); }}>
                                  Details <ChevronRight className="w-3 h-3" />
                                </Button>
                              </TableCell>
                            </TableRow>
                          ))}
                          {filteredGroupedData.length === 0 && (
                            <TableRow><TableCell colSpan={15} className="text-center py-8 text-gray-400 text-sm">No groups match the selected filters</TableCell></TableRow>
                          )}
                        </TableBody>
                      </Table>
                    </div>
                  </CardContent>
                </Card>
              ) : !groupedDrillGroup ? (
                /* Level 2: Show groups for selected Rule */
                <Card className="border shadow-sm">
                  <CardHeader className="pb-3 flex flex-row items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                      <Button variant="ghost" size="sm" className="h-7 text-xs gap-1 px-2" onClick={() => setGroupedDrillRule(null)}>
                        <ArrowLeft className="w-3 h-3" /> All Rules
                      </Button>
                      <ChevronRight className="w-3 h-3 text-gray-400" />
                      <span className="font-mono text-xs">{groupedDrillRule}</span>
                      <Badge variant="secondary" className="ml-2">{groupedRuleGroups.length} groups</Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-auto border rounded-md" style={{ maxHeight: '600px' }}>
                      <Table>
                        <TableHeader className="sticky top-0 z-10 bg-gray-50">
                          <TableRow className="bg-gray-50">
                            <TableHead className="text-xs font-medium text-gray-500">Group Key</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Service PN</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Service PN Desc</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Sales&Marketing Desc</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Service Tier</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Sub Tier</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Starting Point</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Offering Type</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Country</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500 text-center">Checks</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500 text-center">Errors</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Status</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500"></TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {groupedRuleGroups.map((group, idx) => (
                            <TableRow key={idx} className={group.hasFail ? 'hover:bg-red-50/50' : 'hover:bg-green-50/30'}>
                              <TableCell className="py-2 text-xs max-w-[250px] truncate" title={group.groupKey}>{group.groupKey}</TableCell>
                              <TableCell className="py-2 text-xs font-mono max-w-[120px] truncate" title={group.firstRecord?.servicePN}>{group.firstRecord?.servicePN || '-'}</TableCell>
                              <TableCell className="py-2 text-xs max-w-[150px] truncate" title={group.firstRecord?.servicePNShortDescription}>{group.firstRecord?.servicePNShortDescription || '-'}</TableCell>
                              <TableCell className="py-2 text-xs max-w-[200px] truncate" title={group.firstRecord?.salesMarketingLongDescription}>{group.firstRecord?.salesMarketingLongDescription || '-'}</TableCell>
                              <TableCell className="py-2 text-xs">{group.firstRecord?.serviceTier || '-'}</TableCell>
                              <TableCell className="py-2 text-xs">{group.firstRecord?.subServiceTier || '-'}</TableCell>
                              <TableCell className="py-2 text-xs">{group.firstRecord?.serviceStartingPoint || '-'}</TableCell>
                              <TableCell className="py-2 text-xs max-w-[120px] truncate" title={group.firstRecord?.offeringType}>{group.firstRecord?.offeringType || '-'}</TableCell>
                              <TableCell className="py-2 text-xs">
                                <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-gray-100 text-gray-600">{group.firstRecord?.country || '-'}</span>
                              </TableCell>
                              <TableCell className="py-2 text-xs text-center font-medium">{group.totalCount}</TableCell>
                              <TableCell className="py-2 text-center">
                                {group.errorCount > 0 ? <span className="text-xs font-bold text-red-600">{group.errorCount}</span> : <span className="text-xs text-gray-300">0</span>}
                              </TableCell>
                              <TableCell className="py-2">
                                {group.hasFail ? (
                                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-red-100 text-red-700 border border-red-200">Error</span>
                                ) : (
                                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-green-100 text-green-700 border border-green-200">Valid</span>
                                )}
                              </TableCell>
                              <TableCell className="py-2">
                                <Button variant="ghost" size="sm" className="h-7 text-xs gap-1" onClick={() => setGroupedDrillGroup(group.groupKey)}>
                                  Details <ChevronRight className="w-3 h-3" />
                                </Button>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                /* Level 3: Show individual check results for selected Group */
                <Card className="border shadow-sm">
                  <CardHeader className="pb-3 flex flex-row items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                      <Button variant="ghost" size="sm" className="h-7 text-xs gap-1 px-2" onClick={() => { setGroupedDrillRule(null); setGroupedDrillGroup(null); }}>
                        <ArrowLeft className="w-3 h-3" /> All Rules
                      </Button>
                      <ChevronRight className="w-3 h-3 text-gray-400" />
                      <Button variant="ghost" size="sm" className="h-7 text-xs gap-1 px-2" onClick={() => setGroupedDrillGroup(null)}>
                        {groupedDrillRule}
                      </Button>
                      <ChevronRight className="w-3 h-3 text-gray-400" />
                      <span className="text-xs text-gray-500 truncate max-w-[200px]" title={groupedDrillGroup}>{groupedDrillGroup}</span>
                      <Badge variant="secondary" className="ml-2">{groupedGroupResults.length} results</Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-auto border rounded-md" style={{ maxHeight: '600px' }}>
                      <Table>
                        <TableHeader className="sticky top-0 z-10 bg-gray-50">
                          <TableRow className="bg-gray-50">
                            <TableHead className="text-xs font-medium text-gray-500">Compare</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Low Value</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Low Cost</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">High Value</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">High Cost</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Difference</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Status</TableHead>
                            <TableHead className="text-xs font-medium text-gray-500">Validation Error</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {groupedGroupResults.map((result, idx) => (
                            <TableRow key={idx} className={result.status === 'FAIL' ? 'hover:bg-red-50/50' : 'hover:bg-green-50/30'}>
                              <TableCell className="py-2 text-xs">{result.compareFactor}</TableCell>
                              <TableCell className="py-2 text-xs">{result.lowPriorityValue}</TableCell>
                              <TableCell className="py-2 text-xs text-right font-mono">${result.lowPrioritySalesCost.toFixed(4)}</TableCell>
                              <TableCell className="py-2 text-xs">{result.highPriorityValue}</TableCell>
                              <TableCell className="py-2 text-xs text-right font-mono">${result.highPrioritySalesCost.toFixed(4)}</TableCell>
                              <TableCell className="py-2 text-xs text-right font-mono">
                                <span className={result.difference >= 0 ? 'text-green-600' : 'text-red-600'}>
                                  {result.difference >= 0 ? '+' : ''}{result.difference.toFixed(4)}
                                </span>
                              </TableCell>
                              <TableCell className="py-2">
                                {result.status === 'FAIL' ? (
                                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-red-100 text-red-700 border border-red-200">Error</span>
                                ) : (
                                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-green-100 text-green-700 border border-green-200">Valid</span>
                                )}
                              </TableCell>
                              <TableCell className="py-2 text-xs">
                                {result.failReason ? (
                                  <span className="text-red-600 truncate max-w-[300px] inline-block" title={result.failReason}>{result.failReason}</span>
                                ) : (
                                  <span className="text-gray-300">-</span>
                                )}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Missing Check Rules Tab */}
            <TabsContent value="missing" className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Card className="border shadow-sm">
                  <CardContent className="p-5">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm text-gray-500 font-medium">Total Missing Records</p>
                        <p className="text-3xl font-bold text-gray-900 mt-2">{missingRecords.length.toLocaleString()}</p>
                        <p className="text-xs text-gray-400 mt-1">
                          {displayData.length > 0 ? ((missingRecords.length / displayData.length) * 100).toFixed(1) : 0}% of total records
                        </p>
                      </div>
                      <div className="w-9 h-9 bg-orange-50 rounded-lg flex items-center justify-center">
                        <AlertTriangle className="w-4 h-4 text-orange-500" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card className="border shadow-sm">
                  <CardContent className="p-5">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm text-gray-500 font-medium">Checked Records</p>
                        <p className="text-3xl font-bold text-gray-900 mt-2">{(displayData.length - missingRecords.length).toLocaleString()}</p>
                        <p className="text-xs text-gray-400 mt-1">Covered by released rules</p>
                      </div>
                      <div className="w-9 h-9 bg-green-50 rounded-lg flex items-center justify-center">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card className="border shadow-sm">
                  <CardContent className="p-5">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm text-gray-500 font-medium">Total Records</p>
                        <p className="text-3xl font-bold text-gray-900 mt-2">{displayData.length.toLocaleString()}</p>
                        <p className="text-xs text-gray-400 mt-1">All sales cost records</p>
                      </div>
                      <div className="w-9 h-9 bg-blue-50 rounded-lg flex items-center justify-center">
                        <FileText className="w-4 h-4 text-blue-500" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Filters */}
              <Card className="border shadow-sm">
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                    <Filter className="w-4 h-4 text-blue-500" />
                    Filters
                    <span className="text-xs text-gray-400 font-normal ml-2">{filteredMissingRecords.length} records found</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
                    <div className="space-y-1">
                      <Label className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Service Tier</Label>
                      <Select value={missingFilters.serviceTier} onValueChange={(v) => setMissingFilters(prev => ({ ...prev, serviceTier: v }))}>
                        <SelectTrigger className="text-xs h-8"><SelectValue placeholder="All Tiers" /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Tiers</SelectItem>
                          {missingFilterOptions.serviceTiers.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Sub Service Tier</Label>
                      <Select value={missingFilters.subServiceTier} onValueChange={(v) => setMissingFilters(prev => ({ ...prev, subServiceTier: v }))}>
                        <SelectTrigger className="text-xs h-8"><SelectValue placeholder="All Sub Tiers" /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Sub Tiers</SelectItem>
                          {missingFilterOptions.subServiceTiers.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Starting Point</Label>
                      <Select value={missingFilters.startingPoint} onValueChange={(v) => setMissingFilters(prev => ({ ...prev, startingPoint: v }))}>
                        <SelectTrigger className="text-xs h-8"><SelectValue placeholder="All" /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All</SelectItem>
                          {missingFilterOptions.startingPoints.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Offering Type</Label>
                      <Select value={missingFilters.offeringType} onValueChange={(v) => setMissingFilters(prev => ({ ...prev, offeringType: v }))}>
                        <SelectTrigger className="text-xs h-8"><SelectValue placeholder="All" /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All</SelectItem>
                          {missingFilterOptions.offeringTypes.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Country</Label>
                      <Select value={missingFilters.country} onValueChange={(v) => setMissingFilters(prev => ({ ...prev, country: v }))}>
                        <SelectTrigger className="text-xs h-8"><SelectValue placeholder="All" /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All</SelectItem>
                          {missingFilterOptions.countries.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">POS/APOS</Label>
                      <Select value={missingFilters.posOrApos} onValueChange={(v) => setMissingFilters(prev => ({ ...prev, posOrApos: v }))}>
                        <SelectTrigger className="text-xs h-8"><SelectValue placeholder="All" /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All</SelectItem>
                          {missingFilterOptions.posOrApos.map(p => <SelectItem key={p} value={p}>{p}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Missing Records Table */}
              <Card className="border shadow-sm">
                <CardHeader className="pb-3 flex flex-row items-center justify-between">
                  <CardTitle className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                    <FileText className="w-4 h-4 text-orange-500" />
                    Records Without Check Rule Coverage
                    <Badge variant="secondary" className="ml-2">{filteredMissingRecords.length} records</Badge>
                  </CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    className="gap-1.5"
                    onClick={() => {
                      const ws = XLSX.utils.json_to_sheet(filteredMissingRecords.map(r => ({
                        'Service PN': r.servicePN,
                        'Service PN Short Description': r.servicePNShortDescription,
                        'Sales&Marketing Long Description': r.salesMarketingLongDescription,
                        'POS or APOS': r.posOrApos,
                        'Starting Point': r.serviceStartingPoint,
                        'Term': r.term,
                        'Service Tier': r.serviceTier,
                        'Sub Service Tier': r.subServiceTier || '',
                        'OH Code': r.ohCode,
                        'OH Name': r.ohName,
                        'Type of Service': r.typeOfService,
                        'Sub Type of Service': r.subTypeOfService,
                        'Offering Type': r.offeringType,
                        'Country': r.country,
                        'Sales Cost': r.salesCost,
                      })));
                      const wb = XLSX.utils.book_new();
                      XLSX.utils.book_append_sheet(wb, ws, 'Missing Rules');
                      XLSX.writeFile(wb, `missing-check-rules-${new Date().toISOString().split('T')[0]}.xlsx`);
                    }}
                  >
                    <Download className="w-4 h-4" />
                    Export Excel
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="overflow-auto border rounded-md" style={{ maxHeight: '600px' }}>
                    <Table>
                      <TableHeader className="sticky top-0 z-10 bg-gray-50">
                        <TableRow className="bg-gray-50">
                          <TableHead className="text-xs font-medium text-gray-500 whitespace-nowrap">Service PN</TableHead>
                          <TableHead className="text-xs font-medium text-gray-500 whitespace-nowrap">Service PN Desc</TableHead>
                          <TableHead className="text-xs font-medium text-gray-500 whitespace-nowrap">Sales&Marketing Desc</TableHead>
                          <TableHead className="text-xs font-medium text-gray-500 whitespace-nowrap">POS/APOS</TableHead>
                          <TableHead className="text-xs font-medium text-gray-500 whitespace-nowrap">Starting Point</TableHead>
                          <TableHead className="text-xs font-medium text-gray-500 whitespace-nowrap">Term</TableHead>
                          <TableHead className="text-xs font-medium text-gray-500 whitespace-nowrap">Service Tier</TableHead>
                          <TableHead className="text-xs font-medium text-gray-500 whitespace-nowrap">Sub Tier</TableHead>
                          <TableHead className="text-xs font-medium text-gray-500 whitespace-nowrap">OH Code</TableHead>
                          <TableHead className="text-xs font-medium text-gray-500 whitespace-nowrap">OH Name</TableHead>
                          <TableHead className="text-xs font-medium text-gray-500 whitespace-nowrap">Type of Service</TableHead>
                          <TableHead className="text-xs font-medium text-gray-500 whitespace-nowrap">Sub Type of Service</TableHead>
                          <TableHead className="text-xs font-medium text-gray-500 whitespace-nowrap">Offering Type</TableHead>
                          <TableHead className="text-xs font-medium text-gray-500 whitespace-nowrap">Country</TableHead>
                          <TableHead className="text-xs font-medium text-gray-500 text-right whitespace-nowrap">Sales Cost</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filteredMissingRecords.map((record, idx) => (
                          <TableRow key={idx} className="hover:bg-orange-50/30">
                            <TableCell className="py-2 text-xs font-mono whitespace-nowrap">{record.servicePN}</TableCell>
                            <TableCell className="py-2 text-xs max-w-[150px] truncate whitespace-nowrap" title={record.servicePNShortDescription}>{record.servicePNShortDescription}</TableCell>
                            <TableCell className="py-2 text-xs max-w-[200px] truncate whitespace-nowrap" title={record.salesMarketingLongDescription}>{record.salesMarketingLongDescription}</TableCell>
                            <TableCell className="py-2">
                              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-gray-100 text-gray-600">{record.posOrApos}</span>
                            </TableCell>
                            <TableCell className="py-2 text-xs whitespace-nowrap">{record.serviceStartingPoint || '-'}</TableCell>
                            <TableCell className="py-2 text-xs whitespace-nowrap">{record.term}</TableCell>
                            <TableCell className="py-2 text-xs whitespace-nowrap">{record.serviceTier}</TableCell>
                            <TableCell className="py-2 text-xs whitespace-nowrap">{record.subServiceTier || '-'}</TableCell>
                            <TableCell className="py-2 text-xs font-mono whitespace-nowrap">{record.ohCode}</TableCell>
                            <TableCell className="py-2 text-xs max-w-[120px] truncate whitespace-nowrap" title={record.ohName}>{record.ohName}</TableCell>
                            <TableCell className="py-2 text-xs whitespace-nowrap">{record.typeOfService}</TableCell>
                            <TableCell className="py-2 text-xs whitespace-nowrap">{record.subTypeOfService}</TableCell>
                            <TableCell className="py-2 text-xs max-w-[120px] truncate whitespace-nowrap" title={record.offeringType}>{record.offeringType}</TableCell>
                            <TableCell className="py-2">
                              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-gray-100 text-gray-600">{record.country}</span>
                            </TableCell>
                            <TableCell className="py-2 text-xs text-right font-mono whitespace-nowrap">${record.salesCost.toFixed(4)}</TableCell>
                          </TableRow>
                        ))}
                        {filteredMissingRecords.length === 0 && (
                          <TableRow>
                            <TableCell colSpan={15} className="text-center py-8 text-gray-400 text-sm">
                              {missingRecords.length === 0 ? (
                                <div className="flex flex-col items-center gap-2">
                                  <CheckCircle className="w-8 h-8 text-green-300" />
                                  <p>All records are covered by check rules</p>
                                </div>
                              ) : (
                                <p>No records match the selected filters</p>
                              )}
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Drill Down Tab */}
            <TabsContent value="drilldown" className="space-y-4">
              {/* Drill-down Filters */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Filter className="w-4 h-4 text-blue-600" />
                    Filters
                    {(drillFilters.status !== 'all' || drillFilters.search) && (
                      <Button variant="ghost" size="sm" onClick={clearDrillFilters} className="ml-auto">
                        <X className="w-4 h-4 mr-1" />
                        Clear
                      </Button>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-4 pt-0">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <Select
                      value={drillFilters.status}
                      onValueChange={(v) => setDrillFilters(prev => ({ ...prev, status: v as 'all' | 'PASS' | 'FAIL' }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="PASS">Pass</SelectItem>
                        <SelectItem value="FAIL">Fail</SelectItem>
                      </SelectContent>
                    </Select>
                    <div className="relative md:col-span-2">
                      <Search className="w-4 h-4 absolute left-2 top-2.5 text-gray-400" />
                      <Input
                        placeholder="Search group key, priority values..."
                        value={drillFilters.search}
                        onChange={(e) => setDrillFilters(prev => ({ ...prev, search: e.target.value }))}
                        className="pl-8"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Breadcrumb Navigation */}
              {drillView !== 'rules' && (
                <div className="flex items-center gap-2 mb-4">
                  <Button variant="ghost" size="sm" onClick={navigateBack} className="text-blue-600">
                    <ArrowLeft className="w-4 h-4 mr-1" />
                    Back
                  </Button>
                  <span className="text-gray-400">/</span>
                  {drillView === 'groups' && selectedRuleId && (
                    <span className="text-sm font-medium">{selectedRuleId}</span>
                  )}
                  {drillView === 'records' && selectedRuleId && selectedGroupKey && (
                    <>
                      <Button variant="ghost" size="sm" onClick={() => setDrillView('groups')} className="text-blue-600">
                        {selectedRuleId}
                      </Button>
                      <span className="text-gray-400">/</span>
                      <span className="text-sm font-medium truncate max-w-[300px]" title={selectedGroupKey}>{selectedGroupKey}</span>
                    </>
                  )}
                  {drillView === 'detail' && selectedResult && (
                    <>
                      <Button variant="ghost" size="sm" onClick={() => setDrillView('groups')} className="text-blue-600">
                        {selectedResult.ruleId}
                      </Button>
                      <span className="text-gray-400">/</span>
                      <Button variant="ghost" size="sm" onClick={() => setDrillView('records')} className="text-blue-600 truncate max-w-[200px]">
                        {selectedResult.groupKey}
                      </Button>
                      <span className="text-gray-400">/</span>
                      <span className="text-sm font-medium">Detail</span>
                    </>
                  )}
                </div>
              )}

              {/* Rules Level */}
              {drillView === 'rules' && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FolderOpen className="w-5 h-5 text-blue-600" />
                      Select a Rule to View Details
                      <Badge variant="secondary" className="ml-2">{filteredResultsByRule.size} rules</Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {Array.from(filteredResultsByRule.entries()).map(([ruleId, results]) => {
                        const passCount = results.filter(r => r.status === 'PASS').length;
                        const failCount = results.filter(r => r.status === 'FAIL').length;
                        const passRate = (passCount / results.length) * 100;
                        
                        return (
                          <div 
                            key={ruleId} 
                            className="border rounded-lg p-4 hover:bg-blue-50 cursor-pointer transition-colors"
                            onClick={() => navigateToRuleGroups(ruleId)}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                <ChevronRight className="w-5 h-5 text-gray-400" />
                                <div>
                                  <p className="font-medium">{ruleId}</p>
                                  <p className="text-xs text-gray-500 truncate max-w-md">
                                    {ruleDescriptionMap.get(ruleId) || 'No description'}
                                  </p>
                                </div>
                              </div>
                              <div className="flex items-center gap-4">
                                <div className="text-right">
                                  <p className="text-sm">{results.length} checks</p>
                                  <div className="flex gap-2 text-xs">
                                    <span className="text-green-600">{passCount} Pass</span>
                                    <span className="text-red-600">{failCount} Fail</span>
                                  </div>
                                </div>
                                <div className="w-24">
                                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                                    <div 
                                      className="h-full bg-green-500"
                                      style={{ width: `${passRate}%` }}
                                    />
                                  </div>
                                  <p className="text-xs text-right mt-1">{passRate.toFixed(0)}%</p>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Groups Level */}
              {drillView === 'groups' && selectedRuleId && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Layers className="w-5 h-5 text-purple-600" />
                      Groups for {selectedRuleId}
                      <Badge variant="secondary" className="ml-2">{filteredResultsByGroupKey.size} groups</Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {Array.from(filteredResultsByGroupKey.entries()).map(([groupKey, results]) => {
                        const passCount = results.filter(r => r.status === 'PASS').length;
                        const failCount = results.filter(r => r.status === 'FAIL').length;
                        const passRate = (passCount / results.length) * 100;
                        
                        return (
                          <div 
                            key={groupKey} 
                            className="border rounded-lg p-4 hover:bg-purple-50 cursor-pointer transition-colors"
                            onClick={() => navigateToGroupRecords(groupKey)}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                <ChevronRight className="w-5 h-5 text-gray-400" />
                                <div>
                                  <p className="font-medium text-sm truncate max-w-[400px]" title={groupKey}>{groupKey}</p>
                                  <p className="text-xs text-gray-500">{results.length} comparisons</p>
                                </div>
                              </div>
                              <div className="flex items-center gap-4">
                                <div className="text-right">
                                  <div className="flex gap-2 text-xs">
                                    <span className="text-green-600">{passCount} Pass</span>
                                    <span className="text-red-600">{failCount} Fail</span>
                                  </div>
                                </div>
                                <div className="w-24">
                                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                                    <div 
                                      className={`h-full ${passRate === 100 ? 'bg-green-500' : passRate >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
                                      style={{ width: `${passRate}%` }}
                                    />
                                  </div>
                                  <p className="text-xs text-right mt-1">{passRate.toFixed(0)}%</p>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Records Level */}
              {drillView === 'records' && selectedRuleId && selectedGroupKey && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="w-5 h-5 text-orange-600" />
                      Check Comparisons
                      <Badge variant="secondary" className="ml-2">
                        {filteredGroupResults.length} comparisons
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {filteredGroupResults.map((result, idx) => (
                        <div 
                          key={idx} 
                          className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                            result.status === 'FAIL' ? 'hover:bg-red-50 border-red-200' : 'hover:bg-green-50'
                          }`}
                          onClick={() => navigateToDetail(result)}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <ChevronRight className="w-5 h-5 text-gray-400" />
                              <div>
                                <p className="font-medium text-sm">
                                  {result.lowPriorityValue} → {result.highPriorityValue}
                                  <Badge 
                                    className={`ml-2 ${result.status === 'PASS' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}
                                  >
                                    {result.status}
                                  </Badge>
                                </p>
                                <p className="text-xs text-gray-500">
                                  Compare Factor: {result.compareFactor}
                                </p>
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="text-sm">
                                ${result.lowPrioritySalesCost.toFixed(4)} → ${result.highPrioritySalesCost.toFixed(4)}
                              </p>
                              <p className={`text-xs ${result.difference >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                Diff: {result.difference >= 0 ? '+' : ''}{result.difference.toFixed(4)}
                              </p>
                            </div>
                          </div>
                          {result.status === 'FAIL' && result.failReason && (
                            <div className="mt-2 p-2 bg-red-50 rounded text-xs text-red-700">
                              <AlertTriangle className="w-3 h-3 inline mr-1" />
                              {result.failReason}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Detail Level */}
              {drillView === 'detail' && selectedResult && (
                <div className="space-y-4">
                  {/* Check Summary */}
                  <Card className={selectedResult.status === 'FAIL' ? 'border-red-300' : 'border-green-300'}>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        {selectedResult.status === 'PASS' ? (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-600" />
                        )}
                        Check Result: {selectedResult.status}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="p-3 bg-gray-50 rounded-lg">
                          <p className="text-xs text-gray-500">Compare Factor</p>
                          <p className="font-medium">{selectedResult.compareFactor}</p>
                        </div>
                        <div className="p-3 bg-gray-50 rounded-lg">
                          <p className="text-xs text-gray-500">Comparison</p>
                          <p className="font-medium">{selectedResult.lowPriorityValue} → {selectedResult.highPriorityValue}</p>
                        </div>
                        <div className="p-3 bg-gray-50 rounded-lg">
                          <p className="text-xs text-gray-500">Low Priority Cost</p>
                          <p className="font-medium">${selectedResult.lowPrioritySalesCost.toFixed(4)}</p>
                        </div>
                        <div className="p-3 bg-gray-50 rounded-lg">
                          <p className="text-xs text-gray-500">High Priority Cost</p>
                          <p className="font-medium">${selectedResult.highPrioritySalesCost.toFixed(4)}</p>
                        </div>
                      </div>
                      
                      {selectedResult.status === 'FAIL' && selectedResult.failReason && (
                        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                          <p className="text-sm font-medium text-red-800 flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4" />
                            Fail Reason
                          </p>
                          <p className="text-sm text-red-700 mt-1">{selectedResult.failReason}</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Detailed Records */}
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between">
                      <CardTitle className="flex items-center gap-2">
                        <FileText className="w-5 h-5 text-blue-600" />
                        Detailed Sales Cost Records
                        <Badge variant="secondary" className="ml-2">{selectedResult.records.length} records</Badge>
                      </CardTitle>
                      
                      {/* Column Selector */}
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button variant="outline" size="sm" className="gap-2">
                            <Columns className="w-4 h-4" />
                            Columns
                            <Badge variant="secondary" className="ml-1">{visibleColumns.size}</Badge>
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-80 p-0" align="end">
                          <div className="p-3 border-b bg-gray-50">
                            <div className="flex items-center justify-between">
                              <span className="font-medium text-sm">Select Columns to Display</span>
                            </div>
                          </div>
                          <ScrollArea className="h-[300px]">
                            <div className="p-3 space-y-2">
                              {ALL_COLUMNS.map((col) => (
                                <div key={col.key} className="flex items-center space-x-2">
                                  <Checkbox
                                    id={`col-${col.key}`}
                                    checked={visibleColumns.has(col.key)}
                                    onCheckedChange={() => toggleColumn(col.key)}
                                  />
                                  <Label 
                                    htmlFor={`col-${col.key}`}
                                    className="text-sm cursor-pointer flex-1"
                                  >
                                    {col.label}
                                  </Label>
                                </div>
                              ))}
                            </div>
                          </ScrollArea>
                          <div className="p-3 border-t bg-gray-50 flex gap-2">
                            <Button variant="outline" size="sm" onClick={showAllColumns} className="flex-1">
                              Show All
                            </Button>
                            <Button variant="outline" size="sm" onClick={resetColumns} className="flex-1">
                              Reset
                            </Button>
                          </div>
                        </PopoverContent>
                      </Popover>
                    </CardHeader>
                    <CardContent>
                      <div className="overflow-auto border rounded-md" style={{ maxHeight: '400px' }}>
                        <Table className="min-w-[1500px]">
                          <TableHeader className="sticky top-0 z-10 bg-gray-50">
                            <TableRow className="bg-gray-50">
                              {visibleColumns.has('servicePN') && (
                                <TableHead className="text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['servicePN'], minWidth: drillDownColWidths['servicePN'] }}>Service PN</TableHead>
                              )}
                              {visibleColumns.has('servicePNShortDescription') && (
                                <TableHead className="text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['servicePNShortDescription'], minWidth: drillDownColWidths['servicePNShortDescription'] }}>Service PN Desc</TableHead>
                              )}
                              {visibleColumns.has('salesMarketingLongDescription') && (
                                <TableHead className="text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['salesMarketingLongDescription'], minWidth: drillDownColWidths['salesMarketingLongDescription'] }}>Sales&Marketing Desc</TableHead>
                              )}
                              {visibleColumns.has('posOrApos') && (
                                <TableHead className="text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['posOrApos'], minWidth: drillDownColWidths['posOrApos'] }}>POS/APOS</TableHead>
                              )}
                              {visibleColumns.has('serviceStartingPoint') && (
                                <TableHead className="text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['serviceStartingPoint'], minWidth: drillDownColWidths['serviceStartingPoint'] }}>Starting Point</TableHead>
                              )}
                              {visibleColumns.has('term') && (
                                <TableHead className="text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['term'], minWidth: drillDownColWidths['term'] }}>Term</TableHead>
                              )}
                              {visibleColumns.has('serviceTier') && (
                                <TableHead className="text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['serviceTier'], minWidth: drillDownColWidths['serviceTier'] }}>Service Tier</TableHead>
                              )}
                              {visibleColumns.has('subServiceTier') && (
                                <TableHead className="text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['subServiceTier'], minWidth: drillDownColWidths['subServiceTier'] }}>Sub Service Tier</TableHead>
                              )}
                              {visibleColumns.has('ohCode') && (
                                <TableHead className="text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['ohCode'], minWidth: drillDownColWidths['ohCode'] }}>OH Code</TableHead>
                              )}
                              {visibleColumns.has('ohName') && (
                                <TableHead className="text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['ohName'], minWidth: drillDownColWidths['ohName'] }}>OH Name</TableHead>
                              )}
                              {visibleColumns.has('typeOfService') && (
                                <TableHead className="text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['typeOfService'], minWidth: drillDownColWidths['typeOfService'] }}>Type of Service</TableHead>
                              )}
                              {visibleColumns.has('subTypeOfService') && (
                                <TableHead className="text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['subTypeOfService'], minWidth: drillDownColWidths['subTypeOfService'] }}>Sub Type of Service</TableHead>
                              )}
                              {visibleColumns.has('offeringType') && (
                                <TableHead className="text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['offeringType'], minWidth: drillDownColWidths['offeringType'] }}>Offering Type</TableHead>
                              )}
                              {visibleColumns.has('country') && (
                                <TableHead className="text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['country'], minWidth: drillDownColWidths['country'] }}>Country</TableHead>
                              )}
                              {visibleColumns.has('salesCost') && (
                                <TableHead className="text-xs text-right whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['salesCost'], minWidth: drillDownColWidths['salesCost'] }}>Sales Cost</TableHead>
                              )}
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {selectedResult.records.map((record, idx) => (
                              <TableRow key={idx} className="hover:bg-gray-50">
                                {visibleColumns.has('servicePN') && (
                                  <TableCell className="font-mono text-xs py-2 whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['servicePN'], minWidth: drillDownColWidths['servicePN'] }} title={record.servicePN}>{record.servicePN}</TableCell>
                                )}
                                {visibleColumns.has('servicePNShortDescription') && (
                                  <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['servicePNShortDescription'], minWidth: drillDownColWidths['servicePNShortDescription'] }} title={record.servicePNShortDescription}>{record.servicePNShortDescription}</TableCell>
                                )}
                                {visibleColumns.has('salesMarketingLongDescription') && (
                                  <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['salesMarketingLongDescription'], minWidth: drillDownColWidths['salesMarketingLongDescription'] }} title={record.salesMarketingLongDescription}>{record.salesMarketingLongDescription}</TableCell>
                                )}
                                {visibleColumns.has('posOrApos') && (
                                  <TableCell className="py-2 whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['posOrApos'], minWidth: drillDownColWidths['posOrApos'] }}>
                                    <Badge variant="outline" className="text-xs">{record.posOrApos}</Badge>
                                  </TableCell>
                                )}
                                {visibleColumns.has('serviceStartingPoint') && (
                                  <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['serviceStartingPoint'], minWidth: drillDownColWidths['serviceStartingPoint'] }} title={record.serviceStartingPoint || ''}>{record.serviceStartingPoint || '-'}</TableCell>
                                )}
                                {visibleColumns.has('term') && (
                                  <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['term'], minWidth: drillDownColWidths['term'] }}>{record.term}</TableCell>
                                )}
                                {visibleColumns.has('serviceTier') && (
                                  <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['serviceTier'], minWidth: drillDownColWidths['serviceTier'] }} title={record.serviceTier}>{record.serviceTier}</TableCell>
                                )}
                                {visibleColumns.has('subServiceTier') && (
                                  <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['subServiceTier'], minWidth: drillDownColWidths['subServiceTier'] }} title={record.subServiceTier || ''}>{record.subServiceTier || '-'}</TableCell>
                                )}
                                {visibleColumns.has('ohCode') && (
                                  <TableCell className="font-mono text-xs py-2 whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['ohCode'], minWidth: drillDownColWidths['ohCode'] }}>{record.ohCode}</TableCell>
                                )}
                                {visibleColumns.has('ohName') && (
                                  <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['ohName'], minWidth: drillDownColWidths['ohName'] }} title={record.ohName}>{record.ohName}</TableCell>
                                )}
                                {visibleColumns.has('typeOfService') && (
                                  <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['typeOfService'], minWidth: drillDownColWidths['typeOfService'] }} title={record.typeOfService}>{record.typeOfService}</TableCell>
                                )}
                                {visibleColumns.has('subTypeOfService') && (
                                  <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['subTypeOfService'], minWidth: drillDownColWidths['subTypeOfService'] }} title={record.subTypeOfService}>{record.subTypeOfService}</TableCell>
                                )}
                                {visibleColumns.has('offeringType') && (
                                  <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['offeringType'], minWidth: drillDownColWidths['offeringType'] }} title={record.offeringType}>{record.offeringType}</TableCell>
                                )}
                                {visibleColumns.has('country') && (
                                  <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['country'], minWidth: drillDownColWidths['country'] }}>{record.country}</TableCell>
                                )}
                                {visibleColumns.has('salesCost') && (
                                  <TableCell className="py-2 text-right font-medium whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: drillDownColWidths['salesCost'], minWidth: drillDownColWidths['salesCost'] }}>${record.salesCost.toFixed(4)}</TableCell>
                                )}
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                        {visibleColumns.size === 0 && (
                          <div className="text-center py-8 text-gray-500">
                            <Columns className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                            <p>No columns selected. Click "Columns" to choose fields to display.</p>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </TabsContent>

          </Tabs>
        )}
      </div>
    </TooltipProvider>
  );
}
