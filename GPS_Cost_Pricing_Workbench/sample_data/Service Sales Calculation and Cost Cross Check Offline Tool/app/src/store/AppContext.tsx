import { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react';
import type { SalesCostCheckRule, SalesCostUploadRecord, SalesCostDisplayRecord, CheckResult, CheckSummary } from '@/types';
import { sampleCheckRules, sampleUploadData, sampleDisplayData, ohMasterData } from '@/data/sampleData';
import { transformUploadData } from '@/utils/dataTransform';
import { executeAllCrossChecks } from '@/utils/checkLogic';
import { useFileStorage } from '@/hooks/useFileStorage';
import type { AppDataFile } from '@/hooks/useFileStorage';

interface AppState {
  // Rules
  rules: SalesCostCheckRule[];
  addRule: (rule: SalesCostCheckRule) => void;
  updateRule: (rule: SalesCostCheckRule) => void;
  deleteRule: (ruleId: string) => void;

  // Upload Data
  uploadData: SalesCostUploadRecord[];
  setUploadData: (data: SalesCostUploadRecord[]) => void;

  // Display Data (transformed)
  displayData: SalesCostDisplayRecord[];
  setDisplayData: (data: SalesCostDisplayRecord[]) => void;
  transformData: () => void;
  updateDisplayRecord: (index: number, record: SalesCostDisplayRecord) => void;
  deleteDisplayRecord: (index: number) => void;

  // Check Results
  checkResults: CheckResult[];
  checkSummary: CheckSummary | null;
  executeChecks: () => void;

  // Navigation
  currentPage: string;
  setCurrentPage: (page: string) => void;

  // Data management
  clearAllData: () => void;
  resetToDemo: () => void;

  // File storage
  fileStorage: {
    hasFileAssociation: boolean;
    autoSaveEnabled: boolean;
    lastSaved: Date | null;
    isSaving: boolean;
    fileApiSupported: boolean;
    restoredFromIDB: boolean;
  };
  pickSaveLocation: () => Promise<void>;
  loadFromFile: () => Promise<void>;
  toggleAutoSave: () => void;
  resetFileAssociation: () => Promise<void>;

  // Startup
  dataLoaded: boolean;
  isFirstVisit: boolean;
  loadDemoData: () => void;
  loadFileData: () => Promise<void>;
}

const AppContext = createContext<AppState | undefined>(undefined);

// Check if this is the first visit (no cached flag)
const checkIsFirstVisit = (): boolean => {
  try {
    return !sessionStorage.getItem('scc_visited');
  } catch {
    return true;
  }
};

// Mark as visited
const markVisited = () => {
  try {
    sessionStorage.setItem('scc_visited', 'true');
  } catch {
    // ignore
  }
};

export function AppProvider({ children }: { children: React.ReactNode }) {
  // Core data states
  const [rules, setRules] = useState<SalesCostCheckRule[]>(sampleCheckRules);
  const [uploadData, setUploadDataState] = useState<SalesCostUploadRecord[]>(sampleUploadData);
  const [displayData, setDisplayDataState] = useState<SalesCostDisplayRecord[]>(sampleDisplayData);
  const [checkResults, setCheckResults] = useState<CheckResult[]>([]);
  const [checkSummary, setCheckSummary] = useState<CheckSummary | null>(null);
  const [currentPage, setCurrentPage] = useState<string>('upload'); // Start at upload page

  // Startup state
  const [dataLoaded, setDataLoaded] = useState(true); // Initially true (demo data loaded)
  const [isFirstVisit, setIsFirstVisit] = useState(checkIsFirstVisit);

  // File storage hook
  const [fileStorageState, fileStorageActions] = useFileStorage();

  // Ref to track if we should auto-save (prevent save during initial load)
  const shouldAutoSave = useRef(false);

  // Collect all current data into AppDataFile format
  const collectData = useCallback((): Omit<AppDataFile, 'version' | 'exportDate'> => ({
    rules,
    uploadData,
    displayData,
    checkResults,
    checkSummary,
  }), [rules, uploadData, displayData, checkResults, checkSummary]);

  // Auto-save to file when data changes
  useEffect(() => {
    if (shouldAutoSave.current && fileStorageState.autoSaveEnabled) {
      fileStorageActions.saveToFile(collectData());
    }
  }, [rules, uploadData, displayData, checkResults, checkSummary, fileStorageActions, fileStorageState.autoSaveEnabled, collectData]);

  // Rule actions
  const addRule = useCallback((rule: SalesCostCheckRule) => {
    setRules(prev => [...prev, rule]);
  }, []);

  const updateRule = useCallback((updatedRule: SalesCostCheckRule) => {
    setRules(prev => prev.map(rule =>
      rule.id === updatedRule.id ? updatedRule : rule
    ));
  }, []);

  const deleteRule = useCallback((ruleId: string) => {
    setRules(prev => prev.filter(rule => rule.id !== ruleId));
  }, []);

  // Upload data setter with auto-save trigger
  const setUploadData = useCallback((data: SalesCostUploadRecord[]) => {
    setUploadDataState(data);
  }, []);

  // Display data setter
  const setDisplayData = useCallback((data: SalesCostDisplayRecord[]) => {
    setDisplayDataState(data);
  }, []);

  // Transform data
  const transformData = useCallback(() => {
    const transformed = transformUploadData(uploadData, ohMasterData);
    setDisplayDataState(transformed);
  }, [uploadData]);

  // Update a single display record
  const updateDisplayRecord = useCallback((index: number, record: SalesCostDisplayRecord) => {
    setDisplayDataState(prev => {
      const newData = [...prev];
      newData[index] = record;
      return newData;
    });
  }, []);

  // Delete a single display record
  const deleteDisplayRecord = useCallback((index: number) => {
    setDisplayDataState(prev => prev.filter((_, i) => i !== index));
  }, []);

  // Execute checks - only use Released rules
  const executeChecks = useCallback(() => {
    const releasedRules = rules.filter(r => r.status === 'Released');
    const { results, summary } = executeAllCrossChecks(releasedRules, displayData);
    setCheckResults(results);
    setCheckSummary(summary);
  }, [rules, displayData]);

  // Clear all data
  const clearAllData = useCallback(async () => {
    setRules([]);
    setUploadDataState([]);
    setDisplayDataState([]);
    setCheckResults([]);
    setCheckSummary(null);
    await fileStorageActions.resetFileAssociation();
    shouldAutoSave.current = false;
  }, [fileStorageActions]);

  // Reset to demo data
  const resetToDemo = useCallback(async () => {
    setRules(sampleCheckRules);
    setUploadDataState(sampleUploadData);
    setDisplayDataState(sampleDisplayData);
    setCheckResults([]);
    setCheckSummary(null);
    await fileStorageActions.resetFileAssociation();
    shouldAutoSave.current = true;
  }, [fileStorageActions]);

  // Load demo data (startup action)
  const loadDemoData = useCallback(() => {
    setRules(sampleCheckRules);
    setUploadDataState(sampleUploadData);
    setDisplayDataState(sampleDisplayData);
    setCheckResults([]);
    setCheckSummary(null);
    setDataLoaded(true);
    setIsFirstVisit(false);
    markVisited();
    shouldAutoSave.current = true;
  }, []);

  // Load data from file (startup action)
  const loadFileData = useCallback(async () => {
    try {
      const data = await fileStorageActions.loadFromFile();
      if (data) {
        setRules(data.rules as SalesCostCheckRule[]);
        setUploadDataState(data.uploadData as SalesCostUploadRecord[]);
        setDisplayDataState(data.displayData as SalesCostDisplayRecord[]);
        setCheckResults(data.checkResults as CheckResult[]);
        setCheckSummary(data.checkSummary as CheckSummary | null);
        setDataLoaded(true);
        setIsFirstVisit(false);
        markVisited();
        shouldAutoSave.current = true;
      }
    } catch (err) {
      console.error('Failed to load file:', err);
      throw err;
    }
  }, [fileStorageActions]);

  // Auto-load from restored file handle on first visit
  useEffect(() => {
    if (isFirstVisit && fileStorageState.restoredFromIDB && fileStorageState.fileHandle) {
      const handle = fileStorageState.fileHandle;
      (async () => {
        try {
          // Verify permission first
          // @ts-expect-error - permission methods not in types
          const perm = await handle.queryPermission({ mode: 'readwrite' });
          if (perm !== 'granted') {
            // Permission lost — don't auto-load, show welcome dialog
            return;
          }
          const file = await handle.getFile();
          const text = await file.text();
          const data = JSON.parse(text) as AppDataFile;
          setRules(data.rules as SalesCostCheckRule[]);
          setUploadDataState(data.uploadData as SalesCostUploadRecord[]);
          setDisplayDataState(data.displayData as SalesCostDisplayRecord[]);
          setCheckResults(data.checkResults as CheckResult[]);
          setCheckSummary(data.checkSummary as CheckSummary | null);
          setDataLoaded(true);
          setIsFirstVisit(false);
          markVisited();
          shouldAutoSave.current = true;
        } catch {
          // If auto-load fails (file deleted, moved, etc.), let user choose manually
          // Don't mark as not-first-visit so welcome dialog stays open
        }
      })();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isFirstVisit, fileStorageState.restoredFromIDB]);

  // Pick save location
  const pickSaveLocation = useCallback(async () => {
    await fileStorageActions.pickSaveLocation(collectData());
  }, [fileStorageActions, collectData]);

  // Load from file (general)
  const loadFromFile = useCallback(async () => {
    await loadFileData();
  }, [loadFileData]);

  const value: AppState = {
    rules,
    addRule,
    updateRule,
    deleteRule,
    uploadData,
    setUploadData,
    displayData,
    setDisplayData,
    transformData,
    updateDisplayRecord,
    deleteDisplayRecord,
    checkResults,
    checkSummary,
    executeChecks,
    currentPage,
    setCurrentPage,
    clearAllData,
    resetToDemo,
    fileStorage: {
      hasFileAssociation: fileStorageState.hasFileAssociation,
      autoSaveEnabled: fileStorageState.autoSaveEnabled,
      lastSaved: fileStorageState.lastSaved,
      isSaving: fileStorageState.isSaving,
      fileApiSupported: fileStorageState.fileApiSupported,
      restoredFromIDB: fileStorageState.restoredFromIDB,
    },
    pickSaveLocation,
    loadFromFile,
    toggleAutoSave: fileStorageActions.toggleAutoSave,
    resetFileAssociation: fileStorageActions.resetFileAssociation,
    dataLoaded,
    isFirstVisit,
    loadDemoData,
    loadFileData,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
