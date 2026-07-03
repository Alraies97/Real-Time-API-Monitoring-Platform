from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
from .redis_client import redis_client

class RealTimeMonitorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
      if request.url.path.startswith("/ws"):
        return await call_next(request)
      
      await redis_client.incr("active_connections")

      start_time = time.perf_counter()
      
      try:
        response = await call_next(request)
        return response

      finally:
        process_time = (time.perf_counter() - start_time) * 1000

        await redis_client.decr("active_connections")
        
        await redis_client.incr("total_requests")

        await redis_client.lpush("request_times", process_time)
        await redis_client.ltrim("request_times", 0, 99)

        