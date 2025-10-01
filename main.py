import os
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from dotenv import load_dotenv
import logging
from datetime import datetime
from functools import wraps
from app.api.routes import auth


# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(auth.router)


# Get token from environment
API_TOKEN = os.getenv("API_TOKEN", "test-token-12345")


# ============================================
# AUTHENTICATION DEPENDENCY
# ============================================
async def verify_token(authorization: str = Header(None)) -> str:
    """
    This dependency checks if the Authorization header contains a valid Bearer token.
    FastAPI will automatically call this before executing the endpoint.
    """
    # Check if Authorization header exists
    if not authorization:
        logger.warning("Request without Authorization header")
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing. Use: 'Authorization: Bearer your-token'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Split "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning(f"Invalid authorization format: {authorization}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header. Format: 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = parts[1]
    
    # Verify token matches
    if token != API_TOKEN:
        logger.warning(f"Invalid token attempt: ***{token[-4:] if len(token) > 4 else '****'}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"Token verified: ***{token[-4:] if len(token) > 4 else '****'}")
    return token


# ============================================
# LOGGING DECORATOR
# ============================================
def log_request(func):
    """Decorator to log requests with token info"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Find the Request object in kwargs
        request = kwargs.get('request')
        
        # Get client info
        client_ip = request.client.host if request and request.client else "unknown"
        token = request.headers.get("Authorization", "None").replace("Bearer ", "")
        masked_token = f"***{token[-4:]}" if token and len(token) > 4 else "None"
        
        # Log request start
        logger.info(
            f"📥 REQUEST | Endpoint: {func.__name__} | "
            f"IP: {client_ip} | Token: {masked_token}"
        )
        
        import time
        start = time.time()
        
        try:
            # Execute endpoint
            result = await func(*args, **kwargs)
            duration = time.time() - start
            
            # Log success
            logger.info(
                f"✅ SUCCESS | Endpoint: {func.__name__} | "
                f"Duration: {duration:.2f}s | IP: {client_ip}"
            )
            return result
            
        except Exception as e:
            duration = time.time() - start
            # Log error
            logger.error(
                f"❌ ERROR | Endpoint: {func.__name__} | "
                f"Duration: {duration:.2f}s | Error: {str(e)}"
            )
            raise
    
    return wrapper


# ============================================
# ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """
    PUBLIC endpoint - No authentication required
    Use this to test if the API is running
    """
    return {
        "message": "API is running!",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/public")
async def public_endpoint():
    """
    PUBLIC endpoint - No authentication required
    """
    return {
        "message": "This is a public endpoint",
        "auth_required": False
    }


# @app.get("/protected")
# @log_request
# async def protected_endpoint(
#     request: Request,
#     token: str = Depends(verify_token)
# ):
#     """
#     PROTECTED endpoint - Requires valid Bearer token
    
#     How it works:
#     1. FastAPI sees 'token: str = Depends(verify_token)'
#     2. Before running this function, it calls verify_token()
#     3. If verify_token() raises HTTPException, this function never runs
#     4. If verify_token() succeeds, this function runs and gets the token
#     """
#     return {
#         "message": "You have accessed a protected endpoint!",
#         "auth_required": True,
#         "token_valid": True,
#         "masked_token": f"***{token[-4:]}" if len(token) > 4 else "****"
#     }

@app.get("/protected")
@log_request
async def protected_endpoint(request: Request, token_data: dict = Depends(verify_token)):
    return {
        "message": "JWT verified!",
        "user": token_data.get("sub"),
        "token_valid": True
    }


@app.post("/protected/data")
@log_request
async def protected_post_endpoint(
    request: Request,
    data: dict,
    token: str = Depends(verify_token)
):
    """
    PROTECTED POST endpoint - Requires valid Bearer token
    Accepts JSON data
    """
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
    token: str = Depends(verify_token)
):
    """
    PROTECTED admin endpoint - Requires valid Bearer token
    You could add additional role-based checks here
    """
    return {
        "message": "Welcome to admin area",
        "auth_required": True,
        "access_level": "admin"
    }


# ============================================
# INFO ENDPOINT TO SEE YOUR TOKEN
# ============================================
@app.get("/token-info")
async def token_info():
    """
    PUBLIC endpoint that shows you what token is configured
    (Only for development/testing - REMOVE in production!)
    """
    return {
        "message": "Token configuration info",
        "token": API_TOKEN,
        "warning": "Remove this endpoint in production!",
        "usage": "Add this header to your requests: Authorization: Bearer " + API_TOKEN
    }


if __name__ == "__main__":
    import uvicorn
    print(f"\n🔑 Your API Token: {API_TOKEN}")
    print(f"📝 Add this header to Postman: Authorization: Bearer {API_TOKEN}\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)