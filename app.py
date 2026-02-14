from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pdfplumber

app = Flask(__name__)
CORS(app)

# ────────────────────────────────────────────────
# YOUR ORIGINAL SKILLS LIST — NOT CHANGED
# ────────────────────────────────────────────────
SKILLS = [
    "basic python", "python", "basic java", "java", "c++", "sql", "mongodb", "flask",
    "django", "react", "html", "css", "javascript",
    "node", "express", "machine learning", "nlp", "oop", "dsa", "dbms", "nodejs",
    "machine learning", "deep learning", "nlp",
    "tensorflow", "pytorch", "scikit", "git", "github", "docker", "aws", "rest api"
]

# ────────────────────────────────────────────────
# YOUR ORIGINAL JOB ROLE MAPPING — NOT CHANGED
# ────────────────────────────────────────────────
JOB_ROLES = {
    "Backend Developer":   ["python", "flask", "django", "node", "express", "sql"],
    "Frontend Developer":  ["html", "css", "javascript", "react"],
    "Full Stack Developer":["html", "css", "javascript", "react", "node", "flask"],
    "ML Engineer":         ["machine learning", "nlp", "python", "pytorch"],
    "Data Analyst":        ["python", "sql", "excel"],
    "DevOps Engineer":     ["docker", "aws", "git"],
    "Software Engineer":   ["dsa", "oop", "dbms"],
    "Android Developer":   ["java", "kotlin"],
    "Cloud Engineer":      ["aws", "docker", "rest api"]
}

# ────────────────────────────────────────────────
# NEW — keyword lists for score breakdown
# ────────────────────────────────────────────────
TECHNICAL_SKILLS = [
    "python", "java", "c++", "javascript", "typescript", "react", "node", "express",
    "flask", "django", "html", "css", "sql", "mongodb", "tensorflow", "pytorch",
    "scikit", "nlp", "docker", "aws", "azure", "gcp", "git", "kubernetes", "rest api",
    "graphql", "vue", "angular", "sass", "tailwind", "webpack", "machine learning",
    "deep learning", "pandas", "numpy", "dsa", "oop", "kotlin", "android", "firebase"
]

EXPERIENCE_KEYWORDS = [
    "experience", "internship", "intern", "worked", "developed", "built", "implemented",
    "designed", "created", "managed", "led", "project", "team", "deployed", "achieved",
    "improved", "increased", "reduced", "launched", "collaborated", "optimized",
    "delivered", "engineered", "spearheaded"
]

EDUCATION_KEYWORDS = [
    "bachelor", "b.tech", "b.sc", "master", "m.tech", "msc", "phd", "degree",
    "university", "college", "gpa", "cgpa", "computer science", "engineering",
    "information technology", "certification", "certified", "course", "bootcamp"
]

# ────────────────────────────────────────────────
# Upload folder — YOUR ORIGINAL CODE
# ────────────────────────────────────────────────
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# ────────────────────────────────────────────────
# UPLOAD ROUTE — original logic preserved,
# just reads the optional 'role' field and
# adds score_breakdown + suggestions to response
# ────────────────────────────────────────────────
@app.route("/upload", methods=["POST"])
def upload_file():
    # YOUR ORIGINAL CHECKS
    if 'resume' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['resume']

    if file.filename == "":
        return jsonify({"error": "No file part"}), 400

    # NEW — read selected role if sent by frontend (safe to ignore if missing)
    selected_role = request.form.get("role", "")

    # YOUR ORIGINAL FILE SAVE
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # YOUR ORIGINAL FUNCTIONS
    extracted_text  = extract_text_from_pdf(file_path)
    matched_skills  = match_skills(extracted_text)
    predicted_roles, overall_score = predict_job_roles(matched_skills)

    # NEW — extra data (score breakdown + suggestions)
    score_breakdown = calculate_score_breakdown(extracted_text)
    suggestions     = generate_suggestions(extracted_text, matched_skills, selected_role)

    # YOUR ORIGINAL RESPONSE + new fields added
    return jsonify({
        "message":        "PDF uploaded successfully",
        "matched_skills": matched_skills,
        "predicted_roles": predicted_roles,
        "overall_score":  overall_score,
        "score_breakdown": score_breakdown,   # NEW
        "suggestions":    suggestions         # NEW
    })


