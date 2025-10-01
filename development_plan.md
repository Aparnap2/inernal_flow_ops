# HubSpot Operations Orchestrator - Comprehensive Development Plan

## Executive Summary

Short answer: The dev plan is strong and aligned with the scoped goal—an event-driven, internal-ops orchestrator with AGUI HITL on top of HubSpot—yet a few critical tweaks are needed for Cloudflare Workers compatibility, auth, queueing, and observability to ensure a smooth v1 launch.

### What’s already excellent
- **Architecture matches the problem**: HubSpot webhooks → stateful LangGraph workflows with Redis checkpoints → ops hub mirrors and reconciliation → AGUI approvals and KPIs, with temporal lineage for audits.
- **Clear workflows**: Company intake/mirror, Contact role mapping, Deal stage → internal kickoff, and Procurement approval are fully spelled out with validations and HITL.
- **Solid data design**: Envelope+payload event model, Prisma schema for Runs/Approvals/Exceptions/Policies, and nightly reconciliation with auto-repair where safe.
- **DevOps hygiene**: Monorepo, Docker dev stack, CI/CD, replay and recovery, idempotency, and risk mitigation are thoughtfully included.

### Critical adjustments before build
- **Workers + RabbitMQ**: Cloudflare Workers can’t speak AMQP/TCP directly; route webhooks to Workers, then hand off to the Python service for AMQP publish/consume, or use CloudAMQP’s HTTP API from Workers for enqueueing.
- **Auth in Workers**: NextAuth is optimized for Next.js server runtimes; for Hono on Workers prefer Auth.js core (WebCrypto/JWT) or a lightweight RBAC with signed cookies/JWTs to avoid serverful assumptions.
- **Observability scope**: Prometheus/Grafana add operational weight; for v1 use Inngest events as the durable, queryable step log plus Sentry, keeping Grafana optional behind a feature flag.
- **Temporal KG scope**: Keep Neo4j for lineage and as-of policy queries in v1, but defer GraphRAG/NL-to-Cypher until usage proves the need to avoid early complexity.

### HubSpot event handling improvements
- **Subscription strategy**: Subscribe to create/update plus associationChange for companies/contacts/deals, and filter by property masks and specific stage transitions to reduce noise.
- **Burst control**: Debounce bursts using `hs_lastmodifieddate` and per-object locks before launching workflows to prevent duplicate executions from quick successive updates.
- **Delivery reliability**: Use Webhooks Journal (v4 beta) for replay/debug of missed deliveries to bolster reliability during early rollout.

### AGUI and LangGraph best practices
- **Command safety**: AGUI commands map to safe functions with confirmation modals; approvals happen only in the Approval Sheet with diffs, risk flags, and the policy snapshot visible.
- **LangGraph resilience**: Use LangGraph interrupts for HITL and Redis checkpoint resume; ensure every node is idempotent with a correlation key from `object_id + updatedAt + workflow_id`.
- **State partitioning**: Store short-term state in the workflow, and long-term audit facts in Neo4j; don’t overstuff prompts—use the lineage panel to power “explain why” in the UI.

### Data layer and serverless fit
- **Prisma adapter**: Neon + Prisma driver adapter is the right choice for Workers; verify the adapter path and connection caching to avoid cold-start penalty.
- **Redis checkpoints**: Upstash Redis REST client is appropriate for Workers and for LangGraph’s checkpoint store; adopt the current checkpoint package and keep keys namespaced by run.
- **Relational focus**: Keep Mongo optional; Postgres covers analytics and joins better for Runs/Approvals/Exceptions, with JSON columns for flexible payloads.

### Reconciliation and exceptions
- **Nightly + fast reconcile**: Nightly reconcile HubSpot vs Airtable mirrors and queue Exceptions with one-click fixes, but also add a light “after write” reconcile that confirms critical fields within minutes for faster feedback.
- **Exception safety**: In Exceptions, preview diffs and guard “apply fix” with idempotency and a dry-run explain to prevent unwanted changes.

### Security and RBAC
- **Approval controls**: Admin-only approvals enforced in UI and API; add CSRF on approve/reject routes and default PII redaction with “reveal with reason” for admins.
- **Webhook integrity**: Verify HubSpot webhook signatures and store raw payload refs for forensics and replay.

### Phase/timeline tuning
- **Thin v0 first**: Pull a thin v0 into Weeks 1–6: HubSpot webhooks, Company intake/mirror workflow with AGUI Approval Sheet, Runs/Approvals tables, and the reconciliation/Exceptions loop.
- **Defer advanced KG**: Move GraphRAG/NL-to-Cypher into a v1.1 flag after Weeks 12–16; keep lineage queries first to hit value earlier.
- **Observability gating**: Treat Grafana/Prometheus as optional; lead with Inngest dashboards and Sentry to reduce ops burden at launch.

### Go/no-go checklist for v1
- **Webhook ingress**: Workers webhook → verified, debounced, and enqueued to Python service or CloudAMQP HTTP reliably.
- **LangGraph reliability**: LangGraph nodes idempotent with Redis checkpoints; replay from checkpoint tested for each workflow.
- **AGUI approvals**: AGUI Approval Sheet live with admin-only actions and policy snapshots; Exceptions queue delivers one-click safe fixes.
- **Operational visibility**: KPIs and Runs table wired; Inngest event traces visible; Sentry alerts configured; Grafana gated behind a flag.

If these adjustments are accepted, the plan is ready to execute to a robust v1 that fits the serverless runtime, secures HITL to the AGUI, and keeps observability and queueing practical on day one.

## To-Do Summary by Phase

### Phase 1 – Foundation & Core Infrastructure (Weeks 1-4)
1. Environment setup: development/staging/production parity, CI/CD automation, observability scaffolding.
2. Monorepo tooling: shared TypeScript/Python setup, linting/formatting, concurrent dev scripts (root `package.json`).
3. Containerized dev stack: Docker Compose services (Postgres, Redis, Neo4j, RabbitMQ, AI service, frontend, Prometheus, Grafana).
4. Environment configs: `.env.development`, Workers `wrangler.toml`, GitHub Actions workflow templates.

### Phase 2 – Event Infrastructure & Webhook Processing (Weeks 5-8)
1. HubSpot webhook endpoint with signature verification, event dedupe, and idempotency locks.
2. Event envelope schema, queue publisher, and Python webhook processor orchestration.
3. Retry/replay tooling: dead-letter queues, reconciliation scripts, and burst debouncing.

### Phase 3 – AI Service & LangGraph Workflows (Weeks 9-12)
1. LangGraph workflow engine with Redis checkpointing and HITL interrupts.
2. Workflow definitions: company intake/mirror, contact role mapping, deal kickoff, procurement approval.
3. Exception handling: safe auto-repair routines with diff previews and dry-run validations.

### Phase 4 – Frontend & Agentic UI (Weeks 13-16)
1. React 18 + Vite + CopilotKit agentic UI scaffold with approval sheet layout.
2. AGUI command palette, safe function bindings, and confirmation modals.
3. Admin-only approval experience with policy snapshots, risk flags, and lineage explanations.

### Phase 5 – Knowledge Graph & Temporal Lineage (Weeks 17-20)
1. Neo4j temporal model for accounts/contacts/deals with lineage queries.
2. HubSpot mirror sync jobs writing to temporal graph nodes/relationships.
3. Lineage-driven insights powering AGUI “explain why” and audit views (GraphRAG deferred to v1.1).

### Phase 6 – Integration & Data Layer (Weeks 21-24)
1. Prisma schema finalization with Neon adapter caching for Workers.
2. Upstash Redis REST client integration for checkpoints and idempotency stores.
3. Airtable mirror, nightly reconciliations, and after-write validation loops.

### Phase 7 – Security & Compliance (Weeks 25-26)
1. Auth.js (Workers) or JWT-based RBAC with signed cookies, CSRF protection, and session hardening.
2. HubSpot webhook signature storage, payload retention, and audit logging.
3. PII redaction defaults with “reveal with reason” tracking for admins.

### Phase 8 – Testing & Quality Assurance (Weeks 27-28)
1. Automated tests: unit (Workers, FastAPI, LangGraph), integration (workflow runs), end-to-end (AGUI flows).
2. Load/debounce simulations for webhook bursts and queue replay scenarios.
3. Disaster-recovery drills covering Redis checkpoint resumes and Neo4j lineage restores.

### Phase 9 – Deployment & Production Readiness (Weeks 29-30)
1. Go/no-go checklist validation: webhook ingress path, LangGraph replay, AGUI approval sheet, Exceptions queue.
2. Observability: Inngest dashboards, Sentry alerts, Grafana flagging, KPIs wired to Runs table.
3. Launch playbook: staged rollout, rollback plan, and Ops runbooks for approvals and exceptions.

## Phase 1: Foundation & Core Infrastructure (Weeks 1-4)

### 1.1 Development Environment Setup

**Requirements:**
- Set up development, staging, and production environments
- Configure CI/CD pipelines with automated testing
- Establish monitoring and observability stack

**Implementation Details:**

#### Project Structure Setup
```bash
# Initialize monorepo structure
mkdir hubspot-orchestrator && cd hubspot-orchestrator
npm create hono@latest api --template cloudflare-workers
npm create vite@latest frontend -- --template react-ts
mkdir ai-service && cd ai-service && python -m venv venv

# Project structure
hubspot-orchestrator/
├── api/                    # Hono API on Cloudflare Workers
│   ├── src/
│   │   ├── index.ts
│   │   ├── routes/
│   │   ├── middleware/
│   │   └── types/
│   ├── wrangler.toml
│   └── package.json
├── frontend/               # React + Vite + CopilotKit
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── pages/
│   ├── vite.config.ts
│   └── package.json
├── ai-service/            # FastAPI + LangGraph
│   ├── app/
│   │   ├── main.py
│   │   ├── workflows/
│   │   ├── models/
│   │   └── services/
│   ├── requirements.txt
│   └── Dockerfile
├── shared/                # Shared types and utilities
│   ├── types/
│   └── utils/
├── docker-compose.yml     # Local development stack
├── .github/workflows/     # CI/CD pipelines
└── docs/                  # Documentation
```

#### Docker Compose Development Stack (Fixed for Port Access)
```yaml
# docker-compose.yml
version: '3.8'
services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: orchestrator_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis for caching and checkpoints
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Neo4j for temporal knowledge graph
  neo4j:
    image: neo4j:5.15-community
    environment:
      NEO4J_AUTH: neo4j/password
      NEO4J_PLUGINS: '["apoc", "graph-data-science"]'
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "password", "RETURN 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  # RabbitMQ for message queuing
  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  # FastAPI AI Service
  ai-service:
    build: 
      context: ./ai-service
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/orchestrator_dev
      - REDIS_URL=redis://redis:6379
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password
      - RABBITMQ_URL=amqp://admin:admin@rabbitmq:5672
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      neo4j:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    volumes:
      - ./ai-service:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend Development Server (Docker-compatible)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "5173:5173" # Map host port 5173 to container port 5173
    environment:
      - NODE_ENV=development
      - VITE_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules # Prevent node_modules from being overwritten
    command: pnpm run dev:docker
    depends_on:
      - ai-service

  # Prometheus for metrics
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'

  # Grafana for visualization
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

volumes:
  postgres_data:
  redis_data:
  neo4j_data:
  rabbitmq_data:
  prometheus_data:
  grafana_data:

networks:
  default:
    name: hubspot-orchestrator-network
```

#### Frontend Dockerfile for Development
```dockerfile
# frontend/Dockerfile.dev
FROM node:20-alpine

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Expose port
EXPOSE 5173

# Start development server with proper host binding
CMD ["pnpm", "run", "dev:docker"]
```

#### AI Service Dockerfile
```dockerfile
# ai-service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

#### Environment Configuration
```bash
# .env.development
# Database
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/orchestrator_dev"
REDIS_URL="redis://localhost:6379"
NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="password"

# HubSpot
HUBSPOT_CLIENT_ID="your-hubspot-client-id"
HUBSPOT_CLIENT_SECRET="your-hubspot-client-secret"
HUBSPOT_WEBHOOK_SECRET="your-webhook-secret"

# OpenAI
OPENAI_API_KEY="your-openai-api-key"

# Inngest
INNGEST_EVENT_KEY="your-inngest-event-key"
INNGEST_SIGNING_KEY="your-inngest-signing-key"

# Cloudflare Workers
CLOUDFLARE_API_TOKEN="your-cloudflare-api-token"
CLOUDFLARE_ACCOUNT_ID="your-account-id"

# External Services
AIRTABLE_API_KEY="your-airtable-api-key"
NOTION_API_KEY="your-notion-api-key"
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
```

#### Cloudflare Workers Configuration
```toml
# api/wrangler.toml
name = "hubspot-orchestrator-api"
main = "src/index.ts"
compatibility_date = "2024-01-01"
compatibility_flags = ["nodejs_compat"]

[env.development]
name = "hubspot-orchestrator-api-dev"
vars = { ENVIRONMENT = "development" }

[env.staging]
name = "hubspot-orchestrator-api-staging"
vars = { ENVIRONMENT = "staging" }

[env.production]
name = "hubspot-orchestrator-api-prod"
vars = { ENVIRONMENT = "production" }

[[env.production.kv_namespaces]]
binding = "CACHE"
id = "your-kv-namespace-id"

[[env.production.r2_buckets]]
binding = "ASSETS"
bucket_name = "orchestrator-assets"

[env.production.vars]
DATABASE_URL = "your-production-database-url"
REDIS_URL = "your-production-redis-url"
```

#### GitHub Actions CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloudflare Workers

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: |
          npm ci
          cd api && npm ci
          cd ../frontend && npm ci
      
      - name: Run tests
        run: |
          npm run test
          cd api && npm run test
          cd ../frontend && npm run test
      
      - name: Type check
        run: |
          cd api && npm run type-check
          cd ../frontend && npm run type-check

  deploy-api:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Cloudflare Workers
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          workingDirectory: 'api'
          environment: 'production'

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Build and deploy frontend
        run: |
          cd frontend
          npm ci
          npm run build
          # Deploy to your preferred hosting service
```

