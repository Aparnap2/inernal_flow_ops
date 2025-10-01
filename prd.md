

### Scope and goals
- Scope: Internal operations only, triggered by HubSpot company/contact/deal create/update and association changes, with no external customer messaging, and admin‑only approvals performed inside the AGUI.[2][3]
- Goal: Replace brittle duct‑taped iPaaS chains with a stateful, explainable orchestrator and an agentic UI that makes complex internal workflows safe, resumable, auditable, and easy to drive in natural language.[4][5]

### Architecture summary
- Frontend: React 18 + Vite with ShadCN components and CopilotKit for an embedded agentic UI, served from Cloudflare Workers via Hono for globally fast, serverless APIs.[6][7]
- Control plane: Hono on Cloudflare Workers for webhook ingestion, auth, RBAC gating, and admin APIs, with Prisma as the type‑safe ORM to MongoDB or Neon Postgres.[8][1]
- Eventing and queue: HubSpot webhooks invoke the control plane, which enqueues jobs and emits Inngest events for observability, and CloudAMQP RabbitMQ runs durable async tasks.[9][2]
- AI service: Python FastAPI + LangGraph workflows with Redis checkpoints for state persistence, Pydantic validation, and optional Swarm patterns for planner/worker/reviewer agent roles.[10][11]
- Memory and lineage: Neo4j + Graphiti temporal knowledge graph stores “what was true when” for policies, approvals, and entity history to power “explain why” in audits and RCA.[12][13]
- Data layer: Upstash Redis for caching/checkpointing and Neon Postgres or MongoDB for durable ops data, chosen per data shape and analytics needs.[14][15]

### PRD highlights
- Core features: Event‑driven orchestration from HubSpot, agentic AGUI (command bar, approvals, exceptions), reconciliation and one‑click repairs, temporal lineage, and KPI dashboards.[5][2]
- Non‑functional: Idempotent steps, retries with backoff, resumable runs, signed webhook validation, PII redaction in UI, and admin‑only approvals with CSRF‑protected endpoints.[16][2]
- Out of scope: External comms like customer email/SMS, ticket deflection, and marketing automation, keeping the surface internal and secure.[17][18]

### Integrations (v1)
- HubSpot: Subscribe to company/contact/deal create/update and associationChange, validate signatures, debounce with hs_lastmodifieddate, and filter by property masks and pipeline stages.[19][2]
- Airtable: Ops hub for Accounts/Contacts/Deals mirrors, Runs, Approvals, Exceptions, and Reference tables that non‑technical operators can manage and review.[20][21]
- Notion: SOP/policy pages with templates and versioning linked into runs and approvals for in‑context guidance and audit.[22][23]
- Google Drive/Calendar: Internal artifacts and internal kickoffs only, triggered by internal stages without any customer invites or external mail.[24][17]
- Upstash Redis: Serverless Redis with REST client for Workers and FastAPI, used for checkpoints, locks, and idempotency tracking.[25][14]
- CloudAMQP RabbitMQ: Managed RabbitMQ for reliable background processing with AMQP semantics and reliability best practices.[26][9]
- Inngest: Event tracking and step‑level observability with replays and durable execution patterns.[27][28]

### Event model
- Subscriptions: company.creation, company.propertyChange, contact.creation, contact.propertyChange, deal.creation, deal.propertyChange, and associationChange for all three objects.[29][2]
- Correlation keys: correlation_id = hash(object_type, object_id, hs_lastmodifieddate, workflow_id) to ensure deduplication and safe replays.[30][2]
- Webhook hygiene: Verify signatures, ack quickly, persist raw payload refs, and use the HubSpot Webhooks Journal in v4 beta for troubleshooting missed deliveries.[31][2]

### Exact workflows
- Company intake/mirror: On create/update, upsert an Account in Airtable, normalize core fields, attach Notion SOP link, and schedule an internal kickoff task if lifecycle rules match.[2][20]
- Contact role mapping: On create/update, link Contact to Account, infer role from title, seed internal doc/permission checklists, and attach Drive templates.[24][2]
- Deal stage kickoff: On configured stage change, propose internal slots, confirm in AGUI, create a Calendar event, and link artifacts to the Account and Run.[2][24]
- Procurement approval: On risk/threshold properties, create a Procurement record, require admin approval with policy snapshot, then create internal PO record and checkpoint.[12][2]

