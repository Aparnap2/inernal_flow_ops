import React from 'react';
import AGUI from '../components/AGUI';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Settings,
  Search,
  Filter
} from 'lucide-react';

const AGUIPage = () => {
  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Agentic UI Dashboard</h1>
        <div className="flex space-x-2">
          <Button variant="outline">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </Button>
          <Button>
            <Play className="mr-2 h-4 w-4" />
            Start Agent
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main AGUI Panel */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Workflow Control Center</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm">
                    <Filter className="mr-2 h-4 w-4" />
                    Filter
                  </Button>
                  <Button variant="outline" size="sm">
                    <Search className="mr-2 h-4 w-4" />
                    Search
                  </Button>
                  <Button variant="outline" size="sm">
                    <RotateCcw className="mr-2 h-4 w-4" />
                    Refresh
                  </Button>
                </div>
                
                <div className="border rounded-lg p-4 bg-gray-50 min-h-[300px]">
                  <div className="text-center text-gray-500 py-12">
                    Workflow visualization will appear here
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent Activities</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[1, 2, 3].map((item) => (
                  <div key={item} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <div>
                      <div className="font-medium">Workflow {item} executed</div>
                      <div className="text-sm text-gray-500">Just now</div>
                    </div>
                    <div className="text-sm text-green-600">Completed</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* AGUI Assistant Panel */}
        <div className="space-y-6">
          <AGUI />

          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full" variant="outline">
                Approve All Pending
              </Button>
              <Button className="w-full" variant="outline">
                Resolve All Exceptions
              </Button>
              <Button className="w-full" variant="outline">
                Trigger New Workflow
              </Button>
              <Button className="w-full" variant="outline">
                Generate Report
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Status Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span>Active Workflows</span>
                  <span className="font-medium">12</span>
                </div>
                <div className="flex justify-between">
                  <span>Pending Approvals</span>
                  <span className="font-medium">5</span>
                </div>
                <div className="flex justify-between">
                  <span>Open Exceptions</span>
                  <span className="font-medium">2</span>
                </div>
                <div className="flex justify-between">
                  <span>Success Rate</span>
                  <span className="font-medium text-green-600">96%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AGUIPage;