# skill_matcher.py
"""
Module D — Skills Match Analyzer + Full ATS Score (0–100)

Inputs:
- resume.pdf
- jd.txt (job description text)

Outputs:
- Skill Match Score (0–45)
- Final ATS Score (Impact + Structure + Clarity + Skills = 100)

Uses:
- Impact Analyzer (Module A)
- Structure Analyzer (Module B)
- Clarity Analyzer (Module C)
"""

import re
import json
import os
from sentence_transformers import SentenceTransformer
import numpy as np

# -------------------------
# Load your existing analyzers
# -------------------------
from domain_impact_analyzer import analyze_resume_impact
from preprocessing.structure_analyzer import analyze_structure
from preprocessing.clarity_analyzer import analyze_clarity
from utils.pdf_reader import extract_text_from_pdf


# -------------------------
# CONFIG
# -------------------------
EMBED_MODEL = SentenceTransformer("intfloat/e5-base")   # fast, accurate

HARD_SKILL_WEIGHT = 0.65
SOFT_SKILL_WEIGHT = 0.15
TOOL_SKILL_WEIGHT = 0.20

MAX_SKILL_SCORE = 45.0


# -------------------------
# Load predefined skill library
# (You can expand this later)
# -------------------------
SKILL_BANK = {
    "hard": [
        "machine learning", "deep learning", "nlp", "bert", "xgboost", "cnn", "python",
        "sql", "mongodb", "react", "javascript", "api development", "data structures",
        "algorithms", "ocr", "rag", "vector database", "tensorflow", "pytorch"
    ],
    "soft": [
        "communication", "teamwork", "leadership", "problem solving",
        "critical thinking", "adaptability", "ownership"
    ],
    "tools": [
        "git", "github", "firebase", "vs code", "power bi", "cursor", "ollama",
        "numpy", "pandas", "sklearn", "streamlit"
    ]
}


# -------------------------
# Helpers
# -------------------------
def embed(texts):
    return EMBED_MODEL.encode(texts, normalize_embeddings=True)


def cosine_sim(a, b):
    return np.dot(a, b)


def extract_skills_from_text(text):
    text_low = text.lower()
    words = re.findall(r"[a-zA-Z0-9\+\#\.]+", text_low)
    bigrams = [" ".join(words[i:i+2]) for i in range(len(words)-1)]
    tokens = set(words + bigrams)

    found = set()
    for cat, skills in SKILL_BANK.items():
        for s in skills:
            if s in text_low:
                found.add(s)

    return found


def semantic_skill_match(resume_text, jd_text):
    resume_vec = embed([resume_text])[0]
    jd_vec = embed([jd_text])[0]
    sim = cosine_sim(resume_vec, jd_vec)
    return float(sim)


# -------------------------
# MAIN SKILL MATCH LOGIC
# -------------------------
def score_skill_match(resume_text, jd_text):
    resume_skills = extract_skills_from_text(resume_text)
    jd_skills = extract_skills_from_text(jd_text)

    exact_matches = resume_skills.intersection(jd_skills)
    missing_skills = jd_skills - resume_skills

    # semantic similarity bonus
    sem_sim = semantic_skill_match(resume_text, jd_text)
    sem_bonus = sem_sim * 10  # max ~10 pts

    hard_score = len([s for s in exact_matches if s in SKILL_BANK["hard"]]) * HARD_SKILL_WEIGHT
    soft_score = len([s for s in exact_matches if s in SKILL_BANK["soft"]]) * SOFT_SKILL_WEIGHT
    tool_score = len([s for s in exact_matches if s in SKILL_BANK["tools"]]) * TOOL_SKILL_WEIGHT

    raw = hard_score + soft_score + tool_score + sem_bonus
    final = min(MAX_SKILL_SCORE, raw)

    return {
        "skill_score": round(final, 2),
        "exact_matches": sorted(list(exact_matches)),
        "missing_skills": sorted(list(missing_skills)),
        "semantic_similarity": round(sem_sim, 4)
    }


# -------------------------
# FULL ATS SCORE
# -------------------------
def full_ats_score(resume_pdf, jd_path):
    text = extract_text_from_pdf(resume_pdf)

    # load JD
    with open(jd_path, "r", encoding="utf-8") as f:
        jd = f.read()

    impact = analyze_resume_impact(resume_pdf)
    structure = analyze_structure(text)
    clarity = analyze_clarity(text)
    skills = score_skill_match(text, jd)

    final_score = (
        impact["impact_score"] +
        structure["structure_score"] +
        clarity["clarity_score"] +
        skills["skill_score"]
    )

    final_score = max(0, min(100, final_score))

    return {
        "final_ats_score": round(final_score, 2),
        "impact_score": impact["impact_score"],
        "structure_score": structure["structure_score"],
        "clarity_score": clarity["clarity_score"],
        "skill_score": skills["skill_score"],
        "skill_details": skills,
        "impact_details": impact,
        "structure_details": structure,
        "clarity_details": clarity
    }


# -------------------------
# CLI
# -------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python skill_matcher.py resume.pdf jd.txt")
        exit()

    out = full_ats_score(sys.argv[1], sys.argv[2])
    print(json.dumps(out, indent=2, ensure_ascii=False))
