import React from 'react';
import { 
  LayoutDashboard, 
  Activity, 
  Clock, 
  AlertTriangle, 
  Settings,
  Users,
  Building,
  User
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface SidebarProps {
  className?: string;
  pendingApprovals?: number;
  openExceptions?: number;
}

const Sidebar = ({ className, pendingApprovals = 0, openExceptions = 0 }: SidebarProps) => {
  const { isAdmin, isOperator } = useAuth();
  const location = useLocation();

  // Define menu items with role requirements
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, path: '/', requiredRole: null },
    { id: 'runs', label: 'Workflow Runs', icon: Activity, path: '/runs', requiredRole: null },
    { 
      id: 'approvals', 
      label: `Approvals ${pendingApprovals > 0 ? `(${pendingApprovals})` : ''}`, 
      icon: Clock, 
      path: '/approvals', 
      requiredRole: 'OPERATOR' 
    },
    { 
      id: 'exceptions', 
      label: `Exceptions ${openExceptions > 0 ? `(${openExceptions})` : ''}`, 
      icon: AlertTriangle, 
      path: '/exceptions', 
      requiredRole: 'OPERATOR' 
    },
    { id: 'accounts', label: 'Accounts', icon: Building, path: '/accounts', requiredRole: null },
    { id: 'contacts', label: 'Contacts', icon: User, path: '/contacts', requiredRole: null },
    { id: 'settings', label: 'Settings', icon: Settings, path: '/settings', requiredRole: 'ADMIN' },
  ];

  // Filter menu items based on user role
  const filteredMenuItems = menuItems.filter(item => {
    if (!item.requiredRole) return true; // No role required
    if (item.requiredRole === 'ADMIN') return isAdmin;
    if (item.requiredRole === 'OPERATOR') return isOperator;
    return true; // Default to show if no specific role required
  });

  return (
    <div className={cn("w-64 h-full bg-gray-50 border-r p-4 flex flex-col", className)}>
      <div className="mb-8">
        <h1 className="text-xl font-bold text-gray-800">HubSpot Orchestrator</h1>
        <p className="text-sm text-gray-500">Operations Dashboard</p>
      </div>
      
      <nav className="flex-1">
        <ul className="space-y-2">
          {filteredMenuItems.map((item) => (
            <li key={item.id}>
              <Link to={item.path}>
                <Button
                  variant={location.pathname === item.path ? "secondary" : "ghost"}
                  className="w-full justify-start"
                >
                  <item.icon className="mr-2 h-4 w-4" />
                  {item.label}
                </Button>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
      
      {isAdmin && (
        <div className="mt-auto pt-4 border-t">
          <Link to="/admin/users">
            <Button variant="outline" className="w-full">
              <Users className="mr-2 h-4 w-4" />
              Manage Users
            </Button>
          </Link>
        </div>
      )}
    </div>
  );
};

export default Sidebar;