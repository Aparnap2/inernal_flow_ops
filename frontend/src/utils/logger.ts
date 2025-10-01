import React from 'react';

interface LogEntry {
  timestamp: string;
  level: 'info' | 'warn' | 'error' | 'debug';
  message: string;
  context?: Record<string, any>;
  stack?: string;
  component?: string;
  userId?: string;
}

class Logger {
  private logs: LogEntry[] = [];
  private maxLogs = 1000; // Keep only the last 1000 logs
  private userId: string | null = null;

  setUserId(userId: string | null) {
    this.userId = userId;
  }

  log(level: 'info' | 'warn' | 'error' | 'debug', message: string, context?: Record<string, any>, stack?: string, component?: string) {
    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
      stack,
      component,
      userId: this.userId || undefined
    };

    this.logs.push(logEntry);

    // Keep only the last maxLogs entries
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }

    // Output to console
    this.outputToConsole(logEntry);

    // Send to backend for persistent logging in production
    if (process.env.NODE_ENV === 'production') {
      this.sendToBackend(logEntry);
    }
  }

  info(message: string, context?: Record<string, any>, component?: string) {
    this.log('info', message, context, undefined, component);
  }

  warn(message: string, context?: Record<string, any>, component?: string) {
    this.log('warn', message, context, undefined, component);
  }

  error(message: string, context?: Record<string, any>, stack?: string, component?: string) {
    this.log('error', message, context, stack, component);
  }

  debug(message: string, context?: Record<string, any>, component?: string) {
    this.log('debug', message, context, undefined, component);
  }

  getLogs(limit?: number): LogEntry[] {
    return limit ? this.logs.slice(-limit) : [...this.logs];
  }

  clearLogs() {
    this.logs = [];
  }

  private outputToConsole(entry: LogEntry) {
    const { timestamp, level, message, context, stack, component, userId } = entry;
    const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${component ? `[${component}] ` : ''}${message}${userId ? ` [User: ${userId}]` : ''}`;
    
    switch (level) {
      case 'info':
        console.info(logMessage, context || '');
        break;
      case 'warn':
        console.warn(logMessage, context || '');
        break;
      case 'error':
        console.error(logMessage, context || '');
        if (stack) {
          console.error('Stack trace:', stack);
        }
        break;
      case 'debug':
        console.debug(logMessage, context || '');
        break;
    }
  }

  private async sendToBackend(entry: LogEntry) {
    try {
      // In production, send logs to backend for persistent storage and analysis
      // This is a simplified implementation - in a real app, you'd batch logs
      // and send them periodically to reduce network overhead
      await fetch('/api/logs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(entry),
      });
    } catch (error) {
      // Silently fail to avoid infinite error loops
      console.warn('Failed to send log to backend:', error);
    }
  }
}

export const logger = new Logger();

// Export a function to handle uncaught errors
export const setupErrorHandling = () => {
  // Handle uncaught promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    logger.error('Unhandled Promise Rejection', {
      error: event.reason,
      promise: event.promise
    }, event.reason?.stack, 'GlobalErrorHandler');
    
    // Prevent the default behavior (logging to console)
    event.preventDefault();
  });

  // Handle uncaught errors
  window.addEventListener('error', (event) => {
    logger.error('Unhandled Error', {
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
    }, event.error?.stack, 'GlobalErrorHandler');
    
    // Prevent the default behavior (logging to console)
    event.preventDefault();
  });
  
  // Handle fetch errors
  const originalFetch = window.fetch;
  window.fetch = function(...args) {
    return originalFetch.apply(this, args).catch(error => {
      logger.error('Network Error', {
        url: args[0],
        error: error.message
      }, error.stack, 'NetworkHandler');
      throw error;
    });
  };
};

// Error boundary component for React
export class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode; fallback?: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log the error to our logger
    logger.error('React Component Error', {
      error: error.message,
      componentStack: errorInfo.componentStack
    }, error.stack, 'ReactErrorBoundary');
  }

  render() {
    if (this.state.hasError) {
      // Render fallback UI if provided
      return this.props.fallback || React.createElement('div', null, 'Something went wrong. Please try again later.');
    }

    return this.props.children;
  }
}