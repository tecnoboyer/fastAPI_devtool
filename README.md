# fastAPI_devtool
Just a mock of the fastAPI backend for general proporse
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

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install ffmpeg** (required by pydub):
- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt-get install ffmpeg`

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your values
```

4. **Run the application:**
```bash

```

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

#### 2. Transcribe Small Audio (<25MB)
```bash
curl -X POST "http://localhost:8000/transcribe/" \
  -H "Authorization: Bearer your-secret-token-here" \
  -F "file=@audio.mp3"
```

#### 3. Transcribe Large Audio (>25MB)
```bash
curl -X POST "http://localhost:8000/transcribe/large" \
  -H "Authorization: Bearer your-secret-token-here" \
  -F "file=@large_audio.mp3"
```

### Response Example

```json
{
  "chunks_processed": 3,
  "output_file": "transcription_20250930_143052.txt",
  "transcription": "Full transcription text here...",
  "file_size_bytes": 52428800,
  "audio_duration_ms": 3600000
}
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

Example log entry:
```
2025-09-30 14:30:52 - INFO - REQUEST | Endpoint: transcribe_large_audio | IP: 127.0.0.1 | Token: ***k3n1
2025-09-30 14:31:15 - INFO - SUCCESS | Endpoint: transcribe_large_audio | Duration: 23.45s | IP: 127.0.0.1
```

## Security Notes

- Store `API_TOKEN` securely
- Use HTTPS in production
- Configure CORS appropriately
- Consider rate limiting for production use

## Output Files

Transcriptions are saved to the `transcriptions/` directory with timestamped filenames:
```
transcriptions/
├── transcription_20250930_143052.txt
├── transcription_20250930_150123.txt
└── ...
```
