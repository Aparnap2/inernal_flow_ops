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
import { Account } from '../types';
import { apiService } from '../api';
import { logger } from '../utils/logger';

const AccountsPage = () => {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [industryFilter, setIndustryFilter] = useState<string>('all');
  const [lifecycleFilter, setLifecycleFilter] = useState<string>('all');
  const [sizeFilter, setSizeFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  const itemsPerPage = 10;

  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        setLoading(true);
        // This would be a real API call in production
        // const response = await apiService.getAccounts({
        //   page: currentPage,
        //   limit: itemsPerPage,
        // });
        
        // For demo purposes, creating mock data
        const mockAccounts: Account[] = Array.from({ length: 35 }, (_, i) => ({
          id: `acc-${i + 1}`,
          hubspotId: `hub-${i + 1000}`,
          name: ['TechCorp', 'Innovate Inc', 'Global Solutions', 'Data Systems', 'Cloud Services'][i % 5] + ` ${i + 1}`,
          domain: ['techcorp', 'innovate', 'globalsol', 'datasys', 'cloudsvc'][i % 5] + `.com`,
          industry: ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail'][i % 5],
          employeeCount: [50, 200, 500, 1000, 2000, 5000][i % 6],
          annualRevenue: [1000000, 5000000, 10000000, 25000000, 50000000, 100000000][i % 6],
          lifecycleStage: ['lead', 'marketingqualifiedlead', 'salesqualifiedlead', 'customer', 'evangelist'][i % 5],
          lastModifiedDate: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
          createdAt: new Date(Date.now() - Math.floor(Math.random() * 365) * 24 * 60 * 60 * 1000).toISOString(),
          updatedAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
          properties: { 
            customField1: `Value ${i + 1}`,
            customField2: ['A', 'B', 'C', 'D', 'E'][i % 5] 
          },
          customFields: { 
            priority: ['high', 'medium', 'low'][i % 3],
            segment: ['enterprise', 'mid-market', 'smb'][i % 3]
          },
        })).filter(acc => {
          // Apply filters
          return (
            (industryFilter === 'all' || acc.industry === industryFilter) &&
            (lifecycleFilter === 'all' || acc.lifecycleStage === lifecycleFilter) &&
            (sizeFilter === 'all' || 
              (sizeFilter === 'small' && acc.employeeCount && acc.employeeCount < 100) ||
              (sizeFilter === 'medium' && acc.employeeCount && acc.employeeCount >= 100 && acc.employeeCount < 1000) ||
              (sizeFilter === 'large' && acc.employeeCount && acc.employeeCount >= 1000)
            )
          );
        });
        
        // Paginate results
        const paginated = mockAccounts.slice(
          (currentPage - 1) * itemsPerPage,
          currentPage * itemsPerPage
        );
        
        setAccounts(paginated);
        setTotalPages(Math.ceil(mockAccounts.length / itemsPerPage));
      } catch (error) {
        logger.error('Failed to fetch accounts:', error);
        // In a real app, we'd show an error message to the user
      } finally {
        setLoading(false);
      }
    };

    fetchAccounts();
  }, [industryFilter, lifecycleFilter, sizeFilter, currentPage]);

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
        <h1 className="text-3xl font-bold">Accounts Management</h1>
        <div className="flex space-x-3">
          <Select value={industryFilter} onValueChange={(value: string) => {
            setIndustryFilter(value);
            setCurrentPage(1);
          }}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Industry" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Industries</SelectItem>
              <SelectItem value="Technology">Technology</SelectItem>
              <SelectItem value="Healthcare">Healthcare</SelectItem>
              <SelectItem value="Finance">Finance</SelectItem>
              <SelectItem value="Manufacturing">Manufacturing</SelectItem>
              <SelectItem value="Retail">Retail</SelectItem>
            </SelectContent>
          </Select>
          <Select value={lifecycleFilter} onValueChange={(value: string) => {
            setLifecycleFilter(value);
            setCurrentPage(1);
          }}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Lifecycle" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Stages</SelectItem>
              <SelectItem value="lead">Lead</SelectItem>
              <SelectItem value="marketingqualifiedlead">MQL</SelectItem>
              <SelectItem value="salesqualifiedlead">SQL</SelectItem>
              <SelectItem value="customer">Customer</SelectItem>
              <SelectItem value="evangelist">Evangelist</SelectItem>
            </SelectContent>
          </Select>
          <Select value={sizeFilter} onValueChange={(value: string) => {
            setSizeFilter(value);
            setCurrentPage(1);
          }}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Size" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Sizes</SelectItem>
              <SelectItem value="small">Small (&lt;100)</SelectItem>
              <SelectItem value="medium">Medium (100-999)</SelectItem>
              <SelectItem value="large">Large (1000+)</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">Refresh</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Accounts List</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Account ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Domain</TableHead>
                <TableHead>Industry</TableHead>
                <TableHead>Size</TableHead>
                <TableHead>Revenue</TableHead>
                <TableHead>Lifecycle</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {accounts.length > 0 ? (
                accounts.map((account) => (
                  <TableRow key={account.id}>
                    <TableCell className="font-medium">{account.id.substring(0, 8)}...</TableCell>
                    <TableCell className="font-semibold">{account.name}</TableCell>
                    <TableCell>{account.domain}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{account.industry}</Badge>
                    </TableCell>
                    <TableCell>
                      {account.employeeCount ? 
                        account.employeeCount >= 1000 ? 'Large' : 
                        account.employeeCount >= 100 ? 'Medium' : 'Small' : 'N/A'}
                    </TableCell>
                    <TableCell>
                      {account.annualRevenue ? `$${(account.annualRevenue / 1000000).toFixed(1)}M` : 'N/A'}
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant={
                          account.lifecycleStage === 'customer' ? 'default' :
                          account.lifecycleStage === 'evangelist' ? 'secondary' :
                          'outline'
                        }
                      >
                        {account.lifecycleStage}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button variant="outline" size="sm">
                        View Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8 text-gray-500">
                    No accounts found matching the current filters
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
          
          {/* Pagination */}
          <div className="mt-6 flex justify-between items-center">
            <div className="text-sm text-gray-500">
              Showing {accounts.length} of {(currentPage - 1) * itemsPerPage + accounts.length} accounts
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

export default AccountsPage;