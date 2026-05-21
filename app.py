import os
import json
from flask import Flask, render_template, request
from PyPDF2 import PdfReader

app = Flask(__name__)

UPLOAD_FOLDER = "resumes"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

required_skills = [
    "python",
    "java",
    "c++",
    "html",
    "css",
    "javascript",
    "sql",
    "machine learning",
    "communication",
    "teamwork"
]

def extract_text_from_pdf(filepath):
    text = ""
    reader = PdfReader(filepath)
    for page in reader.pages:
        text += page.extract_text()
    return text.lower()

def analyze_resume(text):
    found_skills = []
    for skill in required_skills:
        if skill in text:
            found_skills.append(skill)

    missing_skills = list(set(required_skills) - set(found_skills))
    score = (len(found_skills) / len(required_skills)) * 100

    return round(score, 2), found_skills, missing_skills

def save_to_json(data):
    with open("data.json", "r") as file:
        existing_data = json.load(file)

    existing_data.append(data)

    with open("data.json", "w") as file:
        json.dump(existing_data, file, indent=4)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return "No file uploaded"

    file = request.files["resume"]

    if file.filename == "":
        return "No selected file"

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    resume_text = extract_text_from_pdf(filepath)
    score, found_skills, missing_skills = analyze_resume(resume_text)

    result_data = {
        "filename": file.filename,
        "score": score,
        "skills_found": found_skills,
        "missing_skills": missing_skills
    }

    save_to_json(result_data)

    if score >= 70:
        strength = "Strong Resume"
    elif score >= 40:
        strength = "Average Resume"
    else:
        strength = "Weak Resume"

    return render_template(
        "result.html",
        score=score,
        found_skills=found_skills,
        missing_skills=missing_skills,
        strength=strength
    )

if __name__ == "__main__":
    app.run(debug=True)

    UPLOAD_FOLDER = "resumes"