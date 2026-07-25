import os
import json
import requests
from dotenv import load_dotenv 
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

def analyze_resume(resume_text, job_description):
    """Send resume + JD to Gemini via REST API and get a structured match analysis."""
    prompt = f"""
You are a resume-to-job-description matcher. Compare the resume against the job description.

Return ONLY valid JSON, no markdown, no preamble, in this exact shape:
{{
  "match_score": <integer 0-100>,
  "matching_skills": [<strings>],
  "missing_skills": [<strings>],
  "summary": "<2-3 sentence assessment>"
}}

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(GEMINI_URL, json=payload)
    response.raise_for_status()
    data = response.json()

    raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    return json.loads(raw)