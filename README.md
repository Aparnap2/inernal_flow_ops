# HubSpot Operations Orchestrator

A production-ready system that transforms HubSpot events into reliable, auditable internal workflows with human oversight where needed.

## Overview

The HubSpot Operations Orchestrator is an intelligent automation platform that bridges HubSpot CRM events with internal business processes. It provides:

- **Event-Driven Automation**: Automatically triggers workflows based on HubSpot events
- **Human-in-the-Loop Oversight**: Requires approvals for critical business decisions
- **Exception Handling**: Manages data quality issues and integration errors
- **Audit Trail**: Maintains complete lineage of all operations for compliance
- **Policy Enforcement**: Ensures business rules are consistently applied

## Key Features

### 🤖 AI-Powered Workflows
- LangGraph stateful workflows with Redis checkpointing
- Human-in-the-loop interruptions for approvals
- Automatic data enrichment and validation
- Integration with external systems (Airtable, Notion, Google Workspace)

### 📊 Real-Time Dashboard
- KPI monitoring and workflow visualization
- Pending approvals queue with policy context
- Exception management with one-click fixes
- Run history and audit trails

### 🔐 Security & Compliance
- Role-based access control (Admin, Operator, Viewer)
- JWT-based authentication
- Complete audit logging
- Policy snapshots for compliance

### ⚡ Event Processing
- HubSpot webhook ingestion with signature verification
- Event deduplication and correlation
- Queue-based processing with Redis
- Replay and recovery capabilities

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   HubSpot CRM   │───▶│  Webhook Events  │───▶│  Event Envelopes │
└─────────────────┘    └──────────────────┘    └──────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │   Redis Queue    │
                    └──────────────────┘
                               │
                               ▼
                    ┌──────────────────┐    ┌──────────────────┐
                    │  Inngest Engine  │───▶│ LangGraph Workers│
                    └──────────────────┘    └──────────────────┘
                               │                     │
                               ▼                     ▼
                    ┌──────────────────┐    ┌──────────────────┐
                    │  SQLite Database │    │External Services │
                    └──────────────────┘    └──────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │  Edge Functions  │
                    └──────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │   Frontend UI    │
                    └──────────────────┘
```

## Technology Stack

### Frontend
- **React 18** with TypeScript
- **Hono.js** for Cloudflare Workers
- **TailwindCSS** for styling
- **ShadCN UI** components
- **Prisma ORM** for database operations

### Backend
- **Python 3.11+** with FastAPI
- **LangGraph** for workflow orchestration
- **Redis** for checkpointing and queuing
- **Inngest** for durable execution
- **LangChain** for AI integrations

### Database
- **SQLite** with Prisma ORM
- **Cloudflare D1** (production)

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker (for development)
- Cloudflare account (for deployment)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/hubspot-orchestrator.git
   cd hubspot-orchestrator
   ```

2. **Install frontend dependencies:**
   ```bash
   cd frontend
   pnpm install
   ```

3. **Install backend dependencies:**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Copy and configure .env files
   cp frontend/.env.example frontend/.env
   cp backend/.env.example backend/.env
   ```

### Development

1. **Start the frontend:**
   ```bash
   cd frontend
   pnpm dev
   ```

2. **Start the backend:**
   ```bash
   cd backend
   source .venv/bin/activate
   uvicorn app.main:app --reload
   ```

3. **Run database migrations:**
   ```bash
   cd frontend
   pnpm db:migrate
   pnpm db:seed
   ```

### Testing

```bash
# Frontend tests
cd frontend
pnpm test

# Backend tests
cd backend
pytest

# End-to-end tests
cd frontend
pnpm test:e2e
```

## Deployment

### Frontend (Cloudflare)
```bash
cd frontend
pnpm build
pnpm deploy
```

### Backend (Serverless)
```bash
cd backend
# Deploy with your preferred platform (AWS, GCP, Azure, etc.)
```

## Configuration

### Environment Variables

**Frontend (.env):**
```env
# Cloudflare
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id

# Database
DATABASE_URL=your_database_url

# Authentication
JWT_SECRET=your_jwt_secret
```

**Backend (.env):**
```env
# HubSpot
HUBSPOT_WEBHOOK_SECRET=your_webhook_secret
HUBSPOT_ACCESS_TOKEN=your_access_token

# Redis
REDIS_URL=your_redis_url

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Inngest
INNGEST_EVENT_KEY=your_inngest_event_key
INNGEST_SIGNING_KEY=your_inngest_signing_key
```

## Workflows

### 1. Company Intake/Mirror
Triggers when a new company is created or updated in HubSpot:
- Normalizes company data with AI enrichment
- Upserts to Airtable "Accounts" base
- Attaches Notion SOP for the company type
- Schedules internal kickoff if lifecycle rules match

### 2. Contact Role Mapping
Triggers when a contact is created or updated:
- Infers role from job title using AI
- Seeds internal permission checklists
- Attaches relevant Google Drive templates
- Links to associated account

### 3. Deal Stage Kickoff
Triggers when a deal enters a configured stage:
- Proposes internal meeting time slots
- Waits for human approval via AGUI
- Creates calendar event in Google Calendar
- Links artifacts to Airtable and Notion

### 4. Procurement Approval
Triggers when a deal crosses a monetary threshold:
- Creates procurement record in ops tool
- Waits for admin approval via AGUI with policy snapshot
- Creates internal purchase order after approval
- Tracks spend against budget

## API Endpoints

### Webhooks
- `POST /webhooks/hubspot` - Receive HubSpot webhooks

### Runs
- `GET /api/runs` - List workflow runs
- `GET /api/runs/:id` - Get specific run details

### Approvals
- `GET /api/approvals/pending` - List pending approvals
- `PATCH /api/approvals/:id/decision` - Approve/reject approval

### Exceptions
- `GET /api/exceptions/open` - List open exceptions
- `PATCH /api/exceptions/:id/resolve` - Resolve exception

## Monitoring & Observability

### Logging
Structured logging throughout the application with:
- Request tracing with correlation IDs
- Error tracking with stack traces
- Performance metrics
- Audit trails for compliance

### Health Checks
- `/health` endpoint for service status
- Database connectivity verification
- External service health monitoring

### Metrics
- Workflow execution rates
- Approval turnaround times
- Exception resolution rates
- System resource utilization

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on GitHub or contact the maintainers.