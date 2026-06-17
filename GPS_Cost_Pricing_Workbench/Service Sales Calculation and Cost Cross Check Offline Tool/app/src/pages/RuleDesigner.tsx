import { useState, useEffect } from 'react';
import { useApp } from '@/store/AppContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Plus, 
  X, 
  Save, 
  RefreshCw,
  ChevronRight,
  ChevronLeft,
  Globe,
  Layers,
  ArrowUpDown,
  FileText,
  CheckCircle
} from 'lucide-react';
import type { SalesCostCheckRule, GroupingFactor } from '@/types';
import { ALL_GROUPING_FACTORS } from '@/types';
import { compareFactorPriorityOptions } from '@/data/sampleData';

const GEO_OPTIONS = ['EMEA', 'NA', 'AP', 'LAS'];
const STATUS_OPTIONS = ['Draft', 'Released', 'Retired'];

export function RuleDesigner() {
  const { rules, addRule, updateRule, setCurrentPage } = useApp();
  
  // Check if editing existing rule
  const [editRuleId, setEditRuleId] = useState<string | null>(null);
  
  // Form state
  const [ruleId, setRuleId] = useState('');
  const [description, setDescription] = useState('');
  const [typeOfService, setTypeOfService] = useState('');
  const [selectedGeo, setSelectedGeo] = useState<string[]>([]);
  const [validFrom, setValidFrom] = useState('');
  const [validTo, setValidTo] = useState('');
  const [createdBy, setCreatedBy] = useState('');
  const [status, setStatus] = useState<'Draft' | 'Released' | 'Retired'>('Draft');
  
  // Grouping factors state
  const [availableFactors, setAvailableFactors] = useState<GroupingFactor[]>(ALL_GROUPING_FACTORS);
  const [selectedFactors, setSelectedFactors] = useState<GroupingFactor[]>([]);
  const [selectedAvailable, setSelectedAvailable] = useState<GroupingFactor | null>(null);
  const [selectedSelected, setSelectedSelected] = useState<GroupingFactor | null>(null);
  
  // Compare factor state
  const [compareFactor, setCompareFactor] = useState<GroupingFactor | ''>('');
  const [comparePriority, setComparePriority] = useState<string[]>([]);
  const [priorityInput, setPriorityInput] = useState('');
  const [serviceTierSelection, setServiceTierSelection] = useState('');

  // Load edit rule on mount
  useEffect(() => {
    const editRuleData = sessionStorage.getItem('editRule');
    if (editRuleData) {
      const rule: SalesCostCheckRule = JSON.parse(editRuleData);
      setEditRuleId(rule.id);
      setRuleId(rule.id);
      setDescription(rule.description);
      setTypeOfService(rule.typeOfService);
      setSelectedGeo(rule.geo);
      setValidFrom(rule.validFrom);
      setValidTo(rule.validTo);
      setCreatedBy(rule.createdBy);
      setStatus(rule.status);
      setSelectedFactors(rule.groupingFactors);
      setAvailableFactors(ALL_GROUPING_FACTORS.filter(f => !rule.groupingFactors.includes(f)));
      setCompareFactor(rule.compareFactor);
      setComparePriority(rule.comparePriority);
    } else {
      // Set defaults for new rule
      const today = new Date().toISOString().split('T')[0];
      setValidFrom(today);
      setValidTo('9999-12-31');
      setCreatedBy('Current User');
    }
  }, []);

  // Toggle GEO selection
  const toggleGeo = (geo: string) => {
    setSelectedGeo(prev => 
      prev.includes(geo) 
        ? prev.filter(g => g !== geo)
        : [...prev, geo]
    );
  };

  // Add factor to selected
  const addFactor = () => {
    if (selectedAvailable && !selectedFactors.includes(selectedAvailable)) {
      setSelectedFactors([...selectedFactors, selectedAvailable]);
      setAvailableFactors(availableFactors.filter(f => f !== selectedAvailable));
      setSelectedAvailable(null);
    }
  };

  // Remove factor from selected
  const removeFactor = () => {
    if (selectedSelected) {
      setAvailableFactors([...availableFactors, selectedSelected]);
      setSelectedFactors(selectedFactors.filter(f => f !== selectedSelected));
      setSelectedSelected(null);
    }
  };

  // Handle compare factor change
  const handleCompareFactorChange = (value: GroupingFactor) => {
    setCompareFactor(value);
    setServiceTierSelection('');
    // Do NOT auto-fill default priority for Service Tier - user must define manually
    if (value !== 'Service Tier') {
      const defaultPriority = compareFactorPriorityOptions[value];
      setComparePriority(defaultPriority || []);
    } else {
      setComparePriority([]);
    }
  };

  // Add priority item
  const addPriorityItem = () => {
    if (priorityInput.trim() && !comparePriority.includes(priorityInput.trim())) {
      setComparePriority([...comparePriority, priorityInput.trim()]);
      setPriorityInput('');
    }
  };

  // Add service tier from dropdown
  const addServiceTierFromDropdown = () => {
    if (serviceTierSelection && !comparePriority.includes(serviceTierSelection)) {
      setComparePriority([...comparePriority, serviceTierSelection]);
      setServiceTierSelection('');
    }
  };

  // Remove priority item
  const removePriorityItem = (index: number) => {
    setComparePriority(comparePriority.filter((_, i) => i !== index));
  };

  // Move priority item up
  const movePriorityUp = (index: number) => {
    if (index > 0) {
      const newPriority = [...comparePriority];
      [newPriority[index - 1], newPriority[index]] = [newPriority[index], newPriority[index - 1]];
      setComparePriority(newPriority);
    }
  };

  // Move priority item down
  const movePriorityDown = (index: number) => {
    if (index < comparePriority.length - 1) {
      const newPriority = [...comparePriority];
      [newPriority[index], newPriority[index + 1]] = [newPriority[index + 1], newPriority[index]];
      setComparePriority(newPriority);
    }
  };

  // Generate description
  const generateDescription = () => {
    if (compareFactor && selectedFactors.length > 0) {
      const desc = `Compare sales cost based on ${compareFactor}: Group ${selectedFactors.join('/')}. Compare Factor: ${compareFactor}.`;
      setDescription(desc);
    }
  };

  // Save rule
  const saveRule = () => {
    if (!ruleId || !compareFactor || selectedFactors.length === 0) {
      alert('Please fill in all required fields');
      return;
    }

    const rule: SalesCostCheckRule = {
      id: ruleId,
      description,
      typeOfService,
      geo: selectedGeo,
      validFrom,
      validTo,
      createdBy,
      createdAt: editRuleId ? rules.find(r => r.id === editRuleId)?.createdAt || new Date().toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
      status,
      groupingFactors: selectedFactors,
      compareFactor,
      comparePriority,
      checkLogic: `Group data by grouping factors, filter by compare priority, then compare sales costs across ${compareFactor.toLowerCase()} to ensure higher values have higher sales costs than lower values.`,
      summaryCheckLogic: `Group data by grouping factors, then compare sales costs across ${compareFactor.toLowerCase()} to ensure higher values have higher sales costs than lower values.`
    };

    if (editRuleId) {
      updateRule(rule);
    } else {
      addRule(rule);
    }

    alert(`Rule ${editRuleId ? 'updated' : 'created'} successfully!`);
    setCurrentPage('rules');
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">
            {editRuleId ? 'Edit Check Rule' : 'Create Check Rule'}
          </h2>
          <p className="text-gray-500 mt-1">
            {editRuleId ? 'Modify existing sales cost check rule' : 'Design a new sales cost cross-check rule'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => setCurrentPage('rules')}>
            Cancel
          </Button>
          <Button onClick={saveRule} className="bg-blue-600 hover:bg-blue-700">
            <Save className="w-4 h-4 mr-2" />
            {editRuleId ? 'Update Rule' : 'Save Rule'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* General Info */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              General Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Rule ID *</Label>
                <Input
                  value={ruleId}
                  onChange={(e) => setRuleId(e.target.value)}
                  placeholder="e.g., DEMO-SUP-EMEA-TERM-01"
                />
              </div>
              <div className="space-y-2">
                <Label>Type of Service</Label>
                <Input
                  value={typeOfService}
                  onChange={(e) => setTypeOfService(e.target.value)}
                  placeholder="e.g., Support Services"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Description</Label>
              <div className="flex gap-2">
                <Textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Enter rule description..."
                  className="flex-1"
                  rows={3}
                />
              </div>
              <Button 
                type="button" 
                variant="outline" 
                size="sm"
                onClick={generateDescription}
                className="text-blue-600 border-blue-200"
              >
                <RefreshCw className="w-3 h-3 mr-1" />
                Auto Generate
              </Button>
            </div>

            <div className="space-y-2">
              <Label>GEO</Label>
              <div className="flex flex-wrap gap-2">
                {GEO_OPTIONS.map((geo) => (
                  <Badge
                    key={geo}
                    variant={selectedGeo.includes(geo) ? 'default' : 'outline'}
                    className={`cursor-pointer px-3 py-1 ${
                      selectedGeo.includes(geo) 
                        ? 'bg-blue-600 hover:bg-blue-700' 
                        : 'hover:bg-gray-100'
                    }`}
                    onClick={() => toggleGeo(geo)}
                  >
                    <Globe className="w-3 h-3 mr-1" />
                    {geo}
                  </Badge>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Valid From</Label>
                <Input
                  type="date"
                  value={validFrom}
                  onChange={(e) => setValidFrom(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>Valid To</Label>
                <Input
                  type="date"
                  value={validTo}
                  onChange={(e) => setValidTo(e.target.value)}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Created By</Label>
                <Input
                  value={createdBy}
                  onChange={(e) => setCreatedBy(e.target.value)}
                  placeholder="Your name"
                />
              </div>
              <div className="space-y-2">
                <Label>Status</Label>
                <Select value={status} onValueChange={(v) => setStatus(v as any)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {STATUS_OPTIONS.map((s) => (
                      <SelectItem key={s} value={s}>{s}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Grouping Factors */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Layers className="w-5 h-5 text-purple-600" />
              Grouping Factors
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              {/* Available */}
              <div className="flex-1">
                <Label className="text-sm text-gray-500 mb-2 block">Available</Label>
                <ScrollArea className="h-[250px] border rounded-lg p-2">
                  <div className="space-y-1">
                    {availableFactors.map((factor) => (
                      <div
                        key={factor}
                        onClick={() => setSelectedAvailable(factor)}
                        className={`p-2 rounded cursor-pointer text-sm transition-colors ${
                          selectedAvailable === factor
                            ? 'bg-blue-100 text-blue-800'
                            : 'hover:bg-gray-100'
                        }`}
                      >
                        {factor}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>

              {/* Buttons */}
              <div className="flex flex-col gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={addFactor}
                  disabled={!selectedAvailable}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={removeFactor}
                  disabled={!selectedSelected}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
              </div>

              {/* Selected */}
              <div className="flex-1">
                <Label className="text-sm text-gray-500 mb-2 block">Selected</Label>
                <ScrollArea className="h-[250px] border rounded-lg p-2">
                  <div className="space-y-1">
                    {selectedFactors.map((factor, index) => (
                      <div
                        key={factor}
                        onClick={() => setSelectedSelected(factor)}
                        className={`p-2 rounded cursor-pointer text-sm transition-colors flex items-center gap-2 ${
                          selectedSelected === factor
                            ? 'bg-green-100 text-green-800'
                            : 'hover:bg-gray-100'
                        }`}
                      >
                        <span className="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs">
                          {index + 1}
                        </span>
                        {factor}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Compare Factor */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ArrowUpDown className="w-5 h-5 text-green-600" />
              Compare Factor
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Compare Factor</Label>
              <Select 
                value={compareFactor} 
                onValueChange={(v) => handleCompareFactorChange(v as GroupingFactor)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select compare factor" />
                </SelectTrigger>
                <SelectContent>
                  {ALL_GROUPING_FACTORS.map((f) => (
                    <SelectItem key={f} value={f}>{f}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Compare Priority (From Low to High)</Label>
                {compareFactor && compareFactor !== 'Service Tier' && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCompareFactorChange(compareFactor as GroupingFactor)}
                    className="text-blue-600 hover:text-blue-700"
                  >
                    <RefreshCw className="w-3 h-3 mr-1" />
                    Reset to Default
                  </Button>
                )}
              </div>
              
              {/* Service Tier Dropdown Helper */}
              {compareFactor === 'Service Tier' && (
                <div className="bg-blue-50 rounded-lg p-3 border border-blue-200 space-y-2">
                  <Label className="text-xs text-blue-700 font-medium">Select Service Tier from List</Label>
                  <div className="flex gap-2">
                    <Select value={serviceTierSelection} onValueChange={setServiceTierSelection}>
                      <SelectTrigger className="flex-1">
                        <SelectValue placeholder="Choose a service tier..." />
                      </SelectTrigger>
                      <SelectContent className="max-h-[300px]">
                        {compareFactorPriorityOptions['Service Tier']?.map((tier) => (
                          <SelectItem key={tier} value={tier}>{tier}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Button
                      type="button"
                      onClick={addServiceTierFromDropdown}
                      disabled={!serviceTierSelection || comparePriority.includes(serviceTierSelection)}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                  {comparePriority.includes(serviceTierSelection) && serviceTierSelection && (
                    <p className="text-xs text-amber-600">This tier is already in the priority list</p>
                  )}
                </div>
              )}

              {/* Manual Input (for all factors including Service Tier as fallback) */}
              <div className="flex gap-2">
                <Input
                  placeholder={compareFactor === 'Service Tier' ? "Or type a custom value..." : "Enter priority value"}
                  value={priorityInput}
                  onChange={(e) => setPriorityInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addPriorityItem()}
                />
                <Button
                  type="button"
                  onClick={addPriorityItem}
                  disabled={!priorityInput.trim()}
                >
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
              
              <ScrollArea className="h-[200px] border rounded-lg p-2">
                <div className="space-y-1">
                  {comparePriority.map((item, index) => (
                    <div
                      key={`${item}-${index}`}
                      className="flex items-center gap-2 p-2 bg-gray-50 rounded"
                    >
                      <span className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold">
                        {index + 1}
                      </span>
                      <span className="flex-1">{item}</span>
                      <div className="flex items-center gap-1">
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => movePriorityUp(index)}
                          disabled={index === 0}
                          className="w-7 h-7"
                        >
                          <ChevronLeft className="w-4 h-4" />
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => movePriorityDown(index)}
                          disabled={index === comparePriority.length - 1}
                          className="w-7 h-7"
                        >
                          <ChevronRight className="w-4 h-4" />
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => removePriorityItem(index)}
                          className="w-7 h-7 text-red-600"
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
              <p className="text-xs text-gray-500">
                {comparePriority.length} priority value(s) defined
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Preview */}
        <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-blue-600" />
              Rule Preview
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="p-3 bg-white rounded-lg shadow-sm">
              <p className="text-xs text-gray-500">Rule ID</p>
              <p className="font-mono font-medium">{ruleId || 'Not set'}</p>
            </div>
            <div className="p-3 bg-white rounded-lg shadow-sm">
              <p className="text-xs text-gray-500">Compare Factor</p>
              <p className="font-medium">{compareFactor || 'Not selected'}</p>
            </div>
            <div className="p-3 bg-white rounded-lg shadow-sm">
              <p className="text-xs text-gray-500">Grouping Factors ({selectedFactors.length})</p>
              <div className="flex flex-wrap gap-1 mt-1">
                {selectedFactors.map(f => (
                  <Badge key={f} variant="secondary" className="text-xs">{f}</Badge>
                ))}
              </div>
            </div>
            <div className="p-3 bg-white rounded-lg shadow-sm">
              <p className="text-xs text-gray-500">Priority Order</p>
              <p className="text-sm mt-1">
                {comparePriority.join(' → ') || 'Not defined'}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
