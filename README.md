ResumeMatch AI
An AI-powered web app that compares a resume against a job description and returns a match score, missing keywords/skills, and ATS optimization suggestions — free, no login required.
Live app: https://resumematch-ai-abtalks.netlify.app/
Live API health check: https://resumematch-ai-tai8.onrender.com/health
> **Note:** the backend runs on Render's free tier, which spins down after periods of inactivity. The first request after a period of inactivity can take up to a minute to respond while the server wakes up — this is expected, not a bug. The app will tell you this is happening rather than appearing frozen.
Status
v1.0.0 — complete. Built as the 10-day capstone project for the AB Talks 60-Day Claude AI Challenge, following a full software development lifecycle from requirements gathering through deployment, QA, and security hardening.
How it works
Paste your resume (or upload a PDF/DOCX) and a job description.
The app sends both to Google's Gemini API with a structured prompt asking it to compare them.
You get back an overall match score (0–100), a breakdown by skills/keywords/experience/education, missing keywords and skills, strengths, weaknesses, and concrete suggestions to improve your match.
Features
Upload a resume as PDF/DOCX, or paste resume text directly
Client- and server-side validation (file type, file size, minimum text length)
Animated score visualization (overall score ring + sub-score bars)
Graceful fallback: if a file can't be parsed, the app automatically switches to paste-text mode and explains why
Live backend health indicator in the header
Clear, specific error messages for every failure mode (bad file type, file too large, unparseable file, AI request failed, rate-limited)
Tech stack
Frontend: HTML, CSS, JavaScript — no framework, hosted on Netlify
Backend: Python (Flask) with gunicorn, hosted on Render
AI: Google Gemini API (`gemini-flash-lite-latest`)
File parsing: `pdfplumber` (PDF), `python-docx` (DOCX)
Project structure
```
resumematch-ai/
├── backend/
│   ├── app.py                 # Flask app, routes, request validation
│   ├── utils/
│   │   ├── resume_parser.py   # PDF/DOCX text extraction
│   │   └── ai_client.py       # Gemini API integration, response validation
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── assets/
├── docs/
│   ├── api.md                 # API reference
│   ├── architecture.md
│   ├── project-structure.md
│   ├── schema.md
│   └── ui-wireframes.md
├── LICENSE
└── README.md
```
Setup (run it locally)
Backend
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```
Create a `.env` file in `backend/` (copy `.env.example`) and add your own Gemini API key:
```
GEMINI_API_KEY=your_key_here
```
Get a free key at Google AI Studio.
Run the server:
```bash
python app.py
```
The backend runs at `http://127.0.0.1:5000` by default.
Frontend
Open `frontend/index.html` directly in your browser, or serve it with any static file server. It will automatically point at your local backend when running on `localhost`/`127.0.0.1`, and at the production backend otherwise.
API
See `docs/api.md` for the full API reference, including request/response shapes and error codes.
Known limitations
Rate limiting is a simple global 3-second cooldown, not per-user — this is a demo safeguard against burning through the free-tier Gemini quota, not a production rate limiter.
No sanitization against prompt injection in resume/job description text. Worst case, a user could manipulate their own score; there's no risk to other users' data.
File type is validated by extension, not by inspecting file contents.
No automated test suite yet (see `30-day-growth-plan.md` for the roadmap to add one).
Security
If you're evaluating this project: file uploads are validated for type and size both client- and server-side, CORS is restricted to an explicit origin allowlist, all AI responses are schema-validated before being returned to the client, and API keys are loaded from environment variables (never committed — see `.gitignore`).
License
See LICENSE.
Credits
Built by Sneha Gupta as the capstone project for the AB Talks 60-Day Claude AI Challenge, with Claude as AI pair programmer throughout the build. Learn more about the challenge at abtalks.in.