#### Development Scripts
```json
// package.json (root)
{
  "name": "hubspot-orchestrator",
  "scripts": {
    "dev": "concurrently \"npm run dev:api\" \"npm run dev:frontend\" \"npm run dev:ai\"",
    "dev:api": "cd api && npm run dev",
    "dev:frontend": "cd frontend && npm run dev",
    "dev:ai": "cd ai-service && python -m uvicorn app.main:app --reload",
    "docker:up": "docker-compose up -d",
    "docker:down": "docker-compose down",
    "docker:logs": "docker-compose logs -f",
    "test": "npm run test:api && npm run test:frontend",
    "test:api": "cd api && npm test",
    "test:frontend": "cd frontend && npm test",
    "lint": "eslint . --ext .ts,.tsx",
    "format": "prettier --write .",
    "type-check": "tsc --noEmit"
  },
  "devDependencies": {
    "concurrently": "^8.2.2",
    "eslint": "^8.57.0",
    "prettier": "^3.1.1",
    "typescript": "^5.3.3"
  }
}
```

**Tasks:**
- ✅ Initialize project structure with TypeScript/Python monorepo
- ✅ Configure Docker containers for local development
- ✅ Set up GitHub Actions for automated deployments
- ✅ Configure environment-specific secrets management

**Sub-tasks:**
- ✅ Create `.env` templates for each environment
- ✅ Set up Docker Compose with hot reload for development
- ✅ Configure ESLint, Prettier, and pre-commit hooks
- ✅ Establish branching strategy and PR templates

### 1.2 Database Layer Implementation

**Requirements:**
- Implement dual database strategy (Neon Postgres + Upstash Redis)
- Set up Prisma ORM with type-safe schema
- Configure connection pooling and serverless optimization

**Implementation Details:**

#### Prisma Schema Design
```prisma
// prisma/schema.prisma
generator client {
  provider        = "prisma-client-js"
  previewFeatures = ["driverAdapters"]
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  role      UserRole @default(VIEWER)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Relations
  approvals Approval[]
  runs      Run[]     @relation("RunCreatedBy")

  @@map("users")
}

enum UserRole {
  ADMIN
  OPERATOR
  VIEWER
}

model Account {
  id                String   @id @default(cuid())
  hubspotId         String   @unique
  name              String
  domain            String?
  industry          String?
  employeeCount     Int?
  annualRevenue     Decimal?
  lifecycleStage    String?
  lastModifiedDate  DateTime
  createdAt         DateTime @default(now())
  updatedAt         DateTime @updatedAt

  // Metadata
  properties        Json?
  customFields      Json?
  
  // Relations
  contacts          Contact[]
  deals             Deal[]
  runs              Run[]
  
  @@map("accounts")
}

model Contact {
  id                String   @id @default(cuid())
  hubspotId         String   @unique
  email             String?
  firstName         String?
  lastName          String?
  jobTitle          String?
  phone             String?
  lifecycleStage    String?
  lastModifiedDate  DateTime
  createdAt         DateTime @default(now())
  updatedAt         DateTime @updatedAt

  // Relations
  accountId         String?
  account           Account? @relation(fields: [accountId], references: [id])
  deals             Deal[]
  runs              Run[]

  // Metadata
  properties        Json?
  customFields      Json?

  @@map("contacts")
}

model Deal {
  id                String     @id @default(cuid())
  hubspotId         String     @unique
  name              String
  stage             String
  amount            Decimal?
  closeDate         DateTime?
  probability       Float?
  lastModifiedDate  DateTime
  createdAt         DateTime   @default(now())
  updatedAt         DateTime   @updatedAt

  // Relations
  accountId         String?
  account           Account?   @relation(fields: [accountId], references: [id])
  contactId         String?
  contact           Contact?   @relation(fields: [contactId], references: [id])
  runs              Run[]

  // Metadata
  properties        Json?
  customFields      Json?

  @@map("deals")
}

model Run {
  id                String      @id @default(cuid())
  correlationId     String      @unique
  workflowId        String
  status            RunStatus   @default(PENDING)
  startedAt         DateTime    @default(now())
  completedAt       DateTime?
  errorMessage      String?
  
  // Context
  eventType         String
  objectType        String
  objectId          String
  
  // Relations
  createdById       String?
  createdBy         User?       @relation("RunCreatedBy", fields: [createdById], references: [id])
  accountId         String?
  account           Account?    @relation(fields: [accountId], references: [id])
  contactId         String?
  contact           Contact?    @relation(fields: [contactId], references: [id])
  dealId            String?
  deal              Deal?       @relation(fields: [dealId], references: [id])
  
  // Workflow data
  steps             RunStep[]
  approvals         Approval[]
  exceptions        Exception[]
  
  // Metadata
  payload           Json?
  checkpointData    Json?
  
  @@map("runs")
}

enum RunStatus {
  PENDING
  RUNNING
  WAITING_APPROVAL
  COMPLETED
  FAILED
  CANCELLED
}

model RunStep {
  id            String      @id @default(cuid())
  runId         String
  run           Run         @relation(fields: [runId], references: [id], onDelete: Cascade)
  
  stepName      String
  status        StepStatus  @default(PENDING)
  startedAt     DateTime    @default(now())
  completedAt   DateTime?
  errorMessage  String?
  retryCount    Int         @default(0)
  
  // Step data
  input         Json?
  output        Json?
  
  @@map("run_steps")
}

enum StepStatus {
  PENDING
  RUNNING
  COMPLETED
  FAILED
  SKIPPED
}

model Approval {
  id              String        @id @default(cuid())
  runId           String
  run             Run           @relation(fields: [runId], references: [id], onDelete: Cascade)
  
  type            ApprovalType
  status          ApprovalStatus @default(PENDING)
  requestedAt     DateTime      @default(now())
  respondedAt     DateTime?
  
  // Approval context
  title           String
  description     String?
  riskLevel       RiskLevel     @default(LOW)
  
  // Policy context
  policyId        String?
  policySnapshot  Json?
  
  // Response
  approverId      String?
  approver        User?         @relation(fields: [approverId], references: [id])
  decision        Boolean?
  justification   String?
  
  // Metadata
  metadata        Json?
  
  @@map("approvals")
}

enum ApprovalType {
  PROCUREMENT
  RISK_THRESHOLD
  MANUAL_REVIEW
  POLICY_EXCEPTION
}

enum ApprovalStatus {
  PENDING
  APPROVED
  REJECTED
  EXPIRED
}

enum RiskLevel {
  LOW
  MEDIUM
  HIGH
  CRITICAL
}

model Exception {
  id              String          @id @default(cuid())
  runId           String
  run             Run             @relation(fields: [runId], references: [id], onDelete: Cascade)
  
  type            ExceptionType
  status          ExceptionStatus @default(OPEN)
  createdAt       DateTime        @default(now())
  resolvedAt      DateTime?
  
  // Exception details
  title           String
  description     String
  errorCode       String?
  
  // Resolution
  resolutionType  ResolutionType?
  resolutionData  Json?
  resolvedById    String?
  
  // Metadata
  metadata        Json?
  
  @@map("exceptions")
}

enum ExceptionType {
  DATA_VALIDATION
  INTEGRATION_ERROR
  BUSINESS_RULE_VIOLATION
  TIMEOUT
  UNKNOWN
}

enum ExceptionStatus {
  OPEN
  IN_PROGRESS
  RESOLVED
  IGNORED
}

enum ResolutionType {
  AUTO_REPAIR
  MANUAL_FIX
  IGNORE
  ESCALATE
}

model Policy {
  id              String    @id @default(cuid())
  name            String
  description     String?
  version         String    @default("1.0")
  isActive        Boolean   @default(true)
  
  // Policy rules
  conditions      Json      // JSON schema for conditions
  actions         Json      // JSON schema for actions
  
  // Temporal tracking
  validFrom       DateTime  @default(now())
  validTo         DateTime?
  
  // Metadata
  createdAt       DateTime  @default(now())
  updatedAt       DateTime  @updatedAt
  createdById     String?
  
  @@map("policies")
}

model WebhookEvent {
  id                String    @id @default(cuid())
  hubspotEventId    String?   @unique
  eventType         String
  objectType        String
  objectId          String
  correlationId     String
  
  // Event data
  payload           Json
  signature         String?
  
  // Processing status
  status            EventStatus @default(RECEIVED)
  processedAt       DateTime?
  errorMessage      String?
  retryCount        Int         @default(0)
  
  // Timestamps
  occurredAt        DateTime
  receivedAt        DateTime    @default(now())
  
  @@map("webhook_events")
}

enum EventStatus {
  RECEIVED
  PROCESSING
  PROCESSED
  FAILED
  IGNORED
}
```

#### Prisma Client Configuration
```typescript
// shared/lib/prisma.ts
import { PrismaClient } from '@prisma/client'
import { Pool, neonConfig } from '@neondatabase/serverless'
import { PrismaNeon } from '@prisma/adapter-neon'

// Configure Neon for serverless environments
neonConfig.fetchConnectionCache = true

const connectionString = process.env.DATABASE_URL!

let prisma: PrismaClient

if (process.env.NODE_ENV === 'production') {
  // Use Neon adapter for serverless environments
  const pool = new Pool({ connectionString })
  const adapter = new PrismaNeon(pool)
  prisma = new PrismaClient({ adapter })
} else {
  // Use regular Prisma client for development
  prisma = new PrismaClient({
    log: ['query', 'error', 'warn'],
  })
}

export default prisma

// Connection helper for Cloudflare Workers
export const getPrismaClient = () => {
  if (typeof globalThis !== 'undefined' && globalThis.prisma) {
    return globalThis.prisma
  }
  
  const client = new PrismaClient({
    adapter: new PrismaNeon(new Pool({ connectionString })),
  })
  
  if (typeof globalThis !== 'undefined') {
    globalThis.prisma = client
  }
  
  return client
}
```

#### Redis Configuration with Upstash
```typescript
// shared/lib/redis.ts
import { Redis } from '@upstash/redis'

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
})

// Redis utilities for different use cases
export class RedisService {
  // Session management
  static async setSession(sessionId: string, data: any, ttl = 3600) {
    return redis.setex(`session:${sessionId}`, ttl, JSON.stringify(data))
  }

  static async getSession(sessionId: string) {
    const data = await redis.get(`session:${sessionId}`)
    return data ? JSON.parse(data as string) : null
  }

  static async deleteSession(sessionId: string) {
    return redis.del(`session:${sessionId}`)
  }

  // Rate limiting
  static async checkRateLimit(key: string, limit: number, window: number) {
    const current = await redis.incr(`rate_limit:${key}`)
    if (current === 1) {
      await redis.expire(`rate_limit:${key}`, window)
    }
    return current <= limit
  }

  // Caching
  static async cache<T>(key: string, fetcher: () => Promise<T>, ttl = 300): Promise<T> {
    const cached = await redis.get(`cache:${key}`)
    if (cached) {
      return JSON.parse(cached as string)
    }

    const data = await fetcher()
    await redis.setex(`cache:${key}`, ttl, JSON.stringify(data))
    return data
  }

  // LangGraph checkpoints
  static async saveCheckpoint(threadId: string, checkpointId: string, data: any) {
    return redis.hset(`checkpoint:${threadId}`, checkpointId, JSON.stringify(data))
  }

  static async getCheckpoint(threadId: string, checkpointId?: string) {
    if (checkpointId) {
      const data = await redis.hget(`checkpoint:${threadId}`, checkpointId)
      return data ? JSON.parse(data as string) : null
    }
    
    const allCheckpoints = await redis.hgetall(`checkpoint:${threadId}`)
    return Object.entries(allCheckpoints).reduce((acc, [id, data]) => {
      acc[id] = JSON.parse(data as string)
      return acc
    }, {} as Record<string, any>)
  }

  // Idempotency keys
  static async setIdempotencyKey(key: string, result: any, ttl = 3600) {
    return redis.setex(`idempotent:${key}`, ttl, JSON.stringify(result))
  }

  static async getIdempotencyResult(key: string) {
    const data = await redis.get(`idempotent:${key}`)
    return data ? JSON.parse(data as string) : null
  }
}

export default redis
```

#### Database Migration Scripts
```typescript
// scripts/migrate.ts
import { execSync } from 'child_process'
import prisma from '../shared/lib/prisma'

async function runMigrations() {
  try {
    console.log('🔄 Running database migrations...')
    
    // Generate Prisma client
    execSync('npx prisma generate', { stdio: 'inherit' })
    
    // Run migrations
    execSync('npx prisma migrate deploy', { stdio: 'inherit' })
    
    console.log('✅ Migrations completed successfully')
  } catch (error) {
    console.error('❌ Migration failed:', error)
    process.exit(1)
  } finally {
    await prisma.$disconnect()
  }
}

runMigrations()
```

#### Database Seeding
```typescript
// prisma/seed.ts
import { PrismaClient, UserRole } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  console.log('🌱 Seeding database...')

  // Create admin user
  const adminUser = await prisma.user.upsert({
    where: { email: 'admin@company.com' },
    update: {},
    create: {
      email: 'admin@company.com',
      name: 'Admin User',
      role: UserRole.ADMIN,
    },
  })

  // Create sample policies
  const procurementPolicy = await prisma.policy.upsert({
    where: { id: 'procurement-policy-1' },
    update: {},
    create: {
      id: 'procurement-policy-1',
      name: 'Procurement Approval Policy',
      description: 'Requires approval for deals over $10,000',
      conditions: {
        dealAmount: { gte: 10000 },
        dealStage: { in: ['proposal', 'negotiation'] }
      },
      actions: {
        requireApproval: true,
        approvalType: 'PROCUREMENT',
        riskLevel: 'MEDIUM'
      },
    },
  })

  // Create sample account
  const sampleAccount = await prisma.account.create({
    data: {
      hubspotId: 'sample-account-1',
      name: 'Sample Company Inc.',
      domain: 'sample-company.com',
      industry: 'Technology',
      employeeCount: 100,
      annualRevenue: 1000000,
      lifecycleStage: 'customer',
      lastModifiedDate: new Date(),
      properties: {
        customField1: 'value1',
        customField2: 'value2'
      }
    },
  })

  console.log('✅ Database seeded successfully')
  console.log(`👤 Admin user: ${adminUser.email}`)
  console.log(`📋 Policy created: ${procurementPolicy.name}`)
  console.log(`🏢 Sample account: ${sampleAccount.name}`)
}

main()
  .catch((e) => {
    console.error('❌ Seeding failed:', e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
```

