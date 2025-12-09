from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from ats_score import ats_score
from core.scoring.feedback_engine import generate_feedback
from utils.pdf_reader import extract_text_from_pdf

app = FastAPI(title="ATS Resume Analyzer API", version="1.0.0")

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the job description (you might want to make this configurable)
with open("jd.txt", "r", encoding="utf-8") as f:
    JD_TEXT = f.read()

@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    """
    Analyze a resume PDF and return ATS scores and feedback.
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Validate file size (max 5MB)
    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name

    try:
        # Extract text first to check if PDF is readable
        from utils.pdf_reader import extract_text_from_pdf
        resume_text = extract_text_from_pdf(temp_file_path)

        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF. The file may be scanned, image-based, or corrupted.")

        # Save JD text to temporary file for advanced_score function
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as jd_temp_file:
            jd_temp_file.write(JD_TEXT)
            jd_temp_file_path = jd_temp_file.name

        try:
            # Run ATS analysis
            result = ats_score(temp_file_path, jd_temp_file_path)
        finally:
            # Clean up JD temp file
            if os.path.exists(jd_temp_file_path):
                os.unlink(jd_temp_file_path)

        # Generate AI feedback
        try:
            feedback = generate_feedback(
                resume_text,
                JD_TEXT,
                {
                    "impact": result["impact_score"],
                    "structure": result["structure_score"],
                    "clarity": result["clarity_score"],
                    "skills": result["skill_score"]
                }
            )
        except Exception as feedback_error:
            print(f"Feedback generation failed: {feedback_error}")
            feedback = "AI feedback unavailable\nAnalysis completed successfully\nManual review recommended"

        result["feedback"] = feedback

        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Analysis failed with error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)