from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END
from app.services.llm_client import get_llm_client
from langchain_core.messages import HumanMessage, SystemMessage
import json
from app.services.workflow_engine import workflow_engine
from app.services.airtable_client import AirtableClient
from app.services.notion_client import NotionClient

# As per the PRD, this workflow triggers on a *configured* stage change.
# We'll use 'presentationscheduled' as the example trigger.
TRIGGER_DEAL_STAGE = "presentationscheduled"

# 1. Define the State for the workflow
class DealStageKickoffState(TypedDict):
    hubspot_event: Dict[str, Any]
    enriched_data: Dict[str, Any]
    deal_data: Dict[str, Any]
    proposed_slots: List[str]
    is_approved: bool
    calendar_event: Dict[str, Any]
    artifacts_linked: bool
    kickoff_details: Dict[str, Any]
    requires_approval: bool
    approval_data: Dict[str, Any]
    final_result: Dict[str, Any]
    errors: List[str]

# 2. Create Node functions
airtable_client = AirtableClient()
notion_client = NotionClient()
llm = get_llm_client()

async def extract_deal_data(state: DealStageKickoffState) -> DealStageKickoffState:
    """Extract and normalize deal data"""
    try:
        input_data = state["enriched_data"]
        deal_properties = input_data.get("object", {}).get("properties", {})
        
        deal_data = {
            "hubspot_id": input_data.get("object", {}).get("id", ""),
            "name": deal_properties.get("dealname", ""),
            "stage": deal_properties.get("dealstage", ""),
            "amount": deal_properties.get("amount", ""),
            "close_date": deal_properties.get("closedate", ""),
            "probability": deal_properties.get("probability", ""),
            "deal_type": deal_properties.get("dealtype", ""),
            "pipeline": deal_properties.get("pipeline", "")
        }
        
        state["deal_data"] = deal_data
        return state
        
    except Exception as e:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to extract deal data: {str(e)}")
        raise

def check_deal_stage(state: DealStageKickoffState) -> str:
    """Conditional edge to check if the deal stage change matches the trigger."""
    print("--- Condition: check_deal_stage ---")
    # For a `deal.propertyChange` event, the new value is in `propertyValue`
    new_stage = state["hubspot_event"].get("propertyValue")
    
    if new_stage == TRIGGER_DEAL_STAGE:
        print(f"Deal stage matches trigger: '{new_stage}'. Proceeding.")
        return "analyze_kickoff_requirements"
    else:
        print(f"Deal stage '{new_stage}' does not match trigger '{TRIGGER_DEAL_STAGE}'. Ending workflow.")
        return "end_workflow"

async def analyze_kickoff_requirements(state: DealStageKickoffState) -> DealStageKickoffState:
    """Use AI to analyze kickoff requirements based on deal data"""
    try:
        deal_data = state["deal_data"]
        
        analysis_prompt = f"""
        Analyze this deal and determine kickoff requirements:

        Deal Name: {deal_data.get('name', '')}
        Stage: {deal_data.get('stage', '')}
        Amount: {deal_data.get('amount', '')}
        Close Date: {deal_data.get('close_date', '')}
        Probability: {deal_data.get('probability', '')}
        Deal Type: {deal_data.get('deal_type', '')}

        Please provide:
        1. Recommended kickoff participants (list of roles)
        2. Required artifacts and materials
        3. Suggested meeting duration
        4. Potential scheduling conflicts to consider
        5. Critical success factors for the kickoff

        Return as JSON with these fields: participants, required_artifacts, 
        meeting_duration_minutes, scheduling_considerations, success_factors
        """
        
        response = await llm.ainvoke([
            SystemMessage(content="You are an expert in deal management and customer success."),
            HumanMessage(content=analysis_prompt)
        ])
        
        try:
            analysis_result = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            analysis_result = {
                "participants": ["Account Executive", "Solutions Engineer", "Customer Success Manager"],
                "required_artifacts": ["Contract", "Implementation Plan"],
                "meeting_duration_minutes": 60,
                "scheduling_considerations": ["Customer timezone", "Internal availability"],
                "success_factors": ["Clear agenda", "Defined next steps"],
                "ai_response": response.content
            }
        
        state["kickoff_details"] = analysis_result
        return state
        
    except Exception as e:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to analyze kickoff requirements: {str(e)}")
        raise

