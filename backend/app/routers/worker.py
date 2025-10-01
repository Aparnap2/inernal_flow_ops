import json
from fastapi import APIRouter, BackgroundTasks
from app.services.workflow_engine import workflow_engine
from app.services.webhook_processor import webhook_processor

router = APIRouter()

async def _process_event_task(event: dict):
    """Helper function to wrap the processing of a single event."""
    try:
        print(f"Worker processing event: {event.get('eventId')}")
        await webhook_processor.process_event(event)
    except Exception as e:
        print(f"Worker failed to process event: {event.get('eventId')}. Error: {e}")
        # In a real system, this would trigger a dead-letter or retry mechanism.

@router.post(
    "/process-queue",
    tags=["Worker"],
    summary="Simulate a worker processing all events from the queue",
)
async def process_queue(background_tasks: BackgroundTasks):
    """
    This endpoint simulates a background worker draining the Redis queue.
    It uses BackgroundTasks to process events without blocking the response.
    """
    redis_service = workflow_engine.redis_service
    
    count = 0
    # Process all events currently in the queue
    while await redis_service.queue_size("hubspot_event_queue") > 0:
        raw_event = await redis_service.queue_pop("hubspot_event_queue")
        if raw_event:
            try:
                event = json.loads(raw_event) if isinstance(raw_event, str) else raw_event
                # Add the processing to background tasks to avoid blocking
                background_tasks.add_task(_process_event_task, event)
                count += 1
            except json.JSONDecodeError:
                print(f"Error decoding event from queue: {raw_event}")
            except Exception as e:
                print(f"Error initiating task for event from queue: {e}")

    if count == 0:
        return {"status": "ok", "message": "Queue is empty."}
    
    return {"status": "ok", "message": f"Started processing {count} events from the queue in the background."}
