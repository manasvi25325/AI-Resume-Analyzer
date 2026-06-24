import os
import shutil

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from database import save_analysis, init_db
from parser import extract_text
from analyzer import (
    load_skills_database,
    extract_skills,
    calculate_ats_score,
    find_missing_skills,
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create the database table when the app starts
init_db()

# Folder where uploaded resumes will be stored
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Keep track of the resume the user uploaded last
last_resume_path = None


class JobDescription(BaseModel):
    jd_text: str


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/upload")
def upload_resume(file: UploadFile = File(...)):
    global last_resume_path

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    last_resume_path = file_path

    return {"filename": file.filename, "message": "Resume uploaded successfully"}


@app.get("/analyze", response_class=HTMLResponse)
def analyze_resume(request: Request):
    if last_resume_path is None:
        raise HTTPException(status_code=400, detail="Please upload a resume first")

    resume_text = extract_text(last_resume_path)
 # Step 1: Read text from the resume
    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not read text from this PDF. Try a different file."
        )
   

    # Step 2: Load skills list and find resume skills
    skills_db = load_skills_database()
    resume_skills = extract_skills(resume_text, skills_db)

    # Step 3: Compare with a sample job description's required skills
    jd_skills = ["python", "sql", "fastapi", "pandas", "machine learning"]

    score = calculate_ats_score(resume_skills, jd_skills)
    missing_skills = find_missing_skills(resume_skills, jd_skills)

    suggestions = [f"Consider adding {skill}" for skill in missing_skills]

    # Step 4: Decide score color for the UI
    if score >= 80:
        score_color = "green"
    elif score >= 60:
        score_color = "orange"
    else:
        score_color = "red"

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "ats_score": score,
            "skills_found": resume_skills,
            "missing_skills": missing_skills,
            "suggestions": suggestions,
            "score_color": score_color,
        },
    )


@app.post("/analyze-jd")
def analyze_jd(data: JobDescription):
    if last_resume_path is None:
        raise HTTPException(status_code=400, detail="Please upload a resume first")

    resume_text = extract_text(last_resume_path)
    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not read text from this PDF. Try a different file."
        )
        
    skills_db = load_skills_database()

    resume_skills = extract_skills(resume_text, skills_db)
    jd_skills = extract_skills(data.jd_text, skills_db)

    score = calculate_ats_score(resume_skills, jd_skills)
    missing_skills = find_missing_skills(resume_skills, jd_skills)

    save_analysis(score, missing_skills)

    return {
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "ats_score": score,
        "missing_skills": missing_skills,
    }


@app.get("/history")
def history():
    import sqlite3

    conn = sqlite3.connect("resume_analyzer.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {"history": rows}