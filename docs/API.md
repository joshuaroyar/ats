# ATS API Documentation

This document describes the minimal API exposed by the `model/api.py` FastAPI application.

Base URL (development): `http://localhost:8000`

Endpoints
---------

GET /health
- Returns a simple health JSON: `{ "status": "healthy" }`

POST /analyze
- Accepts a multipart/form-data request with a single `file` field containing a PDF resume.
- Returns JSON with ATS scores and feedback.

Request example (curl):

```bash
curl -X POST \
  -F "file=@resume.pdf;type=application/pdf" \
  http://localhost:8000/analyze
```

Response example:

```json
{
  "impact_score": 8,
  "structure_score": 15,
  "clarity_score": 4,
  "skill_score": 22,
  "final_ats_score": 65.5,
  "feedback": "AI feedback lines..."
}
```

Error responses
---------------

- `400 Bad Request` when uploaded file is not a PDF or text extraction fails (image-only PDF).
- `500 Internal Server Error` when analysis pipeline fails; backend logs will contain stack traces.

Notes
-----
- The API loads `jd.txt` from the `model/` folder by default. To evaluate against other JDs, update the server or extend the endpoint to accept a JD text field.
- Ollama (local LLM) is optional; when unavailable, the API still returns scores with a placeholder feedback message.
