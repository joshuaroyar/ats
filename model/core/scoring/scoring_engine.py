import json
import os
import sys

# Ensure project root is in path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from utils.pdf_reader import extract_text_from_pdf

# Import Analyzers
# Using try-except to handle potential import variances depending on how the script is run
try:
    from core.scoring.domain_impact_analyzer import analyze_resume_impact
    from core.scoring.advanced_skill_matcher import advanced_score
    from core.scoring.feedback_engine import generate_feedback
    from preprocessing.structure_analyzer import analyze_structure
    from preprocessing.clarity_analyzer import analyze_clarity
except ImportError:
    # Fallback for relative imports if running as package
    from .domain_impact_analyzer import analyze_resume_impact
    from .advanced_skill_matcher import advanced_score
    from .feedback_engine import generate_feedback
    from ...preprocessing.structure_analyzer import analyze_structure
    from ...preprocessing.clarity_analyzer import analyze_clarity

def evaluate_resume_against_jd(resume_pdf, jd_text):
    """
    Orchestrator function that runs all ATS analysis modules and aggregates the scores.
    """
    
    # 1. Extract Text
    resume_text = extract_text_from_pdf(resume_pdf)
    
    # 2. Run Modules
    print("Running Impact Analysis...")
    impact_data = analyze_resume_impact(resume_pdf)
    
    print("Running Structure Analysis...")
    structure_data = analyze_structure(resume_text)
    
    print("Running Clarity Analysis...")
    clarity_data = analyze_clarity(resume_text)
    
    print("Running Skill Matcher...")
    skill_data = advanced_score(resume_pdf, jd_text)
    
    # 3. Aggregate Scores
    impact_score = impact_data.get("impact_score", 0)
    structure_score = structure_data.get("structure_score", 0)
    clarity_score = clarity_data.get("clarity_score", 0)
    skill_score = skill_data.get("skill_score", 0)
    
    final_score = impact_score + structure_score + clarity_score + skill_score
    final_score = round(max(0, min(100, final_score)), 1)

    # 4. Generate AI Feedback
    print("Generating AI Feedback...")
    feedback_text = ""
    try:
        # Pass a summary of scores to the LLM
        scores_summary = {
            "Total": final_score,
            "Impact": impact_score,
            "Structure": structure_score,
            "Clarity": clarity_score,
            "Skills": skill_score,
            "Missing Skills": skill_data.get("skill_detail", {}).get("missing_skills", [])
        }
        feedback_text = generate_feedback(resume_text, jd_text, scores_summary)
    except Exception as e:
        print(f"Feedback generation failed: {e}")
        feedback_text = "AI feedback unavailable at the moment."
    
    # 5. Construct Final Response matching Frontend Expectations
    result = {
        "final_ats_score": final_score,
        "impact_score": round(impact_score, 1),
        "structure_score": round(structure_score, 1),
        "clarity_score": round(clarity_score, 1),
        "skill_score": round(skill_score, 1),
        
        "feedback": feedback_text,
        
        # Details (Optional, can be used by frontend for deep dive)
        "impact_detail": impact_data,
        "structure_detail": structure_data,
        "clarity_detail": clarity_data,
        "skill_detail": skill_data
    }
    
    return result