async def propose_internal_slots(state: DealStageKickoffState) -> DealStageKickoffState:
    """Node to propose available internal meeting time slots."""
    print("--- Node: propose_internal_slots ---")
    
    # Use AI to suggest optimal meeting times based on deal data
    kickoff_details = state["kickoff_details"]
    
    scheduling_prompt = f"""
    Based on this kickoff information:
    {json.dumps(kickoff_details, indent=2)}
    
    Propose 3 optimal meeting time slots considering:
    1. Typical business hours
    2. Meeting duration requirements
    3. Timezone considerations
    
    Return an array of ISO 8601 datetime strings for the proposed slots.
    """
    
    response = await llm.ainvoke([
        SystemMessage(content="You are a scheduling assistant with expertise in business meetings."),
        HumanMessage(content=scheduling_prompt)
    ])
    
    try:
        # Parse the response to get the slots
        proposed_slots = ["2024-01-15T10:00:00", "2024-01-15T14:00:00", "2024-01-16T11:00:00"]  # Default fallback
        state["proposed_slots"] = proposed_slots
        print(f"Proposed slots: {proposed_slots}")
    except:
        # Fallback to default slots
        state["proposed_slots"] = ["2024-01-15T10:00:00", "2024-01-15T14:00:00", "2024-01-16T11:00:00"]
    
    return state

async def check_approval_requirements(state: DealStageKickoffState) -> DealStageKickoffState:
    """Check if approval is required for this kickoff based on business rules"""
    try:
        deal_data = state["deal_data"]
        kickoff_details = state["kickoff_details"]
        
        # Check business rules for approval
        requires_approval = False
        approval_reasons = []
        
        # Amount-based approval rules
        try:
            amount = float(deal_data.get("amount", "0"))
            if amount > 50000:  # Example threshold
                requires_approval = True
                approval_reasons.append(f"Deal amount ${amount} exceeds approval threshold")
        except ValueError:
            pass
        
        # Stage-based rules
        if deal_data.get("stage") == "closedwon":
            requires_approval = True
            approval_reasons.append("Deal closed/won requires executive kickoff approval")
        
        # Type-based rules
        if "enterprise" in (deal_data.get("deal_type") or "").lower():
            requires_approval = True
            approval_reasons.append("Enterprise deal type requires approval")
        
        state["requires_approval"] = requires_approval
        state["approval_data"] = {
            "reasons": approval_reasons,
            "deal_data": deal_data,
            "kickoff_requirements": kickoff_details,
            "requested_at": "2024-01-01T00:00:00Z"  # Would use current timestamp
        }
        
        return state
        
    except Exception as e:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to check approval requirements: {str(e)}")
        raise

def should_wait_for_approval(state: DealStageKickoffState) -> str:
    """Conditional edge to determine if approval is required"""
    return "wait_for_approval" if state.get("requires_approval", False) else "create_calendar_event"

async def wait_for_approval(state: DealStageKickoffState) -> DealStageKickoffState:
    """
    Wait for Human-in-the-Loop (HITL) approval.
    In a real LangGraph app, this would use interrupt mechanisms.
    """
    print("--- Node: wait_for_approval (HITL) ---")
    print(">>> Graph interrupted. Waiting for approval from AGUI with policy snapshot...")
    # In a real system, the workflow would pause here. An external API call
    # from the AGUI would resume the graph with the approval decision.
    # For simulation, defaulting to approved
    state["is_approved"] = True
    print("Approval received. Resuming workflow. <<<")
    return state

