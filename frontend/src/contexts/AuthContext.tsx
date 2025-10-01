import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types';
import { apiService } from '../api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (email: string, password: string, name: string) => Promise<void>;
  refreshToken: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  isAdmin: boolean;
  isOperator: boolean;
  isViewer: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('auth_token'));
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated on initial load
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('auth_token');
      if (storedToken) {
        try {
          setToken(storedToken);
          // Try to fetch user details
          const currentUser = await apiService.getCurrentUser();
          setUser(currentUser);
        } catch (error) {
          // Token might be invalid, clear it
          localStorage.removeItem('auth_token');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      // In a real implementation, you would call your backend login API
      // const response = await fetch(`${API_BASE_URL}/auth/login`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email, password })
      // });
      // const data = await response.json();
      // const { user, token } = data;

      // For demo purposes, create a mock user
      const mockUser: User = {
        id: 'user-1',
        email,
        name: email.split('@')[0],
        role: 'ADMIN',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      // Set token (in a real app, this would be from the API response)
      const mockToken = `mock-jwt-token-${Date.now()}`;
      localStorage.setItem('auth_token', mockToken);
      setToken(mockToken);
      setUser(mockUser);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, name: string) => {
    setIsLoading(true);
    try {
      // In a real implementation, you would call your backend register API
      // const response = await fetch(`${API_BASE_URL}/auth/register`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email, password, name })
      // });
      // const data = await response.json();
      // const { user, token } = data;

      // For demo purposes, create a mock user
      const mockUser: User = {
        id: `user-${Date.now()}`,
        email,
        name,
        role: 'VIEWER', // Default role for new users
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      // Set token (in a real app, this would be from the API response)
      const mockToken = `mock-jwt-token-${Date.now()}`;
      localStorage.setItem('auth_token', mockToken);
      setToken(mockToken);
      setUser(mockUser);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
  };

  const refreshToken = async () => {
    // In a real implementation, you would refresh the JWT token
    // This is a simplified version that just re-fetches user data
    try {
      const currentUser = await apiService.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      // If refresh fails, log the user out
      logout();
      throw error;
    }
  };

  const hasPermission = (permission: string): boolean => {
    // Implement permission logic based on user role
    // This is a simplified version - in a real app you might have more granular permissions
    if (!user) return false;

    switch (user.role) {
      case 'ADMIN':
        // Admins have all permissions
        return true;
      case 'OPERATOR':
        // Operators have most permissions except admin-specific ones
        return !permission.includes('admin');
      case 'VIEWER':
        // Viewers can only view
        return permission === 'view';
      default:
        return false;
    }
  };

  // Role-based shortcuts
  const isAdmin = user?.role === 'ADMIN';
  const isOperator = user?.role === 'OPERATOR' || isAdmin;
  const isViewer = Boolean(user); // All authenticated users are at least viewers

  const value = {
    user,
    token,
    isLoading,
    isAuthenticated: !!user && !!token,
    login,
    logout,
    register,
    refreshToken,
    hasPermission,
    isAdmin,
    isOperator,
    isViewer
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};