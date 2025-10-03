import os
import logging
from datetime import datetime
from functools import wraps

from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.routes import auth

# ============================================
# Load environment variables
# ============================================
load_dotenv()

# ============================================
# Logging Configuration
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ============================================
# FastAPI App Initialization
# ============================================
app = FastAPI(title="Linkaxom API", version="1.0.0")

# Include routes (e.g., /login)
app.include_router(auth.router)

# ============================================
# CORS Configuration (🔥 REQUIRED for frontend)
# ============================================
origins = [
    "http://localhost:8050",  # your frontend
    "http://127.0.0.1:8050",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # or ["*"] during dev
    allow_credentials=True,
    allow_methods=["*"],         # allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],         # allow Content-Type, Authorization, etc.
)

# ============================================
# Token Verification
# ============================================
API_TOKEN = os.getenv("API_TOKEN", "test-token-12345")

async def verify_token(authorization: str = Header(None)) -> str:
    """Validates Bearer token in Authorization header."""
    if not authorization:
        logger.warning("❌ Missing Authorization header")
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning(f"❌ Invalid header format: {authorization}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Use 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]
    if token != API_TOKEN:
        logger.warning(f"❌ Invalid token attempt: ***{token[-4:]}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"✅ Token verified: ***{token[-4:]}")
    return token

# ============================================
# Logging Decorator
# ============================================
def log_request(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        client_ip = request.client.host if request and request.client else "unknown"
        token = request.headers.get("Authorization", "None").replace("Bearer ", "")
        masked_token = f"***{token[-4:]}" if token and len(token) > 4 else "None"

        logger.info(f"📥 REQUEST | {func.__name__} | IP: {client_ip} | Token: {masked_token}")

        import time
        start = time.time()

        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start
            logger.info(f"✅ SUCCESS | {func.__name__} | {duration:.2f}s | IP: {client_ip}")
            return result
        except Exception as e:
            duration = time.time() - start
            logger.error(f"❌ ERROR | {func.__name__} | {duration:.2f}s | {e}")
            raise

    return wrapper

# ============================================
# Public Endpoints
# ============================================
@app.get("/")
async def root():
    return {
        "message": "API is running!",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/public")
async def public_endpoint():
    return {
        "message": "This is a public endpoint",
        "auth_required": False,
    }

@app.get("/token-info")
async def token_info():
    return {
        "token": API_TOKEN,
        "usage": "Use this header: Authorization: Bearer " + API_TOKEN,
        "warning": "Remove this endpoint in production!",
    }

# ============================================
# Protected Endpoints
# ============================================
@app.get("/protected")
@log_request
async def protected_endpoint(request: Request, token: str = Depends(verify_token)):
    return {
        "message": "JWT verified!",
        "token_valid": True,
        "masked_token": f"***{token[-4:]}"
    }

@app.post("/protected/data")
@log_request
async def protected_post_endpoint(
    request: Request,
    data: dict,
    token: str = Depends(verify_token),
):
    return {
        "message": "Data received successfully",
        "received_data": data,
        "auth_required": True,
        "masked_token": f"***{token[-4:]}"
    }

@app.get("/admin")
@log_request
async def admin_endpoint(
    request: Request,
    token: str = Depends(verify_token),
):
    return {
        "message": "Welcome to admin area",
        "auth_required": True,
        "access_level": "admin",
    }

# ============================================
# Run the server
# ============================================
if __name__ == "__main__":
    import uvicorn
    print(f"\n🔑 Your API Token: {API_TOKEN}")
    print("📝 Add this header to Postman: Authorization: Bearer " + API_TOKEN + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
