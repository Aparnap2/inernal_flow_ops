from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END
from app.services.llm_client import get_llm_client
from langchain_core.messages import HumanMessage, SystemMessage
import json
from app.services.workflow_engine import workflow_engine
from app.services.airtable_client import AirtableClient
from app.services.notion_client import NotionClient

# As per the PRD, approval is required for deals over a certain threshold.
APPROVAL_THRESHOLD = 10000.0

# 1. Define the State for the workflow
class ProcurementApprovalState(TypedDict):
    hubspot_event: Dict[str, Any]
    enriched_data: Dict[str, Any]
    deal_data: Dict[str, Any]
    procurement_record_id: str
    is_approved: bool
    po_record_id: str
    requires_approval: bool
    approval_data: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    policy_snapshot: Dict[str, Any]
    approvers: List[Dict[str, Any]]
    final_result: Dict[str, Any]
    errors: List[str]

# 2. Create Node functions
airtable_client = AirtableClient()
notion_client = NotionClient()
llm = get_llm_client()

async def extract_deal_data(state: ProcurementApprovalState) -> ProcurementApprovalState:
    """Extract and normalize deal data"""
    try:
        input_data = state["enriched_data"]
        deal_properties = input_data.get("object", {}).get("properties", {})
        
        deal_data = {
            "hubspot_id": input_data.get("object", {}).get("id", ""),
            "name": deal_properties.get("dealname", ""),
            "amount": deal_properties.get("amount", ""),
            "stage": deal_properties.get("dealstage", ""),
            "deal_type": deal_properties.get("dealtype", ""),
            "pipeline": deal_properties.get("pipeline", ""),
            "company_name": "",
            "contact_name": ""
        }
        
        # Get associated company and contact if available
        associations = state.get("enriched_data", {}).get("associations", {})
        if "companies" in associations and len(associations["companies"]) > 0:
            deal_data["company_name"] = associations["companies"][0].get("properties", {}).get("name", "")
        if "contacts" in associations and len(associations["contacts"]) > 0:
            contact = associations["contacts"][0].get("properties", {})
            deal_data["contact_name"] = f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip()
        
        state["deal_data"] = deal_data
        return state
        
    except Exception as e:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to extract deal data: {str(e)}")
        raise

def check_risk_threshold(state: ProcurementApprovalState) -> str:
    """Conditional edge to check if the deal amount exceeds the approval threshold."""
    print("--- Condition: check_risk_threshold ---")
    
    # This workflow is only concerned with changes to the 'amount' property.
    property_name = state["hubspot_event"].get("propertyName")
    if property_name != "amount":
        print(f"Property '{property_name}' is not 'amount'. Skipping procurement check.")
        return "end_workflow"

    try:
        deal_amount = float(state["hubspot_event"].get("propertyValue", 0))
    except (ValueError, TypeError):
        deal_amount = 0.0
    
    if deal_amount > APPROVAL_THRESHOLD:
        print(f"Deal amount ${deal_amount:.2f} exceeds threshold of ${APPROVAL_THRESHOLD:.2f}. Approval required.")
        return "assess_risk"
    else:
        print(f"Deal amount ${deal_amount:.2f} is within threshold. No approval needed.")
        return "end_workflow"

async def assess_risk(state: ProcurementApprovalState) -> ProcurementApprovalState:
    """Use AI to perform comprehensive risk assessment"""
    try:
        deal_data = state["deal_data"]
        
        risk_prompt = f"""
        Perform a comprehensive risk assessment for this deal:

        Deal Name: {deal_data.get('name', '')}
        Amount: ${deal_data.get('amount', '0')}
        Stage: {deal_data.get('stage', '')}
        Deal Type: {deal_data.get('deal_type', '')}
        Company: {deal_data.get('company_name', '')}
        Contact: {deal_data.get('contact_name', '')}

        Please evaluate and provide:
        1. Financial risk level (LOW/MEDIUM/HIGH/CRITICAL)
        2. Customer risk (creditworthiness, history)
        3. Market risk factors
        4. Contract complexity and risk factors
        5. Recommended approval level (who should approve)
        6. Risk mitigation strategies
        7. Red flags or concerns

        Return as JSON with these fields: risk_level, customer_risk, market_risk, 
        contract_risk, recommended_approval_level, mitigation_strategies, red_flags
        """
        
        response = await llm.ainvoke([
            SystemMessage(content="You are an expert in financial risk assessment and procurement approval."),
            HumanMessage(content=risk_prompt)
        ])
        
        try:
            risk_assessment = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            risk_assessment = {
                "risk_level": "MEDIUM",
                "customer_risk": "MODERATE",
                "market_risk": "LOW", 
                "contract_risk": "LOW",
                "recommended_approval_level": "MANAGER",
                "mitigation_strategies": ["Standard contract review"],
                "red_flags": [],
                "ai_response": response.content
            }
        
        state["risk_assessment"] = risk_assessment
        return state
        
    except Exception as e:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to assess risk: {str(e)}")
        raise

