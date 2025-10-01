import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AGUIState } from '../types';
import { apiService } from '../api';

interface AppContextType {
  aguiState: AGUIState;
  refreshAGUIState: () => Promise<void>;
  isLoading: boolean;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [aguiState, setAguiState] = useState<AGUIState>({
    activeRuns: [],
    pendingApprovals: [],
    openExceptions: [],
    kpiData: {
      totalRuns: 0,
      successfulRuns: 0,
      pendingApprovals: 0,
      openExceptions: 0
    }
  });
  const [isLoading, setIsLoading] = useState(true);

  const refreshAGUIState = async () => {
    setIsLoading(true);
    try {
      // Fetch all necessary data
      const [runsRes, approvalsRes, exceptionsRes] = await Promise.all([
        apiService.getRuns({ limit: 20 }),
        apiService.getPendingApprovals(),
        apiService.getOpenExceptions()
      ]);

      // Calculate KPIs
      const totalRuns = runsRes.data.length;
      const successfulRuns = runsRes.data.filter(r => r.status === 'COMPLETED').length;
      
      setAguiState({
        activeRuns: runsRes.data,
        pendingApprovals: approvalsRes,
        openExceptions: exceptionsRes,
        kpiData: {
          totalRuns,
          successfulRuns,
          pendingApprovals: approvalsRes.length,
          openExceptions: exceptionsRes.length
        }
      });
    } catch (error) {
      console.error('Error refreshing AGUI state:', error);
      // In a real app, we'd handle the error appropriately
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshAGUIState();
    
    // Set up periodic refresh (every 30 seconds)
    const interval = setInterval(refreshAGUIState, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <AppContext.Provider value={{ aguiState, refreshAGUIState, isLoading }}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};