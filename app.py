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

        job_skills = str(row["skills"]).lower().split(",")

        score = 0

        for skill in job_skills:
            if skill.strip() in resume_text:
                score += 1

        if score > 0:

            score_percent = score * 20

            # Determine suitability level
            if score_percent >= 80:
                level = "Highly Suitable"
            elif score_percent >= 60:
                level = "Suitable"
            elif score_percent >= 40:
                level = "Moderately Suitable"
            else:
                level = "Not Suitable"

            results.append({
                "title": row["role"],
                "company_name": row["company"],
                "location": str(row["city"]) + ", " + str(row["state"]),
                "salary_lpa": row["salary_lpa"],
                "suitability_level": level
            })

    return jsonify(results[:10])
    



if __name__ == "__main__":
    app.run()
