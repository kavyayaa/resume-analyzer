
from flask import Flask,request,jsonify
from flask import send_from_directory
from flask_cors import CORS
import os
import pdfplumber
app = Flask(__name__)
CORS(app)

# ---------------- SKILLS LIST ----------------
# Ye global list hai (pure app me use hogi)
SKILLS = [
    "basic python", "python", "basic java", "java", "c++", "sql", "mongodb", "flask",
    "django", "react", "html", "css", "javascript",
    "node", "express", "machine learning", "nlp", "oop", "dsa", "dbms", "nodejs", "machine learning", "deep learning", "nlp",
    "tensorflow", "pytorch", "scikit",  "git", "github", "docker", "aws", "rest api"
]
# ---------------- JOB ROLE MAPPING ----------------
JOB_ROLES = {
    "Backend Developer": ["python", "flask", "django", "node", "express", "sql"],
    "Frontend Developer": ["html", "css", "javascript", "react"],
    "Full Stack Developer": ["html", "css", "javascript", "react", "node", "flask"],
    "ML Engineer": ["machine learning", "nlp", "python", "pytorch"],
    "Data Analyst": ["python", "sql", "excel"],
    "DevOps Engineer": ["docker", "aws", "git"],
    "Software Engineer": ["dsa", "oop", "dbms"],
    "Android Developer": ["java", "kotlin"],
    "Cloud Engineer": ["aws", "docker", "rest api"]
}



#folder jaha pdfs save honge
UPLOAD_FOLDER="uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

    


# ---------------- PDF UPLOAD ROUTE ----------------
@app.route("/upload",methods=["POST"])
def upload_file():
    #Check: file request me aayi ya nahi
    if 'resume' not in request.files:
        return jsonify({"error":"No file part"}),400
    file=request.files['resume']

     # Check: file select ki gayi ya nahi
    if file.filename=="":
         return jsonify({"error":"No file part"}),400
    # File save in uploads folder  
    file_path=(os.path.join(UPLOAD_FOLDER,file.filename))
    file.save(file_path)
    #extract text from pdf using seperate function
    extracted_text=extract_text_from_pdf(file_path)
    matched_skills=match_skills(extracted_text)
    predicted_roles, overall_score = predict_job_roles(matched_skills)

    return jsonify({
        "message":"PDF uplaoded successfully",
        "matched_skills": matched_skills,
        "predicted_roles": predicted_roles,
        "overall_score": overall_score
    })



        

# Serve frontend files
@app.route("/")
def serve_index():
    return send_from_directory("frontend", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("frontend", path)


# ---------------- PDF Text Extraction Function ----------------
def extract_text_from_pdf(pdf_path):
    """
    This function receives a PDF path, extracts text from all pages,
    and returns the text as a string.
    """
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text
# ---------------- SKILL MATCHING FUNCTION ----------------
def match_skills(resume_text):
    matched_skills = []

    resume_text = resume_text.lower()

    for skill in SKILLS:
        if skill.lower() in resume_text:
            matched_skills.append(skill)

    return matched_skills


# ---------------- JOB ROLE PREDICTION FUNCTION ----------------
def predict_job_roles(matched_skills):
    role_percentages = []

    for role, skills in JOB_ROLES.items():
        match_count = 0

        for skill in skills:
            if skill in matched_skills:
                match_count += 1

        match_percentage = (match_count / len(skills)) * 100

        role_percentages.append({
            "role": role,
            "match": round(match_percentage, 2)
        })
        overall_score = 0

    if len(role_percentages) > 0:
        total = sum(role["match"] for role in role_percentages)
        overall_score = total / len(role_percentages)

    return role_percentages, round(overall_score, 2)



if __name__ == "__main__":
    app.run(debug=True)
