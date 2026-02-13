from core.scoring.feedback_engine import generate_feedback

resume_text = "Experienced Software Engineer with Python and React skills."
jd_text = "Looking for a Software Engineer with Python, React, and AWS experience."
scores = {"Total": 80, "Skills": 40}

print("Testing feedback generation...")
try:
    feedback = generate_feedback(resume_text, jd_text, scores)
    print("Feedback result:")
    print(f"'{feedback}'")
except Exception as e:
    print(f"Error: {e}")