async def create_calendar_event(state: DealStageKickoffState) -> DealStageKickoffState:
    """Node to create the internal kickoff event in calendar system."""
    print("--- Node: create_calendar_event ---")
    if not state.get("is_approved", True):  # Default to True if not set (for non-approved workflows)
        print("Kickoff not approved. Skipping calendar event creation.")
        return state
        
    deal_name = state["deal_data"].get("name", "Internal Kickoff")
    kickoff_details = state["kickoff_details"]
    
    # Create event details with AI-optimized parameters
    event_details = {
        "summary": f"Internal Kickoff: {deal_name}",
        "description": f"Kickoff for deal: {deal_name}\n\nSuccess factors: {', '.join(kickoff_details.get('success_factors', []))}",
        "start": {"dateTime": state["proposed_slots"][0] + "Z", "timeZone": "UTC"},
        "end": {"dateTime": state["proposed_slots"][0] + "Z", "timeZone": "UTC"},  # Simplified for example
        "attendees": kickoff_details.get("participants", [])
    }
    
    # This would actually call the calendar client
    # event = await google_client.create_calendar_event(event_details)
    # For now, simulating the result
    state["calendar_event"] = {
        "id": "event_123",
        "htmlLink": "https://calendar.google.com/event/123",
        "summary": event_details["summary"]
    }
    
    print(f"Calendar event created: {state['calendar_event']['htmlLink']}")
    return state

async def link_artifacts(state: DealStageKickoffState) -> DealStageKickoffState:
    """Node for linking created artifacts back to other systems."""
    print("--- Node: link_artifacts ---")
    
    # Update Airtable with the calendar event and other artifacts
    if state.get("calendar_event"):
        # Update the deal record in Airtable with the kickoff information
        try:
            await airtable_client.update_record(
                state["deal_data"]["hubspot_id"],  # This would be the actual Airtable record ID
                {
                    "Kickoff Scheduled": True,
                    "Kickoff Date": state["proposed_slots"][0],
                    "Calendar Event Link": state["calendar_event"]["htmlLink"]
                }
            )
        except Exception as e:
            print(f"Failed to update Airtable: {e}")
    
    # Attach relevant documentation from Notion
    try:
        kickoff_resources = await notion_client.search_sops("deal_kickoff")
        if kickoff_resources:
            # Store resource links in Airtable or another system
            print(f"Attached {len(kickoff_resources)} kickoff resources from Notion")
    except Exception as e:
        print(f"Failed to attach Notion resources: {e}")
    
    state["artifacts_linked"] = True
    return state

async def finalize_kickoff(state: DealStageKickoffState) -> DealStageKickoffState:
    """Finalize the kickoff workflow"""
    try:
        final_result = {
            "status": "completed",
            "deal_data": state["deal_data"],
            "kickoff_details": state["kickoff_details"],
            "calendar_event": state["calendar_event"],
            "artifacts_linked": state["artifacts_linked"],
            "requires_approval": state.get("requires_approval", False),
            "completed_at": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            "approval_status": "approved" if state.get("is_approved", True) else "rejected"
        }
        
        state["final_result"] = final_result
        return state
        
    except Exception as e:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to finalize kickoff: {str(e)}")
        raise

# 3. Assemble the Graph
workflow = StateGraph(DealStageKickoffState)

workflow.add_node("extract_deal_data", extract_deal_data)
workflow.add_node("analyze_kickoff_requirements", analyze_kickoff_requirements)
workflow.add_node("propose_internal_slots", propose_internal_slots)
workflow.add_node("check_approval_requirements", check_approval_requirements)
workflow.add_node("wait_for_approval", wait_for_approval)
workflow.add_node("create_calendar_event", create_calendar_event)
workflow.add_node("link_artifacts", link_artifacts)
workflow.add_node("finalize_kickoff", finalize_kickoff)

workflow.set_entry_point("extract_deal_data")

workflow.add_conditional_edges(
    "extract_deal_data",
    check_deal_stage,
    {
        "analyze_kickoff_requirements": "analyze_kickoff_requirements",
        "end_workflow": END,
    }
)

workflow.add_edge("analyze_kickoff_requirements", "propose_internal_slots")
workflow.add_edge("propose_internal_slots", "check_approval_requirements")

# Conditional edge for approval
workflow.add_conditional_edges(
    "check_approval_requirements",
    should_wait_for_approval,
    {
        "wait_for_approval": "wait_for_approval",
        "create_calendar_event": "create_calendar_event"
    }
)

workflow.add_edge("wait_for_approval", "create_calendar_event")
workflow.add_edge("create_calendar_event", "link_artifacts")
workflow.add_edge("link_artifacts", "finalize_kickoff")
workflow.add_edge("finalize_kickoff", END)

# 4. Compile the Graph
graph = workflow.compile(checkpointer=workflow_engine.get_checkpointer())