# clarity_analyzer.py
"""
Module C — Grammar, Readability & Clarity Analyzer
Score: 0–10

Checks performed:
- Passive voice detection
- Long sentence detection
- Weak verbs & weak phrases
- Filler / vague phrases
- Repetition
- Readability score (Flesch-like)
- Overuse of prepositions/adverbs
- Action strength scoring
"""

import re
import json
from collections import Counter

# -------------------------------------
# CONFIG — weights
# -------------------------------------
WEIGHT_PASSIVE = 2.0
WEIGHT_LONG_SENT = 2.0
WEIGHT_WEAK_PHRASE = 2.0
WEIGHT_REPETITION = 1.0
WEIGHT_CLARITY = 3.0

MAX_PENALTY = 10.0

# -------------------------------------
# Patterns
# -------------------------------------
PASSIVE_RE = re.compile(r"\b(been|was|were|is|are|be)\s+\w+ed\b", re.IGNORECASE)

WEAK_PHRASES = [
    "responsible for",
    "worked on",
    "involved in",
    "helped with",
    "participated in",
    "was part of",
    "tasked with",
    "assisted with"
]

FILLER_PHRASES = [
    "utilized", "leveraged", "various", "multiple",
    "really", "very", "extremely", "highly",
    "successfully"  # often unnecessary
]

ACTION_WEAK_VERBS = [
    "did", "made", "got", "gave", "put", "ran", "used"
]

SENTENCE_SPLIT = re.compile(r"[\.!?]\s+")

# -------------------------------------
# Helpers
# -------------------------------------
def split_sentences(text):
    s = SENTENCE_SPLIT.split(text)
    return [x.strip() for x in s if len(x.strip()) > 0]

def count_syllables(word):
    word = word.lower()
    return max(1, len(re.findall(r"[aeiouy]+", word)))

def readability_score(text):
    words = re.findall(r"\w+", text)
    if len(words) == 0:
        return 0
    sentences = max(1, len(split_sentences(text)))
    syllables = sum(count_syllables(w) for w in words)

    # Flesch Reading Ease adaptation
    score = 206.835 - 1.015 * (len(words)/sentences) - 84.6 * (syllables/len(words))
    return score

def detect_passive_voice(sentences):
    hits = []
    for s in sentences:
        if PASSIVE_RE.search(s):
            hits.append(s.strip())
    return hits

def detect_long_sentences(sentences, max_len=22):
    hits = []
    for s in sentences:
        wc = len(s.split())
        if wc > max_len:
            hits.append((s.strip(), wc))
    return hits

def detect_weak_phrases(text):
    found = []
    t = text.lower()
    for w in WEAK_PHRASES:
        if w in t:
            found.append(w)
    return found

def detect_filler_phrases(text):
    found = []
    t = text.lower()
    for f in FILLER_PHRASES:
        if f in t:
            found.append(f)
    return found

def detect_weak_verbs(text):
    words = re.findall(r"\w+", text.lower())
    return [w for w in words if w in ACTION_WEAK_VERBS]

def detect_repetition(words, threshold=4):
    freq = Counter(words)
    rep = [(w, c) for w, c in freq.items() if c >= threshold and len(w) > 3]
    return rep

# -------------------------------------
# Main analysis
# -------------------------------------
def analyze_clarity(text):
    sentences = split_sentences(text)
    words = re.findall(r"\w+", text.lower())

    passive_hits = detect_passive_voice(sentences)
    long_sents = detect_long_sentences(sentences)
    weak_phrases = detect_weak_phrases(text)
    filler = detect_filler_phrases(text)
    weak_verbs = detect_weak_verbs(text)
    repetition = detect_repetition(words)

    # readability 0–100 mapped to 0–3 clarity points
    read_score = readability_score(text)
    clarity_points = max(0.0, min(WEIGHT_CLARITY, (read_score / 100) * WEIGHT_CLARITY))

    # penalties
    penalty = 0.0
    penalty += min(WEIGHT_PASSIVE * len(passive_hits), 3)
    penalty += min(WEIGHT_LONG_SENT * len(long_sents), 3)
    penalty += min(WEIGHT_WEAK_PHRASE * len(weak_phrases), 3)
    penalty += min(WEIGHT_WEAK_PHRASE * len(filler), 2)
    penalty += min(WEIGHT_REPETITION * len(repetition), 2)

    penalty = min(MAX_PENALTY, penalty)

    final = max(0.0, min(10.0, clarity_points + 10 - penalty))

    return {
        "clarity_score": round(final, 2),
        "readability": read_score,
        "issues": {
            "passive_voice_sentences": passive_hits,
            "long_sentences": long_sents,
            "weak_phrases": weak_phrases,
            "filler_words": filler,
            "weak_verbs": weak_verbs,
            "repetition": repetition
        }
    }

# -------------------------------------
# CLI
# -------------------------------------
if __name__ == "__main__":
    import sys
    from utils.pdf_reader import extract_text_from_pdf

    if len(sys.argv) < 2:
        print("Usage: python clarity_analyzer.py resume.pdf")
        sys.exit(1)

    text = extract_text_from_pdf(sys.argv[1])
    out = analyze_clarity(text)
    print(json.dumps(out, indent=2, ensure_ascii=False))
