import subprocess
import json
import re

MODEL = "llama3.1:8b"

def clean_ansi(text):
    # remove ANSI escape codes
    return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)


def generate_feedback(resume_text, jd_text, scores):
    prompt = f"""
Give ONLY 5  LINES of feedback.

1. Resume summary feedback
2. Missing skills vs JD
3. required improvements

Resume:
{resume_text}

Job Description:
{jd_text}

Scores:
{scores}

Respond in exactly required plain lines.
"""

    print(f"--- Starting AI Feedback Generation ({MODEL}) ---")
    try:
        # Removed timeout to allow full execution
        result = subprocess.run(
            ["ollama", "run", MODEL],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        print(f"--- Ollama finished with return code: {result.returncode} ---")

        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8')
            print(f"Ollama STDERR: {error_msg}")
            return f"AI feedback unavailable - Ollama error: {error_msg[:50]}..."

        raw_output = result.stdout.decode("utf-8")
        print(f"Ollama Output Preview: {raw_output[:100]}...")
        
        cleaned = clean_ansi(raw_output).strip()

        # If model returned nothing → fallback safe text
        if not cleaned:
            return "AI feedback generation failed\nOllama may not be responding\nBasic analysis completed"

        # Force split
        lines = cleaned.replace("\r", "").split("\n")
        lines = [line.strip() for line in lines if line.strip()]

        # If model didn't generate 3 lines, pad
        while len(lines) < 7:
            lines.append(".")

        return "\n".join(lines[:6])

    except FileNotFoundError:
        print("Error: Ollama executable not found in PATH")
        return "Ollama not found\nPlease install Ollama\nBasic analysis completed"
    except Exception as e:
        print(f"Feedback generation exception: {e}")
        import traceback
        traceback.print_exc()
        return f"AI feedback error: {str(e)}\nBasic analysis completed"