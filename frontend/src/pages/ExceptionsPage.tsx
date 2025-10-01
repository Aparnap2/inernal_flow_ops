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
import { 
  Exception, 
  ExceptionType, 
  ExceptionStatus, 
  ResolutionType 
} from '../types';
import { apiService } from '../api';
import { logger } from '../utils/logger';

const ExceptionsPage = () => {
  const [exceptions, setExceptions] = useState<Exception[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<ExceptionStatus | 'all'>('all');
  const [typeFilter, setTypeFilter] = useState<ExceptionType | 'all'>('all');
  const [resolutionFilter, setResolutionFilter] = useState<ResolutionType | 'all'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  const itemsPerPage = 10;

  useEffect(() => {
    const fetchExceptions = async () => {
      try {
        setLoading(true);
        // This would be a real API call in production
        // const response = await apiService.getExceptions({
        //   page: currentPage,
        //   limit: itemsPerPage,
        //   status: statusFilter === 'all' ? undefined : statusFilter,
        //   type: typeFilter === 'all' ? undefined : typeFilter,
        //   resolutionType: resolutionFilter === 'all' ? undefined : resolutionFilter,
        // });
        
        // For demo purposes, creating mock data
        const mockExceptions: Exception[] = Array.from({ length: 18 }, (_, i) => ({
          id: `exception-${i + 1}`,
          runId: `run-${i + 200}`,
          type: ['DATA_VALIDATION', 'INTEGRATION_ERROR', 'BUSINESS_RULE_VIOLATION', 'TIMEOUT', 'UNKNOWN'][i % 5] as ExceptionType,
          status: ['OPEN', 'IN_PROGRESS', 'RESOLVED', 'IGNORED'][i % 4] as ExceptionStatus,
          createdAt: new Date(Date.now() - Math.floor(Math.random() * 14) * 24 * 60 * 60 * 1000).toISOString(),
          resolvedAt: i % 4 === 2 ? new Date(Date.now() - Math.floor(Math.random() * 7) * 24 * 60 * 60 * 1000).toISOString() : undefined,
          title: `Exception in ${['Deal', 'Contact', 'Company'][i % 3]} Processing`,
          description: `An issue occurred during ${['Deal', 'Contact', 'Company'][i % 3]} processing: ${['Invalid data format', 'Integration timeout', 'Policy violation'][i % 3]}`,
          errorCode: `ERR_${['VALIDATION', 'TIMEOUT', 'POLICY'][i % 3]}_${i + 100}`,
          resolutionType: i % 4 !== 0 ? ['AUTO_REPAIR', 'MANUAL_FIX', 'IGNORE', 'ESCALATE'][i % 4] as ResolutionType : undefined,
          resolutionData: i % 4 !== 0 ? { 
            appliedFix: 'Updated field format', 
            appliedBy: `user-${i % 3 + 1}` 
          } : undefined,
          resolvedById: i % 4 !== 0 ? `user-${i % 3 + 1}` : undefined,
          metadata: { 
            severity: ['low', 'medium', 'high'][i % 3], 
            source: ['hubspot', 'airtable', 'notion'][i % 3] 
          },
          updatedAt: new Date(Date.now() - Math.floor(Math.random() * 14) * 24 * 60 * 60 * 1000).toISOString(),
        })).filter(exc => {
          // Apply filters
          return (
            (statusFilter === 'all' || exc.status === statusFilter) &&
            (typeFilter === 'all' || exc.type === typeFilter) &&
            (resolutionFilter === 'all' || exc.resolutionType === resolutionFilter)
          );
        });
        
        // Paginate results
        const paginated = mockExceptions.slice(
          (currentPage - 1) * itemsPerPage,
          currentPage * itemsPerPage
        );
        
        setExceptions(paginated);
        setTotalPages(Math.ceil(mockExceptions.length / itemsPerPage));
      } catch (error) {
        logger.error('Failed to fetch exceptions:', error);
        // In a real app, we'd show an error message to the user
      } finally {
        setLoading(false);
      }
    };

    fetchExceptions();
  }, [statusFilter, typeFilter, resolutionFilter, currentPage]);

  const handleResolve = async (exceptionId: string, resolutionType: ResolutionType) => {
    try {
      logger.info(`Resolving exception ${exceptionId} with ${resolutionType}`);
      // In a real app, this would call the actual API
      // await apiService.resolveException(exceptionId, resolutionType);
      setExceptions(prev => 
        prev.map(exc => 
          exc.id === exceptionId 
            ? { 
                ...exc, 
                status: 'RESOLVED', 
                resolutionType,
                resolvedAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
              } 
            : exc
        )
      );
    } catch (error) {
      logger.error(`Failed to resolve exception ${exceptionId}:`, error);
      // In a real app, we'd show an error message to the user
    }
  };

  const handleIgnore = async (exceptionId: string) => {
    try {
      logger.info(`Ignoring exception ${exceptionId}`);
      setExceptions(prev => 
        prev.map(exc => 
          exc.id === exceptionId 
            ? { 
                ...exc, 
                status: 'IGNORED', 
                resolutionType: 'IGNORE',
                resolvedAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
              } 
            : exc
        )
      );
    } catch (error) {
      logger.error(`Failed to ignore exception ${exceptionId}:`, error);
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
        <h1 className="text-3xl font-bold">Exception Management</h1>
        <div className="flex space-x-3">
          <Select value={statusFilter} onValueChange={(value: ExceptionStatus | 'all') => {
            setStatusFilter(value);
            setCurrentPage(1);
          }}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="OPEN">Open</SelectItem>
              <SelectItem value="IN_PROGRESS">In Progress</SelectItem>
              <SelectItem value="RESOLVED">Resolved</SelectItem>
              <SelectItem value="IGNORED">Ignored</SelectItem>
            </SelectContent>
          </Select>
          <Select value={typeFilter} onValueChange={(value: ExceptionType | 'all') => {
            setTypeFilter(value);
            setCurrentPage(1);
          }}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="DATA_VALIDATION">Data Validation</SelectItem>
              <SelectItem value="INTEGRATION_ERROR">Integration Error</SelectItem>
              <SelectItem value="BUSINESS_RULE_VIOLATION">Business Rule Violation</SelectItem>
              <SelectItem value="TIMEOUT">Timeout</SelectItem>
              <SelectItem value="UNKNOWN">Unknown</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">Refresh</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Exception Queue</CardTitle>
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
                <TableHead>Error Code</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {exceptions.length > 0 ? (
                exceptions.map((exception) => (
                  <TableRow key={exception.id}>
                    <TableCell className="font-medium">{exception.id.substring(0, 8)}...</TableCell>
                    <TableCell>{exception.runId.substring(0, 8)}...</TableCell>
                    <TableCell>
                      <Badge variant="outline">{exception.type}</Badge>
                    </TableCell>
                    <TableCell>{exception.title}</TableCell>
                    <TableCell>
                      <Badge 
                        variant={
                          exception.status === 'RESOLVED' ? 'default' :
                          exception.status === 'IGNORED' ? 'secondary' :
                          exception.status === 'IN_PROGRESS' ? 'outline' : 'destructive'
                        }
                      >
                        {exception.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <code className="text-xs bg-gray-100 px-2 py-1 rounded">{exception.errorCode}</code>
                    </TableCell>
                    <TableCell>{new Date(exception.createdAt).toLocaleDateString()}</TableCell>
                    <TableCell>
                      {exception.status === 'OPEN' ? (
                        <div className="flex space-x-2">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleResolve(exception.id, 'AUTO_REPAIR')}
                          >
                            Auto Repair
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleResolve(exception.id, 'MANUAL_FIX')}
                          >
                            Manual Fix
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleIgnore(exception.id)}
                          >
                            Ignore
                          </Button>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-500">
                          {exception.resolutionType || 'Resolved'}
                        </span>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8 text-gray-500">
                    No exceptions found matching the current filters
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
          
          {/* Pagination */}
          <div className="mt-6 flex justify-between items-center">
            <div className="text-sm text-gray-500">
              Showing {exceptions.length} of {(currentPage - 1) * itemsPerPage + exceptions.length} exceptions
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

export default ExceptionsPage;