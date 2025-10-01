import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import UserMenu from './UserMenu';
import { useAppContext } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';
import { Badge } from '@/components/ui/badge';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const { aguiState, isLoading } = useAppContext();
  const { user, isAdmin, isOperator, isViewer } = useAuth();
  const [showWelcome, setShowWelcome] = useState(false);

  useEffect(() => {
    // Show welcome message to new users
    if (user && user.createdAt === user.updatedAt) { // First login
      setShowWelcome(true);
      const timer = setTimeout(() => setShowWelcome(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [user]);

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar 
        pendingApprovals={aguiState.kpiData.pendingApprovals} 
        openExceptions={aguiState.kpiData.openExceptions} 
      />
      <div className="flex flex-col flex-1 overflow-hidden">
        <header className="bg-white shadow-sm z-10">
          <div className="flex items-center justify-between px-6 py-4">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">HubSpot Operations Dashboard</h1>
              <p className="text-sm text-gray-500">Manage your HubSpot workflows</p>
            </div>
            <div className="flex items-center space-x-4">
              {showWelcome && (
                <Badge variant="default" className="bg-green-100 text-green-800">
                  Welcome, {user?.name}!
                </Badge>
              )}
              {user && (
                <div className="text-sm text-muted-foreground">
                  <span className="hidden md:inline">Role: </span>
                  <Badge variant="outline">{user.role}</Badge>
                </div>
              )}
              <UserMenu 
                pendingApprovals={aguiState.kpiData.pendingApprovals} 
                openExceptions={aguiState.kpiData.openExceptions} 
              />
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6 bg-gray-50">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;