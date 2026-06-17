import { useState, useMemo } from 'react';
import { useApp } from '@/store/AppContext';
import { useAutoColumnWidths } from '@/hooks/useColumnWidths';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Search,
  Filter,
  Download,
  RefreshCw,
  Eye,
  X
} from 'lucide-react';
import * as XLSX from 'xlsx';

export function DisplayPage() {
  const { displayData, uploadData, transformData } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    posOrApos: 'all',
    country: 'all',
    serviceTier: 'all',
    subServiceTier: 'all',
    term: 'all',
    startingPoint: 'all',
    offeringType: 'all',
    ohName: 'all'
  });
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  // Get unique values for filters (filter out null/undefined/empty values)
  const filterOptions = useMemo(() => ({
    countries: [...new Set(displayData.map(r => r.country).filter(Boolean))].sort() as string[],
    serviceTiers: [...new Set(displayData.map(r => r.serviceTier).filter(Boolean))].sort() as string[],
    subServiceTiers: [...new Set(displayData.map(r => r.subServiceTier).filter(Boolean))].sort() as string[],
    terms: [...new Set(displayData.map(r => r.term).filter(Boolean))].sort() as string[],
    startingPoints: [...new Set(displayData.map(r => r.serviceStartingPoint).filter(Boolean))].sort() as string[],
    offeringTypes: [...new Set(displayData.map(r => r.offeringType).filter(Boolean))].sort() as string[],
    ohNames: [...new Set(displayData.map(r => r.ohName).filter(Boolean))].sort() as string[]
  }), [displayData]);

  // Filter data
  const filteredData = useMemo(() => {
    return displayData.filter(record => {
      const matchesSearch =
        record.servicePN.toLowerCase().includes(searchTerm.toLowerCase()) ||
        record.servicePNShortDescription.toLowerCase().includes(searchTerm.toLowerCase()) ||
        record.ohName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        record.salesMarketingLongDescription.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesFilters =
        (filters.posOrApos === 'all' || record.posOrApos === filters.posOrApos) &&
        (filters.country === 'all' || record.country === filters.country) &&
        (filters.serviceTier === 'all' || record.serviceTier === filters.serviceTier) &&
        (filters.subServiceTier === 'all' || record.subServiceTier === filters.subServiceTier) &&
        (filters.term === 'all' || record.term === filters.term) &&
        (filters.startingPoint === 'all' || record.serviceStartingPoint === filters.startingPoint) &&
        (filters.offeringType === 'all' || record.offeringType === filters.offeringType) &&
        (filters.ohName === 'all' || record.ohName === filters.ohName);

      return matchesSearch && matchesFilters;
    });
  }, [displayData, searchTerm, filters]);

  // Pagination
  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const paginatedData = filteredData.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const activeFilterCount = Object.values(filters).filter(v => v !== 'all').length;

  // Column definitions for auto-width calculation
  const displayColumns = useMemo(() => [
    { key: 'servicePN', label: 'Service PN', minWidth: 120, maxWidth: 180 },
    { key: 'servicePNShortDescription', label: 'Service PN Short Description', minWidth: 150, maxWidth: 250 },
    { key: 'salesMarketingLongDescription', label: 'Sales&Marketing Long Description', minWidth: 180, maxWidth: 350 },
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

  const colWidths = useAutoColumnWidths(paginatedData, displayColumns);

  const handleExport = () => {
    const exportData = filteredData.map(r => ({
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
      'Sales Cost': r.salesCost
    }));

    const ws = XLSX.utils.json_to_sheet(exportData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Transformed Data');
    XLSX.writeFile(wb, `sales_cost_display_${new Date().toISOString().split('T')[0]}.xlsx`);
  };

  const handleRefresh = () => {
    transformData();
  };

  const clearFilters = () => {
    setFilters({
      posOrApos: 'all',
      country: 'all',
      serviceTier: 'all',
      subServiceTier: 'all',
      term: 'all',
      startingPoint: 'all',
      offeringType: 'all',
      ohName: 'all'
    });
    setCurrentPage(1);
  };

  const updateFilter = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Sales Cost Display</h2>
          <p className="text-gray-500 mt-1">
            Transformed data: {displayData.length} records
            {uploadData.length > 0 && ` (from ${uploadData.length} uploaded)`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={handleRefresh}
            className="flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
          <Button
            onClick={handleExport}
            className="bg-green-600 hover:bg-green-700 flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export Excel
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-base">
              <Filter className="w-4 h-4" />
              Filters
              {activeFilterCount > 0 && (
                <Badge variant="secondary" className="ml-2">{activeFilterCount} active</Badge>
              )}
            </CardTitle>
            {activeFilterCount > 0 && (
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                <X className="w-4 h-4 mr-1" />
                Clear All
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="p-4 pt-0">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-3">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-2 top-2.5 text-gray-400" />
              <Input
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8"
              />
            </div>
            <Select value={filters.posOrApos} onValueChange={(v) => updateFilter('posOrApos', v)}>
              <SelectTrigger><SelectValue placeholder="POS/APOS" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All POS/APOS</SelectItem>
                <SelectItem value="POS">POS</SelectItem>
                <SelectItem value="APOS">APOS</SelectItem>
              </SelectContent>
            </Select>
            <Select value={filters.country} onValueChange={(v) => updateFilter('country', v)}>
              <SelectTrigger><SelectValue placeholder="Country" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Countries</SelectItem>
                {filterOptions.countries.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={filters.serviceTier} onValueChange={(v) => updateFilter('serviceTier', v)}>
              <SelectTrigger><SelectValue placeholder="Service Tier" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Tiers</SelectItem>
                {filterOptions.serviceTiers.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={filters.subServiceTier} onValueChange={(v) => updateFilter('subServiceTier', v)}>
              <SelectTrigger><SelectValue placeholder="Sub Service Tier" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sub Tiers</SelectItem>
                {filterOptions.subServiceTiers.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={filters.term} onValueChange={(v) => updateFilter('term', v)}>
              <SelectTrigger><SelectValue placeholder="Term" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Terms</SelectItem>
                {filterOptions.terms.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={filters.startingPoint} onValueChange={(v) => updateFilter('startingPoint', v)}>
              <SelectTrigger><SelectValue placeholder="Starting Point" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Starting Points</SelectItem>
                {filterOptions.startingPoints.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={filters.offeringType} onValueChange={(v) => updateFilter('offeringType', v)}>
              <SelectTrigger><SelectValue placeholder="Offering Type" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Offering Types</SelectItem>
                {filterOptions.offeringTypes.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={filters.ohName} onValueChange={(v) => updateFilter('ohName', v)}>
              <SelectTrigger><SelectValue placeholder="OH Name" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All OH Names</SelectItem>
                {filterOptions.ohNames.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          {activeFilterCount > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              <Badge variant="secondary">{filteredData.length} results</Badge>
              {filters.posOrApos !== 'all' && <Badge>POS/APOS: {filters.posOrApos}</Badge>}
              {filters.country !== 'all' && <Badge>Country: {filters.country}</Badge>}
              {filters.serviceTier !== 'all' && <Badge>Service Tier: {filters.serviceTier}</Badge>}
              {filters.subServiceTier !== 'all' && <Badge>Sub Tier: {filters.subServiceTier}</Badge>}
              {filters.term !== 'all' && <Badge>Term: {filters.term}</Badge>}
              {filters.startingPoint !== 'all' && <Badge>Starting: {filters.startingPoint}</Badge>}
              {filters.offeringType !== 'all' && <Badge>Offering: {filters.offeringType}</Badge>}
              {filters.ohName !== 'all' && <Badge>OH: {filters.ohName}</Badge>}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Data Table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Eye className="w-5 h-5 text-blue-600" />
            Transformed Records
            <Badge variant="secondary" className="ml-2">
              {filteredData.length} records
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-gray-50">
                  {displayColumns.map(col => (
                    <TableHead
                      key={col.key}
                      className="text-xs whitespace-nowrap overflow-hidden text-ellipsis"
                      style={{ width: colWidths[col.key], minWidth: colWidths[col.key], maxWidth: col.maxWidth }}
                      title={col.label}
                    >
                      {col.label}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {paginatedData.map((record, pageIdx) => (
                  <TableRow key={pageIdx} className="hover:bg-blue-50/50 group">
                    <TableCell className="font-mono text-xs py-2 whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['servicePN'], minWidth: colWidths['servicePN'] }} title={record.servicePN}>{record.servicePN}</TableCell>
                      <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['servicePNShortDescription'], minWidth: colWidths['servicePNShortDescription'] }} title={record.servicePNShortDescription}>{record.servicePNShortDescription}</TableCell>
                      <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['salesMarketingLongDescription'], minWidth: colWidths['salesMarketingLongDescription'] }} title={record.salesMarketingLongDescription}>{record.salesMarketingLongDescription}</TableCell>
                      <TableCell className="py-2" style={{ width: colWidths['posOrApos'], minWidth: colWidths['posOrApos'] }}>
                        <Badge variant={record.posOrApos === 'POS' ? 'default' : 'secondary'} className={`text-xs ${record.posOrApos === 'POS' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}`}>
                          {record.posOrApos}
                        </Badge>
                      </TableCell>
                      <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['serviceStartingPoint'], minWidth: colWidths['serviceStartingPoint'] }} title={record.serviceStartingPoint || ''}>{record.serviceStartingPoint || '-'}</TableCell>
                      <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['term'], minWidth: colWidths['term'] }}>{record.term}</TableCell>
                      <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['serviceTier'], minWidth: colWidths['serviceTier'] }} title={record.serviceTier}>{record.serviceTier}</TableCell>
                      <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['subServiceTier'], minWidth: colWidths['subServiceTier'] }} title={record.subServiceTier || ''}>{record.subServiceTier || '-'}</TableCell>
                      <TableCell className="py-2 font-mono text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['ohCode'], minWidth: colWidths['ohCode'] }}>{record.ohCode}</TableCell>
                      <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['ohName'], minWidth: colWidths['ohName'] }} title={record.ohName}>{record.ohName}</TableCell>
                      <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['typeOfService'], minWidth: colWidths['typeOfService'] }} title={record.typeOfService}>{record.typeOfService}</TableCell>
                      <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['subTypeOfService'], minWidth: colWidths['subTypeOfService'] }} title={record.subTypeOfService}>{record.subTypeOfService}</TableCell>
                      <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['offeringType'], minWidth: colWidths['offeringType'] }} title={record.offeringType}>{record.offeringType}</TableCell>
                      <TableCell className="py-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['country'], minWidth: colWidths['country'] }}>{record.country}</TableCell>
                      <TableCell className="py-2 text-right font-medium whitespace-nowrap overflow-hidden text-ellipsis" style={{ width: colWidths['salesCost'], minWidth: colWidths['salesCost'] }}>${record.salesCost.toFixed(4)}</TableCell>
                    </TableRow>
                  ))
                }
              </TableBody>
            </Table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <p className="text-sm text-gray-500">
                Showing {(currentPage - 1) * itemsPerPage + 1} to {Math.min(currentPage * itemsPerPage, filteredData.length)} of {filteredData.length} records
              </p>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1}>Previous</Button>
                <span className="text-sm text-gray-600">Page {currentPage} of {totalPages}</span>
                <Button variant="outline" size="sm" onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages}>Next</Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

    </div>
  );
}
