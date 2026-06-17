import { useState, useCallback, useMemo, useEffect } from 'react';
import { useApp } from '@/store/AppContext';
import { useAutoColumnWidths } from '@/hooks/useColumnWidths';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Upload,
  FileSpreadsheet,
  CheckCircle,
  AlertTriangle,
  Download,
  Eye,
  Trash2,
  Plus,
  Save,
  X,
  Search,
  Filter,
  Edit2,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight
} from 'lucide-react';
import * as XLSX from 'xlsx';
import { parseExcelFile, convertToUploadRecords, transformUploadData } from '@/utils/dataTransform';
import { ohMasterData } from '@/data/sampleData';
import type { SalesCostUploadRecord } from '@/types';

// All required field names for validation (Sub Service Tier is optional)
const REQUIRED_FIELDS: { key: keyof SalesCostUploadRecord; label: string }[] = [
  { key: 'servicePN', label: 'Service PN' },
  { key: 'servicePNShortDescription', label: 'Service PN Short Description' },
  { key: 'salesMarketingLongDescription', label: 'Sales&Marketing Long Description' },
  { key: 'serviceTier', label: 'Service Tier' },
  { key: 'ohCode', label: 'OH Code' },
  { key: 'country', label: 'Country' },
  { key: 'salesCost', label: 'Sales Cost' },
];

// Validate a single record has all required fields (Sub Service Tier is optional)
function validateRecord(record: SalesCostUploadRecord): string | null {
  for (const field of REQUIRED_FIELDS) {
    const value = record[field.key];
    if (value === null || value === undefined || value === '' || (typeof value === 'number' && (isNaN(value) || value === 0))) {
      return `${field.label} is required`;
    }
  }
  return null;
}

