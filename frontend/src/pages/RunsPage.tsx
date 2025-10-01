import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';
import { Run, RunStatus } from '../types';
import { apiService } from '../api';
import { logger } from '../utils/logger';

const RunsPage = () => {
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<RunStatus | 'all'>('all');
  const [objectTypeFilter, setObjectTypeFilter] = useState<string>('all');
  const [workflowFilter, setWorkflowFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  const itemsPerPage = 10;

  useEffect(() => {
    const fetchRuns = async () => {
      try {
        setLoading(true);
        // This would be a real API call in production
        // const response = await apiService.getRuns({
        //   page: currentPage,
        //   limit: itemsPerPage,
        //   status: statusFilter === 'all' ? undefined : statusFilter,
        // });
        
        // For demo purposes, creating mock data
        const mockRuns: Run[] = Array.from({ length: 42 }, (_, i) => ({
          id: `run-${i + 1}`,
          correlationId: `corr-${i + 1000}`,
          workflowId: ['company-intake', 'contact-role-mapping', 'deal-stage-kickoff', 'procurement-approval'][i % 4],
          status: ['PENDING', 'RUNNING', 'WAITING_APPROVAL', 'COMPLETED', 'FAILED', 'CANCELLED'][i % 6] as RunStatus,
          startedAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
          completedAt: i % 6 !== 0 ? new Date(Date.now() - Math.floor(Math.random() * 15) * 24 * 60 * 60 * 1000).toISOString() : undefined,
          errorMessage: i % 6 === 4 ? 'An error occurred during processing' : undefined,
          eventType: ['company.creation', 'contact.propertyChange', 'deal.propertyChange.amount', 'company.propertyChange'][i % 4],
          objectType: ['company', 'contact', 'deal', 'company'][i % 4],
          objectId: `obj-${i + 100}`,
          createdById: `user-${i % 5 + 1}`,
          accountId: i % 4 !== 2 ? `acc-${i + 50}` : undefined,
          contactId: i % 4 === 1 ? `contact-${i + 30}` : undefined,
          dealId: i % 4 === 2 ? `deal-${i + 20}` : undefined,
          payload: { 
            initialData: `Data for run ${i + 1}`,
            processedAt: new Date().toISOString()
          },
          checkpointData: i % 6 === 1 ? { step: 'step-2', completed: ['step-1'] } : undefined,
          createdAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
          updatedAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
        })).filter(run => {
          // Apply filters
          return (
            (statusFilter === 'all' || run.status === statusFilter) &&
            (objectTypeFilter === 'all' || run.objectType === objectTypeFilter) &&
            (workflowFilter === 'all' || run.workflowId === workflowFilter)
          );
        });
        
        // Paginate results
        const paginated = mockRuns.slice(
          (currentPage - 1) * itemsPerPage,
          currentPage * itemsPerPage
        );
        
        setRuns(paginated);
        setTotalPages(Math.ceil(mockRuns.length / itemsPerPage));
      } catch (error) {
        logger.error('Failed to fetch runs:', error);
        // In a real app, we'd show an error message to the user
      } finally {
        setLoading(false);
      }
    };

    fetchRuns();
  }, [statusFilter, objectTypeFilter, workflowFilter, currentPage]);

  if (loading) {
    return (
      <div className="container mx-auto py-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Workflow Runs</h1>
        <div className="flex space-x-3">
          <Select value={statusFilter} onValueChange={(value: RunStatus | 'all') => {
            setStatusFilter(value);
            setCurrentPage(1);
          }}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="PENDING">Pending</SelectItem>
              <SelectItem value="RUNNING">Running</SelectItem>
              <SelectItem value="WAITING_APPROVAL">Waiting Approval</SelectItem>
              <SelectItem value="COMPLETED">Completed</SelectItem>
              <SelectItem value="FAILED">Failed</SelectItem>
              <SelectItem value="CANCELLED">Cancelled</SelectItem>
            </SelectContent>
          </Select>
          <Select value={objectTypeFilter} onValueChange={(value: string) => {
            setObjectTypeFilter(value);
            setCurrentPage(1);
          }}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Object Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="company">Company</SelectItem>
              <SelectItem value="contact">Contact</SelectItem>
              <SelectItem value="deal">Deal</SelectItem>
            </SelectContent>
          </Select>
          <Select value={workflowFilter} onValueChange={(value: string) => {
            setWorkflowFilter(value);
            setCurrentPage(1);
          }}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Workflow" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Workflows</SelectItem>
              <SelectItem value="company-intake">Company Intake</SelectItem>
              <SelectItem value="contact-role-mapping">Contact Role Mapping</SelectItem>
              <SelectItem value="deal-stage-kickoff">Deal Stage Kickoff</SelectItem>
              <SelectItem value="procurement-approval">Procurement Approval</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">Refresh</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Workflow Execution Runs</CardTitle>
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
                <TableHead>Completed</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {runs.length > 0 ? (
                runs.map((run) => {
                  const startTime = new Date(run.startedAt);
                  const endTime = run.completedAt ? new Date(run.completedAt) : new Date();
                  const duration = Math.floor((endTime.getTime() - startTime.getTime()) / 1000); // in seconds
                  
                  return (
                    <TableRow key={run.id}>
                      <TableCell className="font-medium">{run.id.substring(0, 8)}...</TableCell>
                      <TableCell>
                        <span className="text-xs font-mono bg-gray-100 px-2 py-1 rounded">
                          {run.workflowId}
                        </span>
                      </TableCell>
                      <TableCell>
                        {run.objectType} {run.objectId.substring(0, 8)}...
                      </TableCell>
                      <TableCell>
                        <Badge 
                          variant={
                            run.status === 'COMPLETED' ? 'default' :
                            run.status === 'FAILED' ? 'destructive' :
                            run.status === 'RUNNING' ? 'secondary' :
                            run.status === 'WAITING_APPROVAL' ? 'outline' : 'secondary'
                          }
                        >
                          {run.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{new Date(run.startedAt).toLocaleString()}</TableCell>
                      <TableCell>
                        {run.completedAt ? new Date(run.completedAt).toLocaleString() : '-'}
                      </TableCell>
                      <TableCell>
                        {duration > 60 
                          ? `${Math.floor(duration / 60)}m ${duration % 60}s` 
                          : `${duration}s`}
                      </TableCell>
                      <TableCell>
                        <Button variant="outline" size="sm">
                          View Details
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })
              ) : (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8 text-gray-500">
                    No runs found matching the current filters
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
          
          {/* Pagination */}
          <div className="mt-6 flex justify-between items-center">
            <div className="text-sm text-gray-500">
              Showing {runs.length} of {(currentPage - 1) * itemsPerPage + runs.length} runs
            </div>
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious 
                    href="#" 
                    onClick={(e) => {
                      e.preventDefault();
                      if (currentPage > 1) setCurrentPage(currentPage - 1);
                    }}
                    className={currentPage === 1 ? 'pointer-events-none opacity-50' : ''}
                  />
                </PaginationItem>
                
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (currentPage <= 3) {
                    pageNum = i + 1;
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = currentPage - 2 + i;
                  }
                  
                  return (
                    <PaginationItem key={pageNum}>
                      <PaginationLink
                        href="#"
                        onClick={(e) => {
                          e.preventDefault();
                          setCurrentPage(pageNum);
                        }}
                        isActive={currentPage === pageNum}
                      >
                        {pageNum}
                      </PaginationLink>
                    </PaginationItem>
                  );
                })}
                
                <PaginationItem>
                  <PaginationNext 
                    href="#" 
                    onClick={(e) => {
                      e.preventDefault();
                      if (currentPage < totalPages) setCurrentPage(currentPage + 1);
                    }}
                    className={currentPage === totalPages ? 'pointer-events-none opacity-50' : ''}
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RunsPage;