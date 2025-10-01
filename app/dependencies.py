# app/dependencies.py
from fastapi import Header, HTTPException
from app.core.security import decode_access_token

async def verify_token(authorization: str = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = authorization.split(" ")[1]
    return decode_access_token(token)