export function UploadPage() {
  const { uploadData, setUploadData, setDisplayData, setCurrentPage } = useApp();
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [duplicateWarnings, setDuplicateWarnings] = useState<{ key: string; count: number; rows: number[] }[]>([]);

  // Filter state
  const [filters, setFilters] = useState({
    servicePN: 'all',
    serviceTier: 'all',
    subServiceTier: 'all',
    country: 'all',
    ohCode: 'all',
    search: ''
  });

  // Manual add dialog state
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [newRecord, setNewRecord] = useState<Partial<SalesCostUploadRecord>>({
    servicePN: '',
    servicePNShortDescription: '',
    salesMarketingLongDescription: '',
    serviceTier: '',
    subServiceTier: '',
    ohCode: '',
    country: '',
    salesCost: 0
  });
  const [addError, setAddError] = useState<string | null>(null);

  // Edit dialog state
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState<SalesCostUploadRecord | null>(null);
  const [editingIndex, setEditingIndex] = useState<number>(-1);
  const [editError, setEditError] = useState<string | null>(null);

  // Delete confirmation
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [deleteIndex, setDeleteIndex] = useState<number>(-1);

  // Pagination state
  const [tablePage, setTablePage] = useState(1);
  const itemsPerPage = 20;

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      await processFile(files[0]);
    }
  }, []);

  const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      await processFile(files[0]);
    }
  }, []);

  // Duplicate check function
  const checkDuplicates = (records: SalesCostUploadRecord[]) => {
    const seen = new Map<string, number[]>();
    records.forEach((record, idx) => {
      const key = `${record.servicePN}|${record.country}`;
      if (!seen.has(key)) {
        seen.set(key, []);
      }
      seen.get(key)!.push(idx);
    });

    const duplicates = Array.from(seen.entries())
      .filter(([, rows]) => rows.length > 1)
      .map(([key, rows]) => ({ key, count: rows.length, rows }));

    setDuplicateWarnings(duplicates);
    return duplicates;
  };

  const processFile = async (file: File) => {
    setIsUploading(true);
    setUploadError(null);
    setUploadSuccess(false);
    setDuplicateWarnings([]);

    try {
      if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
        throw new Error('Please upload an Excel file (.xlsx or .xls)');
      }

      const parsedData = await parseExcelFile(file);
      let records = convertToUploadRecords(parsedData);

      if (records.length === 0) {
        throw new Error('No valid records found in the file');
      }

      // Validate all records have required fields
      const invalidRows: number[] = [];
      records = records.filter((record, idx) => {
        const error = validateRecord(record);
        if (error) {
          invalidRows.push(idx + 2); // +2 because row 1 is header
          return false;
        }
        return true;
      });

      if (records.length === 0) {
        throw new Error(`All records are missing required fields. Please check your file. Skipped rows: ${invalidRows.join(', ')}`);
      }

      if (invalidRows.length > 0) {
        setUploadError(`Warning: Skipped ${invalidRows.length} row(s) with missing required fields: rows ${invalidRows.join(', ')}`);
      }

      // Check for duplicates
      const dupWarnings = checkDuplicates(records);

      setUploadData(records);
      setUploadSuccess(true);

      // Auto transform
      const transformed = transformUploadData(records, ohMasterData);
      setDisplayData(transformed);

      if (dupWarnings.length > 0) {
        setUploadError(prev => prev ? `${prev}\nAlso found ${dupWarnings.length} duplicate Service PN + Country combination(s).` : `Warning: Found ${dupWarnings.length} duplicate Service PN + Country combination(s).`);
      }

    } catch (error) {
      setUploadError(error instanceof Error ? error.message : 'Failed to process file');
    } finally {
      setIsUploading(false);
    }
  };

  // Column definitions for auto-width calculation
  const uploadColumns = useMemo(() => [
    { key: '_actions', label: 'Actions', minWidth: 90, maxWidth: 90 },
    { key: 'servicePN', label: 'Service PN', minWidth: 120, maxWidth: 180 },
    { key: 'servicePNShortDescription', label: 'Service PN Short Description', minWidth: 150, maxWidth: 250 },
    { key: 'salesMarketingLongDescription', label: 'Sales&Marketing Long Description', minWidth: 180, maxWidth: 350 },
    { key: 'serviceTier', label: 'Service Tier', minWidth: 120, maxWidth: 200 },
    { key: 'subServiceTier', label: 'Sub Service Tier', minWidth: 120, maxWidth: 200 },
    { key: 'ohCode', label: 'OH Code', minWidth: 100, maxWidth: 140 },
    { key: 'country', label: 'Country', minWidth: 70, maxWidth: 90 },
    { key: 'salesCost', label: 'Sales Cost', minWidth: 110, maxWidth: 140 },
  ], []);

  // Get unique filter options
  const filterOptions = useMemo(() => ({
    servicePNs: [...new Set(uploadData.map(r => r.servicePN).filter(Boolean))].sort() as string[],
    serviceTiers: [...new Set(uploadData.map(r => r.serviceTier).filter(Boolean))].sort() as string[],
    subServiceTiers: [...new Set(uploadData.map(r => r.subServiceTier).filter((v): v is string => !!v))].sort() as string[],
    countries: [...new Set(uploadData.map(r => r.country).filter(Boolean))].sort() as string[],
    ohCodes: [...new Set(uploadData.map(r => r.ohCode).filter(Boolean))].sort() as string[],
  }), [uploadData]);

  // Filtered data
  const filteredData = useMemo(() => {
    return uploadData.filter(record => {
      const matchesSearch =
        filters.search === '' ||
        record.servicePN.toLowerCase().includes(filters.search.toLowerCase()) ||
        record.servicePNShortDescription.toLowerCase().includes(filters.search.toLowerCase()) ||
        record.salesMarketingLongDescription.toLowerCase().includes(filters.search.toLowerCase()) ||
        record.ohCode.toLowerCase().includes(filters.search.toLowerCase()) ||
        record.country.toLowerCase().includes(filters.search.toLowerCase());

      const matchesFilters =
        (filters.servicePN === 'all' || record.servicePN === filters.servicePN) &&
        (filters.serviceTier === 'all' || record.serviceTier === filters.serviceTier) &&
        (filters.subServiceTier === 'all' || record.subServiceTier === filters.subServiceTier) &&
        (filters.country === 'all' || record.country === filters.country) &&
        (filters.ohCode === 'all' || record.ohCode === filters.ohCode);

      return matchesSearch && matchesFilters;
    });
  }, [uploadData, filters]);

  const activeFilterCount = Object.values(filters).filter(v => v !== 'all' && v !== '').length;

  // Paginated data
  const totalPages = Math.max(1, Math.ceil(filteredData.length / itemsPerPage));
  const paginatedData = useMemo(() => {
    const start = (tablePage - 1) * itemsPerPage;
    return filteredData.slice(start, start + itemsPerPage);
  }, [filteredData, tablePage]);

  // Reset to page 1 when filters or data change
  useEffect(() => {
    setTablePage(1);
  }, [uploadData, filters]);

  const colWidths = useAutoColumnWidths(paginatedData, uploadColumns);

  const handleClearData = () => {
    setUploadData([]);
    setUploadSuccess(false);
    setUploadError(null);
    setDuplicateWarnings([]);
  };

  const updateFilter = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      servicePN: 'all',
      serviceTier: 'all',
      subServiceTier: 'all',
      country: 'all',
      ohCode: 'all',
      search: ''
    });
  };

  // Excel export function
  const handleExportExcel = () => {
    const exportData = filteredData.map(r => ({
      'Service PN': r.servicePN,
      'Service PN Short Description': r.servicePNShortDescription,
      'Sales&Marketing Long Description': r.salesMarketingLongDescription,
      'Service Tier': r.serviceTier,
      'Sub Service Tier': r.subServiceTier || '',
      'OH Code': r.ohCode,
      'Country': r.country,
      'Sales Cost': r.salesCost
    }));

    const ws = XLSX.utils.json_to_sheet(exportData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Upload Data');
    XLSX.writeFile(wb, `sales_cost_upload_${new Date().toISOString().split('T')[0]}.xlsx`);
  };

  // ---- Edit / Delete handlers ----

  const handleDeleteRecord = (index: number) => {
    setDeleteIndex(index);
    setDeleteConfirmOpen(true);
  };

  const confirmDelete = () => {
    if (deleteIndex >= 0) {
      const newData = [...uploadData];
      newData.splice(deleteIndex, 1);
      setUploadData(newData);

      // Re-check duplicates after delete
      checkDuplicates(newData);

      // Also update display data
      const transformed = transformUploadData(newData, ohMasterData);
      setDisplayData(transformed);

      if (newData.length === 0) {
        setUploadSuccess(false);
      }
    }
    setDeleteConfirmOpen(false);
    setDeleteIndex(-1);
  };

  const handleEditRecord = (record: SalesCostUploadRecord, index: number) => {
    setEditingRecord({ ...record });
    setEditingIndex(index);
    setEditError(null);
    setEditDialogOpen(true);
  };

  const handleSaveEdit = () => {
    if (!editingRecord || editingIndex < 0) return;

    setEditError(null);

    // Validate ALL required fields
    const error = validateRecord(editingRecord);
    if (error) {
      setEditError(error);
      return;
    }

    const newData = [...uploadData];
    newData[editingIndex] = editingRecord;
    setUploadData(newData);

    // Re-check duplicates after edit
    checkDuplicates(newData);

    // Also update display data
    const transformed = transformUploadData(newData, ohMasterData);
    setDisplayData(transformed);

    setEditDialogOpen(false);
    setEditingRecord(null);
    setEditingIndex(-1);
  };

  // ---- Manual add with ALL fields mandatory ----

  const handleAddRecord = () => {
    setAddError(null);

    const record: SalesCostUploadRecord = {
      servicePN: (newRecord.servicePN || '').trim(),
      servicePNShortDescription: (newRecord.servicePNShortDescription || '').trim(),
      salesMarketingLongDescription: (newRecord.salesMarketingLongDescription || '').trim(),
      serviceTier: (newRecord.serviceTier || '').trim(),
      subServiceTier: (newRecord.subServiceTier || '').trim(),
      ohCode: (newRecord.ohCode || '').trim(),
      country: (newRecord.country || '').trim().toUpperCase(),
      salesCost: Number(newRecord.salesCost) || 0
    };

    // Validate ALL required fields
    const error = validateRecord(record);
    if (error) {
      setAddError(error);
      return;
    }

    // Check for duplicate
    const dupKey = `${record.servicePN}|${record.country}`;
    const existingIndex = uploadData.findIndex(r => r.servicePN === record.servicePN && r.country === record.country);
    if (existingIndex >= 0) {
      const existingDup = duplicateWarnings.find(d => d.key === dupKey);
      if (existingDup) {
        setDuplicateWarnings(prev =>
          prev.map(d => d.key === dupKey ? { ...d, count: d.count + 1, rows: [...d.rows, uploadData.length] } : d)
        );
      } else {
        setDuplicateWarnings(prev => [...prev, { key: dupKey, count: 2, rows: [existingIndex, uploadData.length] }]);
      }
    }

    const newData = [...uploadData, record];
    setUploadData(newData);

    // Auto transform
    const transformed = transformUploadData(newData, ohMasterData);
    setDisplayData(transformed);

    // Reset form
    setNewRecord({
      servicePN: '',
      servicePNShortDescription: '',
      salesMarketingLongDescription: '',
      serviceTier: '',
      subServiceTier: '',
      ohCode: '',
      country: '',
      salesCost: 0
    });
    setAddDialogOpen(false);
    setUploadSuccess(true);
  };

  const downloadTemplate = () => {
    const headers = ['Service PN', 'Service PN Short Description', 'Sales&Marketing Long Description', 'Service Tier', 'Sub Service Tier', 'OH Code', 'Country', 'Sales Cost'];
    const sampleRow = ['5WS1U93867', '1Y Premier Support AIPC', '1Y Premier Support for AIPC upgrade from 1Y Courier/Carry-in', 'Next Gen', 'Sub Tier', 'H00000000NQ1', 'GB', '50.1026'];

    const csvContent = [headers.join(','), sampleRow.join(',')].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sales_cost_upload_template.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Upload Sales Cost Data</h2>
        <p className="text-gray-500 mt-1">Upload your sales cost data from Excel file or add manually</p>
      </div>

      {/* Upload Template Info */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="p-4">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <FileSpreadsheet className="w-5 h-5 text-blue-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-blue-900">Required Format — All Fields Mandatory</h3>
              <p className="text-sm text-blue-700 mt-1">
                Your Excel file must contain all of the following columns (no empty values allowed):
              </p>
              <div className="flex flex-wrap gap-2 mt-2">
                {['Service PN', 'Service PN Short Description', 'Sales&Marketing Long Description', 'Service Tier', 'Sub Service Tier', 'OH Code', 'Country', 'Sales Cost'].map((col) => (
                  <Badge key={col} variant="secondary" className="bg-blue-100 text-blue-800">
                    {col}
                  </Badge>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setAddDialogOpen(true)}
                className="border-blue-600 text-blue-600 hover:bg-blue-100"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Manually
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={downloadTemplate}
                className="border-blue-600 text-blue-600 hover:bg-blue-100"
              >
                <Download className="w-4 h-4 mr-2" />
                Download Template
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Upload Area */}
      <Card>
        <CardContent className="p-6">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`
              border-2 border-dashed rounded-xl p-12 text-center transition-all duration-200
              ${isDragging
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
              }
            `}
          >
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Upload className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              {isDragging ? 'Drop your file here' : 'Drag & drop your Excel file'}
            </h3>
            <p className="text-gray-500 mt-2">or click to browse files</p>
            <input
              type="file"
              accept=".xlsx,.xls"
              onChange={handleFileSelect}
              className="hidden"
              id="file-input"
            />
            <Button
              onClick={() => document.getElementById('file-input')?.click()}
              disabled={isUploading}
              className="mt-4 bg-blue-600 hover:bg-blue-700"
            >
              {isUploading ? 'Uploading...' : 'Select File'}
            </Button>
          </div>

          {/* Alerts */}
          {uploadError && (
            <Alert variant="destructive" className="mt-4">
              <AlertTriangle className="w-4 h-4" />
              <AlertDescription className="whitespace-pre-line">{uploadError}</AlertDescription>
            </Alert>
          )}

          {uploadSuccess && duplicateWarnings.length === 0 && uploadData.length > 0 && (
            <Alert className="mt-4 bg-green-50 border-green-200">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <AlertDescription className="text-green-800">
                Successfully processed {uploadData.length} records! All fields validated. No duplicates found.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Duplicate Warnings */}
      {duplicateWarnings.length > 0 && (
        <Alert variant="destructive" className="border-amber-500 bg-amber-50">
          <AlertTriangle className="w-4 h-4 text-amber-600" />
          <AlertDescription>
            <div className="font-semibold text-amber-800 mb-1">
              Found {duplicateWarnings.length} duplicate Service PN + Country combination(s):
            </div>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {duplicateWarnings.map((dup, idx) => {
                const [pn, country] = dup.key.split('|');
                return (
                  <div key={idx} className="text-sm text-amber-700">
                    {idx + 1}. Service PN <b>{pn}</b> + Country <b>{country}</b>: {dup.count} records (rows: {dup.rows.map(r => r + 1).join(', ')})
                  </div>
                );
              })}
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Data Preview */}
      {uploadData.length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle>Data Preview</CardTitle>
              <CardDescription>{filteredData.length} of {uploadData.length} records{filteredData.length !== uploadData.length ? ' (filtered)' : ''}</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportExcel}
                className="bg-green-600 text-white hover:bg-green-700 border-green-600"
              >
                <Download className="w-4 h-4 mr-2" />
                Export Excel
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage('display')}
              >
                <Eye className="w-4 h-4 mr-2" />
                View Transformed
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearData}
                className="text-red-600 border-red-200 hover:bg-red-50"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Clear All
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {/* Filters */}
            <div className="bg-gray-50 rounded-lg p-3 mb-3">
              <div className="flex items-center gap-2 mb-2">
                <Filter className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Filters</span>
                {activeFilterCount > 0 && (
                  <Badge variant="secondary" className="text-xs">{activeFilterCount} active</Badge>
                )}
                {activeFilterCount > 0 && (
                  <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={clearFilters}>
                    <X className="w-3 h-3 mr-1" />
                    Clear All
                  </Button>
                )}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-2">
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-2 top-2.5 text-gray-400" />
                  <Input
                    placeholder="Search..."
                    value={filters.search}
                    onChange={(e) => updateFilter('search', e.target.value)}
                    className="pl-8 h-8 text-sm"
                  />
                </div>
                <Select value={filters.servicePN} onValueChange={(v) => updateFilter('servicePN', v)}>
                  <SelectTrigger className="h-8 text-sm">
                    <SelectValue placeholder="Service PN" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Service PNs</SelectItem>
                    {filterOptions.servicePNs.map(pn => <SelectItem key={pn} value={pn}>{pn}</SelectItem>)}
                  </SelectContent>
                </Select>
                <Select value={filters.serviceTier} onValueChange={(v) => updateFilter('serviceTier', v)}>
                  <SelectTrigger className="h-8 text-sm">
                    <SelectValue placeholder="Service Tier" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Service Tiers</SelectItem>
                    {filterOptions.serviceTiers.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                  </SelectContent>
                </Select>
                <Select value={filters.subServiceTier} onValueChange={(v) => updateFilter('subServiceTier', v)}>
                  <SelectTrigger className="h-8 text-sm">
                    <SelectValue placeholder="Sub Service Tier" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Sub Tiers</SelectItem>
                    {filterOptions.subServiceTiers.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                  </SelectContent>
                </Select>
                <Select value={filters.country} onValueChange={(v) => updateFilter('country', v)}>
                  <SelectTrigger className="h-8 text-sm">
                    <SelectValue placeholder="Country" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Countries</SelectItem>
                    {filterOptions.countries.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                  </SelectContent>
                </Select>
                <Select value={filters.ohCode} onValueChange={(v) => updateFilter('ohCode', v)}>
                  <SelectTrigger className="h-8 text-sm">
                    <SelectValue placeholder="OH Code" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All OH Codes</SelectItem>
                    {filterOptions.ohCodes.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              {activeFilterCount > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  <Badge variant="secondary" className="text-xs">{filteredData.length} results</Badge>
                  {filters.search && <Badge variant="outline" className="text-xs">Search: {filters.search}</Badge>}
                  {filters.servicePN !== 'all' && <Badge variant="outline" className="text-xs">PN: {filters.servicePN}</Badge>}
                  {filters.serviceTier !== 'all' && <Badge variant="outline" className="text-xs">Tier: {filters.serviceTier}</Badge>}
                  {filters.subServiceTier !== 'all' && <Badge variant="outline" className="text-xs">Sub: {filters.subServiceTier}</Badge>}
                  {filters.country !== 'all' && <Badge variant="outline" className="text-xs">Country: {filters.country}</Badge>}
                  {filters.ohCode !== 'all' && <Badge variant="outline" className="text-xs">OH: {filters.ohCode}</Badge>}
                </div>
              )}
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-gray-50">
                    {uploadColumns.map(col => (
                      <th
                        key={col.key}
                        className="text-left py-2 px-3 font-medium text-gray-500 text-xs whitespace-nowrap overflow-hidden text-ellipsis"
                        style={{ width: colWidths[col.key], minWidth: colWidths[col.key], maxWidth: col.maxWidth }}
                        title={col.label}
                      >
                        {col.label}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {paginatedData.map((record, index) => {
                    const originalIndex = uploadData.indexOf(record);
                    const dupKey = `${record.servicePN}|${record.country}`;
                    const isDuplicate = duplicateWarnings.some(d => d.key === dupKey);

                    return (
                      <tr key={index} className={`border-b hover:bg-gray-50 ${isDuplicate ? 'bg-amber-50' : ''}`}>
                        <td className="py-1 px-2" style={{ width: colWidths['_actions'], minWidth: colWidths['_actions'] }}>
                          <div className="flex items-center gap-0.5">
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-7 w-7"
                              onClick={() => handleEditRecord(record, originalIndex)}
                            >
                              <Edit2 className="w-3.5 h-3.5 text-blue-600" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-7 w-7"
                              onClick={() => handleDeleteRecord(originalIndex)}
                            >
                              <Trash2 className="w-3.5 h-3.5 text-red-600" />
                            </Button>
                          </div>
                        </td>
                        <td className="py-2 px-3 font-mono text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['servicePN'], minWidth: colWidths['servicePN'] }} title={record.servicePN}>
                          <div className="flex items-center gap-1">
                            {record.servicePN}
                            {isDuplicate && <span title="Duplicate: Same Service PN + Country"><AlertTriangle className="w-3 h-3 text-amber-500 inline flex-shrink-0" /></span>}
                          </div>
                        </td>
                        <td className="py-2 px-3 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['servicePNShortDescription'], minWidth: colWidths['servicePNShortDescription'] }} title={record.servicePNShortDescription}>{record.servicePNShortDescription}</td>
                        <td className="py-2 px-3 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['salesMarketingLongDescription'], minWidth: colWidths['salesMarketingLongDescription'] }} title={record.salesMarketingLongDescription}>{record.salesMarketingLongDescription}</td>
                        <td className="py-2 px-3 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['serviceTier'], minWidth: colWidths['serviceTier'] }} title={record.serviceTier}>{record.serviceTier}</td>
                        <td className="py-2 px-3 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['subServiceTier'], minWidth: colWidths['subServiceTier'] }} title={record.subServiceTier || ''}>{record.subServiceTier || '-'}</td>
                        <td className="py-2 px-3 font-mono text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['ohCode'], minWidth: colWidths['ohCode'] }} title={record.ohCode}>{record.ohCode}</td>
                        <td className="py-2 px-3 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['country'], minWidth: colWidths['country'] }} title={record.country}>{record.country}</td>
                        <td className="py-2 px-3 text-right font-medium whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['salesCost'], minWidth: colWidths['salesCost'] }} title={`$${record.salesCost.toFixed(4)}`}>
                          ${record.salesCost.toFixed(4)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            {filteredData.length > itemsPerPage && (
              <div className="flex items-center justify-between mt-4 pt-3 border-t">
                <div className="text-sm text-gray-500">
                  Showing <b>{(tablePage - 1) * itemsPerPage + 1}</b> to <b>{Math.min(tablePage * itemsPerPage, filteredData.length)}</b> of <b>{filteredData.length}</b> records
                </div>
                <div className="flex items-center gap-1">
                  <Button
                    variant="outline"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => setTablePage(1)}
                    disabled={tablePage === 1}
                  >
                    <ChevronsLeft className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => setTablePage(p => Math.max(1, p - 1))}
                    disabled={tablePage === 1}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <span className="text-sm px-3 min-w-[80px] text-center">
                    Page <b>{tablePage}</b> of <b>{totalPages}</b>
                  </span>
                  <Button
                    variant="outline"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => setTablePage(p => Math.min(totalPages, p + 1))}
                    disabled={tablePage === totalPages}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => setTablePage(totalPages)}
                    disabled={tablePage === totalPages}
                  >
                    <ChevronsRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* ---- Manual Add Dialog ---- */}
      <Dialog open={addDialogOpen} onOpenChange={setAddDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Plus className="w-5 h-5 text-blue-600" />
              Add Record Manually
            </DialogTitle>
          </DialogHeader>

          {addError && (
            <Alert variant="destructive" className="mt-2">
              <AlertTriangle className="w-4 h-4" />
              <AlertDescription>{addError}</AlertDescription>
            </Alert>
          )}

          <div className="grid grid-cols-2 gap-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="add-servicePN">Service PN <span className="text-red-500">*</span></Label>
              <Input
                id="add-servicePN"
                value={newRecord.servicePN || ''}
                onChange={(e) => setNewRecord({ ...newRecord, servicePN: e.target.value })}
                placeholder="e.g. 5WS1U93867"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="add-serviceTier">Service Tier <span className="text-red-500">*</span></Label>
              <Input
                id="add-serviceTier"
                value={newRecord.serviceTier || ''}
                onChange={(e) => setNewRecord({ ...newRecord, serviceTier: e.target.value })}
                placeholder="e.g. Next Gen"
              />
            </div>
            <div className="space-y-2 col-span-2">
              <Label htmlFor="add-servicePNShortDescription">Service PN Short Description <span className="text-red-500">*</span></Label>
              <Input
                id="add-servicePNShortDescription"
                value={newRecord.servicePNShortDescription || ''}
                onChange={(e) => setNewRecord({ ...newRecord, servicePNShortDescription: e.target.value })}
                placeholder="e.g. 1Y Premier Support AIPC"
              />
            </div>
            <div className="space-y-2 col-span-2">
              <Label htmlFor="add-salesMarketingLongDescription">Sales&Marketing Long Description <span className="text-red-500">*</span></Label>
              <Input
                id="add-salesMarketingLongDescription"
                value={newRecord.salesMarketingLongDescription || ''}
                onChange={(e) => setNewRecord({ ...newRecord, salesMarketingLongDescription: e.target.value })}
                placeholder="e.g. 1Y Premier Support for AIPC..."
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="add-subServiceTier">Sub Service Tier</Label>
              <Input
                id="add-subServiceTier"
                value={newRecord.subServiceTier || ''}
                onChange={(e) => setNewRecord({ ...newRecord, subServiceTier: e.target.value })}
                placeholder="Optional"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="add-ohCode">OH Code <span className="text-red-500">*</span></Label>
              <Input
                id="add-ohCode"
                value={newRecord.ohCode || ''}
                onChange={(e) => setNewRecord({ ...newRecord, ohCode: e.target.value })}
                placeholder="e.g. H00000000NQ1"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="add-country">Country <span className="text-red-500">*</span></Label>
              <Input
                id="add-country"
                value={newRecord.country || ''}
                onChange={(e) => setNewRecord({ ...newRecord, country: e.target.value.toUpperCase() })}
                placeholder="e.g. GB"
                maxLength={2}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="add-salesCost">Sales Cost <span className="text-red-500">*</span></Label>
              <Input
                id="add-salesCost"
                type="number"
                step="0.0001"
                value={newRecord.salesCost || ''}
                onChange={(e) => setNewRecord({ ...newRecord, salesCost: parseFloat(e.target.value) || 0 })}
                placeholder="e.g. 50.1026"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2 border-t">
            <Button variant="outline" onClick={() => { setAddDialogOpen(false); setAddError(null); }}>
              <X className="w-4 h-4 mr-2" />
              Cancel
            </Button>
            <Button onClick={handleAddRecord} className="bg-blue-600 hover:bg-blue-700">
              <Save className="w-4 h-4 mr-2" />
              Add Record
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* ---- Edit Dialog ---- */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Edit2 className="w-5 h-5 text-blue-600" />
              Edit Record
            </DialogTitle>
          </DialogHeader>

          {editError && (
            <Alert variant="destructive" className="mt-2">
              <AlertTriangle className="w-4 h-4" />
              <AlertDescription>{editError}</AlertDescription>
            </Alert>
          )}

          {editingRecord && (
            <div className="grid grid-cols-2 gap-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="edit-servicePN">Service PN <span className="text-red-500">*</span></Label>
                <Input
                  id="edit-servicePN"
                  value={editingRecord.servicePN}
                  onChange={(e) => setEditingRecord({ ...editingRecord, servicePN: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-serviceTier">Service Tier <span className="text-red-500">*</span></Label>
                <Input
                  id="edit-serviceTier"
                  value={editingRecord.serviceTier}
                  onChange={(e) => setEditingRecord({ ...editingRecord, serviceTier: e.target.value })}
                />
              </div>
              <div className="space-y-2 col-span-2">
                <Label htmlFor="edit-servicePNShortDescription">Service PN Short Description <span className="text-red-500">*</span></Label>
                <Input
                  id="edit-servicePNShortDescription"
                  value={editingRecord.servicePNShortDescription}
                  onChange={(e) => setEditingRecord({ ...editingRecord, servicePNShortDescription: e.target.value })}
                />
              </div>
              <div className="space-y-2 col-span-2">
                <Label htmlFor="edit-salesMarketingLongDescription">Sales&Marketing Long Description <span className="text-red-500">*</span></Label>
                <Input
                  id="edit-salesMarketingLongDescription"
                  value={editingRecord.salesMarketingLongDescription}
                  onChange={(e) => setEditingRecord({ ...editingRecord, salesMarketingLongDescription: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-subServiceTier">Sub Service Tier</Label>
                <Input
                  id="edit-subServiceTier"
                  value={editingRecord.subServiceTier || ''}
                  onChange={(e) => setEditingRecord({ ...editingRecord, subServiceTier: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-ohCode">OH Code <span className="text-red-500">*</span></Label>
                <Input
                  id="edit-ohCode"
                  value={editingRecord.ohCode}
                  onChange={(e) => setEditingRecord({ ...editingRecord, ohCode: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-country">Country <span className="text-red-500">*</span></Label>
                <Input
                  id="edit-country"
                  value={editingRecord.country}
                  onChange={(e) => setEditingRecord({ ...editingRecord, country: e.target.value.toUpperCase() })}
                  maxLength={2}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-salesCost">Sales Cost <span className="text-red-500">*</span></Label>
                <Input
                  id="edit-salesCost"
                  type="number"
                  step="0.0001"
                  value={editingRecord.salesCost}
                  onChange={(e) => setEditingRecord({ ...editingRecord, salesCost: parseFloat(e.target.value) || 0 })}
                />
              </div>
            </div>
          )}

          <div className="flex justify-end gap-2 pt-2 border-t">
            <Button variant="outline" onClick={() => { setEditDialogOpen(false); setEditError(null); }}>
              <X className="w-4 h-4 mr-2" />
              Cancel
            </Button>
            <Button onClick={handleSaveEdit} className="bg-blue-600 hover:bg-blue-700">
              <Save className="w-4 h-4 mr-2" />
              Save Changes
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* ---- Delete Confirm Dialog ---- */}
      <Dialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="w-5 h-5" />
              Confirm Delete
            </DialogTitle>
          </DialogHeader>
          <p className="text-sm text-gray-600 py-4">
            Are you sure you want to delete this record? This action cannot be undone.
          </p>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setDeleteConfirmOpen(false)}>
              Cancel
            </Button>
            <Button onClick={confirmDelete} className="bg-red-600 hover:bg-red-700">
              <Trash2 className="w-4 h-4 mr-2" />
              Delete
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
