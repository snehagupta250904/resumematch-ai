from utils.ai_client import analyze_resume, AIAnalysisError

resume = "Sneha Gupta - Final year Computer Science student. Built projects using Python, Streamlit, SQLite, and Machine Learning. Strong in DSA and DBMS."
jd = "Aspiring Software Developer with knowledge of Java, Python, Data Structures and Algorithms, DBMS, and Web Technologies."

try:
    result = analyze_resume(resume, jd)
    print("SUCCESS:", result)
except AIAnalysisError as e:
    print("REAL ERROR:", e)