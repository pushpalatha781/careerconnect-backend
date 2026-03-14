from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import pdfplumber
import docx

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load dataset
jobs = pd.read_csv("Indian_Fresher_Salary_Skills_2025.csv")


@app.route("/")
def home():
    return "CareerConnect Backend API Running"


# -----------------------------
# Extract Resume Text
# -----------------------------
def extract_text(file_path):

    text = ""

    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text

    else:
        text = open(file_path).read()

    return text.lower()


# -----------------------------
# Resume Upload API
# -----------------------------
@app.route("/upload_resume", methods=["POST"])
def upload_resume():

    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    resume_text = extract_text(path)

    results = []

    for _, row in jobs.iterrows():

        job_skills = [s.strip() for s in str(row["skills"]).lower().split(",")]

        matched_skills = []
        missing_skills = []

        for skill in job_skills:
            if skill in resume_text:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        total = len(job_skills)

        if total == 0:
            continue

        match_percent = round((len(matched_skills) / total) * 100, 2)
        missing_percent = round((len(missing_skills) / total) * 100, 2)

        # Suitability Level
        if match_percent >= 80:
            level = "Highly Suitable"
        elif match_percent >= 60:
            level = "Suitable"
        elif match_percent >= 40:
            level = "Moderately Suitable"
        else:
            level = "Not Suitable"

        results.append({
            "title": row["role"],
            "company_name": row["company"],
            "location": str(row["city"]) + ", " + str(row["state"]),
            "salary_lpa": row["salary_lpa"],
            "suitability_level": level,
            "missing_skills": missing_skills,
            "missing_percent": missing_percent
        })

    return jsonify(results[:10])


if __name__ == "__main__":
    app.run()
