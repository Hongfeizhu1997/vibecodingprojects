import { useState } from 'react';
import { useApp } from '@/store/AppContext';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import {
  LayoutDashboard,
  FileUp,
  Table,
  ClipboardCheck,
  Settings,
  Play,
  Database,
  Trash2,
  RotateCcw,
  AlertTriangle,
  X,
  Save,
  FolderOpen,
  CheckCircle,
  Loader2
} from 'lucide-react';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'upload', label: 'Upload Data', icon: FileUp },
  { id: 'display', label: 'Display Data', icon: Table },
  { id: 'rules', label: 'Check Rules', icon: ClipboardCheck },
  { id: 'designer', label: 'Rule Designer', icon: Settings },
  { id: 'execute', label: 'Execute Check', icon: Play },
];

export function Navigation() {
  const {
    currentPage,
    setCurrentPage,
    clearAllData,
    resetToDemo,
    fileStorage,
    pickSaveLocation,
    loadFromFile,
    toggleAutoSave,
  } = useApp();

  const [dataMenuOpen, setDataMenuOpen] = useState(false);
  const [clearDialogOpen, setClearDialogOpen] = useState(false);
  const [resetDialogOpen, setResetDialogOpen] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [isLoadingFile, setIsLoadingFile] = useState(false);

  const handlePickSaveLocation = async () => {
    setDataMenuOpen(false);
    await pickSaveLocation();
  };

  const handleLoadFromFile = async () => {
    setDataMenuOpen(false);
    setLoadError(null);
    setIsLoadingFile(true);
    try {
      await loadFromFile();
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Failed to load file');
    } finally {
      setIsLoadingFile(false);
    }
  };

  const handleClearAll = async () => {
    await clearAllData();
    setClearDialogOpen(false);
    setDataMenuOpen(false);
  };

  const handleResetDemo = async () => {
    await resetToDemo();
    setResetDialogOpen(false);
    setDataMenuOpen(false);
  };

  return (
    <>
      <nav className="bg-gradient-to-r from-blue-900 via-indigo-900 to-purple-900 text-white p-4 shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm">
              <span className="text-xl">📊</span>
            </div>
            <div>
              <h1 className="text-xl font-bold">Sales Cost Cross Check</h1>
              <p className="text-xs text-blue-200">Global Validation System</p>
            </div>
          </div>

          <div className="flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              return (
                <Button
                  key={item.id}
                  variant={isActive ? 'secondary' : 'ghost'}
                  size="sm"
                  onClick={() => setCurrentPage(item.id)}
                  className={`
                    flex items-center gap-2 transition-all duration-200
                    ${isActive
                      ? 'bg-white text-blue-900 shadow-md font-medium'
                      : 'text-blue-100 hover:bg-white/10 hover:text-white'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden md:inline">{item.label}</span>
                </Button>
              );
            })}

            {/* Data Management Dropdown */}
            <div className="relative ml-2 pl-2 border-l border-white/20">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setDataMenuOpen(!dataMenuOpen)}
                className={`
                  flex items-center gap-2 transition-all duration-200
                  ${dataMenuOpen
                    ? 'bg-white/20 text-white'
                    : 'text-blue-100 hover:bg-white/10 hover:text-white'
                  }
                `}
              >
                <Database className="w-4 h-4" />
                <span className="hidden md:inline">Data</span>
                {fileStorage.isSaving && (
                  <Loader2 className="w-3 h-3 animate-spin" />
                )}
                {!fileStorage.isSaving && fileStorage.lastSaved && (
                  <CheckCircle className="w-3 h-3 text-green-400" />
                )}
              </Button>

              {dataMenuOpen && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setDataMenuOpen(false)} />
                  <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-xl border border-gray-200 z-20 overflow-hidden">
                    {/* Status header */}
                    <div className="p-3 border-b bg-gray-50">
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Data Management</p>
                      {fileStorage.hasFileAssociation ? (
                        <p className="text-xs text-green-600 mt-1">
                          Linked to file — auto-save every 10 min
                        </p>
                      ) : (
                        <p className="text-xs text-amber-600 mt-1">
                          No file linked — click "Pick Save Location" to enable auto-save
                        </p>
                      )}
                      {fileStorage.lastSaved && (
                        <p className="text-xs text-gray-400 mt-0.5">
                          Last saved: {fileStorage.lastSaved.toLocaleTimeString()}
                        </p>
                      )}
                    </div>

                    {/* Pick Save Location */}
                    <button
                      onClick={handlePickSaveLocation}
                      className="w-full flex items-center gap-3 px-4 py-3 text-sm text-gray-700 hover:bg-blue-50 transition-colors text-left"
                    >
                      <Save className="w-4 h-4 text-blue-600" />
                      <div>
                        <p className="font-medium">Pick Save Location</p>
                        <p className="text-xs text-gray-400">Choose where to save your data file</p>
                      </div>
                    </button>

                    {/* Load from File */}
                    <button
                      onClick={handleLoadFromFile}
                      disabled={isLoadingFile}
                      className="w-full flex items-center gap-3 px-4 py-3 text-sm text-gray-700 hover:bg-blue-50 transition-colors text-left disabled:opacity-50"
                    >
                      <FolderOpen className="w-4 h-4 text-blue-600" />
                      <div>
                        <p className="font-medium">{isLoadingFile ? 'Loading...' : 'Load from File'}</p>
                        <p className="text-xs text-gray-400">Open an existing data file</p>
                      </div>
                    </button>

                    {/* Auto-save toggle */}
                    <button
                      onClick={() => { toggleAutoSave(); }}
                      className="w-full flex items-center gap-3 px-4 py-3 text-sm text-gray-700 hover:bg-blue-50 transition-colors text-left border-t"
                    >
                      <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${fileStorage.autoSaveEnabled ? 'border-green-500 bg-green-500' : 'border-gray-300'}`}>
                        {fileStorage.autoSaveEnabled && <CheckCircle className="w-3 h-3 text-white" />}
                      </div>
                      <div>
                        <p className="font-medium">Auto-Save {fileStorage.autoSaveEnabled ? 'On' : 'Off'}</p>
                        <p className="text-xs text-gray-400">Automatically save after changes</p>
                      </div>
                    </button>

                    {/* Reset to Demo */}
                    <button
                      onClick={() => { setResetDialogOpen(true); setDataMenuOpen(false); }}
                      className="w-full flex items-center gap-3 px-4 py-3 text-sm text-gray-700 hover:bg-blue-50 transition-colors text-left border-t"
                    >
                      <RotateCcw className="w-4 h-4 text-blue-600" />
                      <div>
                        <p className="font-medium">Reset to Demo Data</p>
                        <p className="text-xs text-gray-400">Restore original sample data</p>
                      </div>
                    </button>

                    {/* Clear All */}
                    <button
                      onClick={() => { setClearDialogOpen(true); setDataMenuOpen(false); }}
                      className="w-full flex items-center gap-3 px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors text-left border-t"
                    >
                      <Trash2 className="w-4 h-4" />
                      <div>
                        <p className="font-medium">Clear All Data</p>
                        <p className="text-xs text-gray-400">Remove all stored data</p>
                      </div>
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Load Error Dialog */}
      <Dialog open={!!loadError} onOpenChange={() => setLoadError(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="w-5 h-5" />
              Load Failed
            </DialogTitle>
            <DialogDescription>{loadError}</DialogDescription>
          </DialogHeader>
          <div className="flex justify-end">
            <Button variant="outline" onClick={() => setLoadError(null)}>OK</Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Clear All Confirmation */}
      <Dialog open={clearDialogOpen} onOpenChange={setClearDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="w-5 h-5" />
              Clear All Data
            </DialogTitle>
            <DialogDescription>
              This will remove all data from the app. Your saved file on disk will not be affected. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-2 mt-4">
            <Button variant="outline" onClick={() => setClearDialogOpen(false)}>
              <X className="w-4 h-4 mr-2" />
              Cancel
            </Button>
            <Button onClick={handleClearAll} className="bg-red-600 hover:bg-red-700">
              <Trash2 className="w-4 h-4 mr-2" />
              Clear All
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Reset to Demo Confirmation */}
      <Dialog open={resetDialogOpen} onOpenChange={setResetDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-blue-600">
              <RotateCcw className="w-5 h-5" />
              Reset to Demo Data
            </DialogTitle>
            <DialogDescription>
              This will replace all current data with the original demo data. Any custom rules or uploaded data will be overwritten.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-2 mt-4">
            <Button variant="outline" onClick={() => setResetDialogOpen(false)}>
              <X className="w-4 h-4 mr-2" />
              Cancel
            </Button>
            <Button onClick={handleResetDemo} className="bg-blue-600 hover:bg-blue-700">
              <RotateCcw className="w-4 h-4 mr-2" />
              Reset
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
