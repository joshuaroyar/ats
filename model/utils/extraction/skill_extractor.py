import spacy
import re

nlp = spacy.load("en_core_web_sm")

# simple keyword patterns
TECH_PATTERN = re.compile(
    r"\b(python|java|c\+\+|c#|sql|javascript|react|node\.js|docker|kubernetes|aws|azure|linux|git|tensorflow|pytorch|machine learning|deep learning|nlp|data analysis|data science)\b",
    re.IGNORECASE
)

def extract_candidates(text: str):
    doc = nlp(text)
    candidates = set()

    # 1. noun chunks
    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip().lower()
        if len(phrase.split()) <= 5:
            candidates.add(phrase)

    # 2. technical regex matches
    for match in TECH_PATTERN.findall(text):
        candidates.add(match.lower())

    # 3. clean-up
    cleaned = set()
    for c in candidates:
        c = c.strip()
        if len(c) > 1:
            cleaned.add(c)

    return list(cleaned)
