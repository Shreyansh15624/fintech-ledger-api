import json
import os
import redis.asyncio as redis
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

class IdempotencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. THE SHIELD: The SHIELD only needs to protect the exact fund transfer endpoint
        if request.url.path == "/api/v1/records/transfer" and request.method == "POST":
            # 2. Extracting the unique key from the incoming request headers
            idem_key = request.headers.get("Idempotency-Key")

            # Strict Enforcement: If the url doesn't provide a key, we reject the transfer!
            if not idem_key:
                return JSONResponse(
                    status_code=400,
                    detail="Idempotency-Key header key is strictly required for financial transfers!",
                )
            
            # 3. Establish the connection to a local Redis container
            redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
            redis_client = redis.from_url(redis_url)

            try:
                # 4. CACHE HIT: Cheking if the exact key has been seen before!
                cached_response = await redis_client.get(idem_key)
                if cached_response:
                    # If yes, we completely bypass the router and database, returning the memory state
                    return JSONResponse(status_code=200, content=json.loads(cached_response))

                # 5. CACHE MISS: This is a new transaction. Let it pass to the FastAPI Router
                response = await call_next(request)

                # 6. THE STORAGE: If the router successfully processed the transaction -> 200 OK
                # We will hold a success record in Redis for exactly 24 hours (86400 seconds)
                if response.status_code == 200:
                    success_payload = {
                        "status": "success",
                        "message": "Transaction successfully processed. (Cached via Idempotency Middleware)"
                    }
                    await redis_client.setex(idem_key, 86400, json.dumps(success_payload))

                return response
            finally:
                # 7. Cleaning up the connection to prevent memory leaks
                await redis_client.aclose()
        
        # If it is any other route (like GET /reocrds or POST /login), we just let it pass normally
        return await call_next(request)