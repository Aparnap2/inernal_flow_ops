import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'ADMIN' | 'OPERATOR' | 'VIEWER';
  permission?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole, 
  permission 
}) => {
  const { isAuthenticated, user, hasPermission, isAdmin, isOperator } = useAuth();
  const location = useLocation();

  // Check if user is authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role requirements
  if (requiredRole) {
    let hasRequiredRole = false;
    
    switch (requiredRole) {
      case 'ADMIN':
        hasRequiredRole = isAdmin;
        break;
      case 'OPERATOR':
        hasRequiredRole = isOperator; // Operator or Admin
        break;
      case 'VIEWER':
        hasRequiredRole = !!user; // Any authenticated user is at least a viewer
        break;
    }

    if (!hasRequiredRole) {
      // Redirect to unauthorized page or dashboard
      return <Navigate to="/unauthorized" replace />;
    }
  }

  // Check permission requirements
  if (permission && !hasPermission(permission)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;