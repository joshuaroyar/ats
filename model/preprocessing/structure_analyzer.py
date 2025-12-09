# structure_analyzer.py
"""
Module B — Resume Structure & Section Quality Analyzer

Score Range: 0 – 20

Sections detected:
- Summary / Profile
- Experience
- Projects
- Skills
- Education
- Certifications
- Leadership / Activities
- Contact Info

Checks performed:
- Section presence
- Section completeness
- Bullet formatting
- Content density
- Consistency (dates, bullets, alignment)
- Red flags (empty sections, one-line sections)
"""

import re
import json

# ---------------------------
# SECTION HEADERS (strongest dictionaries)
# ---------------------------
SECTION_PATTERNS = {
    "summary":       [r"summary", r"profile", r"about me"],
    "experience":    [r"experience", r"work history", r"employment"],
    "projects":      [r"projects", r"personal projects", r"academic projects"],
    "skills":        [r"skills", r"technical skills", r"skills & tools"],
    "education":     [r"education", r"academics", r"qualifications"],
    "certifications":[r"certifications", r"certificates", r"courses"],
    "leadership":    [r"leadership", r"activities", r"extracurricular"],
    "contact":       [r"contact", r"email", r"phone", r"github", r"linkedin"]
}

BULLET_RE = re.compile(r"^\s*[-•·▪‣*]\s+", re.MULTILINE)
DATE_RE = re.compile(r"(20\d{2}|19\d{2})")
UPPERCASE_HEADER_RE = re.compile(r"^[A-Z][A-Z\s]{2,}$", re.MULTILINE)

# scores per section
SECTION_WEIGHTS = {
    "summary": 3,
    "experience": 5,
    "projects": 3,
    "skills": 3,
    "education": 3,
    "certifications": 1,
    "leadership": 1,
    "contact": 1
}

# ------------------------------------------
#  IDENTIFY SECTIONS
# ------------------------------------------
def detect_sections(text):
    text_low = text.lower()
    found = {}

    for sec, patterns in SECTION_PATTERNS.items():
        found[sec] = False
        for p in patterns:
            if re.search(p, text_low):
                found[sec] = True
                break

    return found

# ------------------------------------------
#  SECTION QUALITY SCORING
# ------------------------------------------
def score_section_presence(sections):
    score = 0
    for sec, present in sections.items():
        if present:
            score += SECTION_WEIGHTS[sec]
    return score

# ------------------------------------------
#  STRUCTURAL ANALYSIS
# ------------------------------------------
def bullet_density(text):
    bullets = BULLET_RE.findall(text)
    lines = text.count("\n") or 1
    density = len(bullets) / lines
    return density, len(bullets)

def detect_bad_formatting(text):
    issues = []
    # too many uppercase blocks = poor readability
    if len(UPPERCASE_HEADER_RE.findall(text)) > 20:
        issues.append("Too many uppercase lines")
    # no spacing between sections
    if "\n\n" not in text:
        issues.append("Insufficient spacing between sections")
    return issues

def detect_incomplete_sections(text, sections):
    issues = []
    for sec, present in sections.items():
        if not present:
            continue
        pattern = SECTION_PATTERNS[sec][0]
        loc = re.search(pattern, text.lower())
        if not loc:
            continue

        start = loc.start()
        snippet = text[start:start+350]

        # section exists but empty or extremely small
        if len(snippet.split()) < 10:
            issues.append(f"{sec} section too short/empty")

    return issues

def structural_score(text, sections):
    score = score_section_presence(sections)

    # add bullet point quality scoring
    density, bullet_count = bullet_density(text)
    if density > 0.02:  # at least 2 bullets per 100 lines
        score += 2
    elif density > 0.01:
        score += 1

    # formatting penalties
    penalties = 0
    if "Insufficient spacing between sections" in detect_bad_formatting(text):
        penalties += 1

    # empty-section penalties
    incomplete = detect_incomplete_sections(text, sections)
    penalties += len(incomplete) * 0.5
    if penalties > 5:
        penalties = 5

    final = max(0, min(20, score - penalties))
    return final, {
        "section_presence_score": score,
        "bullet_count": bullet_count,
        "bullet_density": density,
        "formatting_penalties": penalties,
        "incomplete_section_issues": incomplete,
        "final_score": final
    }

# ------------------------------------------
# MAIN ENTRYPOINT
# ------------------------------------------
def analyze_structure(text):
    sections = detect_sections(text)
    score, details = structural_score(text, sections)

    return {
        "structure_score": score,
        "sections_detected": sections,
        "details": details
    }

# ------------------------------------------
# CLI SUPPORT
# ------------------------------------------
if __name__ == "__main__":
    import sys
    from utils.pdf_reader import extract_text_from_pdf

    if len(sys.argv) < 2:
        print("Usage: python structure_analyzer.py resume.pdf")
        sys.exit(1)

    pdf = sys.argv[1]
    text = extract_text_from_pdf(pdf)
    out = analyze_structure(text)
    print(json.dumps(out, indent=2, ensure_ascii=False))
