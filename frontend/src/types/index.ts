// User types
export type UserRole = 'ADMIN' | 'OPERATOR' | 'VIEWER';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  createdAt: string;
  updatedAt: string;
}

// Account types
export interface Account {
  id: string;
  hubspotId: string;
  name: string;
  domain?: string;
  industry?: string;
  employeeCount?: number;
  annualRevenue?: number;
  lifecycleStage?: string;
  lastModifiedDate: string;
  createdAt: string;
  updatedAt: string;
  properties?: Record<string, any>;
  customFields?: Record<string, any>;
}

// Contact types
export interface Contact {
  id: string;
  hubspotId: string;
  email?: string;
  firstName?: string;
  lastName?: string;
  jobTitle?: string;
  phone?: string;
  lifecycleStage?: string;
  lastModifiedDate: string;
  createdAt: string;
  updatedAt: string;
  accountId?: string;
  properties?: Record<string, any>;
  customFields?: Record<string, any>;
}

// Deal types
export interface Deal {
  id: string;
  hubspotId: string;
  name: string;
  stage: string;
  amount?: number;
  closeDate?: string;
  probability?: number;
  lastModifiedDate: string;
  createdAt: string;
  updatedAt: string;
  accountId?: string;
  contactId?: string;
  properties?: Record<string, any>;
  customFields?: Record<string, any>;
}

// Run types
export type RunStatus = 'PENDING' | 'RUNNING' | 'WAITING_APPROVAL' | 'COMPLETED' | 'FAILED' | 'CANCELLED';

export interface Run {
  id: string;
  correlationId: string;
  workflowId: string;
  status: RunStatus;
  startedAt: string;
  completedAt?: string;
  errorMessage?: string;
  eventType: string;
  objectType: string;
  objectId: string;
  createdById?: string;
  accountId?: string;
  contactId?: string;
  dealId?: string;
  payload?: Record<string, any>;
  checkpointData?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

// RunStep types
export interface RunStep {
  id: string;
  runId: string;
  stepName: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'SKIPPED';
  startedAt: string;
  completedAt?: string;
  errorMessage?: string;
  retryCount: number;
  input?: Record<string, any>;
  output?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

// Approval types
export type ApprovalType = 'PROCUREMENT' | 'RISK_THRESHOLD' | 'MANUAL_REVIEW' | 'POLICY_EXCEPTION';
export type ApprovalStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXPIRED';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface Approval {
  id: string;
  runId: string;
  type: ApprovalType;
  status: ApprovalStatus;
  requestedAt: string;
  respondedAt?: string;
  title: string;
  description?: string;
  riskLevel: RiskLevel;
  policyId?: string;
  policySnapshot?: Record<string, any>;
  approverId?: string;
  decision?: boolean;
  justification?: string;
  metadata?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

// Exception types
export type ExceptionType = 'DATA_VALIDATION' | 'INTEGRATION_ERROR' | 'BUSINESS_RULE_VIOLATION' | 'TIMEOUT' | 'UNKNOWN';
export type ExceptionStatus = 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'IGNORED';
export type ResolutionType = 'AUTO_REPAIR' | 'MANUAL_FIX' | 'IGNORE' | 'ESCALATE';

export interface Exception {
  id: string;
  runId: string;
  type: ExceptionType;
  status: ExceptionStatus;
  createdAt: string;
  resolvedAt?: string;
  title: string;
  description: string;
  errorCode?: string;
  resolutionType?: ResolutionType;
  resolutionData?: Record<string, any>;
  resolvedById?: string;
  metadata?: Record<string, any>;
  updatedAt: string;
}

// Policy types
export interface Policy {
  id: string;
  name: string;
  description?: string;
  version: string;
  isActive: boolean;
  conditions: Record<string, any>;
  actions: Record<string, any>;
  validFrom: string;
  validTo?: string;
  createdAt: string;
  updatedAt: string;
  createdById?: string;
}

// WebhookEvent types
export type EventStatus = 'RECEIVED' | 'PROCESSING' | 'PROCESSED' | 'FAILED' | 'IGNORED';

export interface WebhookEvent {
  id: string;
  hubspotEventId?: string;
  eventType: string;
  objectType: string;
  objectId: string;
  correlationId: string;
  payload: Record<string, any>;
  signature?: string;
  status: EventStatus;
  processedAt?: string;
  errorMessage?: string;
  retryCount: number;
  occurredAt: string;
  receivedAt: string;
  updatedAt: string;
}

// Event Envelope types (from development plan)
export interface EventEnvelope {
  meta: {
    eventId: string;
    source: 'hubspot' | 'manual' | 'system';
    objectType: 'contact' | 'company' | 'deal' | 'ticket';
    objectId: string;
    occurredAt: string; // ISO date string
    receivedAt: string; // ISO date string
    correlationId: string;
    workflowId?: string;
    runId?: string;
    version: string;
  };
  required: Record<string, any>;
  payload: Record<string, any>;
  rawPayloadRef?: string;
}

// AGUI state types
export interface AGUIState {
  activeRuns: Run[];
  pendingApprovals: Approval[];
  openExceptions: Exception[];
  kpiData: {
    totalRuns: number;
    successfulRuns: number;
    pendingApprovals: number;
    openExceptions: number;
  };
}

export interface WorkflowTrigger {
  workflowId: string;
  name: string;
  description: string;
  eventTypes: string[];
  conditions: Record<string, any>;
  enabled: boolean;
  priority: number;
}