from parser import extract_text
from analyzer import (
    load_skills_database,
    extract_skills,
    calculate_ats_score,
    find_missing_skills
)

# Resume text extract
text = extract_text("resume.pdf")

# Skills extract
skills_db = load_skills_database()
resume_skills = extract_skills(text, skills_db)

print("Resume Skills:")
print(resume_skills)

# Sample Job Description Skills
jd_skills = [
    "python",
    "sql",
    "fastapi",
    "pandas",
    "machine learning"
]

score = calculate_ats_score(resume_skills, jd_skills)
missing_skills = find_missing_skills(resume_skills, jd_skills)

print("\nATS Score:", score, "%")
print("Missing Skills:", missing_skills)