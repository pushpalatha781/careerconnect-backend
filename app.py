from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# load dataset
jobs = pd.read_csv("jobs_dataset.csv")


@app.route("/upload_resume", methods=["POST"])
def upload_resume():

    file = request.files["resume"]

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    # example skill extraction
    resume_text = open(path).read().lower()

    results = []

    for _, row in jobs.iterrows():

        job_skills = row["skills"].lower()

        score = 0
        for skill in job_skills.split():
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
