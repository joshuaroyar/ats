# ats_score.py
"""
Unified ATS scoring endpoint:
Runs:
- Impact Analyzer (Module A)
- Structure Analyzer (Module B)
- Clarity Analyzer (Module C)
- Advanced Skill Matcher (Module D)
- LLM Feedback (Module E)

Outputs only:
- impact_score
- structure_score
- clarity_score
- skill_score
- final_ats_score
- feedback (local llama3.1:8b)
"""

import json
import sys
from utils.pdf_reader import extract_text_from_pdf

from core.scoring.domain_impact_analyzer import analyze_resume_impact
from preprocessing.structure_analyzer import analyze_structure
from preprocessing.clarity_analyzer import analyze_clarity
from core.scoring.advanced_skill_matcher import advanced_score
from core.scoring.feedback_engine import generate_feedback


def ats_score(resume_pdf, jd_txt):
    # Extract text
    text = extract_text_from_pdf(resume_pdf)

    # Run modules
    impact = analyze_resume_impact(resume_pdf)
    structure = analyze_structure(text)
    clarity = analyze_clarity(text)
    skill_detail = advanced_score(resume_pdf, jd_txt)
    skill_score = skill_detail["skill_score"]

    # Final ATS Score = sum of all
    final = (
        impact["impact_score"]*1.45
        + structure["structure_score"]*1.5
        + clarity["clarity_score"]*1.3
        + skill_score*1.5
    )

    final = round(max(0, min(100, final)), 2)

    return {
        "impact_score": impact["impact_score"],
        "structure_score": structure["structure_score"],
        "clarity_score": clarity["clarity_score"],
        "skill_score": skill_score,
        "final_ats_score": final
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ats_score.py resume.pdf jd.txt")
        sys.exit(1)

    resume_pdf = sys.argv[1]
    jd_txt = sys.argv[2]

    # 1 — Compute scores
    result = ats_score(resume_pdf, jd_txt)

    # 2 — Extract text for feedback
    resume_text = extract_text_from_pdf(resume_pdf)
    jd_text = open(jd_txt, "r", encoding="utf-8").read()

    # 3 — Generate LLM feedback
    feedback = generate_feedback(
        resume_text,
        jd_text,
        {
            "impact": result["impact_score"],
            "structure": result["structure_score"],
            "clarity": result["clarity_score"],
            "skills": result["skill_score"]
        }
    )

    result["feedback"] = feedback

    # 4 — Final output
    print(json.dumps(result, indent=2))
