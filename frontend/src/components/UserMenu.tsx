import React, { useState } from 'react';
import { 
  User as UserIcon, 
  LogOut,
  Settings,
  Briefcase,
  Users,
  Activity,
  Clock,
  AlertTriangle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';

interface UserMenuProps {
  pendingApprovals?: number;
  openExceptions?: number;
}

const UserMenu: React.FC<UserMenuProps> = ({ 
  pendingApprovals = 0, 
  openExceptions = 0 
}) => {
  const { user, logout, isAdmin, isOperator } = useAuth();
  const navigate = useNavigate();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      logout();
      router.push('/login');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  if (!user) {
    return null;
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="relative h-8 w-8 rounded-full">
          <Avatar className="h-8 w-8">
            <AvatarImage src={`https://avatar.vercel.sh/${user.email}.png`} alt={user.name} />
            <AvatarFallback>
              {user.name?.charAt(0) || user.email.charAt(0)}
            </AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56" align="end" forceMount>
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium leading-none">{user.name}</p>
            <p className="text-xs leading-none text-muted-foreground">
              {user.email}
            </p>
            <Badge variant="outline" className="w-fit mt-1">
              {user.role}
            </Badge>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <div className="p-2 text-xs text-muted-foreground">
          <div className="flex justify-between">
            <span>Pending Approvals:</span>
            <span className="font-medium">{pendingApprovals}</span>
          </div>
          <div className="flex justify-between">
            <span>Open Exceptions:</span>
            <span className="font-medium">{openExceptions}</span>
          </div>
        </div>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => router.push('/settings')}>
          <Settings className="mr-2 h-4 w-4" />
          <span>Settings</span>
        </DropdownMenuItem>
        <DropdownMenuItem disabled={!isOperator} onClick={() => router.push('/approvals')}>
          <Clock className="mr-2 h-4 w-4" />
          <span>Approvals ({pendingApprovals})</span>
        </DropdownMenuItem>
        <DropdownMenuItem disabled={!isOperator} onClick={() => router.push('/exceptions')}>
          <AlertTriangle className="mr-2 h-4 w-4" />
          <span>Exceptions ({openExceptions})</span>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleLogout} disabled={isLoggingOut}>
          <LogOut className="mr-2 h-4 w-4" />
          <span>{isLoggingOut ? 'Logging out...' : 'Log out'}</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default UserMenu;