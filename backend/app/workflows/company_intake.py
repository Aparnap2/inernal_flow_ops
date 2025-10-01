from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
import json
from app.services.workflow_engine import workflow_engine
from app.services.airtable_client import AirtableClient
from app.services.notion_client import NotionClient
from app.services.llm_client import get_llm_client

# 1. Define the State for the workflow
class CompanyIntakeState(TypedDict):
    hubspot_event: Dict[str, Any]
    enriched_data: Dict[str, Any]
    company_data: Dict[str, Any]
    normalized_data: Dict[str, Any]
    airtable_record: Dict[str, Any]
    notion_page_id: str
    kickoff_scheduled: bool
    requires_approval: bool
    approval_data: Dict[str, Any]
    final_result: Dict[str, Any]
    errors: List[str]

# 2. Create Node functions
airtable_client = AirtableClient()
notion_client = NotionClient()
llm = get_llm_client()

async def start_intake(state: CompanyIntakeState) -> CompanyIntakeState:
    """Node to start the workflow and perform initial validation."""
    print("--- Node: start_intake ---")
    # In a real scenario, we might do some initial validation here
    state["kickoff_scheduled"] = False  # Initialize
    state["requires_approval"] = False
    state["approval_data"] = {}
    if "errors" not in state:
        state["errors"] = []
    return state

async def extract_company_data(state: CompanyIntakeState) -> CompanyIntakeState:
    """Extract and normalize company data from HubSpot."""
    print("--- Node: extract_company_data ---")
    try:
        company_details = state["enriched_data"]["details"]["properties"]
        
        company_data = {
            "id": state["enriched_data"]["details"]["id"],
            "Name": company_details.get("name"),
            "Domain": company_details.get("domain"),
            "Industry": company_details.get("industry"),
            "Employee Count": int(company_details.get("numberofemployees", 0) or 0),
            "Annual Revenue": float(company_details.get("annualrevenue", 0) or 0),
            "Lifecycle Stage": company_details.get("lifecyclestage", "prospect"),
            "HubSpot ID": state["enriched_data"]["details"]["id"]
        }
        state["company_data"] = company_data
        print(f"Extracted company data: {company_data}")
        return state
    except Exception as e:
        state["errors"].append(f"Failed to extract company data: {str(e)}")
        raise

async def normalize_company_data(state: CompanyIntakeState) -> CompanyIntakeState:
    """Node to normalize company data from HubSpot using AI enrichment."""
    print("--- Node: normalize_company_data ---")
    try:
        company_data = state["company_data"]
        
        # Use LLM to enrich and validate data
        enrichment_prompt = f"""
        Analyze and enrich this company data:
        {json.dumps(company_data, indent=2)}
        
        Please:
        1. Validate the industry classification
        2. Suggest any missing critical information
        3. Flag any data quality issues
        4. Provide a risk assessment (LOW/MEDIUM/HIGH)
        5. Calculate potential customer value score (1-10)
        6. Recommend onboarding priority level
        
        Return a JSON object with the enriched data and analysis.
        """
        
        response = await llm.ainvoke([
            SystemMessage(content="You are a data analyst specializing in company data enrichment."),
            HumanMessage(content=enrichment_prompt)
        ])
        
        # Parse LLM response and merge with normalized data
        try:
            llm_analysis = json.loads(response.content)
            company_data.update(llm_analysis.get("enriched_data", {}))
            company_data["ai_analysis"] = llm_analysis.get("analysis", {})
        except json.JSONDecodeError:
            company_data["ai_analysis"] = {"error": "Failed to parse LLM response"}
        
        state["normalized_data"] = company_data
        print(f"Normalized data: {company_data}")
        return state
    except Exception as e:
        state["errors"].append(f"Failed to normalize company data: {str(e)}")
        raise

async def check_approval_requirements(state: CompanyIntakeState) -> CompanyIntakeState:
    """Check if approval is needed based on business rules and AI analysis"""
    print("--- Node: check_approval_requirements ---")
    try:
        normalized_data = state["normalized_data"]
        
        # Business rules for approval
        approval_needed = False
        approval_reasons = []
        
        if normalized_data.get("Employee Count", 0) > 1000:
            approval_needed = True
            approval_reasons.append("Large company (>1000 employees)")
        
        if normalized_data.get("Annual Revenue", 0) > 10000000:
            approval_needed = True
            approval_reasons.append("High revenue company (>$10M)")
        
        if normalized_data.get("Industry") in ["Government", "Healthcare", "Financial Services"]:
            approval_needed = True
            approval_reasons.append(f"Regulated industry: {normalized_data.get('Industry')}")
        
        ai_risk = normalized_data.get("ai_analysis", {}).get("risk_level", "LOW")
        if ai_risk in ["HIGH", "CRITICAL"]:
            approval_needed = True
            approval_reasons.append(f"AI flagged as {ai_risk} risk")
        
        state["requires_approval"] = approval_needed
        state["approval_data"] = {
            "reasons": approval_reasons,
            "company_data": normalized_data,
            "risk_level": ai_risk,
            "requested_at": "2024-01-01T00:00:00Z"  # Would use current timestamp
        }
        
        print(f"Approval required: {approval_needed}, reasons: {approval_reasons}")
        return state
    except Exception as e:
        state["errors"].append(f"Failed to check approval requirements: {str(e)}")
        raise

def should_wait_for_approval(state: CompanyIntakeState) -> str:
    """Conditional edge to determine if approval is needed"""
    print("--- Condition: should_wait_for_approval ---")
    return "wait_for_approval" if state.get("requires_approval", False) else "upsert_to_airtable"