**Tasks:**
- ✅ Design and implement Prisma schema for core entities
- ✅ Set up Neon Postgres with branching for preview environments
- ✅ Configure Upstash Redis for caching and checkpoints
- ✅ Implement database migration strategy

**Sub-tasks:**
- ✅ Define models: Account, Contact, Deal, Run, Approval, Exception, Policy
- ✅ Set up Prisma Client with connection pooling
- ✅ Configure Redis for session storage and rate limiting
- ✅ Create database seeding scripts for development

### 1.3 Authentication & RBAC System

**Requirements:**
- Implement JWT-based authentication with NextAuth.js
- Design role-based access control (Admin, Operator, Viewer)
- Secure API endpoints with proper authorization

**Implementation Details:**

#### NextAuth.js Configuration
```typescript
// frontend/src/lib/auth.ts
import { NextAuthOptions } from 'next-auth'
import { PrismaAdapter } from '@next-auth/prisma-adapter'
import GoogleProvider from 'next-auth/providers/google'
import CredentialsProvider from 'next-auth/providers/credentials'
import prisma from '@/lib/prisma'
import { UserRole } from '@prisma/client'
import bcrypt from 'bcryptjs'

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        const user = await prisma.user.findUnique({
          where: { email: credentials.email }
        })

        if (!user || !user.password) {
          return null
        }

        const isPasswordValid = await bcrypt.compare(
          credentials.password,
          user.password
        )

        if (!isPasswordValid) {
          return null
        }

        return {
          id: user.id,
          email: user.email,
          name: user.name,
          role: user.role,
        }
      }
    })
  ],
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  callbacks: {
    async jwt({ token, user, account }) {
      if (user) {
        token.role = user.role
        token.id = user.id
      }
      return token
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string
        session.user.role = token.role as UserRole
      }
      return session
    },
    async signIn({ user, account, profile }) {
      // Auto-assign role based on email domain or other criteria
      if (account?.provider === 'google') {
        const email = user.email!
        const domain = email.split('@')[1]
        
        // Company domain gets admin access
        if (domain === 'yourcompany.com') {
          await prisma.user.upsert({
            where: { email },
            update: { role: UserRole.ADMIN },
            create: {
              email,
              name: user.name || '',
              role: UserRole.ADMIN,
            }
          })
        }
      }
      return true
    }
  },
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error',
  },
}
```

#### Role-Based Access Control Middleware
```typescript
// frontend/src/middleware.ts
import { withAuth } from 'next-auth/middleware'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Define route permissions
const routePermissions = {
  '/dashboard': ['ADMIN', 'OPERATOR', 'VIEWER'],
  '/runs': ['ADMIN', 'OPERATOR', 'VIEWER'],
  '/approvals': ['ADMIN', 'OPERATOR'],
  '/admin': ['ADMIN'],
  '/settings': ['ADMIN'],
  '/users': ['ADMIN'],
  '/policies': ['ADMIN', 'OPERATOR'],
} as const

export default withAuth(
  function middleware(req: NextRequest) {
    const token = req.nextauth.token
    const pathname = req.nextUrl.pathname

    // Check if route requires specific permissions
    for (const [route, allowedRoles] of Object.entries(routePermissions)) {
      if (pathname.startsWith(route)) {
        if (!token?.role || !allowedRoles.includes(token.role as any)) {
          return NextResponse.redirect(new URL('/unauthorized', req.url))
        }
      }
    }

    return NextResponse.next()
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token,
    },
  }
)

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/runs/:path*',
    '/approvals/:path*',
    '/admin/:path*',
    '/settings/:path*',
    '/users/:path*',
    '/policies/:path*',
  ]
}
```

#### API Route Protection
```typescript
// api/src/middleware/auth.ts
import { Context, Next } from 'hono'
import jwt from 'jsonwebtoken'
import { UserRole } from '@prisma/client'

interface AuthContext {
  user: {
    id: string
    email: string
    role: UserRole
  }
}

export const authMiddleware = async (c: Context, next: Next) => {
  const authHeader = c.req.header('Authorization')
  
  if (!authHeader?.startsWith('Bearer ')) {
    return c.json({ error: 'Missing or invalid authorization header' }, 401)
  }

  const token = authHeader.substring(7)
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any
    c.set('user', decoded)
    await next()
  } catch (error) {
    return c.json({ error: 'Invalid token' }, 401)
  }
}

export const requireRole = (allowedRoles: UserRole[]) => {
  return async (c: Context, next: Next) => {
    const user = c.get('user')
    
    if (!user || !allowedRoles.includes(user.role)) {
      return c.json({ error: 'Insufficient permissions' }, 403)
    }
    
    await next()
  }
}

// Usage in routes
export const adminOnly = requireRole([UserRole.ADMIN])
export const operatorOrAdmin = requireRole([UserRole.ADMIN, UserRole.OPERATOR])
export const anyAuthenticated = requireRole([UserRole.ADMIN, UserRole.OPERATOR, UserRole.VIEWER])
```

#### Protected Route Components
```tsx
// frontend/src/components/auth/ProtectedRoute.tsx
import { useSession } from 'next-auth/react'
import { UserRole } from '@prisma/client'
import { ReactNode } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2 } from 'lucide-react'

interface ProtectedRouteProps {
  children: ReactNode
  allowedRoles?: UserRole[]
  fallback?: ReactNode
}

export function ProtectedRoute({ 
  children, 
  allowedRoles = [UserRole.ADMIN, UserRole.OPERATOR, UserRole.VIEWER],
  fallback 
}: ProtectedRouteProps) {
  const { data: session, status } = useSession()

  if (status === 'loading') {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          You must be signed in to access this page.
        </AlertDescription>
      </Alert>
    )
  }

  if (!session?.user?.role || !allowedRoles.includes(session.user.role)) {
    return fallback || (
      <Alert variant="destructive">
        <AlertDescription>
          You don't have permission to access this page.
        </AlertDescription>
      </Alert>
    )
  }

  return <>{children}</>
}

// Role-specific components
export const AdminOnly = ({ children }: { children: ReactNode }) => (
  <ProtectedRoute allowedRoles={[UserRole.ADMIN]}>
    {children}
  </ProtectedRoute>
)

export const OperatorOrAdmin = ({ children }: { children: ReactNode }) => (
  <ProtectedRoute allowedRoles={[UserRole.ADMIN, UserRole.OPERATOR]}>
    {children}
  </ProtectedRoute>
)
```

#### User Management Interface
```tsx
// frontend/src/components/admin/UserManagement.tsx
import { useState, useEffect } from 'react'
import { UserRole } from '@prisma/client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { AdminOnly } from '@/components/auth/ProtectedRoute'

interface User {
  id: string
  email: string
  name: string | null
  role: UserRole
  createdAt: string
  lastLoginAt: string | null
}

export function UserManagement() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [newUserEmail, setNewUserEmail] = useState('')
  const [newUserRole, setNewUserRole] = useState<UserRole>(UserRole.VIEWER)

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await fetch('/api/admin/users')
      const data = await response.json()
      setUsers(data)
    } catch (error) {
      console.error('Failed to fetch users:', error)
    } finally {
      setLoading(false)
    }
  }

  const updateUserRole = async (userId: string, newRole: UserRole) => {
    try {
      await fetch(`/api/admin/users/${userId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: newRole }),
      })
      fetchUsers()
    } catch (error) {
      console.error('Failed to update user role:', error)
    }
  }

  const inviteUser = async () => {
    try {
      await fetch('/api/admin/users/invite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: newUserEmail, role: newUserRole }),
      })
      setNewUserEmail('')
      fetchUsers()
    } catch (error) {
      console.error('Failed to invite user:', error)
    }
  }

  const getRoleBadgeVariant = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN: return 'destructive'
      case UserRole.OPERATOR: return 'default'
      case UserRole.VIEWER: return 'secondary'
    }
  }

  return (
    <AdminOnly>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">User Management</h2>
        </div>

        {/* Invite User Form */}
        <div className="flex gap-4 p-4 border rounded-lg">
          <Input
            placeholder="Email address"
            value={newUserEmail}
            onChange={(e) => setNewUserEmail(e.target.value)}
            className="flex-1"
          />
          <Select value={newUserRole} onValueChange={(value) => setNewUserRole(value as UserRole)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={UserRole.VIEWER}>Viewer</SelectItem>
              <SelectItem value={UserRole.OPERATOR}>Operator</SelectItem>
              <SelectItem value={UserRole.ADMIN}>Admin</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={inviteUser} disabled={!newUserEmail}>
            Invite User
          </Button>
        </div>

        {/* Users Table */}
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Last Login</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>{user.name || 'N/A'}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  <Badge variant={getRoleBadgeVariant(user.role)}>
                    {user.role}
                  </Badge>
                </TableCell>
                <TableCell>{new Date(user.createdAt).toLocaleDateString()}</TableCell>
                <TableCell>
                  {user.lastLoginAt ? new Date(user.lastLoginAt).toLocaleDateString() : 'Never'}
                </TableCell>
                <TableCell>
                  <Select
                    value={user.role}
                    onValueChange={(value) => updateUserRole(user.id, value as UserRole)}
                  >
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={UserRole.VIEWER}>Viewer</SelectItem>
                      <SelectItem value={UserRole.OPERATOR}>Operator</SelectItem>
                      <SelectItem value={UserRole.ADMIN}>Admin</SelectItem>
                    </SelectContent>
                  </Select>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </AdminOnly>
  )
}
```

#### Session Management with Redis
```typescript
// shared/lib/session.ts
import { RedisService } from './redis'
import { UserRole } from '@prisma/client'
import jwt from 'jsonwebtoken'

export interface SessionData {
  userId: string
  email: string
  role: UserRole
  loginAt: Date
  lastActivity: Date
}

export class SessionManager {
  private static readonly SESSION_TTL = 30 * 24 * 60 * 60 // 30 days
  private static readonly JWT_SECRET = process.env.JWT_SECRET!

  static async createSession(userData: Omit<SessionData, 'loginAt' | 'lastActivity'>) {
    const sessionId = crypto.randomUUID()
    const now = new Date()
    
    const sessionData: SessionData = {
      ...userData,
      loginAt: now,
      lastActivity: now,
    }

    await RedisService.setSession(sessionId, sessionData, this.SESSION_TTL)
    
    // Create JWT token
    const token = jwt.sign(
      { sessionId, ...userData },
      this.JWT_SECRET,
      { expiresIn: '30d' }
    )

    return { sessionId, token }
  }

  static async getSession(sessionId: string): Promise<SessionData | null> {
    return RedisService.getSession(sessionId)
  }

  static async updateActivity(sessionId: string) {
    const session = await this.getSession(sessionId)
    if (session) {
      session.lastActivity = new Date()
      await RedisService.setSession(sessionId, session, this.SESSION_TTL)
    }
  }

  static async destroySession(sessionId: string) {
    return RedisService.deleteSession(sessionId)
  }

  static async validateToken(token: string): Promise<SessionData | null> {
    try {
      const decoded = jwt.verify(token, this.JWT_SECRET) as any
      const session = await this.getSession(decoded.sessionId)
      
      if (session) {
        await this.updateActivity(decoded.sessionId)
      }
      
      return session
    } catch (error) {
      return null
    }
  }
}
```

**Tasks:**
- ✅ Set up NextAuth.js with custom providers
- ✅ Implement role-based middleware for API routes
- ✅ Create user management interfaces
- ✅ Configure session management with Redis

**Sub-tasks:**
- ✅ Define user roles and permissions matrix
- ✅ Implement protected route components
- ✅ Create login/logout flows with proper redirects
- ✅ Set up CSRF protection for sensitive operations

## Phase 2: Event Infrastructure & Webhook Processing (Weeks 5-8)

### 2.1 HubSpot Webhook Integration

**Requirements:**
- Implement secure webhook endpoint with signature verification
- Design event correlation and deduplication system
- Set up webhook hygiene and error handling

**Implementation Details:**

#### HubSpot Webhook Signature Verification
```typescript
// api/src/middleware/hubspot.ts
import { Context, Next } from 'hono'
import crypto from 'crypto'

export interface HubSpotWebhookEvent {
  eventId: number
  subscriptionId: number
  portalId: number
  appId: number
  occurredAt: number
  subscriptionType: string
  attemptNumber: number
  objectId: number
  changeSource: string
  changeFlag: string
  propertyName?: string
  propertyValue?: string
}

export const verifyHubSpotSignature = async (c: Context, next: Next) => {
  const signature = c.req.header('x-hubspot-signature-v3')
  const timestamp = c.req.header('x-hubspot-request-timestamp')
  
  if (!signature || !timestamp) {
    return c.json({ error: 'Missing HubSpot signature headers' }, 401)
  }

  // Check timestamp to prevent replay attacks (5 minutes tolerance)
  const requestTime = parseInt(timestamp)
  const currentTime = Date.now()
  const timeDiff = Math.abs(currentTime - requestTime)
  
  if (timeDiff > 5 * 60 * 1000) {
    return c.json({ error: 'Request timestamp too old' }, 401)
  }

  const body = await c.req.text()
  const webhookSecret = c.env.HUBSPOT_WEBHOOK_SECRET

  // Create signature hash
  const sourceString = 'POST' + 'https://your-domain.com/webhooks/hubspot' + body + timestamp
  const hash = crypto.createHmac('sha256', webhookSecret).update(sourceString).digest('hex')
  const expectedSignature = `sha256=${hash}`

  if (signature !== expectedSignature) {
    console.error('Invalid HubSpot signature', {
      received: signature,
      expected: expectedSignature,
      sourceString: sourceString.substring(0, 100) + '...'
    })
    return c.json({ error: 'Invalid signature' }, 401)
  }

  // Store verified body for processing
  c.set('webhookBody', body)
  c.set('hubspotTimestamp', requestTime)
  
  await next()
}
```

#### Webhook Processing Endpoint
```typescript
// api/src/routes/webhooks.ts
import { Hono } from 'hono'
import { verifyHubSpotSignature, HubSpotWebhookEvent } from '../middleware/hubspot'
import { getPrismaClient } from '../../../shared/lib/prisma'
import { RedisService } from '../../../shared/lib/redis'
import { publishToQueue } from '../services/queue'

