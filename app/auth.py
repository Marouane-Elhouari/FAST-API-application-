import os
from fastapi import Header, HTTPException, status

API_KEY = os.getenv("GNN_API_KEY", "Marwan elhaouari")


async def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
    return True
