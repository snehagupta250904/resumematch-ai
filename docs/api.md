# API Reference

Base URL (production): `https://resumematch-ai-tai8.onrender.com`

## `GET /health`

Liveness check.

**Response `200`**
```json
{ "status": "ok" }
```

## `POST /analyze`

Analyzes a resume against a job description. Send as `multipart/form-data`.

**Form fields**

| Field | Type | Required | Notes |
|---|---|---|---|
| `job_description` | text | Yes | Minimum 50 characters |
| `resume_text` | text | One of `resume_text` / `resume_file` required | Minimum 40 characters |
| `resume_file` | file | One of `resume_text` / `resume_file` required | PDF or DOCX, max 5MB |

**Response `200`**
```json
{
  "overall_score": 88,
  "sub_scores": {
    "skills": 90,
    "keywords": 85,
    "experience": 80,
    "education": 95
  },
  "missing_keywords": ["debugging", "database management"],
  "missing_skills": ["Machine Learning", "Streamlit", "SQLite"],
  "strengths": ["..."],
  "weaknesses": ["..."],
  "suggestions": ["..."]
}
```

**Error responses**

| Status | `error` value | Meaning |
|---|---|---|
| 400 | `missing_fields` | Required text missing or too short |
| 413 | `file_too_large` | Uploaded file exceeds 5MB |
| 415 | `unsupported_file_type` | File is not `.pdf` or `.docx` |
| 422 | `extraction_failed` | File couldn't be read (e.g. scanned image with no text layer) |
| 429 | `cooldown` | Requests are rate-limited to one every 3 seconds per server instance |
| 502 | `ai_analysis_failed` | The Gemini API call failed or returned an unusable response |

All error responses share this shape:
```json
{ "error": "error_code", "message": "Human-readable explanation" }
```