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

    result = subprocess.run(
        ["ollama", "run", MODEL],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode != 0:
        print(f"Ollama execution failed: {result.stderr.decode('utf-8')}")
        return "AI Feedback unavailable (Model Error)"

    raw_output = result.stdout.decode("utf-8")
    cleaned = clean_ansi(raw_output).strip()
    
    # Debug log
    print(f"Ollama Raw Output Length: {len(raw_output)}")

    # If model returned nothing → fallback safe text
    if not cleaned:
        return "No output\nMissing skills unknown\nTry again"

    # Force split
    lines = cleaned.replace("\r", "").split("\n")
    lines = [line.strip() for line in lines if line.strip()]

    # If model didn't generate 3 lines, pad
    while len(lines) < 7:
        lines.append(".")

    return "\n".join(lines[:6])