async def determine_approval_requirements(state: ProcurementApprovalState) -> ProcurementApprovalState:
    """Determine specific approval requirements based on risk assessment"""
    try:
        risk_assessment = state["risk_assessment"]
        deal_data = state["deal_data"]
        
        # Determine if approval is required and who should approve
        requires_approval = True  # For deals over threshold, approval is always required
        policy_snapshot = {
            "threshold": APPROVAL_THRESHOLD,
            "risk_level": risk_assessment["risk_level"],
            "approval_required": True,
            "recommended_approver": risk_assessment["recommended_approval_level"],
            "effective_date": "2024-01-01T00:00:00Z"  # Would use current timestamp
        }
        
        # Determine approvers based on risk level and amount
        approvers = []
        amount = float(deal_data.get("amount", 0))
        
        if risk_assessment["risk_level"] in ["HIGH", "CRITICAL"] or amount > 50000:
            approvers.append({
                "name": "Head of Sales",
                "email": "head-sales@company.com", 
                "level": "EXECUTIVE",
                "required": True
            })
        elif risk_assessment["risk_level"] in ["MEDIUM"] or amount > 25000:
            approvers.append({
                "name": "Sales Manager",
                "email": "sales-manager@company.com",
                "level": "MANAGER", 
                "required": True
            })
        else:
            approvers.append({
                "name": "Sales Director",
                "email": "sales-dir@company.com",
                "level": "SENIOR_MANAGER",
                "required": True
            })
        
        # Add finance approver for high-risk deals
        if risk_assessment["risk_level"] in ["HIGH", "CRITICAL"]:
            approvers.append({
                "name": "Finance Manager",
                "email": "finance@company.com",
                "level": "MANAGER",
                "required": True
            })
        
        state["requires_approval"] = requires_approval
        state["policy_snapshot"] = policy_snapshot
        state["approvers"] = approvers
        
        return state
        
    except Exception as e:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to determine approval requirements: {str(e)}")
        raise

async def create_procurement_record(state: ProcurementApprovalState) -> ProcurementApprovalState:
    """Create a procurement record in the operations system."""
    print("--- Node: create_procurement_record ---")
    
    try:
        deal_data = state["deal_data"]
        risk_assessment = state["risk_assessment"]
        
        # Create procurement record with all relevant data
        procurement_record = {
            "Deal Name": deal_data.get("name", ""),
            "Amount": deal_data.get("amount", ""),
            "Company": deal_data.get("company_name", ""),
            "Contact": deal_data.get("contact_name", ""),
            "Stage": deal_data.get("stage", ""),
            "Risk Level": risk_assessment.get("risk_level", "UNKNOWN"),
            "Red Flags": json.dumps(risk_assessment.get("red_flags", [])),
            "Created Date": "2024-01-01T00:00:00Z",  # Would use current timestamp
            "Status": "PENDING_APPROVAL"
        }
        
        # This would create the record in Airtable or another ops system
        # For now, simulating:
        record_id = f"proc_{deal_data['hubspot_id']}"
        state["procurement_record_id"] = record_id
        
        print(f"Procurement record created: {record_id}")
        return state
        
    except Exception as e:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to create procurement record: {str(e)}")
        raise

async def prepare_approval_request(state: ProcurementApprovalState) -> ProcurementApprovalState:
    """Prepare detailed approval request with all necessary context"""
    try:
        deal_data = state["deal_data"]
        risk_assessment = state["risk_assessment"]
        policy_snapshot = state["policy_snapshot"]
        
        approval_request_data = {
            "deal_id": deal_data["hubspot_id"],
            "deal_name": deal_data["name"],
            "amount": float(deal_data.get("amount", 0)),
            "company": deal_data.get("company_name", ""),
            "contact": deal_data.get("contact_name", ""),
            "risk_assessment": risk_assessment,
            "policy_snapshot": policy_snapshot,
            "approvers": state["approvers"],
            "required_approvals": len([a for a in state["approvers"] if a["required"]]),
            "business_justification": f"Deal for {deal_data.get('company_name', 'Unknown Client')} to expand business relationship",
            "mitigation_strategies": risk_assessment.get("mitigation_strategies", []),
            "created_at": "2024-01-01T00:00:00Z"  # Would use current timestamp
        }
        
        state["approval_data"] = approval_request_data
        
        # Update the procurement record with approval details
        if state["procurement_record_id"]:
            await airtable_client.update_record(
                state["procurement_record_id"],
                {
                    "Approval Request": json.dumps(approval_request_data, indent=2),
                    "Approvers": json.dumps(state["approvers"]),
                    "Risk Assessment": json.dumps(risk_assessment)
                }
            )
        
        return state
        
    except Exception as e:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to prepare approval request: {str(e)}")
        raise

