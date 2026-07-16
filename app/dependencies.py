from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from app.config import settings

api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(x_api_key: str = Security(api_key_scheme)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key
