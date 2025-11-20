from fastapi import APIRouter, Request, HTTPException, Depends, Header
from typing import Optional
import httpx

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "api-gateway"}

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(path: str, request: Request):
    """
    Catch-all route to proxy requests to downstream services.
    For now, it just echoes the request.
    """
    # Placeholder for Rate Limiting and Caching logic (Step 8)
    
    return {
        "message": "Proxy request received",
        "path": path,
        "method": request.method,
        "headers": dict(request.headers)
    }
