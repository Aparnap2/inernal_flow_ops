import { User, Run, Approval, Exception, Account, Contact, Deal, Policy, WebhookEvent } from '../types';
import { logger } from '../utils/logger';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const startTime = Date.now();
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // If we have an auth token, add it to the header
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers = {
        ...config.headers,
        'Authorization': `Bearer ${token}`,
      };
    }

    logger.info(`API request: ${config.method || 'GET'} ${url}`, { 
      endpoint, 
      startTime: new Date(startTime).toISOString() 
    });

    try {
      const response = await fetch(url, config);
      
      const duration = Date.now() - startTime;
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const error = new Error(errorData.message || `API request failed: ${response.status}`);
        
        logger.error(`API request failed: ${config.method || 'GET'} ${url}`, { 
          status: response.status, 
          statusText: response.statusText,
          error: error.message,
          duration: `${duration}ms`,
          endpoint
        });
        
        throw error;
      }
      
      logger.info(`API request succeeded: ${config.method || 'GET'} ${url}`, { 
        status: response.status,
        duration: `${duration}ms`,
        endpoint
      });
      
      // Handle responses without body (e.g., 204 No Content)
      if (response.status === 204) {
        return {} as T;
      }
      
      return response.json();
    } catch (error) {
      const duration = Date.now() - startTime;
      
      logger.error(`API request network error: ${config.method || 'GET'} ${url}`, { 
        error: error instanceof Error ? error.message : String(error),
        duration: `${duration}ms`,
        endpoint
      });
      
      throw error;
    }
  }

  // User API
  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/users/me');
  }

  // Run API
  async getRuns(params?: { page?: number; limit?: number; status?: string }): Promise<{ data: Run[]; total: number; page: number; pages: number }> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.status) queryParams.append('status', params.status);
    
    const queryString = queryParams.toString();
    return this.request(`/api/runs${queryString ? `?${queryString}` : ''}`);
  }

  async getRunById(runId: string): Promise<Run> {
    return this.request<Run>(`/api/runs/${runId}`);
  }

  // Approval API
  async getPendingApprovals(): Promise<Approval[]> {
    return this.request<Approval[]>('/api/approvals/pending');
  }

  async approveRun(approvalId: string, decision: boolean, justification?: string): Promise<Approval> {
    return this.request<Approval>(`/api/approvals/${approvalId}/decision`, {
      method: 'PATCH',
      body: JSON.stringify({ decision, justification }),
    });
  }

  // Exception API
  async getOpenExceptions(): Promise<Exception[]> {
    return this.request<Exception[]>('/api/exceptions/open');
  }

  async resolveException(exceptionId: string, resolutionType: string, resolutionData?: any): Promise<Exception> {
    return this.request<Exception>(`/api/exceptions/${exceptionId}/resolve`, {
      method: 'PATCH',
      body: JSON.stringify({ resolutionType, resolutionData }),
    });
  }

  // Other APIs would be added as needed
}

export const apiService = new ApiService();