# ────────────────────────────────────────────────
# SERVE FRONTEND — YOUR ORIGINAL ROUTES
# ────────────────────────────────────────────────
@app.route("/")
def serve_index():
    return send_from_directory("frontend", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("frontend", path)


# ────────────────────────────────────────────────
# YOUR ORIGINAL FUNCTIONS — NOT CHANGED AT ALL
# ────────────────────────────────────────────────
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def match_skills(resume_text):
    matched_skills = []
    resume_text = resume_text.lower()
    for skill in SKILLS:
        if skill.lower() in resume_text:
            matched_skills.append(skill)
    return matched_skills


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


# ────────────────────────────────────────────────
# NEW FUNCTIONS — added below your originals
# ────────────────────────────────────────────────
def calculate_score_breakdown(resume_text):
    """
    Breaks overall score into 3 recruiter-weighted categories:
      Technical Skills — 50 pts max
      Experience       — 30 pts max
      Education        — 20 pts max
    """
    t = resume_text.lower()

    tech_found = sum(1 for s in TECHNICAL_SKILLS if s in t)
    tech_score = min(round((tech_found / 15) * 50, 1), 50)

    exp_found  = sum(1 for kw in EXPERIENCE_KEYWORDS if kw in t)
    exp_score  = min(round((exp_found / 10) * 30, 1), 30)

    edu_found  = sum(1 for kw in EDUCATION_KEYWORDS if kw in t)
    edu_score  = min(round((edu_found / 6) * 20, 1), 20)

    total = round(tech_score + exp_score + edu_score, 1)

    return {
        "technical": {
            "score": tech_score,
            "max": 50,
            "keywords_found": tech_found
        },
        "experience": {
            "score": exp_score,
            "max": 30,
            "keywords_found": exp_found
        },
        "education": {
            "score": edu_score,
            "max": 20,
            "keywords_found": edu_found
        },
        "total": total
    }


def generate_suggestions(resume_text, matched_skills, selected_role):
    """
    Returns up to 6 personalised improvement tips based on what's
    missing or weak in the resume.
    """
    t    = resume_text.lower()
    sugs = []

    # 1 — Missing skills for chosen role
    if selected_role and selected_role in JOB_ROLES:
        role_skills = JOB_ROLES[selected_role]
        missing = [s for s in role_skills if s not in matched_skills]
        if missing:
            sugs.append({
                "type":   "skills",
                "icon":   "🔧",
                "title":  f"Add {selected_role} Skills",
                "detail": f"Missing keywords: {', '.join(missing[:5])}"
            })

    # 2 — Quantifiable achievements
    if not any(w in t for w in ["increased", "reduced", "improved", "%", "percent", "achieved", "delivered"]):
        sugs.append({
            "type":   "impact",
            "icon":   "📊",
            "title":  "Quantify Your Achievements",
            "detail": "Use numbers and percentages e.g. \"Improved load time by 40%\""
        })

    # 3 — Weak action verbs
    if not any(v in t for v in ["architected", "spearheaded", "engineered", "optimized", "launched", "deployed"]):
        sugs.append({
            "type":   "language",
            "icon":   "✍️",
            "title":  "Use Stronger Action Verbs",
            "detail": "Try: Architected, Spearheaded, Engineered, Optimized, Deployed"
        })

    # 4 — Profile links
    if not any(link in t for link in ["github", "portfolio", "linkedin"]):
        sugs.append({
            "type":   "links",
            "icon":   "🔗",
            "title":  "Add Profile Links",
            "detail": "Include GitHub, LinkedIn or Portfolio URL to stand out"
        })

    # 5 — Certifications
    if not any(c in t for c in ["certified", "certification", "certificate"]):
        sugs.append({
            "type":   "certs",
            "icon":   "🏆",
            "title":  "Add Certifications",
            "detail": "AWS, Google or Meta certs significantly boost ATS scores"
        })

    # 6 — Projects
    if "project" not in t:
        sugs.append({
            "type":   "projects",
            "icon":   "🚀",
            "title":  "Highlight Personal Projects",
            "detail": "List 2–3 projects with tech stack used and outcomes achieved"
        })

    # 7 — Education section
    if not any(e in t for e in ["university", "college", "degree", "b.tech", "bachelor"]):
        sugs.append({
            "type":   "education",
            "icon":   "🎓",
            "title":  "Include Education Details",
            "detail": "Add your degree, institution and graduation year"
        })

    return sugs[:6]


if __name__ == "__main__":
    app.run(debug=True)