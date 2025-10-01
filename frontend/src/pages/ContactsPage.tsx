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
import { Contact } from '../types';
import { apiService } from '../api';
import { logger } from '../utils/logger';

const ContactsPage = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [lifecycleFilter, setLifecycleFilter] = useState<string>('all');
  const [roleFilter, setRoleFilter] = useState<string>('all');
  const [engagementFilter, setEngagementFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  const itemsPerPage = 10;

  useEffect(() => {
    const fetchContacts = async () => {
      try {
        setLoading(true);
        // This would be a real API call in production
        // const response = await apiService.getContacts({
        //   page: currentPage,
        //   limit: itemsPerPage,
        // });
        
        // For demo purposes, creating mock data
        const mockContacts: Contact[] = Array.from({ length: 48 }, (_, i) => ({
          id: `contact-${i + 1}`,
          hubspotId: `hub-contact-${i + 1000}`,
          email: `contact${i + 1}@${['techcorp', 'innovate', 'globalsol', 'datasys', 'cloudsvc'][i % 5]}.com`,
          firstName: ['John', 'Jane', 'Robert', 'Emily', 'Michael', 'Sarah'][i % 6],
          lastName: ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia'][i % 6],
          jobTitle: ['CEO', 'CTO', 'Director', 'Manager', 'Engineer', 'Analyst'][i % 6],
          phone: `+1-${Math.floor(100 + Math.random() * 900)}-${Math.floor(100 + Math.random() * 900)}-${Math.floor(1000 + Math.random() * 9000)}`,
          lifecycleStage: ['subscriber', 'lead', 'marketingqualifiedlead', 'salesqualifiedlead', 'customer', 'evangelist'][i % 6],
          lastModifiedDate: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
          createdAt: new Date(Date.now() - Math.floor(Math.random() * 365) * 24 * 60 * 60 * 1000).toISOString(),
          updatedAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
          accountId: `acc-${i % 20 + 1}`,
          properties: { 
            customField1: `Value ${i + 1}`,
            customField2: ['A', 'B', 'C', 'D', 'E'][i % 5] 
          },
          customFields: { 
            engagementScore: Math.floor(Math.random() * 100),
            priority: ['high', 'medium', 'low'][i % 3]
          },
        })).filter(contact => {
          // Apply filters
          return (
            (lifecycleFilter === 'all' || contact.lifecycleStage === lifecycleFilter) &&
            (roleFilter === 'all' || contact.jobTitle?.toLowerCase().includes(roleFilter.toLowerCase())) &&
            (engagementFilter === 'all' || 
              (engagementFilter === 'high' && contact.customFields?.engagementScore && contact.customFields.engagementScore >= 70) ||
              (engagementFilter === 'medium' && contact.customFields?.engagementScore && contact.customFields.engagementScore >= 40 && contact.customFields.engagementScore < 70) ||
              (engagementFilter === 'low' && contact.customFields?.engagementScore && contact.customFields.engagementScore < 40)
            )
          );
        });
        
        // Paginate results
        const paginated = mockContacts.slice(
          (currentPage - 1) * itemsPerPage,
          currentPage * itemsPerPage
        );
        
        setContacts(paginated);
        setTotalPages(Math.ceil(mockContacts.length / itemsPerPage));
      } catch (error) {
        logger.error('Failed to fetch contacts:', error);
        // In a real app, we'd show an error message to the user
      } finally {
        setLoading(false);
      }
    };

    fetchContacts();
  }, [lifecycleFilter, roleFilter, engagementFilter, currentPage]);

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
        <h1 className="text-3xl font-bold">Contacts Management</h1>
        <div className="flex space-x-3">
          <Select value={lifecycleFilter} onValueChange={(value: string) => {
            setLifecycleFilter(value);
            setCurrentPage(1);
          }}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Lifecycle" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Stages</SelectItem>
              <SelectItem value="subscriber">Subscriber</SelectItem>
              <SelectItem value="lead">Lead</SelectItem>
              <SelectItem value="marketingqualifiedlead">MQL</SelectItem>
              <SelectItem value="salesqualifiedlead">SQL</SelectItem>
              <SelectItem value="customer">Customer</SelectItem>
              <SelectItem value="evangelist">Evangelist</SelectItem>
            </SelectContent>
          </Select>
          <Select value={roleFilter} onValueChange={(value: string) => {
            setRoleFilter(value);
            setCurrentPage(1);
          }}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Role" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Roles</SelectItem>
              <SelectItem value="ceo">CEO</SelectItem>
              <SelectItem value="cto">CTO</SelectItem>
              <SelectItem value="director">Director</SelectItem>
              <SelectItem value="manager">Manager</SelectItem>
              <SelectItem value="engineer">Engineer</SelectItem>
              <SelectItem value="analyst">Analyst</SelectItem>
            </SelectContent>
          </Select>
          <Select value={engagementFilter} onValueChange={(value: string) => {
            setEngagementFilter(value);
            setCurrentPage(1);
          }}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Engagement" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Levels</SelectItem>
              <SelectItem value="high">High (70+)</SelectItem>
              <SelectItem value="medium">Medium (40-69)</SelectItem>
              <SelectItem value="low">Low (&lt;40)</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">Refresh</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Contacts List</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Contact ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Job Title</TableHead>
                <TableHead>Lifecycle</TableHead>
                <TableHead>Engagement</TableHead>
                <TableHead>Account</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {contacts.length > 0 ? (
                contacts.map((contact) => (
                  <TableRow key={contact.id}>
                    <TableCell className="font-medium">{contact.id.substring(0, 8)}...</TableCell>
                    <TableCell className="font-semibold">
                      {contact.firstName} {contact.lastName}
                    </TableCell>
                    <TableCell>{contact.email}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{contact.jobTitle}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant={
                          contact.lifecycleStage === 'customer' ? 'default' :
                          contact.lifecycleStage === 'evangelist' ? 'secondary' :
                          contact.lifecycleStage === 'subscriber' ? 'outline' : 'outline'
                        }
                      >
                        {contact.lifecycleStage}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2.5 mr-2">
                          <div 
                            className={`h-2.5 rounded-full ${
                              contact.customFields?.engagementScore && contact.customFields.engagementScore >= 70 ? 'bg-green-600' :
                              contact.customFields?.engagementScore && contact.customFields.engagementScore >= 40 ? 'bg-yellow-500' : 'bg-red-600'
                            }`}
                            style={{ width: `${contact.customFields?.engagementScore || 0}%` }}
                          ></div>
                        </div>
                        <span>{contact.customFields?.engagementScore || 0}</span>
                      </div>
                    </TableCell>
                    <TableCell>acc-{parseInt(contact.accountId?.substring(4) || '0')}</TableCell>
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
                    No contacts found matching the current filters
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
          
          {/* Pagination */}
          <div className="mt-6 flex justify-between items-center">
            <div className="text-sm text-gray-500">
              Showing {contacts.length} of {(currentPage - 1) * itemsPerPage + contacts.length} contacts
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

export default ContactsPage;