# fastAPI_devtool
Just a mock of the fastAPI backend for general proporse\

### Dependencies to install
pip install "uvicorn[standard]" fastapi
pip install python-jose



# ApI_integrated
The repository is for new approach with Python

### to run
# Development
1. uvicorn main:app --reload  


2. http://127.0.0.1:8000/docs   <!-- the Swagger documentation will appear -->



## Project Structure

```
app/
├── main.py                    # FastAPI app initialization
├── config.py                  # Configuration settings
├── api/
│   └── routes/
│       └── health.py          # Health check endpoints
├── core/
│   ├── security.py           # Authentication
│   └── logging.py            # Logging decorator & utilities

```

## Setup


## API Usage

### Authentication

All transcription endpoints require a Bearer token:

```bash
Authorization: Bearer your-secret-token-here
```

### Endpoints

#### 1. Health Check
```bash
curl http://localhost:8000/
```





## Logging

All requests are automatically logged with:
- Endpoint name
- Client IP address
- Masked token (last 4 characters)
- Execution duration
- Success/error status

Logs are written to:
- Console (stdout)
- `app.log` file



## Security Notes

- Store `API_TOKEN` securely
- Use HTTPS in production
- Configure CORS appropriately
- Consider rate limiting for production use

