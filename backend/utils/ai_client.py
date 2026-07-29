import os
import json
import re
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("resumematch.ai_client")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = "gemini-flash-lite-latest"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{MODEL_NAME}:generateContent"
)

PROMPT_TEMPLATE = """You are an expert technical recruiter and ATS (Applicant Tracking System) analyst.

Compare the RESUME below against the JOB DESCRIPTION below and produce a match analysis.

Respond with ONLY valid JSON, no markdown formatting, no code fences, no extra text before or after. The JSON must match this exact structure:

{{
  "overall_score": <integer 0-100>,
  "sub_scores": {{
    "skills": <integer 0-100>,
    "keywords": <integer 0-100>,
    "experience": <integer 0-100>,
    "education": <integer 0-100>
  }},
  "missing_keywords": [<strings>],
  "missing_skills": [<strings>],
  "strengths": [<strings>],
  "weaknesses": [<strings>],
  "suggestions": [<strings>]
}}

Rules:
- overall_score and all sub_scores must be integers from 0 to 100.
- missing_keywords, missing_skills, strengths, weaknesses, suggestions must always be arrays (use an empty array if none apply, never null).
- strengths and weaknesses: 2-5 concise bullet-style items each.
- suggestions: 2-5 specific, actionable improvements the candidate could make.
- Base every judgment strictly on the text provided below. Do not invent experience the resume doesn't mention.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""


class AIAnalysisError(Exception):
    """Raised when the Gemini call fails or returns unusable output."""
    pass


def _extract_json(raw_text):
    text = raw_text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def _validate_shape(data):
    required_top = [
        "overall_score", "sub_scores", "missing_keywords",
        "missing_skills", "strengths", "weaknesses", "suggestions",
    ]
    for key in required_top:
        if key not in data:
            raise AIAnalysisError(f"Missing field: {key}")

    if not isinstance(data["overall_score"], (int, float)):
        raise AIAnalysisError("overall_score must be numeric")

    sub = data["sub_scores"]
    for sub_key in ["skills", "keywords", "experience", "education"]:
        if sub_key not in sub or not isinstance(sub[sub_key], (int, float)):
            raise AIAnalysisError(f"sub_scores.{sub_key} missing or not numeric")

    for list_key in ["missing_keywords", "missing_skills", "strengths", "weaknesses", "suggestions"]:
        if not isinstance(data[list_key], list):
            raise AIAnalysisError(f"{list_key} must be a list")

    data["overall_score"] = int(round(data["overall_score"]))
    for sub_key in ["skills", "keywords", "experience", "education"]:
        sub[sub_key] = int(round(sub[sub_key]))

    return data


def analyze_resume(resume_text, job_description):
    if not GEMINI_API_KEY:
        raise AIAnalysisError("GEMINI_API_KEY is not configured on the server.")

    prompt = PROMPT_TEMPLATE.format(
        resume_text=resume_text.strip(),
        job_description=job_description.strip(),
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3},
    }

    try:
        response = requests.post(
            GEMINI_URL,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=25,
        )
        response.raise_for_status()
        data_raw = response.json()
        raw_text = data_raw["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.RequestException as exc:
        logger.error("Gemini request failed: %s", exc)
        raise AIAnalysisError(f"Gemini request failed: {exc}") from exc
    except (KeyError, IndexError) as exc:
        logger.error("Unexpected Gemini response shape: %s | raw=%s", exc, data_raw)
        raise AIAnalysisError(f"Unexpected Gemini response shape: {exc}") from exc

    try:
        data = _extract_json(raw_text)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("Gemini returned invalid JSON: %s | raw_text=%s", exc, raw_text)
        raise AIAnalysisError(f"Gemini returned invalid JSON: {exc}") from exc

    return _validate_shape(data)