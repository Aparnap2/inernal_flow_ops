import React from 'react';

interface SelectProps {
  value?: string;
  onValueChange?: (value: string) => void;
  children: React.ReactNode;
}

interface SelectTriggerProps {
  children: React.ReactNode;
  className?: string;
}

interface SelectContentProps {
  children: React.ReactNode;
}

interface SelectItemProps {
  value: string;
  children: React.ReactNode;
}

export function Select({ value, onValueChange, children }: SelectProps) {
  return (
    <div className="relative">
      {React.Children.map(children, child => 
        React.isValidElement(child) ? React.cloneElement(child, { value, onValueChange } as any) : child
      )}
    </div>
  );
}

export function SelectTrigger({ children, className = '' }: SelectTriggerProps) {
  return (
    <button className={`flex h-10 w-full items-center justify-between rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ${className}`}>
      {children}
    </button>
  );
}

export function SelectContent({ children }: SelectContentProps) {
  return (
    <div className="absolute z-50 min-w-[8rem] overflow-hidden rounded-md border bg-white shadow-md">
      {children}
    </div>
  );
}

export function SelectItem({ value, children }: SelectItemProps) {
  return (
    <div className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm hover:bg-gray-100">
      {children}
    </div>
  );
}

export function SelectValue({ placeholder }: { placeholder?: string }) {
  return <span className="text-gray-500">{placeholder}</span>;
}
