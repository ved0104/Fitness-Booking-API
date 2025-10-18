import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self, request: Request, call_next):
        # Log incoming request
        start_time = time.time()
        logger.info(f"→ Incoming request: {request.method} {request.url.path}")
        
        # Process request
        try:
            response: Response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log successful response
            logger.info(
                f"← Completed request: {request.method} {request.url.path} "
                f"- Status: {response.status_code} "
                f"- Duration: {process_time:.3f}s"
            )
            
            # Custom header with processing time
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"✗ Request failed: {request.method} {request.url.path} "
                f"- Error: {str(e)} "
                f"- Duration: {process_time:.3f}s",
                exc_info=True
            )
            raise