async def wait_for_approval(state: CompanyIntakeState) -> CompanyIntakeState:
    """Wait for human approval (interrupt point)"""
    print("--- Node: wait_for_approval (HITL) ---")
    print(">>> Graph interrupted. Waiting for approval with policy snapshot in AGUI...")
    print("...simulating approval process...")
    # In a real system, workflow would pause here waiting for AGUI approval
    # For simulation, defaulting to approved
    print("Approval received. Resuming workflow. <<<")
    return state

async def upsert_to_airtable(state: CompanyIntakeState) -> CompanyIntakeState:
    """Node to upsert the normalized company data to Airtable."""
    print("--- Node: upsert_to_airtable ---")
    try:
        # In a real app, these would come from config
        BASE_ID = "app_your_base_id"  # Would come from config
        TABLE_NAME = "Accounts"
        
        record = await airtable_client.upsert_record(
            base_id=BASE_ID,
            table_name=TABLE_NAME,
            record=state["normalized_data"]
        )
        state["airtable_record"] = record
        print(f"Airtable record upserted: {record['id']}")
        return state
    except Exception as e:
        state["errors"].append(f"Failed to upsert to Airtable: {str(e)}")
        raise

async def attach_notion_sop(state: CompanyIntakeState) -> CompanyIntakeState:
    """Node to attach a link to the relevant SOP in Notion."""
    print("--- Node: attach_notion_sop ---")
    try:
        # Assuming the Airtable record has a field for the Notion Page ID
        notion_page_id = state["airtable_record"]["fields"].get("Notion Page ID", "default_page_id")
        SOP_URL = "https://www.notion.so/your-company-intake-sop"
        
        await notion_client.attach_sop_link(page_id=notion_page_id, sop_url=SOP_URL)
        state["notion_page_id"] = notion_page_id
        return state
    except Exception as e:
        state["errors"].append(f"Failed to attach Notion SOP: {str(e)}")
        raise

def should_schedule_kickoff(state: CompanyIntakeState) -> str:
    """Conditional edge to decide if a kickoff should be scheduled."""
    print("--- Condition: should_schedule_kickoff ---")
    lifecycle_stage = state["normalized_data"].get("Lifecycle Stage")
    
    # As per the PRD, schedule a task if lifecycle rules match.
    if lifecycle_stage == "customer":
        print("Rule matched: Lifecycle stage is 'customer'. Proceeding to schedule kickoff.")
        return "schedule_kickoff"
    else:
        print("Rule not matched. Ending workflow.")
        return "end_workflow"

async def schedule_kickoff(state: CompanyIntakeState) -> CompanyIntakeState:
    """Node to schedule the internal kickoff task."""
    print("--- Node: schedule_kickoff ---")
    # This is a placeholder for the actual kickoff logic.
    # e.g., call Google Client, create a task in Asana, etc.
    state["kickoff_scheduled"] = True
    print("Kickoff task placeholder executed successfully.")
    return state

async def finalize_intake(state: CompanyIntakeState) -> CompanyIntakeState:
    """Finalize the company intake process"""
    try:
        final_result = {
            "status": "completed",
            "company_data": state["normalized_data"],
            "airtable_record": state["airtable_record"],
            "notion_page_id": state.get("notion_page_id"),
            "approval_required": state.get("requires_approval", False),
            "kickoff_scheduled": state.get("kickoff_scheduled", False),
            "completed_at": "2024-01-01T00:00:00Z",  # Would use current timestamp
            "total_steps": len(state.get("normalized_data", {}).keys())
        }
        
        state["final_result"] = final_result
        return state
    except Exception as e:
        state["errors"].append(f"Failed to finalize intake: {str(e)}")
        raise

# 3. Assemble the Graph
workflow = StateGraph(CompanyIntakeState)

workflow.add_node("start_intake", start_intake)
workflow.add_node("extract_company_data", extract_company_data)
workflow.add_node("normalize_data", normalize_company_data)
workflow.add_node("check_approval_requirements", check_approval_requirements)
workflow.add_node("wait_for_approval", wait_for_approval)
workflow.add_node("upsert_to_airtable", upsert_to_airtable)
workflow.add_node("attach_notion_sop", attach_notion_sop)
workflow.add_node("schedule_kickoff", schedule_kickoff)
workflow.add_node("finalize_intake", finalize_intake)

workflow.set_entry_point("start_intake")
workflow.add_edge("start_intake", "extract_company_data")
workflow.add_edge("extract_company_data", "normalize_data")
workflow.add_edge("normalize_data", "check_approval_requirements")

# Add the conditional edge for approval decision
workflow.add_conditional_edges(
    "check_approval_requirements",
    should_wait_for_approval,
    {
        "wait_for_approval": "wait_for_approval",
        "upsert_to_airtable": "upsert_to_airtable"
    }
)

workflow.add_edge("wait_for_approval", "upsert_to_airtable")
workflow.add_edge("upsert_to_airtable", "attach_notion_sop")

# Add the conditional edge based on the company's lifecycle stage.
workflow.add_conditional_edges(
    "attach_notion_sop",
    should_schedule_kickoff,
    {
        "schedule_kickoff": "schedule_kickoff",
        "end_workflow": END,
    },
)

workflow.add_edge("schedule_kickoff", "finalize_intake")
workflow.add_edge("finalize_intake", END)

# 4. Compile the Graph with the Redis checkpointer
graph = workflow.compile(checkpointer=workflow_engine.get_checkpointer())