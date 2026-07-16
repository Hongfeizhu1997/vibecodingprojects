import { useApp } from '@/store/AppContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  TrendingUp,
  ArrowRight,
  BarChart3,
  Globe,
  Calendar
} from 'lucide-react';

export function Dashboard() {
  const { rules, displayData, checkSummary, setCurrentPage } = useApp();

  const stats = [
    {
      title: 'Total Rules',
      value: rules.length,
      icon: FileText,
      color: 'bg-blue-500',
      onClick: () => setCurrentPage('rules')
    },
    {
      title: 'Active Rules',
      value: rules.filter(r => r.status === 'Released').length,
      icon: CheckCircle,
      color: 'bg-green-500',
      onClick: () => setCurrentPage('rules')
    },
    {
      title: 'Draft Rules',
      value: rules.filter(r => r.status === 'Draft').length,
      icon: AlertCircle,
      color: 'bg-yellow-500',
      onClick: () => setCurrentPage('rules')
    },
    {
      title: 'Data Records',
      value: displayData.length,
      icon: BarChart3,
      color: 'bg-purple-500',
      onClick: () => setCurrentPage('display')
    }
  ];

  const recentRules = rules.slice(0, 5);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
          <p className="text-gray-500 mt-1">Overview of your sales cost cross check system</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="flex items-center gap-1 px-3 py-1">
            <Calendar className="w-3 h-3" />
            {new Date().toLocaleDateString()}
          </Badge>
          <Badge variant="outline" className="flex items-center gap-1 px-3 py-1">
            <Globe className="w-3 h-3" />
            EMEA, NA, AP, LAS
          </Badge>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card 
              key={index} 
              className="cursor-pointer hover:shadow-lg transition-shadow"
              onClick={stat.onClick}
            >
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">{stat.title}</p>
                    <p className="text-3xl font-bold mt-1">{stat.value}</p>
                  </div>
                  <div className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Quick Actions */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="flex flex-wrap gap-3">
            <Button 
              onClick={() => setCurrentPage('upload')}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <FileText className="w-4 h-4 mr-2" />
              Upload Sales Cost Data
            </Button>
            <Button 
              onClick={() => setCurrentPage('designer')}
              variant="outline"
              className="border-blue-600 text-blue-600 hover:bg-blue-50"
            >
              <TrendingUp className="w-4 h-4 mr-2" />
              Create New Rule
            </Button>
            <Button 
              onClick={() => setCurrentPage('execute')}
              variant="outline"
              className="border-green-600 text-green-600 hover:bg-green-50"
            >
              <CheckCircle className="w-4 h-4 mr-2" />
              Execute Cross Check
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Recent Rules */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              Recent Check Rules
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentRules.map((rule) => (
                <div 
                  key={rule.id} 
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                  onClick={() => setCurrentPage('rules')}
                >
                  <div>
                    <p className="font-medium text-sm">{rule.id}</p>
                    <p className="text-xs text-gray-500 truncate max-w-md">{rule.description}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant={rule.status === 'Released' ? 'default' : 'secondary'}
                      className={rule.status === 'Released' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}
                    >
                      {rule.status}
                    </Badge>
                    <ArrowRight className="w-4 h-4 text-gray-400" />
                  </div>
                </div>
              ))}
            </div>
            <Button 
              variant="ghost" 
              className="w-full mt-4 text-blue-600"
              onClick={() => setCurrentPage('rules')}
            >
              View All Rules
            </Button>
          </CardContent>
        </Card>

        {/* Check Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-green-600" />
              Last Check Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            {checkSummary ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-green-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-green-600">{checkSummary.passCount}</p>
                    <p className="text-sm text-green-700">Passed</p>
                  </div>
                  <div className="p-4 bg-red-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-red-600">{checkSummary.failCount}</p>
                    <p className="text-sm text-red-700">Failed</p>
                  </div>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Total Rules Checked:</span>
                    <span className="font-medium">{checkSummary.totalRules}</span>
                  </div>
                  <div className="flex justify-between text-sm mt-2">
                    <span className="text-gray-600">Total Groups:</span>
                    <span className="font-medium">{checkSummary.totalGroups}</span>
                  </div>
                  <div className="flex justify-between text-sm mt-2">
                    <span className="text-gray-600">Total Checks:</span>
                    <span className="font-medium">{checkSummary.totalChecks}</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <AlertCircle className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No check results yet</p>
                <Button 
                  onClick={() => setCurrentPage('execute')}
                  variant="outline"
                  className="mt-4"
                >
                  Run First Check
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
