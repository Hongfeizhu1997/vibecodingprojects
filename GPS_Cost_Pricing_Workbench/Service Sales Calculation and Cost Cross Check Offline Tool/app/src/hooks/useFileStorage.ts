import { useState, useCallback, useRef, useEffect } from 'react';

export interface AppDataFile {
  version: number;
  exportDate: string;
  rules: unknown;
  uploadData: unknown;
  displayData: unknown;
  checkResults: unknown;
  checkSummary: unknown | null;
}

// Type augmentation for File System Access API
declare global {
  interface Window {
    showSaveFilePicker?: (options?: {
      suggestedName?: string;
      types?: Array<{
        description?: string;
        accept: Record<string, string[]>;
      }>;
    }) => Promise<FileSystemFileHandle>;
    showOpenFilePicker?: (options?: {
      types?: Array<{
        description?: string;
        accept: Record<string, string[]>;
      }>;
      multiple?: boolean;
    }) => Promise<FileSystemFileHandle[]>;
  }
}

const FILE_NAME = 'sales_cost_cross_check_data.json';
const MIME_TYPE = 'application/json';
const FILE_EXTENSION = '.json';
const IDB_DB_NAME = 'scc_file_storage';
const IDB_STORE_NAME = 'file_handle';
const IDB_KEY = 'active_handle';

// Auto-save interval: 10 minutes (600,000 ms)
const AUTO_SAVE_INTERVAL_MS = 600000;

// Check if File System Access API is supported
const supportsFileSystemAPI = (): boolean => {
  return typeof window !== 'undefined' && 'showSaveFilePicker' in window && 'showOpenFilePicker' in window;
};

// IndexedDB helpers to persist file handle across page refreshes
function openIDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(IDB_DB_NAME, 1);
    req.onerror = () => reject(req.error);
    req.onsuccess = () => resolve(req.result);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(IDB_STORE_NAME)) {
        db.createObjectStore(IDB_STORE_NAME);
      }
    };
  });
}

async function saveHandleToIDB(handle: FileSystemFileHandle): Promise<void> {
  const db = await openIDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(IDB_STORE_NAME, 'readwrite');
    const store = tx.objectStore(IDB_STORE_NAME);
    const req = store.put(handle, IDB_KEY);
    req.onsuccess = () => resolve();
    req.onerror = () => reject(req.error);
    tx.oncomplete = () => db.close();
  });
}

async function getHandleFromIDB(): Promise<FileSystemFileHandle | null> {
  try {
    const db = await openIDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(IDB_STORE_NAME, 'readonly');
      const store = tx.objectStore(IDB_STORE_NAME);
      const req = store.get(IDB_KEY);
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => reject(req.error);
      tx.oncomplete = () => db.close();
    });
  } catch {
    return null;
  }
}

async function clearHandleFromIDB(): Promise<void> {
  try {
    const db = await openIDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(IDB_STORE_NAME, 'readwrite');
      const store = tx.objectStore(IDB_STORE_NAME);
      const req = store.delete(IDB_KEY);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
      tx.oncomplete = () => db.close();
    });
  } catch {
    // ignore
  }
}

// Verify and request permission for a stored handle
async function verifyHandlePermission(handle: FileSystemFileHandle): Promise<boolean> {
  try {
    // @ts-expect-error - FileSystemFileHandle types may not include permission methods
    let perm = await handle.queryPermission({ mode: 'readwrite' });
    if (perm === 'granted') return true;
    // @ts-expect-error
    perm = await handle.requestPermission({ mode: 'readwrite' });
    return perm === 'granted';
  } catch {
    // Older implementations may not have permission methods
    return true;
  }
}

// Create a JSON blob from data
const createDataBlob = (data: Omit<AppDataFile, 'version' | 'exportDate'>): Blob => {
  const fileData: AppDataFile = {
    version: 1,
    exportDate: new Date().toISOString(),
    ...data,
  };
  const json = JSON.stringify(fileData, null, 2);
  return new Blob([json], { type: MIME_TYPE });
};

export interface FileStorageState {
  fileHandle: FileSystemFileHandle | null;
  hasFileAssociation: boolean;
  autoSaveEnabled: boolean;
  lastSaved: Date | null;
  isSaving: boolean;
  fileApiSupported: boolean;
  restoredFromIDB: boolean;
}

export interface FileStorageActions {
  saveToFile: (data: Omit<AppDataFile, 'version' | 'exportDate'>) => Promise<void>;
  loadFromFile: () => Promise<AppDataFile | null>;
  pickSaveLocation: (data: Omit<AppDataFile, 'version' | 'exportDate'>) => Promise<void>;
  toggleAutoSave: () => void;
  resetFileAssociation: () => Promise<void>;
}

