import os
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from utils.resume_parser import extract_resume_text, ResumeExtractionError, get_extension
from utils.ai_client import analyze_resume, AIAnalysisError

load_dotenv()

app = Flask(__name__)
CORS(app)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MIN_JD_LENGTH = 50
MIN_RESUME_TEXT_LENGTH = 40

COOLDOWN_SECONDS = 3
# Simple in-memory cooldown guard -- not a security feature, just a basic
# safeguard against burning through the free-tier Gemini quota with rapid
# repeat clicks during testing/demoing.
_last_request_time = {"ts": 0.0}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/analyze", methods=["POST"])
def analyze():
    now = time.time()
    if now - _last_request_time["ts"] < COOLDOWN_SECONDS:
        return jsonify({
            "error": "cooldown",
            "message": "Please wait a few seconds before analyzing again."
        }), 429

    job_description = request.form.get("job_description", "").strip()
    resume_text = request.form.get("resume_text", "").strip()
    resume_file = request.files.get("resume_file")

    if not job_description or len(job_description) < MIN_JD_LENGTH:
        return jsonify({
            "error": "missing_fields",
            "message": f"Job description must be at least {MIN_JD_LENGTH} characters."
        }), 400

    if not resume_file and not resume_text:
        return jsonify({
            "error": "missing_fields",
            "message": "Provide either a resume file or pasted resume text."
        }), 400

    final_resume_text = resume_text

    if resume_file:
        ext = get_extension(resume_file.filename)
        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({
                "error": "unsupported_file_type",
                "message": "Only PDF or DOCX files are supported."
            }), 415

        resume_file.stream.seek(0, os.SEEK_END)
        size = resume_file.stream.tell()
        resume_file.stream.seek(0)
        if size > MAX_FILE_SIZE:
            return jsonify({
                "error": "file_too_large",
                "message": "File is too large. Maximum size is 5MB."
            }), 413

        try:
            final_resume_text = extract_resume_text(resume_file)
        except ResumeExtractionError:
            return jsonify({
                "error": "extraction_failed",
                "message": "Couldn't read text from that file. Try pasting your resume text instead."
            }), 422

    if not final_resume_text or len(final_resume_text.strip()) < MIN_RESUME_TEXT_LENGTH:
        return jsonify({
            "error": "missing_fields",
            "message": "Resume text is empty or too short."
        }), 400

    _last_request_time["ts"] = now

    try:
        result = analyze_resume(final_resume_text, job_description)
    except AIAnalysisError:
        return jsonify({
            "error": "ai_analysis_failed",
            "message": "Something went wrong analyzing your resume. Please try again."
        }), 502

    return jsonify(result), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)