const webhooks = new Hono()

webhooks.post('/hubspot', verifyHubSpotSignature, async (c) => {
  const body = c.get('webhookBody')
  const timestamp = c.get('hubspotTimestamp')
  
  try {
    const events: HubSpotWebhookEvent[] = JSON.parse(body)
    const processedEvents = []

    for (const event of events) {
      const correlationId = generateCorrelationId(event)
      
      // Check for duplicate events
      const existingEvent = await RedisService.getIdempotencyResult(`webhook:${event.eventId}`)
      if (existingEvent) {
        console.log(`Duplicate event ignored: ${event.eventId}`)
        continue
      }

      // Store event in database
      const prisma = getPrismaClient()
      const webhookEvent = await prisma.webhookEvent.create({
        data: {
          hubspotEventId: event.eventId.toString(),
          eventType: event.subscriptionType,
          objectType: getObjectType(event.subscriptionType),
          objectId: event.objectId.toString(),
          correlationId,
          payload: event,
          signature: c.req.header('x-hubspot-signature-v3'),
          occurredAt: new Date(event.occurredAt),
          status: 'RECEIVED'
        }
      })

      // Set idempotency key
      await RedisService.setIdempotencyKey(`webhook:${event.eventId}`, { processed: true }, 3600)

      // Enqueue for processing
      await publishToQueue('webhook-processing', {
        webhookEventId: webhookEvent.id,
        correlationId,
        event
      })

      processedEvents.push({
        eventId: event.eventId,
        correlationId,
        status: 'queued'
      })
    }

    return c.json({
      message: 'Webhooks received',
      processed: processedEvents.length,
      events: processedEvents
    })

  } catch (error) {
    console.error('Webhook processing error:', error)
    return c.json({ error: 'Failed to process webhook' }, 500)
  }
})

function generateCorrelationId(event: HubSpotWebhookEvent): string {
  // Create deterministic correlation ID for deduplication
  const source = `${event.subscriptionType}-${event.objectId}-${event.occurredAt}`
  return crypto.createHash('sha256').update(source).digest('hex').substring(0, 16)
}

function getObjectType(subscriptionType: string): string {
  if (subscriptionType.startsWith('contact.')) return 'contact'
  if (subscriptionType.startsWith('company.')) return 'company'
  if (subscriptionType.startsWith('deal.')) return 'deal'
  if (subscriptionType.startsWith('ticket.')) return 'ticket'
  return 'unknown'
}

export default webhooks
```

#### Event Envelope Structure
```typescript
// shared/types/events.ts
export interface EventEnvelope {
  meta: {
    eventId: string
    source: 'hubspot' | 'manual' | 'system'
    objectType: 'contact' | 'company' | 'deal' | 'ticket'
    objectId: string
    occurredAt: Date
    receivedAt: Date
    correlationId: string
    workflowId?: string
    runId?: string
    version: string
  }
  required: {
    [key: string]: any // Minimum required fields per workflow
  }
  payload: {
    [key: string]: any // Full HubSpot properties
  }
  rawPayloadRef?: string // Reference to stored raw payload
}

export interface WorkflowTrigger {
  workflowId: string
  name: string
  description: string
  eventTypes: string[]
  conditions: {
    [key: string]: any // JSON schema for matching conditions
  }
  enabled: boolean
  priority: number
}
```

#### Webhook Event Processor
```typescript
// ai-service/app/services/webhook_processor.py
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import WebhookEvent, Run
from app.services.workflow_engine import WorkflowEngine
from app.services.hubspot_client import HubSpotClient

