from typing import Any, Dict, Optional, Union
import json
import asyncio
import redis.asyncio as redis
from app.config import settings
from datetime import datetime, timedelta


class RedisService:
    """
    Service for Redis operations including caching, session management, 
    and LangGraph checkpointing as specified in the development plan.
    """
    
    def __init__(self):
        self.client = None
        self.redis_url = settings.REDIS_URL
    
    async def connect(self):
        """Connect to Redis."""
        self.client = redis.from_url(self.redis_url, decode_responses=True)
        try:
            await self.client.ping()
            print("Connected to Redis successfully")
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
    
    async def ping(self) -> bool:
        """Check if Redis is accessible."""
        try:
            await self.client.ping()
            return True
        except:
            return False
    
    # Caching utilities
    async def cache_set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set a value in Redis cache with TTL (in seconds)."""
        try:
            # Convert value to JSON string if it's not already a string
            value_str = json.dumps(value) if not isinstance(value, str) else value
            result = await self.client.setex(key, ttl, value_str)
            return result == "OK"
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """Get a value from Redis cache."""
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            # Try to decode as JSON, return as-is if it fails
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            print(f"Error getting cache: {e}")
            return None
    
    async def cache_delete(self, key: str) -> bool:
        """Delete a key from Redis cache."""
        try:
            result = await self.client.delete(key)
            return result > 0
        except Exception as e:
            print(f"Error deleting cache: {e}")
            return False
    
    # Session management utilities
    async def set_session(self, session_id: str, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Set session data in Redis."""
        try:
            key = f"session:{session_id}"
            return await self.cache_set(key, data, ttl)
        except Exception as e:
            print(f"Error setting session: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from Redis."""
        try:
            key = f"session:{session_id}"
            return await self.cache_get(key)
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session data from Redis."""
        try:
            key = f"session:{session_id}"
            return await self.cache_delete(key)
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    # Rate limiting utilities
    async def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """
        Check if a rate limit is exceeded.
        Returns True if the request is within the rate limit, False otherwise.
        """
        try:
            current = await self.client.incr(key)
            if current == 1:
                await self.client.expire(key, window)
            
            return current <= limit
        except Exception as e:
            print(f"Error checking rate limit: {e}")
            # If Redis is down, allow the request through
            return True
    
    # Idempotency utilities for preventing duplicate processing
    async def set_idempotency_key(self, key: str, result: Any, ttl: int = 3600) -> bool:
        """Set an idempotency key to prevent duplicate processing."""
        try:
            idempotency_key = f"idempotent:{key}"
            return await self.cache_set(idempotency_key, result, ttl)
        except Exception as e:
            print(f"Error setting idempotency key: {e}")
            return False
    
    async def get_idempotency_result(self, key: str) -> Optional[Any]:
        """Get the result of a previous operation using idempotency key."""
        try:
            idempotency_key = f"idempotent:{key}"
            return await self.cache_get(idempotency_key)
        except Exception as e:
            print(f"Error getting idempotency result: {e}")
            return None
    
    # LangGraph checkpoint utilities
    async def save_checkpoint(self, thread_id: str, checkpoint_id: str, data: Any) -> bool:
        """Save a LangGraph checkpoint."""
        try:
            key = f"checkpoint:{thread_id}:{checkpoint_id}"
            return await self.cache_set(key, data, 86400)  # Keep checkpoints for 24 hours
        except Exception as e:
            print(f"Error saving checkpoint: {e}")
            return False
    
    async def get_checkpoint(self, thread_id: str, checkpoint_id: str) -> Optional[Any]:
        """Get a LangGraph checkpoint."""
        try:
            key = f"checkpoint:{thread_id}:{checkpoint_id}"
            return await self.cache_get(key)
        except Exception as e:
            print(f"Error getting checkpoint: {e}")
            return None
    
    async def get_all_checkpoints(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get all checkpoints for a thread."""
        try:
            # Use Redis keys command to find all checkpoints for this thread
            pattern = f"checkpoint:{thread_id}:*"
            keys = await self.client.keys(pattern)
            
            if not keys:
                return None
            
            # Get all checkpoint values
            checkpoints = {}
            for key in keys:
                # Extract checkpoint_id from the key
                checkpoint_id = key.split(":")[-1]
                checkpoint_data = await self.cache_get(key)
                if checkpoint_data:
                    checkpoints[checkpoint_id] = checkpoint_data
            
            return checkpoints
        except Exception as e:
            print(f"Error getting all checkpoints: {e}")
            return None
    
    async def delete_checkpoint(self, thread_id: str, checkpoint_id: str) -> bool:
        """Delete a specific checkpoint."""
        try:
            key = f"checkpoint:{thread_id}:{checkpoint_id}"
            return await self.cache_delete(key)
        except Exception as e:
            print(f"Error deleting checkpoint: {e}")
            return False
    
    # Workflow run utilities
    async def save_workflow_run_state(self, run_id: str, state: Any, ttl: int = 86400) -> bool:
        """Save the current state of a workflow run."""
        try:
            key = f"workflow_run:{run_id}:state"
            return await self.cache_set(key, state, ttl)
        except Exception as e:
            print(f"Error saving workflow run state: {e}")
            return False
    
    async def get_workflow_run_state(self, run_id: str) -> Optional[Any]:
        """Get the current state of a workflow run."""
        try:
            key = f"workflow_run:{run_id}:state"
            return await self.cache_get(key)
        except Exception as e:
            print(f"Error getting workflow run state: {e}")
            return None
    
    # Queue utilities (for the hubspot_event_queue)
    async def queue_push(self, queue_name: str, item: Any) -> int:
        """Push an item to a Redis list (queue)."""
        try:
            item_str = json.dumps(item) if not isinstance(item, str) else item
            length = await self.client.lpush(queue_name, item_str)
            return length
        except Exception as e:
            print(f"Error pushing to queue: {e}")
            return 0
    
    async def queue_pop(self, queue_name: str) -> Optional[Any]:
        """Pop an item from a Redis list (queue)."""
        try:
            item = await self.client.rpop(queue_name)
            if item is None:
                return None
            # Try to decode as JSON, return as-is if it fails
            try:
                return json.loads(item)
            except json.JSONDecodeError:
                return item
        except Exception as e:
            print(f"Error popping from queue: {e}")
            return None
    
    async def queue_size(self, queue_name: str) -> int:
        """Get the size of a Redis list (queue)."""
        try:
            size = await self.client.llen(queue_name)
            return size
        except Exception as e:
            print(f"Error getting queue size: {e}")
            return 0


# Global instance
redis_service = RedisService()