### AGUI components
- Dashboard: KPI cards for SLA adherence, first‑pass yield, exception rate, connector health, and area charts with drilldowns to runs.[32][33]
- Runs: Live table with filters (workflow, status, SLA age), and Run Detail with tabs for Steps, Diffs, Payload (redacted), Checkpoints, and Retries.[34][6]
- Approvals: Admin‑only queue with an Approval Sheet showing summary, diffs, risk flags, and policy snapshot, with Approve/Reject/Request changes and required justification on reject.[3][12]
- Exceptions: Queue listing reconciliation diffs with safe, one‑click fixes gated by confirmations and idempotency locks.[35][26]
- Command bar: Natural‑language commands mapped to safe functions like “Reconcile HubSpot mirror,” “Open pending approvals,” and “Explain last run.”[36][5]

### LangGraph best practices
- HITL via interrupts: Use static interrupts before/after risky nodes and dynamic interrupts when confidence is low, resuming from Redis checkpoints on admin response.[11][16]
- Redis checkpointing: Adopt the updated checkpoint store for low‑latency resume and list operations with denormalized JSON and pipelined reads/writes.[37][38]
- Idempotent nodes: Each node records completion and uses idempotency keys to avoid duplicate side effects; retries skip completed steps.[39][34]
- Memory pattern: Keep short‑term memory in state and long‑term audit facts in the temporal graph rather than stuffing prompts, improving determinism and explainability.[40][12]

### Temporal knowledge graph
- Model: Nodes for Account, Contact, Deal, Run, Approval, Policy, SOP, Doc, and Event, with edges VERSION_OF, GOVERNS, APPLIES_TO, PERFORMED, APPROVED, CAUSED, and RECONCILES.[13][12]
- Time: Every assertion carries t_valid/t_invalid and provenance (source, event_id, hash) to support “as‑of” questions and audit trails in AGUI.[41][13]
- Queries: “Why did this need approval?” returns the policy and snapshot valid at that time; “What changed between runs?” computes subgraph deltas on the timeline.[42][12]

### Data structures
- Event envelope: meta {event_id, source “hubspot”, object_type, object_id, occurred_at, received_at, correlation_id, workflow_id, run_id, version}, required {min fields per workflow}, payload {HubSpot properties}, raw_payload_ref {blob pointer}.[43][2]
- Airtable base: Entities (Accounts, Contacts, Deals), Operations (Runs, Approvals, Exceptions, Reconciliations), Reference (Policies, RiskRules, Owners), linked via record IDs and displayed in operator views.[44][20]
- DB choice: Neon Postgres recommended for consistency and analytics; MongoDB viable for highly variable payloads; Prisma supports both with type‑safe clients.[15][8]

### Security and RBAC
- Auth: NextAuth/Auth.js with a minimal role set—admin for approvals, operator for execution/edits requiring admin confirm, and viewer for read‑only access.[45][46]
- Guards: Admin‑only Approve/Reject routes with CSRF and session checks; PII redaction in UI with “reveal with reason” gated to admin actions.[46][7]
- Webhooks: Verify HubSpot signatures, time‑limit processing, and store raw payload for forensics and replay.[47][2]

### Reliability and EDA
- Inngest: Step‑level events and status hooks with durable retries and replays to simplify audit and incident response.[28][27]
- RabbitMQ: Quorum queues with CloudAMQP best practices, idempotency by correlation key, and message‑level dedupe using unique IDs where needed.[48][49]
- Idempotency: Acquire locks or key‑based “already processed” records before side effects to guarantee at‑least‑once semantics don’t double‑apply.[30][26]

### Monitoring and SLOs
- Metrics: SLA adherence per workflow, first‑pass yield, exception rate, approval latency, and connector error rate surfaced in AGUI charts and cards.[33][32]
- Alerts: Notify‑only Slack pings with deep links to AGUI for pending approvals over SLA or stuck runs; keep decisions in‑app for security.[50][51]
- Replays: Admins can replay from checkpoints for targeted steps after fixing configuration or transient failures.[16][27]

