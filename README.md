# ResumeMatch AI

An AI-powered web app that compares a resume against a job description and returns a match score, missing keywords/skills, and ATS optimization suggestions — free, no login required.

**Live app:** https://resumematch-ai-abtalks.netlify.app/
**Live API:** https://resumematch-ai-tai8.onrender.com/health

> Note: the backend runs on Render's free tier, which spins down after periods of inactivity. The first request after a period of inactivity can take up to a minute to respond while the server wakes up — this is expected, not a bug.

## How it works

1. Paste your resume (or upload a PDF/DOCX) and a job description.
2. The app sends both to Google's Gemini API with a structured prompt asking it to compare them.
3. You get back an overall match score, a breakdown by skills/keywords/experience/education, missing keywords and skills, strengths, weaknesses, and concrete suggestions to improve your match.

## Tech stack

- **Frontend:** HTML, CSS, JavaScript — no framework, hosted on Netlify
- **Backend:** Python (Flask) with gunicorn, hosted on Render
- **AI:** Google Gemini API (`gemini-flash-lite-latest`)
- **File parsing:** `pdfplumber` (PDF), `python-docx` (DOCX)

## Project structure 