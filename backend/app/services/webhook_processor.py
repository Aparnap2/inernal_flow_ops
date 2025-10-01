import uuid
from typing import Dict, Any
from app.services.hubspot_client import HubSpotClient
from app.services.workflow_engine import workflow_engine
from app.services.redis_service import redis_service

# The actual workflow graphs will be imported here once they are defined.
from app.workflows import company_intake, contact_role_mapping, deal_stage_kickoff, procurement_approval

class WebhookProcessor:
    """
    Handles incoming webhook events, enriches them, and triggers the appropriate workflow.
    """
    def __init__(self):
        self.hubspot_client = HubSpotClient()
        self.redis_service = redis_service
        # The workflow_registry maps event types (sometimes with property specifics) to graphs.
        self.workflow_registry = {
            "company.creation": company_intake.graph,
            "company.propertyChange": company_intake.graph,
            "contact.creation": contact_role_mapping.graph,
            "contact.propertyChange": contact_role_mapping.graph,
            "deal.propertyChange.dealstage": deal_stage_kickoff.graph,
            "deal.propertyChange.amount": procurement_approval.graph,
        }

    async def process_event(self, hubspot_event: Dict[str, Any]):
        """
        Processes a single HubSpot webhook event.
        """
        event_type = hubspot_event.get("subscriptionType")
        object_id = str(hubspot_event.get("objectId"))

        # Idempotency Check for Burst Control.
        # This uses the objectId and a timestamp to prevent running a workflow
        # for the same object state multiple times in quick succession.
        occurred_at = hubspot_event.get("occurredAt")
        idempotency_key = f"workflow_run:{object_id}:{occurred_at}"
        
        # Check if this specific object state change has already been processed
        existing_result = await self.redis_service.get_idempotency_result(idempotency_key)
        if existing_result:
            print(f"Duplicate workflow run for object {object_id} at {occurred_at} ignored.")
            return {"status": "ignored", "reason": "Duplicate run for object state", "cached_result": existing_result}

        graph = None
        # Simple router for deal property changes
        if event_type == "deal.propertyChange":
            property_name = hubspot_event.get("propertyName")
            lookup_key = f"{event_type}.{property_name}"
            graph = self.workflow_registry.get(lookup_key)
        else:
            graph = self.workflow_registry.get(event_type)

        if not graph:
            print(f"No workflow could be resolved for event: {event_type} with property {hubspot_event.get('propertyName')}. Ignored.")
            return {"status": "ignored", "reason": "No workflow resolved"}

        # 1. Enrich data
        print(f"Enriching data for event: {event_type} - objectId: {object_id}")
        enriched_data = await self._enrich_data(event_type, object_id)

        # 2. Prepare workflow input
        # A unique thread_id is created for each run to ensure state isolation
        thread_id = f"{event_type}-{object_id}-{uuid.uuid4()}"
        workflow_input = {
            "hubspot_event": hubspot_event,
            "enriched_data": enriched_data,
        }

        # 3. Invoke the workflow
        print(f"Invoking workflow for thread_id: {thread_id}")
        try:
            final_state = await workflow_engine.invoke_workflow(graph, workflow_input, thread_id)
            print(f"Workflow finished for thread_id: {thread_id}.")
            
            # Cache the result for idempotency
            result = {"thread_id": thread_id, "final_state": final_state}
            await self.redis_service.set_idempotency_key(idempotency_key, result)
            
            return result
        except Exception as e:
            print(f"Error in workflow execution for thread_id {thread_id}: {str(e)}")
            # In a real system, we'd want to implement a retry mechanism or dead-letter queue
            raise

    async def _enrich_data(self, event_type: str, object_id: str) -> Dict[str, Any]:
        """
        Fetches additional object details and associations from HubSpot.
        """
        data = {}
        object_type = event_type.split('.')[0]  # e.g., 'company', 'contact', 'deal'

        if object_type == "company":
            data['details'] = await self.hubspot_client.get_company(object_id)
        elif object_type == "contact":
            data['details'] = await self.hubspot_client.get_contact(object_id)
        elif object_type == "deal":
            data['details'] = await self.hubspot_client.get_deal(object_id)
        
        # Also fetch associated objects (e.g., company for a contact)
        data['associations'] = await self.hubspot_client.get_associations(object_type, object_id)
        
        return data

# Create a singleton instance to be used across the application
webhook_processor = WebhookProcessor()