### SOPs (v1)
- Workflow creation: Define outcomes, inputs, validations, HITL rules, and rollback steps; implement nodes, idempotency, and compensations; test replays in staging; document in Notion.[23][34]
- Intake and triage: Store envelope + raw payload, generate correlation keys, minimal normalization, and enqueue orchestration.[44][2]
- Approvals: Use Approval Sheet; require justification on reject/over‑threshold; store approver, timestamp, and policy version; resume the exact node.[3][12]
- Reconciliation: Nightly compare HubSpot vs ops hub; auto‑repair safe diffs and open Exceptions with one‑click fixes.[35][44]
- Incident response: Inspect Inngest traces, Redis checkpoints, and last successful idempotent writes; replay from checkpoint after mitigation; postmortem in Notion.[22][27]

### User stories
- As an admin, approve or reject procurement over threshold with a clear policy snapshot and diffs, then resume the workflow automatically.[3][12]
- As an operator, reconcile CRM updates into the ops hub with one‑click safe fixes from the Exceptions queue.[35][44]
- As a manager, view weekly SLA and exception KPIs with drilldowns to runs and lineage to understand bottlenecks and errors.[32][33]

### API surface (control plane)
- Webhooks: POST /webhooks/hubspot validates signature, stores envelope, and enqueues events; returns 200 rapidly.[47][2]
- Runs: GET /runs, GET /runs/:id, POST /runs/:id/replay guarded by RBAC to allow admin replays with correlation safety.[46][27]
- Approvals: POST /runs/:id/approve|reject|request‑changes with required justification for rejects and threshold overrides. [46][3]  

### Deployment plan
- Edge: Hono + Workers for webhook/API with Prisma Client using Neon’s serverless Postgres or MongoDB, plus Upstash Redis HTTP client.[52][6]
- Services: FastAPI + LangGraph on a managed runtime with access to Upstash Redis and CloudAMQP RabbitMQ, scaled horizontally per queue depth.[9][11]
- Databases: Neon Postgres for ops tables and lineage pointers, with Prisma migrations and branching for dev/test preview envs.[53][15]

### Risks and mitigations
- Event storms: Debounce by hs_lastmodifieddate and property masks, and buffer via RabbitMQ with backpressure controls.[54][2]
- Duplicate effects: Enforce idempotency keys and lock‑then‑write semantics per node to ensure repeatable outcomes.[26][30]
- Scope creep: Keep external comms out of scope and Slack notify‑only; all decisions live in AGUI to maintain consistency and auditability.[51][50]

This end‑to‑end plan applies CopilotKit and LangGraph best practices, wires the most common SMB ops tools safely, and makes internal workflows autonomous, explainable, and easy to control—turning “HubSpot changed” into “our internal work just happened correctly” with admin approvals only where policy requires it.[5][16]

