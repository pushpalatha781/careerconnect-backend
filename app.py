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
jobs = pd.read_excel("jobpostings.xlsx")

def extract_text(file_path):

    text = ""

    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()

    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text

    else:
        text = open(file_path).read()

    return text.lower()


@app.route("/upload_resume", methods=["POST"])
def upload_resume():

    file = request.files["resume"]

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    resume_text = extract_text(path)

    results = []

    for _, row in jobs.iterrows():

        job_skills = row["skills"].lower().split()

        score = 0

        for skill in job_skills:
            if skill in resume_text:
                score += 1

        results.append({
            "title": row["job_title"],
            "company_name": row["company"],
            "location": row["location"],
            "suitability_score": score * 20
        })

    return jsonify(results)


if __name__ == "__main__":
    app.run()
