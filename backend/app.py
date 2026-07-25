from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from utils.resume_parser import parse_resume
from utils.ai_client import analyze_resume  # noqa: F401  (not called yet — wired for real on Day 6)
import tempfile
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MIN_JOB_DESCRIPTION_LENGTH = 50
ALLOWED_EXTENSIONS = (".pdf", ".docx")

# Day 2 API contract — hardcoded placeholder response for Day 5.
# Day 6 replaces the "result = PLACEHOLDER_ANALYSIS" line below with a
# real call to analyze_resume(resume_text, job_description).
PLACEHOLDER_ANALYSIS = {
    "overall_score": 78,
    "sub_scores": {
        "skills": 72,
        "keywords": 65,
        "experience": 85,
        "education": 90
    },
    "missing_keywords": ["Docker", "CI/CD", "REST APIs"],
    "missing_skills": ["Kubernetes", "Unit Testing"],
    "strengths": ["Strong Python experience", "Relevant academic projects"],
    "weaknesses": ["No cloud deployment experience mentioned", "Missing quantifiable achievements"],
    "suggestions": [
        "Add 'Docker' and 'CI/CD' explicitly if you have exposure to them",
        "Quantify project impact with numbers (e.g., 'reduced load time by 30%')"
    ]
}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/analyze", methods=["POST"])
def analyze():
    job_description = request.form.get("job_description", "").strip()

    if not job_description or len(job_description) < MIN_JOB_DESCRIPTION_LENGTH:
        return jsonify({
            "error": "invalid_job_description",
            "message": f"Job description must be at least {MIN_JOB_DESCRIPTION_LENGTH} characters."
        }), 400

    resume_text = request.form.get("resume_text", "").strip()
    resume_file = request.files.get("resume_file")

    if not resume_file and not resume_text:
        return jsonify({
            "error": "missing_resume",
            "message": "Please upload a resume file or paste your resume text."
        }), 400

    # A file takes priority over pasted text if both are somehow present,
    # matching the frontend's mode toggle (only one is ever sent at a time).
    if resume_file:
        filename = resume_file.filename or ""
        ext = os.path.splitext(filename)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({
                "error": "unsupported_file_type",
                "message": "Please upload a PDF or DOCX file."
            }), 400

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                resume_file.save(tmp.name)
                tmp_path = tmp.name

            resume_text = parse_resume(tmp_path)

        except ValueError:
            return jsonify({
                "error": "parsing_failed",
                "message": "We couldn't read that file. Please paste your resume text instead."
            }), 422

        except Exception as e:
            return jsonify({
                "error": "server_error",
                "message": str(e)
            }), 500

        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    if not resume_text:
        return jsonify({
            "error": "parsing_failed",
            "message": "We couldn't read that file. Please paste your resume text instead."
        }), 422

    # --- Day 5: hardcoded placeholder response (Day 2 API contract) ---
    # Day 6: result = analyze_resume(resume_text, job_description)
    result = PLACEHOLDER_ANALYSIS

    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
