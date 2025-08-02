from fastapi import Header, HTTPException
from .config import HACKRX_BEARER_TOKEN # Use relative import for config

async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer ") or authorization.split(" ")[1] != HACKRX_BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing Bearer token")
    return True