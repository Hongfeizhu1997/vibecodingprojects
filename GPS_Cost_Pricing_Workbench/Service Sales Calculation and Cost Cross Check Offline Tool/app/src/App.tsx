import { useState } from 'react';
import { AppProvider, useApp } from '@/store/AppContext';
import { Navigation } from '@/components/Navigation';
import { Dashboard } from '@/pages/Dashboard';
import { UploadPage } from '@/pages/UploadPage';
import { DisplayPage } from '@/pages/DisplayPage';
import { RulesPage } from '@/pages/RulesPage';
import { RuleDesigner } from '@/pages/RuleDesigner';
import { ExecutePage } from '@/pages/ExecutePage';
import { Toaster } from '@/components/ui/sonner';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import {
  FileUp,
  Database,
  AlertTriangle
} from 'lucide-react';

function StartupDialog() {
  const { isFirstVisit, loadDemoData, loadFileData, fileStorage } = useApp();
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  if (!isFirstVisit) return null;

  const handleLoadFile = async () => {
    setLoading(true);
    setLoadError(null);
    try {
      await loadFileData();
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Failed to load file');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={true}>
      <DialogContent className="max-w-lg" onPointerDownOutside={(e) => e.preventDefault()}>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <Database className="w-6 h-6 text-blue-600" />
            Welcome to Sales Cost Cross Check
          </DialogTitle>
          <DialogDescription>
            Your data is now stored in a local file that works across all browsers. Choose how to get started:
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3 py-4">
          {fileStorage.fileApiSupported ? (
            <Button
              onClick={handleLoadFile}
              disabled={loading}
              className="w-full h-auto py-4 justify-start gap-4 bg-blue-600 hover:bg-blue-700"
            >
              <FileUp className="w-6 h-6 flex-shrink-0" />
              <div className="text-left">
                <p className="font-semibold">{loading ? 'Loading...' : 'Load from Data File'}</p>
                <p className="text-xs text-blue-200 font-normal">Select your existing sales_cost_cross_check_data.json file</p>
              </div>
            </Button>
          ) : (
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-amber-800">File System Access Not Available</p>
                  <p className="text-xs text-amber-700 mt-1">
                    Your browser does not support the File System Access API. Data will be auto-saved as downloads. To use file-based storage, please use Chrome or Edge.
                  </p>
                </div>
              </div>
            </div>
          )}

          <Button
            onClick={loadDemoData}
            disabled={loading}
            variant="outline"
            className="w-full h-auto py-4 justify-start gap-4"
          >
            <Database className="w-6 h-6 text-gray-500 flex-shrink-0" />
            <div className="text-left">
              <p className="font-semibold text-gray-700">Use Demo Data</p>
              <p className="text-xs text-gray-400 font-normal">Start with sample data to explore the app</p>
            </div>
          </Button>
        </div>

        {loadError && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-3 flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-700">{loadError}</p>
          </div>
        )}

        <div className="text-xs text-gray-400 text-center border-t pt-3">
          Data is auto-saved to a file after every change. Use the <b>Data</b> menu to manage your file.
        </div>
      </DialogContent>
    </Dialog>
  );
}

function AppContent() {
  const { currentPage, dataLoaded } = useApp();

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <main className="pb-8">
        {dataLoaded && currentPage === 'dashboard' && <Dashboard />}
        {dataLoaded && currentPage === 'upload' && <UploadPage />}
        {dataLoaded && currentPage === 'display' && <DisplayPage />}
        {dataLoaded && currentPage === 'rules' && <RulesPage />}
        {dataLoaded && currentPage === 'designer' && <RuleDesigner />}
        {dataLoaded && currentPage === 'execute' && <ExecutePage />}
      </main>
      <StartupDialog />
      <Toaster />
    </div>
  );
}

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

export default App;