export function useFileStorage(): [FileStorageState, FileStorageActions] {
  const [fileHandle, setFileHandle] = useState<FileSystemFileHandle | null>(null);
  const [hasFileAssociation, setHasFileAssociation] = useState(false);
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [restoredFromIDB, setRestoredFromIDB] = useState(false);
  const autoSaveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fileApiSupported = supportsFileSystemAPI();

  // On mount: try to restore file handle from IndexedDB
  useEffect(() => {
    if (!fileApiSupported) return;

    let cancelled = false;
    (async () => {
      try {
        const storedHandle = await getHandleFromIDB();
        if (cancelled || !storedHandle) return;

        const hasPermission = await verifyHandlePermission(storedHandle);
        if (!hasPermission) {
          // Permission lost, clear from IDB
          await clearHandleFromIDB();
          return;
        }

        setFileHandle(storedHandle);
        setHasFileAssociation(true);
        setRestoredFromIDB(true);
      } catch {
        // ignore restore errors
      }
    })();

    return () => { cancelled = true; };
  }, [fileApiSupported]);

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (autoSaveTimer.current) {
        clearTimeout(autoSaveTimer.current);
      }
    };
  }, []);

  const saveToFile = useCallback(
    async (data: Omit<AppDataFile, 'version' | 'exportDate'>) => {
      if (!autoSaveEnabled) return;

      if (autoSaveTimer.current) {
        clearTimeout(autoSaveTimer.current);
      }

      autoSaveTimer.current = setTimeout(async () => {
        setIsSaving(true);
        try {
          const blob = createDataBlob(data);

          if (fileHandle && fileApiSupported) {
            // Re-verify permission before writing
            const hasPermission = await verifyHandlePermission(fileHandle);
            if (hasPermission) {
              const writable = await fileHandle.createWritable();
              await writable.write(blob);
              await writable.close();
              setLastSaved(new Date());
            } else {
              // Permission lost, clear handle
              setFileHandle(null);
              setHasFileAssociation(false);
              await clearHandleFromIDB();
            }
          }
          // If no fileHandle, we do nothing — user must "Pick Save Location" first
        } catch {
          // On error, clear the association so user can re-pick
          setFileHandle(null);
          setHasFileAssociation(false);
          await clearHandleFromIDB();
        } finally {
          setIsSaving(false);
        }
      }, AUTO_SAVE_INTERVAL_MS);
    },
    [autoSaveEnabled, fileHandle, fileApiSupported]
  );

  const pickSaveLocation = useCallback(
    async (data: Omit<AppDataFile, 'version' | 'exportDate'>) => {
      if (!fileApiSupported) {
        // Browser doesn't support File System API — must download
        alert('Your browser does not support the File System Access API.\n\nTo auto-save to the same file, please use Chrome or Edge.\n\nAlternatively, click "Export" to manually download your data file.');
        return;
      }

      setIsSaving(true);
      try {
        const blob = createDataBlob(data);

        const handle = await window.showSaveFilePicker!({
          suggestedName: FILE_NAME,
          types: [
            {
              description: 'Sales Cost Cross Check Data',
              accept: { [MIME_TYPE]: [FILE_EXTENSION] },
            },
          ],
        });

        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();

        setFileHandle(handle);
        setHasFileAssociation(true);
        setLastSaved(new Date());

        // Persist handle to IndexedDB for cross-session restore
        await saveHandleToIDB(handle);
      } catch (err: unknown) {
        const error = err as Error;
        if (error.name === 'AbortError') {
          // User cancelled picker — no action needed
          return;
        }
        console.warn('Save location pick failed:', err);
      } finally {
        setIsSaving(false);
      }
    },
    [fileApiSupported]
  );

  const loadFromFile = useCallback(async (): Promise<AppDataFile | null> => {
    try {
      // Always show file picker for explicit load — lets user choose which file to open
      if (fileApiSupported) {
        const [handle] = await window.showOpenFilePicker!({
          types: [
            {
              description: 'Sales Cost Cross Check Data',
              accept: { [MIME_TYPE]: [FILE_EXTENSION] },
            },
          ],
          multiple: false,
        });

        const file = await handle.getFile();
        const text = await file.text();
        const data = JSON.parse(text) as AppDataFile;

        // Validate the loaded data has the expected shape
        if (!data || typeof data !== 'object') {
          throw new Error('Invalid file format');
        }

        setFileHandle(handle);
        setHasFileAssociation(true);

        // Persist handle to IndexedDB for auto-save
        await saveHandleToIDB(handle);

        return data;
      }

      return null;
    } catch (err: unknown) {
      const error = err as Error;
      if (error.name === 'AbortError') {
        return null; // User cancelled
      }
      console.error('Load file error:', err);
      throw new Error('Failed to read data file. Please ensure it is a valid JSON file from this app.');
    }
  }, [fileApiSupported]);

  const toggleAutoSave = useCallback(() => {
    setAutoSaveEnabled((prev) => !prev);
  }, []);

  const resetFileAssociation = useCallback(async () => {
    setFileHandle(null);
    setHasFileAssociation(false);
    await clearHandleFromIDB();
  }, []);

  const state: FileStorageState = {
    fileHandle,
    hasFileAssociation,
    autoSaveEnabled,
    lastSaved,
    isSaving,
    fileApiSupported,
    restoredFromIDB,
  };

  const actions: FileStorageActions = {
    saveToFile,
    loadFromFile,
    pickSaveLocation,
    toggleAutoSave,
    resetFileAssociation,
  };

  return [state, actions];
}
