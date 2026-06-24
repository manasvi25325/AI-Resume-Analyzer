import json


def load_skills_database():
    """Load the list of known skills from skills_db.json."""
    with open("skills_db.json", "r") as file:
        data = json.load(file)
    return data["skills"]


def extract_skills(text, skills_db):
    """Check which skills from skills_db appear in the given text."""
    text = text.lower()
    found_skills = []

    for skill in skills_db:
        if skill.lower() in text:
            found_skills.append(skill)

    return found_skills


def calculate_ats_score(resume_skills, jd_skills):
    """Calculate what % of required (JD) skills are present in the resume."""
    if len(jd_skills) == 0:
        return 0

    # Skills that appear in both the resume and the job description
    matched_skills = set(resume_skills) & set(jd_skills)

    score = (len(matched_skills) / len(jd_skills)) * 100
    return round(score, 2)


def find_missing_skills(resume_skills, jd_skills):
    """Find skills required by the JD but missing from the resume."""
    missing = set(jd_skills) - set(resume_skills)
    return list(missing)