import React from 'react';

interface AvatarProps {
  children: React.ReactNode;
  className?: string;
}

interface AvatarImageProps {
  src?: string;
  alt?: string;
}

interface AvatarFallbackProps {
  children: React.ReactNode;
}

export function Avatar({ children, className = '' }: AvatarProps) {
  return (
    <div className={`relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full ${className}`}>
      {children}
    </div>
  );
}

export function AvatarImage({ src, alt }: AvatarImageProps) {
  return <img src={src} alt={alt} className="aspect-square h-full w-full" />;
}

export function AvatarFallback({ children }: AvatarFallbackProps) {
  return (
    <div className="flex h-full w-full items-center justify-center rounded-full bg-gray-100">
      {children}
    </div>
  );
}
