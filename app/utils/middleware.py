import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api_performance.log")
    ]
)
performance_logger = logging.getLogger("api_performance")

class PerformanceMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, log_threshold_ms: int = 500):
        super().__init__(app)
        self.log_threshold_ms = log_threshold_ms
        
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            # Add processing time header to response
            response.headers["X-Process-Time-MS"] = str(int(process_time))
            
            # Log endpoint performance
            log_message = f"{request.method} {request.url.path} - {int(process_time)}ms"
            
            # Log all requests, but use different log levels based on response time
            if process_time > self.log_threshold_ms:
                performance_logger.warning(f"SLOW API CALL: {log_message}")
            else:
                performance_logger.info(log_message)
                
            # Log potential timeout risk
            if process_time > 25000:  # If approaching 30s timeout limit
                performance_logger.error(f"TIMEOUT RISK: {log_message}")
                
            return response
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            performance_logger.error(f"EXCEPTION: {request.method} {request.url.path} - {int(process_time)}ms - {str(e)}")
            raise