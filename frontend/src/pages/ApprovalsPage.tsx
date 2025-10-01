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
import { Approval, ApprovalType, ApprovalStatus, RiskLevel } from '../types';
import { apiService } from '../api';
import { logger } from '../utils/logger';

const ApprovalsPage = () => {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<ApprovalStatus | 'all'>('all');
  const [typeFilter, setTypeFilter] = useState<ApprovalType | 'all'>('all');
  const [riskFilter, setRiskFilter] = useState<RiskLevel | 'all'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  const itemsPerPage = 10;

  useEffect(() => {
    const fetchApprovals = async () => {
      try {
        setLoading(true);
        // This would be a real API call in production
        // const response = await apiService.getApprovals({
        //   page: currentPage,
        //   limit: itemsPerPage,
        //   status: statusFilter === 'all' ? undefined : statusFilter,
        //   type: typeFilter === 'all' ? undefined : typeFilter,
        //   riskLevel: riskFilter === 'all' ? undefined : riskFilter,
        // });
        
        // For demo purposes, creating mock data
        const mockApprovals: Approval[] = Array.from({ length: 25 }, (_, i) => ({
          id: `approval-${i + 1}`,
          runId: `run-${i + 100}`,
          type: ['PROCUREMENT', 'RISK_THRESHOLD', 'MANUAL_REVIEW', 'POLICY_EXCEPTION'][i % 4] as ApprovalType,
          status: ['PENDING', 'APPROVED', 'REJECTED'][i % 3] as ApprovalStatus,
          requestedAt: new Date(Date.now() - Math.floor(Math.random() * 7) * 24 * 60 * 60 * 1000).toISOString(),
          respondedAt: i % 3 !== 0 ? new Date(Date.now() - Math.floor(Math.random() * 3) * 24 * 60 * 60 * 1000).toISOString() : undefined,
          title: `Approval for ${['Deal', 'Contract', 'Purchase', 'Access'][i % 4]} #${i + 1}`,
          description: `Request for ${['Deal', 'Contract', 'Purchase', 'Access'][i % 4]} #${i + 1} requires admin approval`,
          riskLevel: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'][i % 4] as RiskLevel,
          policyId: `policy-${i % 5 + 1}`,
          policySnapshot: { threshold: 10000, condition: 'amount > 10000' },
          approverId: i % 3 !== 0 ? `user-${i % 5 + 1}` : undefined,
          decision: i % 3 !== 0 ? [true, false][i % 2] : undefined,
          justification: i % 3 === 2 ? 'Business justification provided' : undefined,
          metadata: { department: 'Sales', region: ['NA', 'EU', 'APAC'][i % 3] },
          createdAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
          updatedAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
        })).filter(apt => {
          // Apply filters
          return (
            (statusFilter === 'all' || apt.status === statusFilter) &&
            (typeFilter === 'all' || apt.type === typeFilter) &&
            (riskFilter === 'all' || apt.riskLevel === riskFilter)
          );
        });
        
        // Paginate results
        const paginated = mockApprovals.slice(
          (currentPage - 1) * itemsPerPage,
          currentPage * itemsPerPage
        );
        
        setApprovals(paginated);
        setTotalPages(Math.ceil(mockApprovals.length / itemsPerPage));
      } catch (error) {
        logger.error('Failed to fetch approvals:', error);
        // In a real app, we'd show an error message to the user
      } finally {
        setLoading(false);
      }
    };

    fetchApprovals();
  }, [statusFilter, typeFilter, riskFilter, currentPage]);

  const handleApprove = async (approvalId: string) => {
    try {
      logger.info(`Approving approval ${approvalId}`);
      // In a real app, this would call the actual API
      // await apiService.approveRun(approvalId, true);
      setApprovals(prev => 
        prev.map(apt => 
          apt.id === approvalId 
            ? { ...apt, status: 'APPROVED', decision: true, respondedAt: new Date().toISOString() } 
            : apt
        )
      );
    } catch (error) {
      logger.error(`Failed to approve ${approvalId}:`, error);
      // In a real app, we'd show an error message to the user
    }
  };

  const handleReject = async (approvalId: string) => {
    try {
      logger.info(`Rejecting approval ${approvalId}`);
      // In a real app, this would call the actual API
      // await apiService.approveRun(approvalId, false, 'Not applicable');
      setApprovals(prev => 
        prev.map(apt => 
          apt.id === approvalId 
            ? { ...apt, status: 'REJECTED', decision: false, respondedAt: new Date().toISOString() } 
            : apt
        )
      );
    } catch (error) {
      logger.error(`Failed to reject ${approvalId}:`, error);
      // In a real app, we'd show an error message to the user
    }
  };

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
        <h1 className="text-3xl font-bold">Approvals Dashboard</h1>
        <div className="flex space-x-3">
          <Select value={statusFilter} onValueChange={(value: ApprovalStatus | 'all') => {
            setStatusFilter(value);
            setCurrentPage(1);
          }}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="PENDING">Pending</SelectItem>
              <SelectItem value="APPROVED">Approved</SelectItem>
              <SelectItem value="REJECTED">Rejected</SelectItem>
              <SelectItem value="EXPIRED">Expired</SelectItem>
            </SelectContent>
          </Select>
          <Select value={typeFilter} onValueChange={(value: ApprovalType | 'all') => {
            setTypeFilter(value);
            setCurrentPage(1);
          }}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="PROCUREMENT">Procurement</SelectItem>
              <SelectItem value="RISK_THRESHOLD">Risk Threshold</SelectItem>
              <SelectItem value="MANUAL_REVIEW">Manual Review</SelectItem>
              <SelectItem value="POLICY_EXCEPTION">Policy Exception</SelectItem>
            </SelectContent>
          </Select>
          <Select value={riskFilter} onValueChange={(value: RiskLevel | 'all') => {
            setRiskFilter(value);
            setCurrentPage(1);
          }}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Risk" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Risks</SelectItem>
              <SelectItem value="LOW">Low</SelectItem>
              <SelectItem value="MEDIUM">Medium</SelectItem>
              <SelectItem value="HIGH">High</SelectItem>
              <SelectItem value="CRITICAL">Critical</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">Refresh</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Approval Queue</CardTitle>
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
                <TableHead>Status</TableHead>
                <TableHead>Requested</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {approvals.length > 0 ? (
                approvals.map((approval) => (
                  <TableRow key={approval.id}>
                    <TableCell className="font-medium">{approval.id.substring(0, 8)}...</TableCell>
                    <TableCell>{approval.runId.substring(0, 8)}...</TableCell>
                    <TableCell>{approval.title}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{approval.type}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant={
                          approval.riskLevel === 'HIGH' || approval.riskLevel === 'CRITICAL' 
                            ? 'destructive' 
                            : approval.riskLevel === 'MEDIUM' 
                              ? 'secondary' 
                              : 'default'
                        }
                      >
                        {approval.riskLevel}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant={
                          approval.status === 'APPROVED' ? 'default' :
                          approval.status === 'REJECTED' ? 'destructive' :
                          approval.status === 'EXPIRED' ? 'secondary' : 'outline'
                        }
                      >
                        {approval.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{new Date(approval.requestedAt).toLocaleDateString()}</TableCell>
                    <TableCell>
                      {approval.status === 'PENDING' ? (
                        <div className="flex space-x-2">
                          <Button 
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
                      ) : (
                        <span className="text-sm text-gray-500">
                          {approval.decision ? 'Approved' : 'Rejected'}
                        </span>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8 text-gray-500">
                    No approvals found matching the current filters
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
          
          {/* Pagination */}
          <div className="mt-6 flex justify-between items-center">
            <div className="text-sm text-gray-500">
              Showing {approvals.length} of {(currentPage - 1) * itemsPerPage + approvals.length} approvals
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

export default ApprovalsPage;