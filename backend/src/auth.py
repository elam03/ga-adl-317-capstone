import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

_API_KEY_NAME = "X-API-Key"
_api_key_header = APIKeyHeader(name=_API_KEY_NAME, auto_error=False)
_API_SECRET_KEY = os.getenv("API_SECRET_KEY", "")

if not _API_SECRET_KEY:
    raise RuntimeError("API_SECRET_KEY env var is not set. Add it to backend/.env")

def verify_api_key(api_key: str = Security(_api_key_header)) -> str:
    """Dependency that validates the X-API-Key header."""
    if not api_key or api_key != _API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key",
        )
    return api_key
