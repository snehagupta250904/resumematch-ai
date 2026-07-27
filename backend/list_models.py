import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")

r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={key}")
print("Status code:", r.status_code)

models = r.json().get("models", [])

print("\n--- Models supporting generateContent (flash/pro only) ---")
for m in models:
    name = m.get("name", "")
    methods = m.get("supportedGenerationMethods", [])
    if "generateContent" not in methods:
        continue
    if "flash" not in name and "pro" not in name:
        continue
    skip_terms = ["preview", "robotics", "computer-use", "research", "image", "tts", "embedding", "antigravity"]
    if any(term in name for term in skip_terms):
        continue
    print(name)