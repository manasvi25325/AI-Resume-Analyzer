import sqlite3

DB_NAME = "resume_analyzer.db"


def init_db():
    """Create the 'analysis' table if it doesn't already exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ats_score REAL,
            missing_skills TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_analysis(score, missing_skills):
    """Save one ATS score result into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Convert the list of missing skills into one text string
    # e.g. ["sql", "pandas"] -> "sql, pandas"
    missing_skills_text = ", ".join(missing_skills)

    cursor.execute(
        "INSERT INTO analysis (ats_score, missing_skills) VALUES (?, ?)",
        (score, missing_skills_text)
    )

    conn.commit()
    conn.close()