async def wait_for_procurement_approval(state: ProcurementApprovalState) -> ProcurementApprovalState:
    """
    Wait for procurement approval from authorized approvers.
    In a real LangGraph app, this would use interrupt mechanisms.
    """
    print("--- Node: wait_for_procurement_approval (HITL) ---")
    print(">>> Graph interrupted. Waiting for procurement approval with policy snapshot in AGUI...")
    print("...simulating approval process...")
    # In a real system, this would wait for explicit approval from authorized users
    # For simulation, defaulting to approved
    state["is_approved"] = True
    print("Procurement approval received. Resuming workflow. <<<")
    return state

async def create_po_record(state: ProcurementApprovalState) -> ProcurementApprovalState:
    """Create an internal Purchase Order record after approval."""
    print("--- Node: create_po_record ---")
    if not state["is_approved"]:
        print("Procurement not approved. Skipping PO record creation.")
        # Still return the state to allow for proper completion handling
        state["final_result"] = {
            "status": "rejected",
            "procurement_record_id": state["procurement_record_id"],
            "deal_id": state["deal_data"]["hubspot_id"]
        }
        return state
        
    try:
        # Create PO record in internal system
        po_record_id = f"po_{state['procurement_record_id']}"
        deal_data = state["deal_data"]
        
        po_record = {
            "Procurement Record ID": state["procurement_record_id"],
            "Deal ID": deal_data["hubspot_id"],
            "Deal Name": deal_data["name"],
            "Amount": deal_data["amount"],
            "Company": deal_data["company_name"],
            "Approved By": "Automated System",  # Would be actual approver
            "Approved At": "2024-01-01T00:00:00Z",  # Would use current timestamp
            "Status": "CREATED"
        }
        
        state["po_record_id"] = po_record_id
        
        # Update procurement record to reflect PO creation
        if state["procurement_record_id"]:
            await airtable_client.update_record(
                state["procurement_record_id"],
                {
                    "PO Record ID": po_record_id,
                    "Status": "APPROVED_AND_PO_CREATED",
                    "PO Created At": "2024-01-01T00:00:00Z"  # Would use current timestamp
                }
            )
        
        print(f"Internal PO Record created: {po_record_id}")
        return state
        
    except Exception as e:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to create PO record: {str(e)}")
        raise

async def finalize_procurement_approval(state: ProcurementApprovalState) -> ProcurementApprovalState:
    """Finalize the procurement approval workflow"""
    try:
        final_result = {
            "status": "completed",
            "deal_data": state["deal_data"],
            "risk_assessment": state["risk_assessment"],
            "procurement_record_id": state["procurement_record_id"],
            "po_record_id": state["po_record_id"],
            "is_approved": state["is_approved"],
            "completed_at": "2024-01-01T00:00:00Z",  # Would use current timestamp
            "approvers": state["approvers"]
        }
        
        state["final_result"] = final_result
        return state
        
    except Exception as e:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to finalize procurement approval: {str(e)}")
        raise

# 3. Assemble the Graph
workflow = StateGraph(ProcurementApprovalState)

workflow.add_node("extract_deal_data", extract_deal_data)
workflow.add_node("assess_risk", assess_risk)
workflow.add_node("determine_approval_requirements", determine_approval_requirements)
workflow.add_node("create_procurement_record", create_procurement_record)
workflow.add_node("prepare_approval_request", prepare_approval_request)
workflow.add_node("wait_for_procurement_approval", wait_for_procurement_approval)
workflow.add_node("create_po_record", create_po_record)
workflow.add_node("finalize_procurement_approval", finalize_procurement_approval)

workflow.set_entry_point("extract_deal_data")

workflow.add_conditional_edges(
    "extract_deal_data",
    check_risk_threshold,
    {
        "assess_risk": "assess_risk",
        "end_workflow": END,
    }
)

workflow.add_edge("assess_risk", "determine_approval_requirements")
workflow.add_edge("determine_approval_requirements", "create_procurement_record")
workflow.add_edge("create_procurement_record", "prepare_approval_request")
workflow.add_edge("prepare_approval_request", "wait_for_procurement_approval")
workflow.add_edge("wait_for_procurement_approval", "create_po_record")
workflow.add_edge("create_po_record", "finalize_procurement_approval")
workflow.add_edge("finalize_procurement_approval", END)

# 4. Compile the Graph
graph = workflow.compile(checkpointer=workflow_engine.get_checkpointer())