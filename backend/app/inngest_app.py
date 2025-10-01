from fastapi import FastAPI
import inngest
from app.config import settings
from app.services.inngest_service import inngest_service
from app.workflows.company_intake import graph as company_intake_graph
from app.workflows.contact_role_mapping import graph as contact_role_mapping_graph
from app.workflows.deal_stage_kickoff import graph as deal_stage_kickoff_graph
from app.workflows.procurement_approval import graph as procurement_approval_graph

# Create FastAPI app for Inngest endpoints
app = FastAPI(title="HubSpot Orchestrator Inngest API")

# Register workflow functions with Inngest
# These would typically be triggered by specific HubSpot events
company_intake_fn = inngest_service.create_workflow_function(
    name="company-intake-workflow",
    workflow_graph=company_intake_graph,
    trigger_event="hubspot/company.creation"
)

contact_role_mapping_fn = inngest_service.create_workflow_function(
    name="contact-role-mapping-workflow",
    workflow_graph=contact_role_mapping_graph,
    trigger_event="hubspot/contact.creation"
)

deal_stage_kickoff_fn = inngest_service.create_workflow_function(
    name="deal-stage-kickoff-workflow",
    workflow_graph=deal_stage_kickoff_graph,
    trigger_event="hubspot/deal.propertyChange.dealstage"
)

procurement_approval_fn = inngest_service.create_workflow_function(
    name="procurement-approval-workflow",
    workflow_graph=procurement_approval_graph,
    trigger_event="hubspot/deal.propertyChange.amount"
)

# Mount the Inngest client's API routes
app.mount("/api/inngest", inngest_service.inngest_client)

@app.get("/")
async def root():
    return {"message": "HubSpot Orchestrator Inngest API"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "HubSpot Orchestrator Inngest"}