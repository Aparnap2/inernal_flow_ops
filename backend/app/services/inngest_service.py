from typing import Dict, Any, Optional
import asyncio
import json
from datetime import datetime
from langgraph.checkpoint.redis import RedisSaver
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage
from .workflow_engine import workflow_engine
from ..config import settings
import inngest


class InngestService:
    """
    Service to integrate with Inngest for durable execution and observability
    """
    def __init__(self):
        self.redis_checkpointer = workflow_engine.checkpointer
        # Initialize Inngest client
        self.inngest_client = inngest.Inngest(
            app_id="hubspot-orchestrator",
            event_key=settings.INNGEST_EVENT_KEY if hasattr(settings, 'INNGEST_EVENT_KEY') else None,
            signing_key=settings.INNGEST_SIGNING_KEY if hasattr(settings, 'INNGEST_SIGNING_KEY') else None,
        )
        
    async def send_event(self, name: str, data: Dict[str, Any], user: Optional[Dict[str, Any]] = None):
        """
        Send an event to Inngest for tracking workflow execution
        """
        try:
            # Send event to Inngest
            event_id = await self.inngest_client.send(name, data=data, user=user)
            return {"status": "sent", "event_id": event_id}
        except Exception as e:
            print(f"Failed to send Inngest event {name}: {e}")
            # Fallback to console logging
            event = {
                "name": name,
                "data": data,
                "user": user,
                "timestamp": datetime.utcnow().isoformat(),
                "env": settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else 'development'
            }
            print(f"Inngest Event (fallback): {json.dumps(event, indent=2)}")
            return {"status": "sent", "event_id": f"event_{datetime.utcnow().timestamp()}"}
    
    def create_workflow_function(self, name: str, workflow_graph: StateGraph, 
                                  trigger_event: str, concurrency: int = 10):
        """
        Create an Inngest function that triggers workflow execution
        """
        # Define the Inngest function using the proper decorator
        @self.inngest_client.step(name=name)
        async def inngest_function(
            ctx: inngest.Context,
            step: inngest.Step,
        ) -> dict:
            """
            Inngest function that orchestrates LangGraph workflow execution
            """
            # Extract workflow input data from event
            event_data = ctx.event.data
            envelope = event_data.get("event_data", {})
            
            # Extract critical information from envelope
            correlation_id = envelope.get("meta", {}).get("correlationId", f"corr_{datetime.utcnow().timestamp()}")
            run_id = f"run_{correlation_id}_{datetime.utcnow().timestamp()}"
            
            # Prepare LangGraph workflow input from the envelope
            workflow_input = {
                "hubspot_event": envelope.get("payload", {}),
                "enriched_data": {},  # This would be populated by the event processor
                "correlation_id": correlation_id,
                "workflow_name": name
            }
            
            # Configure the graph with Redis checkpointer
            config = {
                "configurable": {
                    "thread_id": run_id,
                    "checkpoint_ns": name
                }
            }
            
            # Execute the workflow
            print(f"Starting workflow execution: {name} with run_id: {run_id} and correlation_id: {correlation_id}")
            
            # Send progress event
            await self.send_event("workflow/execution.started", {
                "run_id": run_id,
                "correlation_id": correlation_id,
                "workflow_name": name,
                "input_data": {
                    "object_type": envelope.get("meta", {}).get("objectType"),
                    "object_id": envelope.get("meta", {}).get("objectId"),
                    "event_type": envelope.get("meta", {}).get("eventType")
                }
            })
            
            try:
                # Execute the workflow graph with astream to capture events
                workflow_events = []
                async for event_output in workflow_graph.astream(workflow_input, config):
                    print(f"Workflow event: {event_output}")
                    workflow_events.append(event_output)
                    
                    # Send intermediate events for observability
                    await self.send_event("workflow/execution.progress", {
                        "run_id": run_id,
                        "correlation_id": correlation_id,
                        "workflow_name": name,
                        "event_output": event_output
                    })
                
                # Get final state
                final_state = await workflow_graph.aget_state(config)
                
                # Send completion event
                await self.send_event("workflow/execution.completed", {
                    "run_id": run_id,
                    "correlation_id": correlation_id,
                    "workflow_name": name,
                    "final_state": final_state.values if final_state else None,
                    "completed_at": datetime.utcnow().isoformat()
                })
                
                return {
                    "status": "completed",
                    "run_id": run_id,
                    "correlation_id": correlation_id,
                    "final_state": final_state.values if final_state else None
                }
                
            except Exception as e:
                # Send error event
                await self.send_event("workflow/execution.failed", {
                    "run_id": run_id,
                    "correlation_id": correlation_id,
                    "workflow_name": name,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "failed_at": datetime.utcnow().isoformat()
                })
                
                raise e
        
        # Register the function to listen for the trigger event
        self.inngest_client.on(trigger_event, inngest_function)
        
        return inngest_function
    
    async def process_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a webhook event and trigger appropriate Inngest workflows
        """
        # Extract event metadata from envelope structure
        event_type = event_data.get("meta", {}).get("eventType", "")
        object_type = event_data.get("meta", {}).get("objectType", "")
        object_id = event_data.get("meta", {}).get("objectId", "")
        correlation_id = event_data.get("meta", {}).get("correlationId", "")
        
        # Send initial event to Inngest
        await self.send_event("hubspot/webhook.received", {
            "event_type": event_type,
            "object_type": object_type,
            "object_id": object_id,
            "correlation_id": correlation_id,
            "payload": event_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Determine which workflow to trigger based on event type
        workflow_name = self._get_workflow_for_event(event_type, object_type)
        
        if not workflow_name:
            return {
                "status": "ignored", 
                "reason": f"No workflow configured for event type: {event_type}, object type: {object_type}"
            }
        
        # Send event to trigger workflow via Inngest
        await self.send_event(f"workflow/{workflow_name}.triggered", {
            "workflow_name": workflow_name,
            "event_data": event_data,
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "status": "triggered",
            "workflow_name": workflow_name,
            "correlation_id": correlation_id
        }
    
    def _get_workflow_for_event(self, event_type: str, object_type: str) -> Optional[str]:
        """
        Map HubSpot event types to appropriate workflows based on development plan
        """
        event_mapping = {
            # Company workflows
            ("company.creation", "company"): "company-intake",
            ("company.propertyChange", "company"): "company-intake", 
            ("company.associationChange", "company"): "company-intake",
            
            # Contact workflows
            ("contact.creation", "contact"): "contact-role-mapping",
            ("contact.propertyChange", "contact"): "contact-role-mapping",
            ("contact.associationChange", "contact"): "contact-role-mapping",
            
            # Deal workflows
            ("deal.propertyChange.dealstage", "deal"): "deal-stage-kickoff",
            ("deal.propertyChange.amount", "deal"): "procurement-approval",
            ("deal.creation", "deal"): "deal-stage-kickoff",  # New deals might need kickoff workflows
        }
        
        return event_mapping.get((event_type, object_type))


# Global instance
inngest_service = InngestService()

# Expose the Inngest client for route registration
inngest_client = inngest_service.inngest_client