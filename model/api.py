import shutil
import os
import uvicorn
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# Import the scoring engine
# Ensure the model directory is in the python path if running from elsewhere, 
# although running `python api.py` from model/ should work.
from core.scoring.scoring_engine import evaluate_resume_against_jd

app = FastAPI(title="ATS API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. adjust for production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze")
def analyze_resume(
    file: UploadFile = File(...),
    jd_text: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None),
    include_feedback: bool = Form(True)
):
    # Log the content type for debugging
    print(f"Received file: {file.filename}, content_type: {file.content_type}")
    
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed for resume.")
    
    # Save the uploaded resume temporarily
    temp_resume_path = f"temp_{file.filename}"
    with open(temp_resume_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Determine JD content
        final_jd_text = ""
        
        if jd_text and jd_text.strip():
            final_jd_text = jd_text
        elif jd_file:
             # Process uploaded JD file
             # Use synchronous read since we are in a def (threadpool)
             content = jd_file.file.read()
             final_jd_text = content.decode("utf-8")
        else:
            # Fallback to default local JD
            default_jd_path = os.path.join(os.path.dirname(__file__), "jd.txt")
            if os.path.exists(default_jd_path):
                with open(default_jd_path, "r", encoding="utf-8") as f:
                    final_jd_text = f.read()
            else:
                final_jd_text = "Software Engineer job description placeholder."

        # Run analysis
        # Note: evaluate_resume_against_jd typically takes a file path for the resume
        result = evaluate_resume_against_jd(temp_resume_path, final_jd_text)
        
        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(temp_resume_path):
            os.remove(temp_resume_path)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
