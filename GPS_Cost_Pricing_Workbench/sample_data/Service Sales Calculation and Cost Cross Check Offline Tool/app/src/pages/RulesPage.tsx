import { useState, useMemo } from 'react';
import { useApp } from '@/store/AppContext';
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
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { 
  Search, 
  Plus, 
  Edit2, 
  Trash2, 
  Eye,
  FileText,
  CheckCircle,
  AlertCircle,
  ArrowRight
} from 'lucide-react';
import type { SalesCostCheckRule } from '@/types';

export function RulesPage() {
  const { rules, deleteRule, setCurrentPage } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [selectedRule, setSelectedRule] = useState<SalesCostCheckRule | null>(null);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);

  // Filter rules
  const filteredRules = useMemo(() => {
    return rules.filter(rule => {
      const matchesSearch = 
        rule.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rule.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rule.typeOfService.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesStatus = filterStatus === 'all' || rule.status === filterStatus;
      
      return matchesSearch && matchesStatus;
    });
  }, [rules, searchTerm, filterStatus]);

  const handleViewRule = (rule: SalesCostCheckRule) => {
    setSelectedRule(rule);
    setIsViewDialogOpen(true);
  };

  const handleEditRule = (rule: SalesCostCheckRule) => {
    // Store selected rule in session storage for designer page
    sessionStorage.setItem('editRule', JSON.stringify(rule));
    setCurrentPage('designer');
  };

  const handleDeleteRule = (ruleId: string) => {
    if (confirm('Are you sure you want to delete this rule?')) {
      deleteRule(ruleId);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Sales Cost Check Rules</h2>
          <p className="text-gray-500 mt-1">Manage and view all your cross-check rules</p>
        </div>
        <Button 
          onClick={() => {
            sessionStorage.removeItem('editRule');
            setCurrentPage('designer');
          }}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create New Rule
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-900">{rules.length}</p>
              <p className="text-sm text-blue-700">Total Rules</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-2xl font-bold text-green-900">
                {rules.filter(r => r.status === 'Released').length}
              </p>
              <p className="text-sm text-green-700">Released</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-yellow-50 border-yellow-200">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="w-10 h-10 bg-yellow-500 rounded-lg flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-2xl font-bold text-yellow-900">
                {rules.filter(r => r.status === 'Draft').length}
              </p>
              <p className="text-sm text-yellow-700">Draft</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gray-50 border-gray-200">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="w-10 h-10 bg-gray-500 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {rules.filter(r => r.status === 'Retired').length}
              </p>
              <p className="text-sm text-gray-700">Retired</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2 flex-1 min-w-[300px]">
              <Search className="w-4 h-4 text-gray-400" />
              <Input
                placeholder="Search by Rule ID, Description, Type of Service..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="flex-1"
              />
            </div>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Filter by Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="Draft">Draft</SelectItem>
                <SelectItem value="Released">Released</SelectItem>
                <SelectItem value="Retired">Retired</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Rules Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-600" />
            All Rules
            <Badge variant="secondary" className="ml-2">
              {filteredRules.length}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-gray-50">
                  <TableHead className="text-xs">Rule ID</TableHead>
                  <TableHead className="text-xs">Description</TableHead>
                  <TableHead className="text-xs">Compare Factor</TableHead>
                  <TableHead className="text-xs">Grouping Factors</TableHead>
                  <TableHead className="text-xs">Status</TableHead>
                  <TableHead className="text-xs">Valid From</TableHead>
                  <TableHead className="text-xs text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredRules.map((rule) => (
                  <TableRow key={rule.id} className="hover:bg-blue-50/50">
                    <TableCell className="font-mono text-xs py-3">
                      {rule.id}
                    </TableCell>
                    <TableCell className="py-3">
                      <p className="text-sm truncate max-w-[300px]" title={rule.description}>
                        {rule.description}
                      </p>
                    </TableCell>
                    <TableCell className="py-3">
                      <Badge variant="outline" className="text-xs">
                        {rule.compareFactor}
                      </Badge>
                    </TableCell>
                    <TableCell className="py-3">
                      <p className="text-xs text-gray-500">
                        {rule.groupingFactors.length} factors
                      </p>
                    </TableCell>
                    <TableCell className="py-3">
                      <Badge 
                        className={`
                          text-xs
                          ${rule.status === 'Released' ? 'bg-green-100 text-green-800' : ''}
                          ${rule.status === 'Draft' ? 'bg-yellow-100 text-yellow-800' : ''}
                          ${rule.status === 'Retired' ? 'bg-gray-100 text-gray-800' : ''}
                        `}
                      >
                        {rule.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="py-3 text-xs">
                      {rule.validFrom}
                    </TableCell>
                    <TableCell className="py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleViewRule(rule)}
                          className="h-8 w-8"
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleEditRule(rule)}
                          className="h-8 w-8"
                        >
                          <Edit2 className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDeleteRule(rule.id)}
                          className="h-8 w-8 text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* View Rule Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              Rule Details
            </DialogTitle>
            <DialogDescription>
              {selectedRule?.id}
            </DialogDescription>
          </DialogHeader>
          
          {selectedRule && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500">Type of Service</p>
                  <p className="font-medium">{selectedRule.typeOfService}</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500">Status</p>
                  <Badge 
                    className={`
                      ${selectedRule.status === 'Released' ? 'bg-green-100 text-green-800' : ''}
                      ${selectedRule.status === 'Draft' ? 'bg-yellow-100 text-yellow-800' : ''}
                      ${selectedRule.status === 'Retired' ? 'bg-gray-100 text-gray-800' : ''}
                    `}
                  >
                    {selectedRule.status}
                  </Badge>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500">Valid From</p>
                  <p className="font-medium">{selectedRule.validFrom}</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500">Valid To</p>
                  <p className="font-medium">{selectedRule.validTo}</p>
                </div>
              </div>

              <div className="p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-500">GEO</p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {selectedRule.geo.map(g => (
                    <Badge key={g} variant="outline" className="text-xs">{g}</Badge>
                  ))}
                </div>
              </div>

              <div className="p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-500">Description</p>
                <p className="text-sm mt-1">{selectedRule.description}</p>
              </div>

              <div className="p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-500">Grouping Factors ({selectedRule.groupingFactors.length})</p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {selectedRule.groupingFactors.map(f => (
                    <Badge key={f} variant="secondary" className="text-xs">{f}</Badge>
                  ))}
                </div>
              </div>

              <div className="p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-500">Compare Factor</p>
                <p className="font-medium">{selectedRule.compareFactor}</p>
              </div>

              <div className="p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-500">Compare Priority</p>
                <div className="flex items-center gap-1 mt-1 flex-wrap">
                  {selectedRule.comparePriority.map((p, i) => (
                    <span key={p} className="flex items-center">
                      <Badge variant="outline" className="text-xs">{p}</Badge>
                      {i < selectedRule.comparePriority.length - 1 && (
                        <ArrowRight className="w-3 h-3 mx-1 text-gray-400" />
                      )}
                    </span>
                  ))}
                </div>
              </div>

              <div className="p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-500">Check Logic</p>
                <p className="text-sm mt-1">{selectedRule.checkLogic}</p>
              </div>

              <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-xs text-blue-600">Summary Check Logic</p>
                <p className="text-sm mt-1 text-blue-800">{selectedRule.summaryCheckLogic}</p>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
