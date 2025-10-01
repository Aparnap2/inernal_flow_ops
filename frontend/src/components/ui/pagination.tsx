import React from 'react';

interface PaginationProps {
  children: React.ReactNode;
  className?: string;
}

interface PaginationContentProps {
  children: React.ReactNode;
}

interface PaginationItemProps {
  children: React.ReactNode;
}

interface PaginationLinkProps {
  href?: string;
  isActive?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

interface PaginationPreviousProps {
  href?: string;
  onClick?: () => void;
}

interface PaginationNextProps {
  href?: string;
  onClick?: () => void;
}

export function Pagination({ children, className = '' }: PaginationProps) {
  return (
    <nav className={`flex justify-center ${className}`}>
      {children}
    </nav>
  );
}

export function PaginationContent({ children }: PaginationContentProps) {
  return (
    <ul className="flex items-center space-x-1">
      {children}
    </ul>
  );
}

export function PaginationItem({ children }: PaginationItemProps) {
  return <li>{children}</li>;
}

export function PaginationLink({ href, isActive, children, onClick }: PaginationLinkProps) {
  const baseClasses = 'px-3 py-2 text-sm rounded-md';
  const activeClasses = isActive ? 'bg-blue-500 text-white' : 'text-gray-700 hover:bg-gray-100';
  
  return (
    <button 
      onClick={onClick}
      className={`${baseClasses} ${activeClasses}`}
    >
      {children}
    </button>
  );
}

export function PaginationPrevious({ href, onClick }: PaginationPreviousProps) {
  return (
    <button 
      onClick={onClick}
      className="px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
    >
      Previous
    </button>
  );
}

export function PaginationNext({ href, onClick }: PaginationNextProps) {
  return (
    <button 
      onClick={onClick}
      className="px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
    >
      Next
    </button>
  );
}