class WebhookProcessor:
    def __init__(self):
        self.hubspot_client = HubSpotClient()
        self.workflow_engine = WorkflowEngine()
    
    async def process_webhook_event(self, webhook_event_id: str) -> Dict[str, Any]:
        """Process a webhook event and trigger appropriate workflows"""
        
        with get_db() as db:
            # Get webhook event
            webhook_event = db.query(WebhookEvent).filter(
                WebhookEvent.id == webhook_event_id
            ).first()
            
            if not webhook_event:
                raise ValueError(f"Webhook event {webhook_event_id} not found")
            
            try:
                # Update status to processing
                webhook_event.status = "PROCESSING"
                db.commit()
                
                # Enrich event data from HubSpot
                enriched_data = await self._enrich_event_data(webhook_event)
                
                # Find matching workflows
                matching_workflows = await self._find_matching_workflows(
                    webhook_event.event_type,
                    enriched_data
                )
                
                # Create runs for each matching workflow
                created_runs = []
                for workflow in matching_workflows:
                    run = await self._create_workflow_run(
                        webhook_event,
                        workflow,
                        enriched_data,
                        db
                    )
                    created_runs.append(run)
                
                # Update webhook event status
                webhook_event.status = "PROCESSED"
                webhook_event.processed_at = datetime.utcnow()
                db.commit()
                
                return {
                    "webhook_event_id": webhook_event_id,
                    "status": "processed",
                    "runs_created": len(created_runs),
                    "run_ids": [run.id for run in created_runs]
                }
                
            except Exception as e:
                webhook_event.status = "FAILED"
                webhook_event.error_message = str(e)
                webhook_event.retry_count += 1
                db.commit()
                
                # Schedule retry if under limit
                if webhook_event.retry_count < 3:
                    await self._schedule_retry(webhook_event_id, webhook_event.retry_count)
                
                raise
    
    async def _enrich_event_data(self, webhook_event: WebhookEvent) -> Dict[str, Any]:
        """Enrich webhook event with additional HubSpot data"""
        
        payload = webhook_event.payload
        object_type = webhook_event.object_type
        object_id = webhook_event.object_id
        
        # Fetch full object data from HubSpot
        if object_type == "contact":
            full_data = await self.hubspot_client.get_contact(object_id)
        elif object_type == "company":
            full_data = await self.hubspot_client.get_company(object_id)
        elif object_type == "deal":
            full_data = await self.hubspot_client.get_deal(object_id)
        else:
            full_data = {}
        
        # Get associated objects
        associations = await self.hubspot_client.get_associations(object_type, object_id)
        
        return {
            "event": payload,
            "object": full_data,
            "associations": associations,
            "metadata": {
                "correlation_id": webhook_event.correlation_id,
                "event_type": webhook_event.event_type,
                "occurred_at": webhook_event.occurred_at.isoformat(),
                "received_at": webhook_event.received_at.isoformat()
            }
        }
    
    async def _find_matching_workflows(
        self, 
        event_type: str, 
        enriched_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find workflows that match the event type and conditions"""
        
        # This would typically query a workflow registry
        # For now, we'll define workflows inline
        workflows = [
            {
                "id": "company-intake",
                "name": "Company Intake Workflow",
                "event_types": ["company.creation", "company.propertyChange"],
                "conditions": {
                    "properties": {
                        "lifecyclestage": {"in": ["lead", "marketingqualifiedlead"]}
                    }
                },
                "enabled": True,
                "priority": 1
            },
            {
                "id": "contact-role-mapping",
                "name": "Contact Role Mapping",
                "event_types": ["contact.creation", "contact.propertyChange"],
                "conditions": {
                    "properties": {
                        "jobtitle": {"exists": True}
                    }
                },
                "enabled": True,
                "priority": 2
            },
            {
                "id": "deal-stage-kickoff",
                "name": "Deal Stage Kickoff",
                "event_types": ["deal.propertyChange"],
                "conditions": {
                    "property_name": "dealstage",
                    "properties": {
                        "dealstage": {"in": ["qualifiedtobuy", "presentationscheduled"]}
                    }
                },
                "enabled": True,
                "priority": 1
            }
        ]
        
        matching = []
        for workflow in workflows:
            if not workflow["enabled"]:
                continue
                
            # Check event type match
            if event_type not in workflow["event_types"]:
                continue
            
            # Check conditions
            if self._evaluate_conditions(workflow["conditions"], enriched_data):
                matching.append(workflow)
        
        # Sort by priority
        return sorted(matching, key=lambda w: w["priority"])
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Evaluate workflow conditions against enriched data"""
        
        if "properties" in conditions:
            object_properties = data.get("object", {}).get("properties", {})
            
            for prop_name, condition in conditions["properties"].items():
                prop_value = object_properties.get(prop_name)
                
                if "exists" in condition:
                    if condition["exists"] and not prop_value:
                        return False
                    if not condition["exists"] and prop_value:
                        return False
                
                if "in" in condition:
                    if prop_value not in condition["in"]:
                        return False
                
                if "equals" in condition:
                    if prop_value != condition["equals"]:
                        return False
        
        if "property_name" in conditions:
            event_property = data.get("event", {}).get("propertyName")
            if event_property != conditions["property_name"]:
                return False
        
        return True
    
    async def _create_workflow_run(
        self,
        webhook_event: WebhookEvent,
        workflow: Dict[str, Any],
        enriched_data: Dict[str, Any],
        db: Session
    ) -> Run:
        """Create a new workflow run"""
        
        run = Run(
            correlation_id=webhook_event.correlation_id,
            workflow_id=workflow["id"],
            status="PENDING",
            event_type=webhook_event.event_type,
            object_type=webhook_event.object_type,
            object_id=webhook_event.object_id,
            payload=enriched_data
        )
        
        db.add(run)
        db.commit()
        db.refresh(run)
        
        # Trigger workflow execution
        await self.workflow_engine.start_workflow(run.id, workflow, enriched_data)
        
        return run
    
    async def _schedule_retry(self, webhook_event_id: str, retry_count: int):
        """Schedule webhook event retry with exponential backoff"""
        
        delay = min(300, 2 ** retry_count * 10)  # Max 5 minutes
        
        # This would use your job queue system (RabbitMQ, Inngest, etc.)
        await asyncio.sleep(delay)
        await self.process_webhook_event(webhook_event_id)
```

#### HubSpot Client Service
```typescript
// shared/services/hubspot.ts
import { Client } from '@hubspot/api-client'

export class HubSpotService {
  private client: Client

  constructor(accessToken?: string) {
    this.client = new Client({
      accessToken: accessToken || process.env.HUBSPOT_ACCESS_TOKEN
    })
  }

  async getContact(contactId: string) {
    try {
      const response = await this.client.crm.contacts.basicApi.getById(
        contactId,
        ['email', 'firstname', 'lastname', 'jobtitle', 'phone', 'lifecyclestage'],
        ['companies', 'deals']
      )
      return response
    } catch (error) {
      console.error(`Failed to fetch contact ${contactId}:`, error)
      throw error
    }
  }

  async getCompany(companyId: string) {
    try {
      const response = await this.client.crm.companies.basicApi.getById(
        companyId,
        ['name', 'domain', 'industry', 'numberofemployees', 'annualrevenue', 'lifecyclestage'],
        ['contacts', 'deals']
      )
      return response
    } catch (error) {
      console.error(`Failed to fetch company ${companyId}:`, error)
      throw error
    }
  }

  async getDeal(dealId: string) {
    try {
      const response = await this.client.crm.deals.basicApi.getById(
        dealId,
        ['dealname', 'dealstage', 'amount', 'closedate', 'probability'],
        ['companies', 'contacts']
      )
      return response
    } catch (error) {
      console.error(`Failed to fetch deal ${dealId}:`, error)
      throw error
    }
  }

  async getAssociations(objectType: string, objectId: string) {
    try {
      const associations = await this.client.crm.associations.v4.basicApi.getPage(
        objectType,
        objectId,
        'contacts'
      )
      return associations.results
    } catch (error) {
      console.error(`Failed to fetch associations for ${objectType} ${objectId}:`, error)
      return []
    }
  }

  async createWebhookSubscription(eventType: string, targetUrl: string) {
    try {
      const subscription = await this.client.webhooks.subscriptionsApi.create({
        eventType,
        active: true,
        propertyName: eventType.includes('propertyChange') ? 'lifecyclestage' : undefined
      })
      return subscription
    } catch (error) {
      console.error(`Failed to create webhook subscription for ${eventType}:`, error)
      throw error
    }
  }
}
```

**Tasks:**
- ✅ Create webhook endpoint with Hono on Cloudflare Workers
- ✅ Implement HubSpot signature verification
- ✅ Design correlation key generation system
- ✅ Set up webhook payload storage and processing

**Sub-tasks:**
- ✅ Implement webhook signature validation middleware
- ✅ Create event envelope structure with metadata
- ✅ Set up webhook retry logic with exponential backoff
- ✅ Configure webhook debugging and monitoring

### 2.2 Event Queue & Processing System

**Requirements:**
- Implement CloudAMQP RabbitMQ for reliable message processing
- Design idempotent event processing patterns
- Set up Inngest for durable execution and observability

**Implementation Details:**

#### RabbitMQ Configuration with Quorum Queues
```typescript
// shared/services/queue.ts
import amqp, { Connection, Channel, ConsumeMessage } from 'amqplib'
import { RedisService } from '../lib/redis'

export class QueueService {
  private connection: Connection | null = null
  private channel: Channel | null = null
  private readonly connectionUrl: string

  constructor() {
    this.connectionUrl = process.env.CLOUDAMQP_URL || 'amqp://localhost:5672'
  }

  async connect(): Promise<void> {
    try {
      this.connection = await amqp.connect(this.connectionUrl)
      this.channel = await this.connection.createChannel()

      // Set up error handlers
      this.connection.on('error', (err) => {
        console.error('RabbitMQ connection error:', err)
      })

      this.connection.on('close', () => {
        console.log('RabbitMQ connection closed')
        this.reconnect()
      })

      await this.setupExchangesAndQueues()
      console.log('✅ Connected to RabbitMQ')
    } catch (error) {
      console.error('❌ Failed to connect to RabbitMQ:', error)
      throw error
    }
  }

  private async reconnect(): Promise<void> {
    console.log('🔄 Attempting to reconnect to RabbitMQ...')
    setTimeout(() => this.connect(), 5000)
  }

  private async setupExchangesAndQueues(): Promise<void> {
    if (!this.channel) throw new Error('Channel not initialized')

    // Create exchanges
    await this.channel.assertExchange('hubspot.events', 'topic', { durable: true })
    await this.channel.assertExchange('workflow.events', 'topic', { durable: true })
    await this.channel.assertExchange('dlx', 'direct', { durable: true })

    // Create quorum queues for high availability
    const queueOptions = {
      durable: true,
      arguments: {
        'x-queue-type': 'quorum',
        'x-dead-letter-exchange': 'dlx',
        'x-dead-letter-routing-key': 'failed',
        'x-message-ttl': 24 * 60 * 60 * 1000, // 24 hours
        'x-max-retries': 3
      }
    }

    // Webhook processing queue
    await this.channel.assertQueue('webhook-processing', queueOptions)
    await this.channel.bindQueue('webhook-processing', 'hubspot.events', 'webhook.*')

    // Workflow execution queues
    await this.channel.assertQueue('workflow-execution', queueOptions)
    await this.channel.bindQueue('workflow-execution', 'workflow.events', 'execute.*')

    // Approval processing queue
    await this.channel.assertQueue('approval-processing', queueOptions)
    await this.channel.bindQueue('approval-processing', 'workflow.events', 'approval.*')

    // Dead letter queue
    await this.channel.assertQueue('failed-messages', { durable: true })
    await this.channel.bindQueue('failed-messages', 'dlx', 'failed')

    // Set prefetch count for fair distribution
    await this.channel.prefetch(10)
  }

  async publishMessage(
    exchange: string,
    routingKey: string,
    message: any,
    options: { persistent?: boolean; messageId?: string; correlationId?: string } = {}
  ): Promise<void> {
    if (!this.channel) throw new Error('Channel not initialized')

    const messageBuffer = Buffer.from(JSON.stringify(message))
    const publishOptions = {
      persistent: options.persistent ?? true,
      messageId: options.messageId || crypto.randomUUID(),
      correlationId: options.correlationId,
      timestamp: Date.now(),
      headers: {
        'x-retry-count': 0,
        'x-original-routing-key': routingKey
      }
    }

    // Check for idempotency
    if (options.messageId) {
      const existing = await RedisService.getIdempotencyResult(`msg:${options.messageId}`)
      if (existing) {
        console.log(`Message ${options.messageId} already processed, skipping`)
        return
      }
    }

    const published = this.channel.publish(exchange, routingKey, messageBuffer, publishOptions)
    
    if (!published) {
      throw new Error('Failed to publish message to queue')
    }

    // Set idempotency key
    if (options.messageId) {
      await RedisService.setIdempotencyKey(`msg:${options.messageId}`, { published: true }, 3600)
    }
  }

  async consumeMessages(
    queueName: string,
    processor: (message: any, metadata: MessageMetadata) => Promise<void>,
    options: { concurrency?: number } = {}
  ): Promise<void> {
    if (!this.channel) throw new Error('Channel not initialized')

    const concurrency = options.concurrency || 1

    for (let i = 0; i < concurrency; i++) {
      await this.channel.consume(queueName, async (msg) => {
        if (!msg) return

        const metadata: MessageMetadata = {
          messageId: msg.properties.messageId,
          correlationId: msg.properties.correlationId,
          timestamp: msg.properties.timestamp,
          retryCount: msg.properties.headers?.['x-retry-count'] || 0,
          originalRoutingKey: msg.properties.headers?.['x-original-routing-key']
        }

        try {
          // Check idempotency
          if (metadata.messageId) {
            const existing = await RedisService.getIdempotencyResult(`processed:${metadata.messageId}`)
            if (existing) {
              console.log(`Message ${metadata.messageId} already processed, acknowledging`)
              this.channel!.ack(msg)
              return
            }
          }

          const messageContent = JSON.parse(msg.content.toString())
          await processor(messageContent, metadata)

          // Mark as processed
          if (metadata.messageId) {
            await RedisService.setIdempotencyKey(`processed:${metadata.messageId}`, { processed: true }, 3600)
          }

          this.channel!.ack(msg)
          console.log(`✅ Processed message ${metadata.messageId}`)

        } catch (error) {
          console.error(`❌ Failed to process message ${metadata.messageId}:`, error)
          
          const retryCount = metadata.retryCount + 1
          const maxRetries = 3

          if (retryCount <= maxRetries) {
            // Retry with exponential backoff
            const delay = Math.min(300000, Math.pow(2, retryCount) * 1000) // Max 5 minutes
            
            setTimeout(async () => {
              await this.publishMessage(
                'hubspot.events',
                metadata.originalRoutingKey || 'retry',
                messageContent,
                {
                  messageId: metadata.messageId,
                  correlationId: metadata.correlationId
                }
              )
            }, delay)

            this.channel!.ack(msg)
          } else {
            // Send to dead letter queue
            this.channel!.nack(msg, false, false)
          }
        }
      })
    }
  }

  async close(): Promise<void> {
    if (this.channel) {
      await this.channel.close()
    }
    if (this.connection) {
      await this.connection.close()
    }
  }
}

interface MessageMetadata {
  messageId?: string
  correlationId?: string
  timestamp?: number
  retryCount: number
  originalRoutingKey?: string
}

// Singleton instance
export const queueService = new QueueService()

// Helper functions
export async function publishToQueue(routingKey: string, message: any, options?: any) {
  await queueService.publishMessage('hubspot.events', routingKey, message, options)
}

export async function publishWorkflowEvent(routingKey: string, message: any, options?: any) {
  await queueService.publishMessage('workflow.events', routingKey, message, options)
}
```

#### Idempotent Event Processor
```typescript
// ai-service/app/services/idempotent_processor.py
import asyncio
import json
import hashlib
from typing import Dict, Any, Callable, Optional
from datetime import datetime, timedelta
from app.services.redis_service import RedisService

class IdempotentProcessor:
    """
    Ensures that event processing is idempotent using Redis for state tracking.
    Based on the Fency pattern for RabbitMQ consumers.
    """
    
    def __init__(self, redis_service: RedisService):
        self.redis = redis_service
    
    async def process_with_idempotency(
        self,
        message_id: str,
        consumer_name: str,
        processor_func: Callable[[Dict[str, Any]], Any],
        message_data: Dict[str, Any],
        ttl_seconds: int = 3600
    ) -> Dict[str, Any]:
        """
        Process a message with idempotency guarantees.
        
        Args:
            message_id: Unique identifier for the message
            consumer_name: Name of the consumer processing the message
            processor_func: Function to process the message
            message_data: The message data to process
            ttl_seconds: TTL for idempotency key
        
        Returns:
            Processing result with metadata
        """
        
        # Create unique key for this message + consumer combination
        idempotency_key = f"idempotent:{consumer_name}:{message_id}"
        
        # Check if already processed
        existing_result = await self.redis.get(idempotency_key)
        if existing_result:
            result = json.loads(existing_result)
            return {
                "status": "already_processed",
                "result": result["result"],
                "processed_at": result["processed_at"],
                "message_id": message_id
            }
        
        try:
            # Process the message
            start_time = datetime.utcnow()
            result = await processor_func(message_data)
            end_time = datetime.utcnow()
            
            # Store result with metadata
            processing_result = {
                "result": result,
                "processed_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "processing_time_ms": int((end_time - start_time).total_seconds() * 1000),
                "message_id": message_id,
                "consumer": consumer_name
            }
            
            # Store in Redis with TTL
            await self.redis.setex(
                idempotency_key,
                ttl_seconds,
                json.dumps(processing_result)
            )
            
            return {
                "status": "processed",
                **processing_result
            }
            
        except Exception as e:
            # Store error result to prevent reprocessing of failed messages
            error_result = {
                "error": str(e),
                "error_type": type(e).__name__,
                "processed_at": datetime.utcnow().isoformat(),
                "message_id": message_id,
                "consumer": consumer_name
            }
            
            # Store error with shorter TTL
            await self.redis.setex(
                f"{idempotency_key}:error",
                300,  # 5 minutes
                json.dumps(error_result)
            )
            
            raise

class WebhookEventProcessor:
    """Processes webhook events with idempotency guarantees"""
    
    def __init__(self):
        self.redis = RedisService()
        self.idempotent_processor = IdempotentProcessor(self.redis)
    
    async def process_webhook_event(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook event with idempotency"""
        
        webhook_event_id = message_data.get("webhookEventId")
        correlation_id = message_data.get("correlationId")
        
        if not webhook_event_id:
            raise ValueError("Missing webhookEventId in message")
        
        return await self.idempotent_processor.process_with_idempotency(
            message_id=webhook_event_id,
            consumer_name="webhook-processor",
            processor_func=self._process_webhook_event_internal,
            message_data=message_data
        )
    
    async def _process_webhook_event_internal(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal webhook processing logic"""
        
        webhook_event_id = message_data["webhookEventId"]
        correlation_id = message_data["correlationId"]
        event = message_data["event"]
        
        # Your webhook processing logic here
        # This is where you would:
        # 1. Enrich the event data
        # 2. Find matching workflows
        # 3. Create workflow runs
        # 4. Trigger workflow execution
        
        return {
            "webhook_event_id": webhook_event_id,
            "correlation_id": correlation_id,
            "workflows_triggered": ["company-intake", "contact-role-mapping"],
            "runs_created": 2
        }
```

#### Inngest Integration for Durable Execution
```typescript
// ai-service/app/services/inngest_service.ts
import { Inngest } from 'inngest'
import { serve } from 'inngest/hono'

// Initialize Inngest client
export const inngest = new Inngest({
  id: 'hubspot-orchestrator',
  eventKey: process.env.INNGEST_EVENT_KEY!,
})

// Webhook processing function
export const processWebhookEvent = inngest.createFunction(
  {
    id: 'process-webhook-event',
    concurrency: {
      limit: 50,
      key: 'event.data.correlationId'
    },
    retries: 3,
    rateLimit: {
      limit: 100,
      duration: '1m'
    }
  },
  { event: 'hubspot/webhook.received' },
  async ({ event, step }) => {
    const { webhookEventId, correlationId, eventData } = event.data

    // Step 1: Validate and enrich event data
    const enrichedData = await step.run('enrich-event-data', async () => {
      // Fetch additional data from HubSpot
      const hubspotService = new HubSpotService()
      
      if (eventData.objectType === 'contact') {
        const contact = await hubspotService.getContact(eventData.objectId)
        return { ...eventData, enrichedObject: contact }
      } else if (eventData.objectType === 'company') {
        const company = await hubspotService.getCompany(eventData.objectId)
        return { ...eventData, enrichedObject: company }
      }
      
      return eventData
    })

    // Step 2: Find matching workflows
    const matchingWorkflows = await step.run('find-matching-workflows', async () => {
      // Workflow matching logic
      const workflows = []
      
      if (eventData.eventType === 'company.creation') {
        workflows.push({
          id: 'company-intake',
          name: 'Company Intake Workflow',
          priority: 1
        })
      }
      
      if (eventData.eventType === 'contact.creation') {
        workflows.push({
          id: 'contact-role-mapping',
          name: 'Contact Role Mapping',
          priority: 2
        })
      }
      
      return workflows
    })

    // Step 3: Create workflow runs
    const workflowRuns = await step.run('create-workflow-runs', async () => {
      const runs = []
      
      for (const workflow of matchingWorkflows) {
        const run = await createWorkflowRun({
          correlationId,
          workflowId: workflow.id,
          eventType: eventData.eventType,
          objectType: eventData.objectType,
          objectId: eventData.objectId,
          payload: enrichedData
        })
        runs.push(run)
      }
      
      return runs
    })

    // Step 4: Trigger workflow executions
    for (const run of workflowRuns) {
      await step.sendEvent(`trigger-workflow-${run.id}`, {
        name: 'workflow/execution.start',
        data: {
          runId: run.id,
          workflowId: run.workflowId,
          correlationId,
          payload: enrichedData
        }
      })
    }

    return {
      webhookEventId,
      correlationId,
      workflowsTriggered: matchingWorkflows.length,
      runsCreated: workflowRuns.length
    }
  }
)

// Workflow execution function
export const executeWorkflow = inngest.createFunction(
  {
    id: 'execute-workflow',
    concurrency: {
      limit: 10,
      key: 'event.data.runId'
    },
    retries: 5
  },
  { event: 'workflow/execution.start' },
  async ({ event, step }) => {
    const { runId, workflowId, correlationId, payload } = event.data

    // Update run status
    await step.run('update-run-status', async () => {
      await updateRunStatus(runId, 'RUNNING')
    })

    try {
      // Execute workflow based on type
      let result
      
      if (workflowId === 'company-intake') {
        result = await executeCompanyIntakeWorkflow(step, payload)
      } else if (workflowId === 'contact-role-mapping') {
        result = await executeContactRoleMappingWorkflow(step, payload)
      } else if (workflowId === 'deal-stage-kickoff') {
        result = await executeDealStageKickoffWorkflow(step, payload)
      } else {
        throw new Error(`Unknown workflow: ${workflowId}`)
      }

      // Update run status to completed
      await step.run('complete-run', async () => {
        await updateRunStatus(runId, 'COMPLETED', result)
      })

      return result

    } catch (error) {
      // Update run status to failed
      await step.run('fail-run', async () => {
        await updateRunStatus(runId, 'FAILED', null, error.message)
      })
      
      throw error
    }
  }
)

// Company intake workflow
async function executeCompanyIntakeWorkflow(step: any, payload: any) {
  // Step 1: Normalize company data
  const normalizedData = await step.run('normalize-company-data', async () => {
    return {
      name: payload.enrichedObject.properties.name,
      domain: payload.enrichedObject.properties.domain,
      industry: payload.enrichedObject.properties.industry,
      employeeCount: payload.enrichedObject.properties.numberofemployees,
      lifecycleStage: payload.enrichedObject.properties.lifecyclestage
    }
  })

  // Step 2: Create Airtable record
  const airtableRecord = await step.run('create-airtable-record', async () => {
    const airtableService = new AirtableService()
    return await airtableService.createAccount(normalizedData)
  })

  // Step 3: Check if approval needed
  const approvalNeeded = await step.run('check-approval-needed', async () => {
    // Check business rules for approval requirements
    return normalizedData.employeeCount > 1000 || 
           normalizedData.industry === 'Government'
  })

  if (approvalNeeded) {
    // Step 4: Request approval
    const approval = await step.waitForEvent('wait-for-approval', {
      event: 'approval/decision.made',
      timeout: '7d',
      if: `async.data.runId == '${payload.runId}'`
    })

    if (!approval || !approval.data.approved) {
      throw new Error('Approval rejected or timed out')
    }
  }

  // Step 5: Schedule kickoff if needed
  if (normalizedData.lifecycleStage === 'customer') {
    await step.run('schedule-kickoff', async () => {
      const calendarService = new GoogleCalendarService()
      return await calendarService.scheduleKickoffMeeting(normalizedData)
    })
  }

  return {
    airtableRecordId: airtableRecord.id,
    approvalRequired: approvalNeeded,
    kickoffScheduled: normalizedData.lifecycleStage === 'customer'
  }
}

// Helper functions
async function createWorkflowRun(data: any) {
  // Implementation to create workflow run in database
  return { id: 'run-123', ...data }
}

async function updateRunStatus(runId: string, status: string, result?: any, error?: string) {
  // Implementation to update run status in database
}

// Export Inngest serve handler for Hono
export const inngestHandler = serve({
  client: inngest,
  functions: [
    processWebhookEvent,
    executeWorkflow,
  ],
})
```

#### Queue Monitoring and Metrics
```typescript
// shared/services/queue-monitor.ts
import { queueService } from './queue'
import { RedisService } from '../lib/redis'

export class QueueMonitor {
  private metricsInterval: NodeJS.Timeout | null = null

  async startMonitoring(intervalMs: number = 30000) {
    this.metricsInterval = setInterval(async () => {
      await this.collectMetrics()
    }, intervalMs)
  }

  async stopMonitoring() {
    if (this.metricsInterval) {
      clearInterval(this.metricsInterval)
      this.metricsInterval = null
    }
  }

  private async collectMetrics() {
    try {
      const queues = [
        'webhook-processing',
        'workflow-execution',
        'approval-processing',
        'failed-messages'
      ]

      for (const queueName of queues) {
        const queueInfo = await this.getQueueInfo(queueName)
        
        // Store metrics in Redis for Prometheus scraping
        await RedisService.cache(
          `queue_metrics:${queueName}`,
          {
            messageCount: queueInfo.messageCount,
            consumerCount: queueInfo.consumerCount,
            timestamp: Date.now()
          },
          60 // 1 minute TTL
        )

        // Log alerts for high queue depths
        if (queueInfo.messageCount > 1000) {
          console.warn(`⚠️  High queue depth: ${queueName} has ${queueInfo.messageCount} messages`)
        }
      }
    } catch (error) {
      console.error('Failed to collect queue metrics:', error)
    }
  }

  private async getQueueInfo(queueName: string) {
    // This would use RabbitMQ Management API
    // For now, return mock data
    return {
      messageCount: Math.floor(Math.random() * 100),
      consumerCount: Math.floor(Math.random() * 5) + 1
    }
  }
}

export const queueMonitor = new QueueMonitor()
```

**Tasks:**
- ✅ Configure RabbitMQ with quorum queues
- ✅ Implement event processors with idempotency keys
- ✅ Set up Inngest for workflow orchestration
- ✅ Create event replay and recovery mechanisms

**Sub-tasks:**
- ✅ Design message routing and exchange patterns
- ✅ Implement dead letter queues for failed messages
- ✅ Set up consumer scaling based on queue depth
- ✅ Create event processing metrics and alerts

## Phase 3: AI Service & LangGraph Workflows (Weeks 9-12)

### 3.1 FastAPI AI Service Architecture
**Requirements:**
- Implement FastAPI service with LangGraph integration
- Set up Redis checkpointing for stateful workflows
- Design agent patterns with human-in-the-loop capabilities

**Tasks:**
- Create FastAPI application with async endpoints
- Implement LangGraph workflows for each business process
- Set up Redis checkpoint store for workflow persistence
- Design interrupt patterns for human approvals

**Sub-tasks:**
- Implement workflow nodes with idempotency
- Create checkpoint serialization/deserialization
- Set up workflow state management
- Design approval interrupt patterns

### 3.2 Core Workflow Implementation
**Requirements:**
- Implement company intake/mirror workflow
- Create contact role mapping workflow
- Design deal stage kickoff workflow
- Implement procurement approval workflow

**Tasks:**
- Create LangGraph nodes for each workflow step
- Implement Airtable integration for ops hub
- Set up Notion integration for SOPs and policies
- Design Google Drive/Calendar integration patterns

**Sub-tasks:**
- Implement company normalization and enrichment
- Create contact role inference logic
- Set up calendar scheduling with conflict detection
- Design procurement risk assessment rules

## Phase 4: Frontend & Agentic UI (Weeks 13-16)

### 4.1 React Frontend with CopilotKit
**Requirements:**
- Implement React 18 application with ShadCN components
- Integrate CopilotKit for agentic UI capabilities
- Design responsive dashboard with real-time updates

**Tasks:**
- Set up React application with Vite and TypeScript
- Integrate CopilotKit with LangGraph backend
- Implement dashboard components with KPI cards
- Create real-time update system with WebSockets

**Sub-tasks:**
- Design component library with ShadCN
- Implement state management with Zustand
- Create responsive layouts for mobile/desktop
- Set up real-time data synchronization

### 4.2 AGUI Components Implementation
**Requirements:**
- Create dashboard with KPI visualization
- Implement runs management interface
- Design approvals queue with policy context
- Build exceptions handling interface

**Tasks:**
- Implement dashboard with area charts and drilldowns
- Create runs table with filtering and pagination
- Design approval interface with policy snapshots
- Build exception queue with one-click fixes

**Sub-tasks:**
- Create data visualization components
- Implement advanced filtering and search
- Design approval workflow UI components
- Build exception resolution interfaces

## Phase 5: Knowledge Graph & Temporal Lineage (Weeks 17-20)

### 5.1 Neo4j Temporal Knowledge Graph
**Requirements:**
- Implement Neo4j database for temporal knowledge storage
- Design graph schema for entities and relationships
- Create temporal query patterns for audit trails

**Tasks:**
- Set up Neo4j database with temporal extensions
- Design graph schema for business entities
- Implement temporal relationship tracking
- Create audit query interfaces

**Sub-tasks:**
- Define node types and relationship patterns
- Implement time-based versioning system
- Create graph ingestion pipelines
- Design audit trail visualization

### 5.2 GraphRAG Integration
**Requirements:**
- Implement GraphRAG for explainable decisions
- Create natural language query interface
- Design policy reasoning system

**Tasks:**
- Set up Neo4j GraphRAG Python integration
- Implement natural language to Cypher translation
- Create policy reasoning workflows
- Design explanation generation system

**Sub-tasks:**
- Configure embedding models for graph search
- Implement semantic search over policies
- Create explanation templates
- Design reasoning chain visualization

## Phase 6: Integration & Data Layer (Weeks 21-24)

### 6.1 External System Integrations
**Requirements:**
- Complete Airtable integration for ops hub
- Implement Notion integration for SOPs
- Set up Google Workspace integration
- Configure monitoring and alerting systems

**Tasks:**
- Implement Airtable API client with rate limiting
- Create Notion API integration for policy management
- Set up Google Drive/Calendar API integration
- Configure Prometheus/Grafana monitoring stack

**Sub-tasks:**
- Design data synchronization patterns
- Implement API rate limiting and retry logic
- Create integration health checks
- Set up alerting rules and notifications

### 6.2 Reconciliation & Data Quality
**Requirements:**
- Implement nightly reconciliation processes
- Design data quality monitoring
- Create automated repair mechanisms

**Tasks:**
- Create reconciliation workflows for data consistency
- Implement data quality checks and metrics
- Design automated repair processes
- Set up data lineage tracking

**Sub-tasks:**
- Implement diff detection algorithms
- Create data validation rules
- Design repair workflow patterns
- Set up data quality dashboards

## Phase 7: Security & Compliance (Weeks 25-26)

### 7.1 Security Hardening
**Requirements:**
- Implement comprehensive security measures
- Set up PII redaction and data protection
- Configure audit logging and compliance

**Tasks:**
- Implement PII detection and redaction
- Set up comprehensive audit logging
- Configure security headers and CORS
- Implement rate limiting and DDoS protection

**Sub-tasks:**
- Create PII detection patterns
- Implement audit log encryption
- Set up security monitoring
- Configure compliance reporting

## Phase 8: Testing & Quality Assurance (Weeks 27-28)

### 8.1 Comprehensive Testing Strategy
**Requirements:**
- Implement unit, integration, and end-to-end tests
- Set up performance testing and load testing
- Create security testing and vulnerability scanning

**Tasks:**
- Create comprehensive test suites
- Set up automated testing pipelines
- Implement performance benchmarking
- Configure security scanning

**Sub-tasks:**
- Write unit tests for all components
- Create integration test scenarios
- Set up load testing with realistic data
- Implement security test automation

## Phase 9: Deployment & Production Readiness (Weeks 29-30)

### 9.1 Production Deployment
**Requirements:**
- Deploy to production infrastructure
- Set up monitoring and alerting
- Configure backup and disaster recovery
- Implement gradual rollout strategy

**Tasks:**
- Deploy to Cloudflare Workers and supporting services
- Configure production monitoring and alerting
- Set up automated backups and recovery procedures
- Implement feature flags for gradual rollout

**Sub-tasks:**
- Configure production environment variables
- Set up health checks and monitoring
- Create disaster recovery procedures
- Implement rollback strategies

## Technology Stack Summary

### Frontend
- **React 18** with TypeScript and Vite
- **ShadCN** components for UI consistency
- **CopilotKit** for agentic UI capabilities
- **Zustand** for state management

### Backend Services
- **Hono** on Cloudflare Workers for API layer
- **FastAPI** with Python for AI service
- **LangGraph** for workflow orchestration
- **Prisma** ORM for type-safe database access

### Databases & Storage
- **Neon Postgres** for operational data
- **Upstash Redis** for caching and checkpoints
- **Neo4j** for temporal knowledge graph
- **CloudAMQP RabbitMQ** for message queuing

### AI & ML
- **LangGraph** for stateful AI workflows
- **Neo4j GraphRAG** for explainable AI
- **OpenAI** models for language processing
- **CopilotKit** for human-in-the-loop patterns

### Infrastructure
- **Cloudflare Workers** for edge computing
- **Inngest** for durable execution
- **Docker** for containerization
- **GitHub Actions** for CI/CD

### Monitoring & Observability
- **Prometheus** for metrics collection
- **Grafana** for visualization
- **Sentry** for error tracking
- **Uptime monitoring** for service health

## Key Implementation Patterns

### Event-Driven Architecture
```typescript
// Webhook processing with signature verification
app.post('/webhooks/hubspot', async (c) => {
  const signature = c.req.header('x-hubspot-signature-v3')
  const payload = await c.req.text()
  
  if (!verifySignature(payload, signature)) {
    return c.json({ error: 'Invalid signature' }, 401)
  }
  
  const event = parseHubSpotEvent(payload)
  await enqueueEvent(event)
  
  return c.json({ status: 'received' }, 200)
})
```

### LangGraph Workflow with Checkpoints
```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.redis import RedisCheckpointSaver

checkpointer = RedisCheckpointSaver(redis_client)

@entrypoint(checkpointer=checkpointer)
def company_intake_workflow(event):
    # Normalize company data
    normalized = step.run("normalize-company", lambda: normalize_company(event.data))
    
    # Create Airtable record
    airtable_record = step.run("create-airtable-record", 
                              lambda: create_airtable_record(normalized))
    
    # Check if approval needed
    if requires_approval(normalized):
        approval = interrupt({
            "type": "approval_required",
            "data": normalized,
            "policy": get_applicable_policy(normalized)
        })
        
        if not approval.approved:
            return {"status": "rejected", "reason": approval.reason}
    
    # Schedule kickoff if needed
    if should_schedule_kickoff(normalized):
        step.run("schedule-kickoff", lambda: schedule_kickoff(normalized))
    
    return {"status": "completed", "record_id": airtable_record.id}
```

### CopilotKit Integration
```tsx
import { useCoAgent, useCoAgentStateRender } from "@copilotkit/react-core"

function WorkflowDashboard() {
  const { agentState } = useCoAgent({
    name: "workflow_orchestrator",
    initialState: { activeRuns: [], pendingApprovals: [] }
  })

  useCoAgentStateRender({
    name: "workflow_orchestrator",
    render: ({ state }) => (
      <div>
        <RunsTable runs={state.activeRuns} />
        <ApprovalsQueue approvals={state.pendingApprovals} />
      </div>
    )
  })

  return <div>Workflow Dashboard</div>
}
```

### Temporal Knowledge Graph Queries
```cypher
// Find policy that was active when approval was made
MATCH (approval:Approval {id: $approvalId})-[:GOVERNED_BY]->(policy:Policy)
WHERE policy.validFrom <= approval.timestamp <= policy.validTo
RETURN policy

// Trace lineage of a decision
MATCH path = (event:Event)-[:CAUSED*]->(approval:Approval)
WHERE event.id = $eventId
RETURN path
```

## Risk Mitigation Strategies

### Technical Risks
- **Event storms**: Implement debouncing and rate limiting
- **Duplicate processing**: Use correlation keys and idempotency
- **Service failures**: Design for graceful degradation
- **Data consistency**: Implement eventual consistency patterns

### Operational Risks
- **Scope creep**: Maintain strict boundaries on external communications
- **Performance issues**: Implement comprehensive monitoring
- **Security vulnerabilities**: Regular security audits and updates
- **Compliance issues**: Built-in audit trails and data protection

## Success Metrics

### Technical Metrics
- **SLA adherence**: >99% of workflows complete within SLA
- **First-pass yield**: >95% of workflows complete without manual intervention
- **Exception rate**: <5% of events require manual resolution
- **System uptime**: >99.9% availability

### Business Metrics
- **Process automation**: 90% reduction in manual workflow steps
- **Approval latency**: <2 hours average approval time
- **Audit compliance**: 100% of decisions traceable and explainable
- **Operator efficiency**: 50% reduction in manual operations work

This comprehensive development plan provides a structured approach to building a production-ready, stateful orchestrator that transforms HubSpot events into reliable, auditable internal workflows with human oversight where needed.pe: ev
entType,
        active: true,
        propertyName: eventType.includes('propertyChange') ? 'lifecyclestage' : undefined
      })
      return subscription
    } catch (error) {
      console.error(`Failed to create webhook subscription for ${eventType}:`, error)
      throw error
    }
  }
}
```

**Tasks:**
- ✅ Create webhook endpoint with Hono on Cloudflare Workers
- ✅ Implement HubSpot signature verification
- ✅ Design correlation key generation system
- ✅ Set up webhook payload storage and processing

**Sub-tasks:**
- ✅ Implement webhook signature validation middleware
- ✅ Create event envelope structure with metadata
- ✅ Set up webhook retry logic with exponential backoff
- ✅ Configure webhook debugging and monitoring
#
# Phase 3: AI Service & LangGraph Workflows (Weeks 9-12)

### 3.1 FastAPI AI Service Architecture

**Requirements:**
- Implement FastAPI service with LangGraph integration
- Set up Redis checkpointing for stateful workflows
- Design agent patterns with human-in-the-loop capabilities

**Implementation Details:**

#### FastAPI Application Setup
```python
# ai-service/app/main.py
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Dict, Any, List, Optional

from app.services.workflow_engine import WorkflowEngine
from app.services.langgraph_service import LangGraphService
from app.services.redis_service import RedisService
from app.database import init_db
from app.models import WorkflowRun, ApprovalRequest
from app.schemas import (
    WorkflowExecutionRequest,
    WorkflowExecutionResponse,
    ApprovalResponse,
    WorkflowStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
workflow_engine = WorkflowEngine()
langgraph_service = LangGraphService()
redis_service = RedisService()
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting AI Service...")
    await init_db()
    await redis_service.connect()
    await workflow_engine.initialize()
    logger.info("✅ AI Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AI Service...")
    await redis_service.disconnect()
    logger.info("✅ AI Service shutdown complete")

app = FastAPI(
    title="HubSpot Orchestrator AI Service",
    description="AI-powered workflow orchestration service",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token and return user info"""
    try:
        # Implement JWT validation logic
        token = credentials.credentials
        # Validate token and extract user info
        return {"user_id": "user123", "role": "admin"}  # Placeholder
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "redis": await redis_service.ping(),
            "workflow_engine": workflow_engine.is_healthy(),
            "langgraph": langgraph_service.is_healthy()
        }
    }

@app.post("/workflows/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Execute a workflow"""
    try:
        # Start workflow execution in background
        run_id = await workflow_engine.start_workflow(
            workflow_id=request.workflow_id,
            input_data=request.input_data,
            correlation_id=request.correlation_id,
            user_id=user["user_id"]
        )
        
        return WorkflowExecutionResponse(
            run_id=run_id,
            status=WorkflowStatus.STARTED,
            message="Workflow execution started"
        )
        
    except Exception as e:
        logger.error(f"Failed to execute workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflows/runs/{run_id}")
async def get_workflow_run(
    run_id: str,
    user: dict = Depends(get_current_user)
):
    """Get workflow run status and details"""
    try:
        run_details = await workflow_engine.get_run_details(run_id)
        if not run_details:
            raise HTTPException(status_code=404, detail="Workflow run not found")
        
        return run_details
        
    except Exception as e:
        logger.error(f"Failed to get workflow run: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflows/runs/{run_id}/approve")
async def approve_workflow_step(
    run_id: str,
    approval: ApprovalResponse,
    user: dict = Depends(get_current_user)
):
    """Approve or reject a workflow step"""
    try:
        result = await workflow_engine.handle_approval(
            run_id=run_id,
            approval_id=approval.approval_id,
            approved=approval.approved,
            justification=approval.justification,
            approver_id=user["user_id"]
        )
        
        return {"status": "success", "result": result}
        
    except Exception as e:
        logger.error(f"Failed to handle approval: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflows/runs/{run_id}/resume")
async def resume_workflow(
    run_id: str,
    user: dict = Depends(get_current_user)
):
    """Resume a paused workflow"""
    try:
        result = await workflow_engine.resume_workflow(run_id)
        return {"status": "success", "result": result}
        
    except Exception as e:
        logger.error(f"Failed to resume workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

#### LangGraph Service Implementation
```python
# ai-service/app/services/langgraph_service.py
import asyncio
import json
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.redis import RedisCheckpointSaver
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool

from app.services.redis_service import RedisService
from app.services.hubspot_client import HubSpotClient
from app.services.airtable_client import AirtableClient
from app.services.notion_client import NotionClient

class WorkflowState(TypedDict):
    """State schema for LangGraph workflows"""
    run_id: str
    correlation_id: str
    workflow_id: str
    input_data: Dict[str, Any]
    current_step: str
    step_results: Dict[str, Any]
    errors: List[str]
    requires_approval: bool
    approval_data: Optional[Dict[str, Any]]
    final_result: Optional[Dict[str, Any]]

class LangGraphService:
    """Service for managing LangGraph workflows with Redis checkpointing"""
    
    def __init__(self):
        self.redis_service = RedisService()
        self.hubspot_client = HubSpotClient()
        self.airtable_client = AirtableClient()
        self.notion_client = NotionClient()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.checkpointer = None
        self.workflows = {}
        
    async def initialize(self):
        """Initialize the service and create workflow graphs"""
        # Initialize Redis checkpointer
        self.checkpointer = RedisCheckpointSaver(
            redis_client=self.redis_service.client
        )
        
        # Create workflow graphs
        self.workflows = {
            "company-intake": self._create_company_intake_workflow(),
            "contact-role-mapping": self._create_contact_role_mapping_workflow(),
            "deal-stage-kickoff": self._create_deal_stage_kickoff_workflow(),
            "procurement-approval": self._create_procurement_approval_workflow()
        }
        
    def _create_company_intake_workflow(self) -> StateGraph:
        """Create company intake workflow graph"""
        
        workflow = StateGraph(WorkflowState)
        
        # Define workflow nodes
        workflow.add_node("normalize_company_data", self._normalize_company_data)
        workflow.add_node("create_airtable_record", self._create_airtable_record)
        workflow.add_node("attach_notion_sop", self._attach_notion_sop)
        workflow.add_node("check_approval_needed", self._check_approval_needed)
        workflow.add_node("wait_for_approval", self._wait_for_approval)
        workflow.add_node("schedule_kickoff", self._schedule_kickoff)
        workflow.add_node("finalize_intake", self._finalize_intake)
        
        # Define workflow edges
        workflow.add_edge(START, "normalize_company_data")
        workflow.add_edge("normalize_company_data", "create_airtable_record")
        workflow.add_edge("create_airtable_record", "attach_notion_sop")
        workflow.add_edge("attach_notion_sop", "check_approval_needed")
        
        # Conditional edge for approval
        workflow.add_conditional_edges(
            "check_approval_needed",
            self._should_wait_for_approval,
            {
                "wait": "wait_for_approval",
                "proceed": "schedule_kickoff"
            }
        )
        
        workflow.add_edge("wait_for_approval", "schedule_kickoff")
        workflow.add_edge("schedule_kickoff", "finalize_intake")
        workflow.add_edge("finalize_intake", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def _normalize_company_data(self, state: WorkflowState) -> WorkflowState:
        """Normalize company data from HubSpot"""
        try:
            input_data = state["input_data"]
            company_data = input_data.get("object", {}).get("properties", {})
            
            normalized = {
                "name": company_data.get("name", ""),
                "domain": company_data.get("domain", ""),
                "industry": company_data.get("industry", ""),
                "employee_count": int(company_data.get("numberofemployees", 0) or 0),
                "annual_revenue": float(company_data.get("annualrevenue", 0) or 0),
                "lifecycle_stage": company_data.get("lifecyclestage", ""),
                "hubspot_id": input_data.get("object", {}).get("id", "")
            }
            
            # Use LLM to enrich and validate data
            enrichment_prompt = f"""
            Analyze and enrich this company data:
            {json.dumps(normalized, indent=2)}
            
            Please:
            1. Validate the industry classification
            2. Suggest any missing critical information
            3. Flag any data quality issues
            4. Provide a risk assessment (LOW/MEDIUM/HIGH)
            
            Return a JSON object with the enriched data and analysis.
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a data analyst specializing in company data enrichment."),
                HumanMessage(content=enrichment_prompt)
            ])
            
            # Parse LLM response and merge with normalized data
            try:
                llm_analysis = json.loads(response.content)
                normalized.update(llm_analysis.get("enriched_data", {}))
                normalized["ai_analysis"] = llm_analysis.get("analysis", {})
            except json.JSONDecodeError:
                normalized["ai_analysis"] = {"error": "Failed to parse LLM response"}
            
            state["step_results"]["normalize_company_data"] = normalized
            state["current_step"] = "normalize_company_data"
            
            return state
            
        except Exception as e:
            state["errors"].append(f"Failed to normalize company data: {str(e)}")
            raise
    
    async def _create_airtable_record(self, state: WorkflowState) -> WorkflowState:
        """Create record in Airtable ops hub"""
        try:
            normalized_data = state["step_results"]["normalize_company_data"]
            
            airtable_record = await self.airtable_client.create_account({
                "Name": normalized_data["name"],
                "Domain": normalized_data["domain"],
                "Industry": normalized_data["industry"],
                "Employee Count": normalized_data["employee_count"],
                "Annual Revenue": normalized_data["annual_revenue"],
                "Lifecycle Stage": normalized_data["lifecycle_stage"],
                "HubSpot ID": normalized_data["hubspot_id"],
                "Created Date": datetime.now().isoformat(),
                "AI Analysis": json.dumps(normalized_data.get("ai_analysis", {}))
            })
            
            state["step_results"]["create_airtable_record"] = {
                "record_id": airtable_record["id"],
                "record_url": f"https://airtable.com/app123/tbl456/{airtable_record['id']}"
            }
            state["current_step"] = "create_airtable_record"
            
            return state
            
        except Exception as e:
            state["errors"].append(f"Failed to create Airtable record: {str(e)}")
            raise
    
    async def _attach_notion_sop(self, state: WorkflowState) -> WorkflowState:
        """Attach relevant Notion SOP documents"""
        try:
            normalized_data = state["step_results"]["normalize_company_data"]
            industry = normalized_data.get("industry", "")
            lifecycle_stage = normalized_data.get("lifecycle_stage", "")
            
            # Find relevant SOPs based on industry and lifecycle stage
            sop_query = f"industry:{industry} OR lifecycle:{lifecycle_stage}"
            sops = await self.notion_client.search_sops(sop_query)
            
            # Attach SOPs to Airtable record
            airtable_data = state["step_results"]["create_airtable_record"]
            if sops:
                sop_links = [{"url": sop["url"], "title": sop["title"]} for sop in sops[:3]]
                await self.airtable_client.update_record(
                    airtable_data["record_id"],
                    {"SOPs": json.dumps(sop_links)}
                )
            
            state["step_results"]["attach_notion_sop"] = {
                "sops_attached": len(sops),
                "sop_links": sop_links if sops else []
            }
            state["current_step"] = "attach_notion_sop"
            
            return state
            
        except Exception as e:
            state["errors"].append(f"Failed to attach Notion SOPs: {str(e)}")
            raise
    
    async def _check_approval_needed(self, state: WorkflowState) -> WorkflowState:
        """Check if approval is needed based on business rules"""
        try:
            normalized_data = state["step_results"]["normalize_company_data"]
            
            # Business rules for approval
            approval_needed = False
            approval_reasons = []
            
            if normalized_data.get("employee_count", 0) > 1000:
                approval_needed = True
                approval_reasons.append("Large company (>1000 employees)")
            
            if normalized_data.get("annual_revenue", 0) > 10000000:
                approval_needed = True
                approval_reasons.append("High revenue company (>$10M)")
            
            if normalized_data.get("industry") in ["Government", "Healthcare", "Financial Services"]:
                approval_needed = True
                approval_reasons.append(f"Regulated industry: {normalized_data.get('industry')}")
            
            ai_risk = normalized_data.get("ai_analysis", {}).get("risk_level", "LOW")
            if ai_risk in ["HIGH", "CRITICAL"]:
                approval_needed = True
                approval_reasons.append(f"AI flagged as {ai_risk} risk")
            
            state["requires_approval"] = approval_needed
            state["approval_data"] = {
                "reasons": approval_reasons,
                "company_data": normalized_data,
                "risk_level": ai_risk,
                "requested_at": datetime.now().isoformat()
            }
            
            state["step_results"]["check_approval_needed"] = {
                "approval_needed": approval_needed,
                "reasons": approval_reasons
            }
            state["current_step"] = "check_approval_needed"
            
            return state
            
        except Exception as e:
            state["errors"].append(f"Failed to check approval requirements: {str(e)}")
            raise
    
    def _should_wait_for_approval(self, state: WorkflowState) -> str:
        """Conditional edge function to determine if approval is needed"""
        return "wait" if state.get("requires_approval", False) else "proceed"
    
    async def _wait_for_approval(self, state: WorkflowState) -> WorkflowState:
        """Wait for human approval (interrupt point)"""
        # This is where the workflow will pause and wait for external approval
        # The approval will be handled via the API endpoint
        state["current_step"] = "wait_for_approval"
        return state
    
    async def _schedule_kickoff(self, state: WorkflowState) -> WorkflowState:
        """Schedule internal kickoff meeting if needed"""
        try:
            normalized_data = state["step_results"]["normalize_company_data"]
            lifecycle_stage = normalized_data.get("lifecycle_stage", "")
            
            if lifecycle_stage in ["customer", "opportunity"]:
                # Schedule kickoff meeting
                meeting_data = {
                    "title": f"Kickoff Meeting - {normalized_data['name']}",
                    "description": f"Internal kickoff for new {lifecycle_stage}: {normalized_data['name']}",
                    "attendees": ["sales@company.com", "success@company.com"],
                    "duration": 60,  # minutes
                    "company_data": normalized_data
                }
                
                # This would integrate with Google Calendar API
                # For now, we'll simulate the scheduling
                meeting_result = {
                    "meeting_id": f"meeting_{state['run_id']}",
                    "scheduled_for": "2024-01-15T10:00:00Z",
                    "calendar_link": "https://calendar.google.com/event/123"
                }
                
                state["step_results"]["schedule_kickoff"] = meeting_result
            else:
                state["step_results"]["schedule_kickoff"] = {
                    "skipped": True,
                    "reason": f"No kickoff needed for lifecycle stage: {lifecycle_stage}"
                }
            
            state["current_step"] = "schedule_kickoff"
            return state
            
        except Exception as e:
            state["errors"].append(f"Failed to schedule kickoff: {str(e)}")
            raise
    
    async def _finalize_intake(self, state: WorkflowState) -> WorkflowState:
        """Finalize the company intake process"""
        try:
            # Compile final results
            final_result = {
                "status": "completed",
                "company_data": state["step_results"]["normalize_company_data"],
                "airtable_record": state["step_results"]["create_airtable_record"],
                "sops_attached": state["step_results"]["attach_notion_sop"],
                "approval_required": state.get("requires_approval", False),
                "kickoff_scheduled": state["step_results"]["schedule_kickoff"],
                "completed_at": datetime.now().isoformat(),
                "total_steps": len(state["step_results"])
            }
            
            state["final_result"] = final_result
            state["current_step"] = "completed"
            
            return state
            
        except Exception as e:
            state["errors"].append(f"Failed to finalize intake: {str(e)}")
            raise
    
    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        run_id: str,
        correlation_id: str
    ) -> Dict[str, Any]:
        """Execute a workflow with the given input data"""
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        # Initialize state
        initial_state = WorkflowState(
            run_id=run_id,
            correlation_id=correlation_id,
            workflow_id=workflow_id,
            input_data=input_data,
            current_step="starting",
            step_results={},
            errors=[],
            requires_approval=False,
            approval_data=None,
            final_result=None
        )
        
        # Configure thread for checkpointing
        config = {
            "configurable": {
                "thread_id": run_id,
                "checkpoint_ns": workflow_id
            }
        }
        
        try:
            # Execute workflow
            result = await workflow.ainvoke(initial_state, config=config)
            return result
            
        except Exception as e:
            # Save error state to checkpoint
            error_state = initial_state.copy()
            error_state["errors"].append(f"Workflow execution failed: {str(e)}")
            error_state["current_step"] = "failed"
            
            await self.checkpointer.aput(config, error_state)
            raise
    
    async def resume_workflow(
        self,
        run_id: str,
        workflow_id: str,
        approval_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Resume a paused workflow"""
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        config = {
            "configurable": {
                "thread_id": run_id,
                "checkpoint_ns": workflow_id
            }
        }
        
        # Get current state from checkpoint
        checkpoint = await self.checkpointer.aget(config)
        if not checkpoint:
            raise ValueError(f"No checkpoint found for run {run_id}")
        
        current_state = checkpoint.state
        
        # Update state with approval data if provided
        if approval_data:
            current_state["approval_data"].update(approval_data)
            current_state["requires_approval"] = False
        
        # Resume execution
        result = await workflow.ainvoke(current_state, config=config)
        return result
    
    def is_healthy(self) -> bool:
        """Check if the service is healthy"""
        return (
            self.checkpointer is not None and
            len(self.workflows) > 0 and
            self.redis_service.is_connected()
        )
```

**Tasks:**
- ✅ Create FastAPI application with async endpoints
- ✅ Implement LangGraph workflows for each business process
- ✅ Set up Redis checkpoint store for workflow persistence
- ✅ Design interrupt patterns for human approvals

**Sub-tasks:**
- ✅ Implement workflow nodes with idempotency
- ✅ Create checkpoint serialization/deserialization
- ✅ Set up workflow state management
- ✅ Design approval interrupt patterns#
## 3.2 Core Workflow Implementation

**Requirements:**
- Implement company intake/mirror workflow
- Create contact role mapping workflow
- Design deal stage kickoff workflow
- Implement procurement approval workflow

**Implementation Details:**

#### Contact Role Mapping Workflow
```python
# ai-service/app/workflows/contact_role_mapping.py
from typing import Dict, Any, TypedDict, List
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json

class ContactRoleMappingState(TypedDict):
    run_id: str
    correlation_id: str
    input_data: Dict[str, Any]
    contact_data: Dict[str, Any]
    inferred_role: Dict[str, Any]
    permission_checklist: List[Dict[str, Any]]
    drive_templates: List[Dict[str, Any]]
    final_result: Dict[str, Any]
    errors: List[str]

class ContactRoleMappingWorkflow:
    def __init__(self, langgraph_service):
        self.langgraph_service = langgraph_service
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    def create_workflow(self) -> StateGraph:
        """Create contact role mapping workflow"""
        
        workflow = StateGraph(ContactRoleMappingState)
        
        # Add nodes
        workflow.add_node("extract_contact_data", self._extract_contact_data)
        workflow.add_node("infer_role_from_title", self._infer_role_from_title)
        workflow.add_node("link_to_account", self._link_to_account)
        workflow.add_node("generate_permission_checklist", self._generate_permission_checklist)
        workflow.add_node("attach_drive_templates", self._attach_drive_templates)
        workflow.add_node("finalize_role_mapping", self._finalize_role_mapping)
        
        # Add edges
        workflow.add_edge(START, "extract_contact_data")
        workflow.add_edge("extract_contact_data", "infer_role_from_title")
        workflow.add_edge("infer_role_from_title", "link_to_account")
        workflow.add_edge("link_to_account", "generate_permission_checklist")
        workflow.add_edge("generate_permission_checklist", "attach_drive_templates")
        workflow.add_edge("attach_drive_templates", "finalize_role_mapping")
        workflow.add_edge("finalize_role_mapping", END)
        
        return workflow.compile(checkpointer=self.langgraph_service.checkpointer)
    
    async def _extract_contact_data(self, state: ContactRoleMappingState) -> ContactRoleMappingState:
        """Extract and normalize contact data"""
        try:
            input_data = state["input_data"]
            contact_properties = input_data.get("object", {}).get("properties", {})
            
            contact_data = {
                "hubspot_id": input_data.get("object", {}).get("id", ""),
                "email": contact_properties.get("email", ""),
                "first_name": contact_properties.get("firstname", ""),
                "last_name": contact_properties.get("lastname", ""),
                "job_title": contact_properties.get("jobtitle", ""),
                "phone": contact_properties.get("phone", ""),
                "company": contact_properties.get("company", ""),
                "lifecycle_stage": contact_properties.get("lifecyclestage", ""),
                "lead_source": contact_properties.get("hs_lead_source", ""),
                "seniority": contact_properties.get("seniority", ""),
                "department": contact_properties.get("department", "")
            }
            
            state["contact_data"] = contact_data
            return state
            
        except Exception as e:
            state["errors"].append(f"Failed to extract contact data: {str(e)}")
            raise
    
    async def _infer_role_from_title(self, state: ContactRoleMappingState) -> ContactRoleMappingState:
        """Use AI to infer role and responsibilities from job title"""
        try:
            contact_data = state["contact_data"]
            job_title = contact_data.get("job_title", "")
            company = contact_data.get("company", "")
            department = contact_data.get("department", "")
            seniority = contact_data.get("seniority", "")
            
            role_inference_prompt = f"""
            Analyze this contact's professional information and infer their role:
            
            Job Title: {job_title}
            Company: {company}
            Department: {department}
            Seniority: {seniority}
            
            Please provide:
            1. Primary role category (e.g., "Decision Maker", "Influencer", "End User", "Gatekeeper")
            2. Functional area (e.g., "Engineering", "Sales", "Marketing", "Operations")
            3. Seniority level (e.g., "Executive", "Manager", "Individual Contributor")
            4. Key responsibilities (list of 3-5 items)
            5. Likely decision-making authority (scale 1-10)
            6. Recommended engagement strategy
            7. Internal permissions likely needed (list)
            
            Return as JSON with these fields: role_category, functional_area, seniority_level, 
            responsibilities, decision_authority, engagement_strategy, permissions_needed
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content="You are an expert in B2B sales and organizational analysis."),
                HumanMessage(content=role_inference_prompt)
            ])
            
            try:
                inferred_role = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                inferred_role = {
                    "role_category": "Unknown",
                    "functional_area": department or "Unknown",
                    "seniority_level": seniority or "Unknown",
                    "responsibilities": ["Role analysis failed"],
                    "decision_authority": 5,
                    "engagement_strategy": "Standard approach",
                    "permissions_needed": ["Basic access"],
                    "ai_response": response.content
                }
            
            state["inferred_role"] = inferred_role
            return state
            
        except Exception as e:
            state["errors"].append(f"Failed to infer role from title: {str(e)}")
            raise
    
    async def _link_to_account(self, state: ContactRoleMappingState) -> ContactRoleMappingState:
        """Link contact to account and update relationships"""
        try:
            contact_data = state["contact_data"]
            
            # Get associated companies from HubSpot
            associations = await self.langgraph_service.hubspot_client.get_associations(
                "contact", 
                contact_data["hubspot_id"]
            )
            
            # Update Airtable with contact-account relationship
            if associations:
                primary_company = associations[0]  # Take first associated company
                
                # Create or update contact record in Airtable
                airtable_contact = await self.langgraph_service.airtable_client.create_contact({
                    "Name": f"{contact_data['first_name']} {contact_data['last_name']}",
                    "Email": contact_data["email"],
                    "Job Title": contact_data["job_title"],
                    "Phone": contact_data["phone"],
                    "HubSpot ID": contact_data["hubspot_id"],
                    "Company": primary_company.get("name", ""),
                    "Role Category": state["inferred_role"]["role_category"],
                    "Functional Area": state["inferred_role"]["functional_area"],
                    "Seniority Level": state["inferred_role"]["seniority_level"],
                    "Decision Authority": state["inferred_role"]["decision_authority"]
                })
                
                state["contact_data"]["airtable_record_id"] = airtable_contact["id"]
                state["contact_data"]["primary_company"] = primary_company
            
            return state
            
        except Exception as e:
            state["errors"].append(f"Failed to link contact to account: {str(e)}")
            raise
    
    async def _generate_permission_checklist(self, state: ContactRoleMappingState) -> ContactRoleMappingState:
        """Generate internal permission checklist based on role"""
        try:
            inferred_role = state["inferred_role"]
            contact_data = state["contact_data"]
            
            # Generate role-specific permission checklist
            permissions_needed = inferred_role.get("permissions_needed", [])
            
            checklist_items = []
            
            # Base permissions for all contacts
            checklist_items.extend([
                {
                    "item": "CRM Access",
                    "description": "Basic CRM record access",
                    "required": True,
                    "assigned_to": "sales_ops",
                    "status": "pending"
                },
                {
                    "item": "Email Marketing Consent",
                    "description": "Verify opt-in status for marketing emails",
                    "required": True,
                    "assigned_to": "marketing",
                    "status": "pending"
                }
            ])
            
            # Role-specific permissions
            if inferred_role["role_category"] == "Decision Maker":
                checklist_items.extend([
                    {
                        "item": "Executive Communication Access",
                        "description": "Access to executive-level communications",
                        "required": True,
                        "assigned_to": "executive_team",
                        "status": "pending"
                    },
                    {
                        "item": "Pricing Information Access",
                        "description": "Access to detailed pricing and proposals",
                        "required": True,
                        "assigned_to": "sales_manager",
                        "status": "pending"
                    }
                ])
            
            if inferred_role["functional_area"] == "Engineering":
                checklist_items.extend([
                    {
                        "item": "Technical Documentation Access",
                        "description": "Access to technical specs and API docs",
                        "required": False,
                        "assigned_to": "technical_team",
                        "status": "pending"
                    },
                    {
                        "item": "Demo Environment Access",
                        "description": "Access to technical demo environment",
                        "required": False,
                        "assigned_to": "solutions_engineering",
                        "status": "pending"
                    }
                ])
            
            state["permission_checklist"] = checklist_items
            return state
            
        except Exception as e:
            state["errors"].append(f"Failed to generate permission checklist: {str(e)}")
            raise
    
    async def _attach_drive_templates(self, state: ContactRoleMappingState) -> ContactRoleMappingState:
        """Attach relevant Google Drive templates based on role"""
        try:
            inferred_role = state["inferred_role"]
            
            # Template mapping based on role
            template_mapping = {
                "Decision Maker": [
                    {
                        "name": "Executive Summary Template",
                        "url": "https://drive.google.com/file/d/exec-summary-template",
                        "description": "Template for executive-level communications"
                    },
                    {
                        "name": "ROI Calculator",
                        "url": "https://drive.google.com/file/d/roi-calculator",
                        "description": "ROI calculation template"
                    }
                ],
                "Influencer": [
                    {
                        "name": "Technical Evaluation Guide",
                        "url": "https://drive.google.com/file/d/tech-eval-guide",
                        "description": "Guide for technical evaluation"
                    }
                ],
                "End User": [
                    {
                        "name": "User Onboarding Checklist",
                        "url": "https://drive.google.com/file/d/user-onboarding",
                        "description": "Checklist for user onboarding"
                    }
                ]
            }
            
            role_category = inferred_role.get("role_category", "")
            templates = template_mapping.get(role_category, [])
            
            # Add functional area specific templates
            functional_area = inferred_role.get("functional_area", "")
            if functional_area == "Engineering":
                templates.extend([
                    {
                        "name": "API Integration Guide",
                        "url": "https://drive.google.com/file/d/api-integration",
                        "description": "Technical integration documentation"
                    }
                ])
            elif functional_area == "Sales":
                templates.extend([
                    {
                        "name": "Sales Enablement Kit",
                        "url": "https://drive.google.com/file/d/sales-kit",
                        "description": "Sales tools and resources"
                    }
                ])
            
            state["drive_templates"] = templates
            
            # Update Airtable record with templates
            if state["contact_data"].get("airtable_record_id"):
                await self.langgraph_service.airtable_client.update_record(
                    state["contact_data"]["airtable_record_id"],
                    {"Drive Templates": json.dumps(templates)}
                )
            
            return 