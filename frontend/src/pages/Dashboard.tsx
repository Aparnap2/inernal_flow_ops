import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  Users, 
  Clock, 
  CheckCircle, 
  XCircle,
  AlertTriangle,
  Activity
} from 'lucide-react';
import { Run, Approval, Exception } from '../types';
import { apiService } from '../api';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const [runs, setRuns] = useState<Run[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [exceptions, setExceptions] = useState<Exception[]>([]);
  const [kpiData, setKpiData] = useState({
    totalRuns: 0,
    successfulRuns: 0,
    pendingApprovals: 0,
    openExceptions: 0,
  });
  const [loading, setLoading] = useState(true);

  // Mock data for the chart (would be replaced with actual data)
  const chartData = [
    { date: '2024-01-01', runs: 45 },
    { date: '2024-01-02', runs: 52 },
    { date: '2024-01-03', runs: 48 },
    { date: '2024-01-04', runs: 58 },
    { date: '2024-01-05', runs: 63 },
    { date: '2024-01-06', runs: 56 },
    { date: '2024-01-07', runs: 61 },
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Simulate API calls (would be real API calls in production)
        const [runsRes, approvalsRes, exceptionsRes] = await Promise.all([
          apiService.getRuns({ limit: 5 }),
          apiService.getPendingApprovals(),
          apiService.getOpenExceptions(),
        ]);

        setRuns(runsRes.runs || []);
        setApprovals(approvalsRes.approvals || []);
        setExceptions(exceptionsRes.exceptions || []);

        // Calculate KPIs
        setKpiData({
          totalRuns: runsRes.runs?.length || 0,
          successfulRuns: runsRes.runs?.filter(r => r.status === 'completed').length || 0,
          pendingApprovals: approvalsRes.approvals?.length || 0,
          openExceptions: exceptionsRes.exceptions?.length || 0,
        });
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        // In a real app, we'd show an error message to the user
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Mock function to approve an item
  const handleApprove = async (approvalId: string) => {
    try {
      // In a real app, this would call the actual API
      // await apiService.approveRun(approvalId, true);
      console.log(`Approving ${approvalId}`);
    } catch (error) {
      console.error('Failed to approve:', error);
    }
  };

  // Mock function to reject an item
  const handleReject = async (approvalId: string) => {
    try {
      // In a real app, this would call the actual API
      // await apiService.approveRun(approvalId, false, 'Reason needed');
      console.log(`Rejecting ${approvalId}`);
    } catch (error) {
      console.error('Failed to reject:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">HubSpot Operations Dashboard</h1>
        <div className="flex space-x-2">
          <Button variant="outline">Refresh</Button>
          <Button>Settings</Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Runs</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpiData.totalRuns}</div>
            <p className="text-xs text-muted-foreground">
              +12% from last week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {kpiData.totalRuns > 0 ? Math.round((kpiData.successfulRuns / kpiData.totalRuns) * 100) : 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              {kpiData.successfulRuns} successful
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpiData.pendingApprovals}</div>
            <p className="text-xs text-muted-foreground">
              Requires attention
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Exceptions</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpiData.openExceptions}</div>
            <p className="text-xs text-muted-foreground">
              Need resolution
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Chart Section */}
      <Card>
        <CardHeader>
          <CardTitle>Workflow Activity</CardTitle>
          <CardDescription>
            Showing workflow runs over the last 7 days
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={chartData}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="colorRuns" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" />
                <YAxis />
                <CartesianGrid strokeDasharray="3 3" />
                <Tooltip />
                <Area 
                  type="monotone" 
                  dataKey="runs" 
                  stroke="#8884d8" 
                  fillOpacity={1} 
                  fill="url(#colorRuns)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Recent Runs */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Workflow Runs</CardTitle>
          <CardDescription>
            Latest workflow executions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Run ID</TableHead>
                <TableHead>Workflow</TableHead>
                <TableHead>Object</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Started</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {runs.map((run) => (
                <TableRow key={run.id}>
                  <TableCell className="font-medium">{run.id}</TableCell>
                  <TableCell>{run.workflow_type}</TableCell>
                  <TableCell>{run.metadata?.company_name || run.metadata?.deal_amount || 'N/A'}</TableCell>
                  <TableCell>
                    <Badge 
                      variant={run.status === 'completed' ? 'default' : 
                              run.status === 'failed' ? 'destructive' : 
                              run.status === 'RUNNING' ? 'secondary' : 
                              'outline'}
                    >
                      {run.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{new Date(run.startedAt).toLocaleDateString()}</TableCell>
                  <TableCell>
                    <Button variant="outline" size="sm">
                      View Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Pending Approvals */}
      <Card>
        <CardHeader>
          <CardTitle>Pending Approvals</CardTitle>
          <CardDescription>
            Actions required for workflow continuation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Approval ID</TableHead>
                <TableHead>Run ID</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Risk Level</TableHead>
                <TableHead>Requested</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {approvals.map((approval) => (
                <TableRow key={approval.id}>
                  <TableCell className="font-medium">{approval.id}</TableCell>
                  <TableCell>{approval.runId}</TableCell>
                  <TableCell>{approval.title}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{approval.type}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge 
                      variant={approval.riskLevel === 'HIGH' || approval.riskLevel === 'CRITICAL' ? 'destructive' : 
                              approval.riskLevel === 'MEDIUM' ? 'secondary' : 'default'}
                    >
                      {approval.riskLevel}
                    </Badge>
                  </TableCell>
                  <TableCell>{new Date(approval.requestedAt).toLocaleDateString()}</TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => handleApprove(approval.id)}
                      >
                        Approve
                      </Button>
                      <Button 
                        variant="destructive" 
                        size="sm" 
                        onClick={() => handleReject(approval.id)}
                      >
                        Reject
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Open Exceptions */}
      <Card>
        <CardHeader>
          <CardTitle>Open Exceptions</CardTitle>
          <CardDescription>
            Issues requiring manual intervention
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Exception ID</TableHead>
                <TableHead>Run ID</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {exceptions.map((exception) => (
                <TableRow key={exception.id}>
                  <TableCell className="font-medium">{exception.id}</TableCell>
                  <TableCell>{exception.runId}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{exception.type}</Badge>
                  </TableCell>
                  <TableCell>{exception.title}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{exception.status}</Badge>
                  </TableCell>
                  <TableCell>{new Date(exception.createdAt).toLocaleDateString()}</TableCell>
                  <TableCell>
                    <Button variant="outline" size="sm">
                      View Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;