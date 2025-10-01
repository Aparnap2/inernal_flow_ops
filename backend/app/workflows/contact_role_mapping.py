from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
import json
from app.services.workflow_engine import workflow_engine
from app.services.airtable_client import AirtableClient
from app.services.notion_client import NotionClient
from app.services.llm_client import get_llm_client

# 1. Define the State for the workflow
class ContactRoleMappingState(TypedDict):
    hubspot_event: Dict[str, Any]
    enriched_data: Dict[str, Any]
    contact_data: Dict[str, Any]
    inferred_role: Dict[str, Any]
    permission_checklist: List[Dict[str, Any]]
    drive_templates: List[Dict[str, Any]]
    airtable_record_id: str
    final_result: Dict[str, Any]
    errors: List[str]

# 2. Create Node functions
airtable_client = AirtableClient()
notion_client = NotionClient()
llm = get_llm_client()

async def extract_contact_data(state: ContactRoleMappingState) -> ContactRoleMappingState:
    """Extract and normalize contact data"""
    try:
        input_data = state["enriched_data"]
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
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to extract contact data: {str(e)}")
        raise

async def infer_role_from_title(state: ContactRoleMappingState) -> ContactRoleMappingState:
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
        
        response = await llm.ainvoke([
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
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to infer role from title: {str(e)}")
        raise

async def link_to_account(state: ContactRoleMappingState) -> ContactRoleMappingState:
    """Link contact to account and update relationships"""
    try:
        contact_data = state["contact_data"]
        
        # Get associated companies from HubSpot (this would use the hubspot_client)
        # For now, simulating the associations
        associations = state["enriched_data"].get("associations", {}).get("companies", [])
        
        # Update Airtable with contact-account relationship
        if associations:
            primary_company = associations[0] if associations else {}  # Take first associated company
            
            # Create or update contact record in Airtable
            airtable_contact = await airtable_client.create_contact({
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
            
            state["airtable_record_id"] = airtable_contact["id"]
            state["contact_data"]["primary_company"] = primary_company
        
        return state
        
    except Exception as e:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to link contact to account: {str(e)}")
        raise

async def generate_permission_checklist(state: ContactRoleMappingState) -> ContactRoleMappingState:
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
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to generate permission checklist: {str(e)}")
        raise

async def attach_drive_templates(state: ContactRoleMappingState) -> ContactRoleMappingState:
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
        
        # Update Airtable record with templates if available
        if state.get("airtable_record_id"):
            await airtable_client.update_record(
                state["airtable_record_id"],
                {"Drive Templates": json.dumps(templates)}
            )
        
        return state
        
    except Exception as e:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to attach drive templates: {str(e)}")
        raise

async def finalize_role_mapping(state: ContactRoleMappingState) -> ContactRoleMappingState:
    """Finalize the contact role mapping process"""
    try:
        # Compile final results
        final_result = {
            "status": "completed",
            "contact_data": state["contact_data"],
            "inferred_role": state["inferred_role"],
            "airtable_record_id": state.get("airtable_record_id"),
            "permission_checklist": state["permission_checklist"],
            "drive_templates": state["drive_templates"],
            "completed_at": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            "total_checklist_items": len(state["permission_checklist"])
        }
        
        state["final_result"] = final_result
        return state
        
    except Exception as e:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Failed to finalize role mapping: {str(e)}")
        raise

# 3. Assemble the Graph
workflow = StateGraph(ContactRoleMappingState)

workflow.add_node("extract_contact_data", extract_contact_data)
workflow.add_node("infer_role_from_title", infer_role_from_title)
workflow.add_node("link_to_account", link_to_account)
workflow.add_node("generate_permission_checklist", generate_permission_checklist)
workflow.add_node("attach_drive_templates", attach_drive_templates)
workflow.add_node("finalize_role_mapping", finalize_role_mapping)

workflow.set_entry_point("extract_contact_data")
workflow.add_edge("extract_contact_data", "infer_role_from_title")
workflow.add_edge("infer_role_from_title", "link_to_account")
workflow.add_edge("link_to_account", "generate_permission_checklist")
workflow.add_edge("generate_permission_checklist", "attach_drive_templates")
workflow.add_edge("attach_drive_templates", "finalize_role_mapping")
workflow.add_edge("finalize_role_mapping", END)

# 4. Compile the Graph
graph = workflow.compile(checkpointer=workflow_engine.get_checkpointer())