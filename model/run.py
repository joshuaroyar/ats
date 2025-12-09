from core.scoring.scoring_engine import evaluate_resume_against_jd
import json

if __name__ == "__main__":
    resume_file = "resume3.pdf"
    
    with open("jd.txt", "r", encoding="utf-8") as f:
        jd_text = f.read()

    result = evaluate_resume_against_jd(resume_file, jd_text)

    print(json.dumps(result, indent=2))
