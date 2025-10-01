from langgraph.checkpoint.redis import RedisSaver
from app.config import settings
from .redis_service import redis_service

class WorkflowEngine:
    """
    Provides the core components for running stateful LangGraph workflows.
    It initializes a Redis checkpointer to persist the state of graphs.
    """
    def __init__(self):
        # Connect to Redis service
        self.redis_service = redis_service
        self.checkpointer = None

    async def initialize(self):
        """Initialize the workflow engine."""
        await self.redis_service.connect()
        # Initialize Redis checkpointer for LangGraph after Redis connection is established
        self.checkpointer = RedisSaver(redis_client=self.redis_service.client)

    def get_checkpointer(self):
        """
        Returns the Redis checkpointer instance.
        """
        return self.checkpointer

    async def invoke_workflow(self, graph, workflow_input: dict, thread_id: str):
        """
        Invokes a compiled LangGraph workflow and streams events.

        Args:
            graph: The compiled LangGraph runnable.
            workflow_input: The initial state or input for the workflow.
            thread_id: A unique identifier for the workflow run.
        """
        config = {"configurable": {"thread_id": thread_id}}
        final_state = None
        
        print(f"--- Invoking Workflow for Thread ID: {thread_id} ---")
        async for event in graph.astream(workflow_input, config):
            # The event stream can be used for real-time logging or updates
            print("--- Workflow Event ---")
            print(event)
            print("--- End Event ---")
            # The final state is captured from the stream
            if event.get("event") == "on_chain_end":
                final_state = event.get("data", {}).get("output")

        # If the stream didn't provide a final state, get it directly
        if final_state is None:
            final_state = await graph.aget_state(config)

        print(f"--- Workflow Finished for Thread ID: {thread_id} ---")
        return final_state

# Create a singleton instance to be used across the application
workflow_engine = WorkflowEngine()
