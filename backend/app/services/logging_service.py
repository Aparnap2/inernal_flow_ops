import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create router for log endpoints
router = APIRouter(prefix="/logs", tags=["Logging"])

class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    context: Optional[Dict[str, Any]] = None
    stack: Optional[str] = None
    component: Optional[str] = None
    userId: Optional[str] = None

@router.post("/")
async def log_entry(entry: LogEntry):
    """
    Receive log entries from frontend and store them
    """
    try:
        # Log the entry on the backend
        log_method = getattr(logger, entry.level.lower(), logger.info)
        log_message = f"[FRONTEND] {entry.component or 'Unknown'}: {entry.message}"
        if entry.context:
            log_message += f" | Context: {json.dumps(entry.context)}"
        if entry.userId:
            log_message += f" | User: {entry.userId}"
            
        log_method(log_message)
        
        # If it's an error, also log the stack trace
        if entry.level == "error" and entry.stack:
            logger.error(f"Stack trace: {entry.stack}")
            
        return {"status": "logged"}
    except Exception as e:
        logger.error(f"Failed to process frontend log entry: {e}")
        raise HTTPException(status_code=500, detail="Failed to process log entry")

class BackendLogger:
    """
    Enhanced backend logging service with structured logging and monitoring
    """
    
    def __init__(self):
        self.logger = logger
    
    def log_with_context(self, level: str, message: str, context: Dict[str, Any] = None, 
                         component: str = None, user_id: str = None):
        """
        Log a message with structured context
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "component": component,
            "user_id": user_id,
            "context": context or {}
        }
        
        # Output to console
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        context_str = json.dumps(context) if context else "{}"
        user_str = f" [User: {user_id}]" if user_id else ""
        component_str = f" [{component}]" if component else ""
        log_method(f"{component_str}{message}{user_str} | Context: {context_str}")
        
        # In production, you might send this to a monitoring service like Sentry, Datadog, etc.
        # self.send_to_monitoring_service(log_entry)
        
        return log_entry
    
    def info(self, message: str, context: Dict[str, Any] = None, component: str = None, user_id: str = None):
        return self.log_with_context("info", message, context, component, user_id)
        
    def warn(self, message: str, context: Dict[str, Any] = None, component: str = None, user_id: str = None):
        return self.log_with_context("warn", message, context, component, user_id)
        
    def error(self, message: str, context: Dict[str, Any] = None, component: str = None, user_id: str = None, 
              exception: Exception = None):
        # Include exception details if provided
        if exception:
            if context is None:
                context = {}
            context["exception_type"] = type(exception).__name__
            context["exception_message"] = str(exception)
            if hasattr(exception, '__traceback__'):
                import traceback
                context["stack_trace"] = traceback.format_tb(exception.__traceback__)
                
        return self.log_with_context("error", message, context, component, user_id)
        
    def debug(self, message: str, context: Dict[str, Any] = None, component: str = None, user_id: str = None):
        return self.log_with_context("debug", message, context, component, user_id)
    
    def audit_log(self, action: str, user_id: str, resource_type: str, resource_id: str, 
                  details: Dict[str, Any] = None):
        """
        Log security audit events
        """
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {}
        }
        
        self.logger.info(
            f"AUDIT: {action} on {resource_type}/{resource_id} by user {user_id}", 
            extra={"audit": audit_entry}
        )
        
        return audit_entry

# Global instance
backend_logger = BackendLogger()