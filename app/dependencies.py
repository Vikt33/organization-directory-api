from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os

API_KEY = os.getenv("API_KEY", "default-secret-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return api_key