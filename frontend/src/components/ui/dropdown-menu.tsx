import React from 'react';

interface DropdownMenuProps {
  children: React.ReactNode;
}

interface DropdownMenuTriggerProps {
  asChild?: boolean;
  children: React.ReactNode;
}

interface DropdownMenuContentProps {
  children: React.ReactNode;
  align?: 'start' | 'center' | 'end';
}

interface DropdownMenuItemProps {
  children: React.ReactNode;
  onClick?: () => void;
}

interface DropdownMenuSeparatorProps {}

interface DropdownMenuLabelProps {
  children: React.ReactNode;
}

export function DropdownMenu({ children }: DropdownMenuProps) {
  return <div className="relative inline-block">{children}</div>;
}

export function DropdownMenuTrigger({ asChild, children }: DropdownMenuTriggerProps) {
  return <div>{children}</div>;
}

export function DropdownMenuContent({ children, align = 'center' }: DropdownMenuContentProps) {
  return (
    <div className="absolute z-50 min-w-[8rem] overflow-hidden rounded-md border bg-white p-1 shadow-md">
      {children}
    </div>
  );
}

export function DropdownMenuItem({ children, onClick }: DropdownMenuItemProps) {
  return (
    <div 
      onClick={onClick}
      className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm hover:bg-gray-100"
    >
      {children}
    </div>
  );
}

export function DropdownMenuSeparator({}: DropdownMenuSeparatorProps) {
  return <div className="my-1 h-px bg-gray-200" />;
}

export function DropdownMenuLabel({ children }: DropdownMenuLabelProps) {
  return (
    <div className="px-2 py-1.5 text-sm font-semibold text-gray-900">
      {children}
    </div>
  );
}
