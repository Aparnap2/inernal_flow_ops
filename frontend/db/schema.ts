import { sql } from 'drizzle-orm';
import { 
  sqliteTable, 
  text, 
  integer, 
  real, 
  numeric, 
  primaryKey,
  index
} from 'drizzle-orm/sqlite-core';
import { createId } from '@paralleldrive/cuid2';
import { relations } from 'drizzle-orm';

// User model
export const users = sqliteTable('users', {
  id: text('id').$defaultFn(() => createId()).primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name'),
  role: text('role', { enum: ['ADMIN', 'OPERATOR', 'VIEWER'] }).notNull().default('VIEWER'),
  createdAt: integer('created_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`)
});

// Account model
export const accounts = sqliteTable('accounts', {
  id: text('id').$defaultFn(() => createId()).primaryKey(),
  hubspotId: text('hubspot_id').notNull().unique(),
  name: text('name').notNull(),
  domain: text('domain'),
  industry: text('industry'),
  employeeCount: integer('employee_count'),
  annualRevenue: numeric('annual_revenue'),
  lifecycleStage: text('lifecycle_stage'),
  lastModifiedDate: integer('last_modified_date', { mode: 'timestamp' }).notNull(),
  createdAt: integer('created_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  properties: text('properties', { mode: 'json' }),
  customFields: text('custom_fields', { mode: 'json' })
});

// Contact model
export const contacts = sqliteTable('contacts', {
  id: text('id').$defaultFn(() => createId()).primaryKey(),
  hubspotId: text('hubspot_id').notNull().unique(),
  email: text('email'),
  firstName: text('first_name'),
  lastName: text('last_name'),
  jobTitle: text('job_title'),
  phone: text('phone'),
  lifecycleStage: text('lifecycle_stage'),
  lastModifiedDate: integer('last_modified_date', { mode: 'timestamp' }).notNull(),
  createdAt: integer('created_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  accountId: text('account_id').references(() => accounts.id),
  properties: text('properties', { mode: 'json' }),
  customFields: text('custom_fields', { mode: 'json' })
});

// Deal model
export const deals = sqliteTable('deals', {
  id: text('id').$defaultFn(() => createId()).primaryKey(),
  hubspotId: text('hubspot_id').notNull().unique(),
  name: text('name').notNull(),
  stage: text('stage').notNull(),
  amount: numeric('amount'),
  closeDate: integer('close_date', { mode: 'timestamp' }),
  probability: real('probability'),
  lastModifiedDate: integer('last_modified_date', { mode: 'timestamp' }).notNull(),
  createdAt: integer('created_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  accountId: text('account_id').references(() => accounts.id),
  contactId: text('contact_id').references(() => contacts.id),
  properties: text('properties', { mode: 'json' }),
  customFields: text('custom_fields', { mode: 'json' })
});

// Run model
export const runs = sqliteTable('runs', {
  id: text('id').$defaultFn(() => createId()).primaryKey(),
  correlationId: text('correlation_id').notNull().unique(),
  workflowId: text('workflow_id').notNull(),
  status: text('status', { enum: ['PENDING', 'RUNNING', 'WAITING_APPROVAL', 'COMPLETED', 'FAILED', 'CANCELLED'] })
    .notNull()
    .default('PENDING'),
  startedAt: integer('started_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  completedAt: integer('completed_at', { mode: 'timestamp' }),
  errorMessage: text('error_message'),
  eventType: text('event_type').notNull(),
  objectType: text('object_type').notNull(),
  objectId: text('object_id').notNull(),
  createdById: text('created_by_id').references(() => users.id),
  accountId: text('account_id').references(() => accounts.id),
  contactId: text('contact_id').references(() => contacts.id),
  dealId: text('deal_id').references(() => deals.id),
  payload: text('payload', { mode: 'json' }),
  checkpointData: text('checkpoint_data', { mode: 'json' }),
  createdAt: integer('created_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`)
});

// Run Step model
export const runSteps = sqliteTable('run_steps', {
  id: text('id').$defaultFn(() => createId()).primaryKey(),
  runId: text('run_id').notNull().references(() => runs.id, { onDelete: 'cascade' }),
  stepName: text('step_name').notNull(),
  status: text('status', { enum: ['PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'SKIPPED'] })
    .notNull()
    .default('PENDING'),
  startedAt: integer('started_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  completedAt: integer('completed_at', { mode: 'timestamp' }),
  errorMessage: text('error_message'),
  retryCount: integer('retry_count').default(0),
  input: text('input', { mode: 'json' }),
  output: text('output', { mode: 'json' }),
  createdAt: integer('created_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`)
});

// Approval model
export const approvals = sqliteTable('approvals', {
  id: text('id').$defaultFn(() => createId()).primaryKey(),
  runId: text('run_id').notNull().references(() => runs.id, { onDelete: 'cascade' }),
  type: text('type', { enum: ['PROCUREMENT', 'RISK_THRESHOLD', 'MANUAL_REVIEW', 'POLICY_EXCEPTION'] }).notNull(),
  status: text('status', { enum: ['PENDING', 'APPROVED', 'REJECTED', 'EXPIRED'] })
    .notNull()
    .default('PENDING'),
  requestedAt: integer('requested_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  respondedAt: integer('responded_at', { mode: 'timestamp' }),
  title: text('title').notNull(),
  description: text('description'),
  riskLevel: text('risk_level', { enum: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'] }).default('LOW'),
  policyId: text('policy_id'),
  policySnapshot: text('policy_snapshot', { mode: 'json' }),
  approverId: text('approver_id').references(() => users.id),
  decision: integer('decision', { mode: 'boolean' }),
  justification: text('justification'),
  metadata: text('metadata', { mode: 'json' }),
  createdAt: integer('created_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`)
});

// Exception model
export const exceptions = sqliteTable('exceptions', {
  id: text('id').$defaultFn(() => createId()).primaryKey(),
  runId: text('run_id').notNull().references(() => runs.id, { onDelete: 'cascade' }),
  type: text('type', { enum: ['DATA_VALIDATION', 'INTEGRATION_ERROR', 'BUSINESS_RULE_VIOLATION', 'TIMEOUT', 'UNKNOWN'] }).notNull(),
  status: text('status', { enum: ['OPEN', 'IN_PROGRESS', 'RESOLVED', 'IGNORED'] })
    .notNull()
    .default('OPEN'),
  createdAt: integer('created_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  resolvedAt: integer('resolved_at', { mode: 'timestamp' }),
  title: text('title').notNull(),
  description: text('description').notNull(),
  errorCode: text('error_code'),
  resolutionType: text('resolution_type', { enum: ['AUTO_REPAIR', 'MANUAL_FIX', 'IGNORE', 'ESCALATE'] }),
  resolutionData: text('resolution_data', { mode: 'json' }),
  resolvedById: text('resolved_by_id').references(() => users.id),
  metadata: text('metadata', { mode: 'json' }),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`)
});

// Policy model
export const policies = sqliteTable('policies', {
  id: text('id').$defaultFn(() => createId()).primaryKey(),
  name: text('name').notNull(),
  description: text('description'),
  version: text('version').notNull().default('1.0'),
  isActive: integer('is_active', { mode: 'boolean' }).notNull().default(true),
  conditions: text('conditions', { mode: 'json' }).notNull(),
  actions: text('actions', { mode: 'json' }).notNull(),
  validFrom: integer('valid_from', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  validTo: integer('valid_to', { mode: 'timestamp' }),
  createdById: text('created_by_id').references(() => users.id),
  createdAt: integer('created_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`)
});

// Webhook Event model
export const webhookEvents = sqliteTable('webhook_events', {
  id: text('id').$defaultFn(() => createId()).primaryKey(),
  hubspotEventId: text('hubspot_event_id').unique(),
  eventType: text('event_type').notNull(),
  objectType: text('object_type').notNull(),
  objectId: text('object_id').notNull(),
  correlationId: text('correlation_id').notNull(),
  payload: text('payload', { mode: 'json' }).notNull(),
  signature: text('signature'),
  status: text('status', { enum: ['RECEIVED', 'PROCESSING', 'PROCESSED', 'FAILED', 'IGNORED'] })
    .notNull()
    .default('RECEIVED'),
  processedAt: integer('processed_at', { mode: 'timestamp' }),
  errorMessage: text('error_message'),
  retryCount: integer('retry_count').default(0),
  occurredAt: integer('occurred_at', { mode: 'timestamp' }).notNull(),
  receivedAt: integer('received_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`),
  createdAt: integer('created_at', { mode: 'timestamp' }).default(sql`CURRENT_TIMESTAMP`)
});

// Relations
export const usersRelations = relations(users, ({ many }) => ({
  approvals: many(approvals),
  runs: many(runs)
}));

export const accountsRelations = relations(accounts, ({ many }) => ({
  contacts: many(contacts),
  deals: many(deals),
  runs: many(runs)
}));

export const contactsRelations = relations(contacts, ({ one, many }) => ({
  account: one(accounts, { fields: [contacts.accountId], references: [accounts.id] }),
  deals: many(deals),
  runs: many(runs)
}));

export const dealsRelations = relations(deals, ({ one, many }) => ({
  account: one(accounts, { fields: [deals.accountId], references: [accounts.id] }),
  contact: one(contacts, { fields: [deals.contactId], references: [contacts.id] }),
  runs: many(runs)
}));

export const runsRelations = relations(runs, ({ one, many }) => ({
  createdBy: one(users, { fields: [runs.createdById], references: [users.id] }),
  account: one(accounts, { fields: [runs.accountId], references: [accounts.id] }),
  contact: one(contacts, { fields: [runs.contactId], references: [contacts.id] }),
  deal: one(deals, { fields: [runs.dealId], references: [deals.id] }),
  steps: many(runSteps),
  approvals: many(approvals),
  exceptions: many(exceptions)
}));

export const runStepsRelations = relations(runSteps, ({ one }) => ({
  run: one(runs, { fields: [runSteps.runId], references: [runs.id] })
}));

export const approvalsRelations = relations(approvals, ({ one }) => ({
  run: one(runs, { fields: [approvals.runId], references: [runs.id] }),
  approver: one(users, { fields: [approvals.approverId], references: [users.id] })
}));

export const exceptionsRelations = relations(exceptions, ({ one }) => ({
  run: one(runs, { fields: [exceptions.runId], references: [runs.id] }),
  resolvedBy: one(users, { fields: [exceptions.resolvedById], references: [users.id] })
}));

export const policiesRelations = relations(policies, ({ one }) => ({
  createdBy: one(users, { fields: [policies.createdById], references: [users.id] })
}));