[1](https://developers.cloudflare.com/workers/framework-guides/web-apps/more-web-frameworks/hono/)
[2](https://developers.hubspot.com/docs/api-reference/webhooks-webhooks-v3/guide)
[3](https://dev.to/copilotkit/easily-build-a-ui-for-your-langgraph-ai-agent-in-minutes-with-copilotkit-1khj)
[4](https://zapier.com/blog/n8n-vs-zapier/)
[5](https://www.copilotkit.ai/blog/heres-how-to-build-fullstack-agent-apps-gemini-copilotkit-langgraph)
[6](https://developers.cloudflare.com/workers/framework-guides/web-apps/react/)
[7](https://github.com/CopilotKit/CopilotKit)
[8](https://www.prisma.io/docs/orm)
[9](https://www.cloudamqp.com/docs/index.html)
[10](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template)
[11](https://redis.io/blog/langgraph-redis-build-smarter-ai-agents-with-memory-persistence/)
[12](https://neo4j.com/blog/developer/neo4j-graphrag-workflow-langchain-langgraph/)
[13](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)
[14](https://upstash.com/docs/introduction)
[15](https://neon.com/docs/introduction/serverless)
[16](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
[17](https://knowledge.hubspot.com/get-started/automate-your-processes)
[18](https://blog.hubspot.com/marketing/workflow-automation)
[19](https://knowledge.hubspot.com/workflows/create-workflows)
[20](https://estuary.dev/blog/top-airtable-integrations/)
[21](https://www.airtable.com/platform)
[22](https://www.notion.com/help/guides/best-practices-internal-communications-on-notion)
[23](https://www.notion.com/templates/standard-operating-procedure-sop-golden)
[24](https://developers.cloudflare.com/workers/vite-plugin/tutorial/)
[25](https://github.com/upstash/redis-js)
[26](https://www.rabbitmq.com/docs/reliability)
[27](https://www.inngest.com/docs/features/events-triggers)
[28](https://www.inngest.com/docs)
[29](https://community.hubspot.com/t5/APIs-Integrations/Trigger-webhook-when-Deal-associations-changes/m-p/290766)
[30](https://www.architecture-weekly.com/p/ordering-grouping-and-consistency)
[31](https://developers.hubspot.com/docs/api-reference/webhooks-webhooks-v4/webhooks-journal)
[32](https://www.eesel.ai/blog/slack-automation)
[33](https://www.airtable.com/solutions)
[34](https://langchain-ai.github.io/langgraph/tutorials/workflows/)
[35](https://www.inngest.com/docs/getting-started/python-quick-start)
[36](https://dev.to/copilotkit/automate-90-of-your-work-with-ai-agents-real-examples-code-inside-46ke)
[37](https://redis.io/blog/langgraph-redis-checkpoint-010/)
[38](https://pypi.org/project/langgraph-checkpoint-redis/)
[39](https://blog.bytebytego.com/p/mastering-idempotency-building-reliable)
[40](https://langchain-ai.github.io/langgraph/how-tos/memory/add-memory/)
[41](https://neo4j.com/blog/developer/rag-tutorial/)
[42](https://neo4j.com/blog/developer/mastering-fraud-detection-temporal-graph/)
[43](https://www.bytebase.com/blog/postgres-vs-mongodb/)
[44](https://www.airtable.com/guides/build/bring-your-workflow-into-airtable)
[45](https://www.axelerant.com/blog/how-to-setup-role-based-access-control-with-next-auth)
[46](https://authjs.dev/guides/role-based-access-control)
[47](https://coefficient.io/hubspot-api/hubspot-webhooks)
[48](https://support.huaweicloud.com/intl/en-us/bestpractice-rabbitmq/bp-0015.html)
[49](https://www.cloudamqp.com/blog/part1-rabbitmq-best-practice.html)
[50](https://clearfeed.ai/blogs/slack-approval-workflow-guide)
[51](https://docs.ag2.ai/latest/docs/blog/2025/05/07/AG2-Copilot-Integration/)
[52](https://upstash.com)
[53](https://www.prisma.io/docs/getting-started)
[54](https://www.cloudamqp.com/blog/part1-rabbitmq-for-beginners-what-is-rabbitmq.html)
[55](https://www.prisma.io/docs)
[56](https://www.prisma.io/orm)
[57](https://www.prisma.io/docs/guides/nextjs)
[58](https://docs.stacktape.com/3rd-party-resources/upstash-redises)
[59](https://www.prisma.io/docs/orm/prisma-client)
[60](https://javascript.plainenglish.io/role-based-access-control-rbac-in-next-js-with-nextauth-js-ad3f40dabdda)
[61](https://github.com/prisma/prisma/issues/27503)
[62](https://www.prisma.io/docs/orm/overview)
[63](https://www.nextbuild.co/blog/a-practical-guide-to-implementing-rbac-in-next-js)
[64](https://authjs.dev/getting-started/adapters/prisma)
[65](https://github.com/nextauthjs/next-auth/discussions/9609)
[66](https://upstash.com/docs/redis/tutorials/using_serverless_framework)
[67](https://docs.nestjs.com/recipes/prisma)
[68](https://www.cloudamqp.com/docs/http.html)
[69](https://www.cloudamqp.com/docs/rabbitmq-server.html)
[70](https://www.cloudamqp.com)
[71](https://www.cloudamqp.com/docs/amqp.html)
[72](https://techcommunity.microsoft.com/blog/partnernews/neon-serverless-postgres-is-now-generally-available/4411249)
[73](https://www.qovery.com/blog/leveraging-neons-serverless-postgres-with-qovery-preview-environments)
[74](https://www.rabbitmq.com/docs)
[75](https://neon.com/docs/introduction)
[76](https://www.gocodeo.com/post/getting-started-with-rabbitmq-architecture-use-cases-and-best-practices)
[77](https://www.rabbitmq.com/release-information)
[78](https://github.com/neondatabase/serverless)
[79](https://registry.terraform.io/providers/cloudamqp/cloudamqp/latest/docs/resources/rabbitmq_configuration)