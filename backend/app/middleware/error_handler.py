import traceback
import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.services.logging_service import backend_logger

logger = logging.getLogger(__name__)

async def error_handling_middleware(request: Request, call_next):
    """
    Global error handling middleware for the FastAPI application
    """
    try:
        response = await call_next(request)
        return response
    except HTTPException as e:
        # Log HTTP exceptions
        backend_logger.error(
            f"HTTP Exception: {e.detail}",
            context={
                "status_code": e.status_code,
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client": request.client.host if request.client else "unknown"
            },
            component="HTTPMiddleware"
        )
        raise e
    except StarletteHTTPException as e:
        # Log Starlette HTTP exceptions
        backend_logger.error(
            f"Starlette HTTP Exception: {e.detail}",
            context={
                "status_code": e.status_code,
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client": request.client.host if request.client else "unknown"
            },
            component="HTTPMiddleware"
        )
        raise e
    except Exception as e:
        # Log unexpected exceptions
        backend_logger.error(
            f"Unexpected server error: {str(e)}",
            context={
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client": request.client.host if request.client else "unknown",
                "traceback": traceback.format_exc()
            },
            component="HTTPMiddleware",
            exception=e
        )
        
        # Return a generic error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "error_code": "INTERNAL_ERROR"
            }
        )

class ErrorHandler:
    """
    Centralized error handling service
    """
    
    @staticmethod
    def handle_validation_error(errors: list) -> dict:
        """
        Handle Pydantic validation errors
        """
        error_messages = []
        for error in errors:
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_messages.append(f"{field}: {message}")
            
        return {
            "detail": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "errors": error_messages
        }
    
    @staticmethod
    def handle_business_logic_error(error: Exception) -> dict:
        """
        Handle business logic errors
        """
        return {
            "detail": str(error),
            "error_code": "BUSINESS_LOGIC_ERROR"
        }
    
    @staticmethod
    def handle_external_service_error(service: str, error: Exception) -> dict:
        """
        Handle errors from external services
        """
        return {
            "detail": f"External service error: {service}",
            "error_code": "EXTERNAL_SERVICE_ERROR",
            "service": service
        }
    
    @staticmethod
    def handle_security_error(action: str, user_id: str = None, resource: str = None) -> dict:
        """
        Handle security-related errors
        """
        # Log security audit event
        backend_logger.audit_log(
            action=f"SECURITY_VIOLATION_{action}",
            user_id=user_id or "unknown",
            resource_type="system",
            resource_id=resource or "unknown",
            details={"violation_type": action}
        )
        
        return {
            "detail": "Forbidden",
            "error_code": "FORBIDDEN"
        }

# Custom exception classes
class BusinessLogicError(Exception):
    """Custom exception for business logic errors"""
    pass

class ExternalServiceError(Exception):
    """Custom exception for external service errors"""
    def __init__(self, service: str, message: str, original_error: Exception = None):
        super().__init__(message)
        self.service = service
        self.original_error = original_error

class SecurityError(Exception):
    """Custom exception for security violations"""
    def __init__(self, action: str, message: str):
        super().__init__(message)
        self.action = action