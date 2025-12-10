# domain_impact_analyzer_fixed.py
"""
Fixed domain-aware Impact Analyzer
- whole-word matching for verbs/nouns
- filters numeric noise (phone numbers / years)
- ignores tiny tokens and common stopwords
- safer weights & caps to avoid easy clipping
Usage:
    python domain_impact_analyzer_fixed.py resume.pdf
"""

import re
import json
import os
from collections import Counter

DOMAINS = ["tech", "business", "marketing", "finance", "operations", "hr", "design"]

# Metric regexes (same as before)
RE_PERCENT = re.compile(r"\b\d+(\.\d+)?\s?%|\bpercent\b", re.IGNORECASE)
RE_CURRENCY = re.compile(r"(?:₹|Rs\.?|INR|\$|€|£)\s?\d[\d,\.]*", re.IGNORECASE)
RE_MULTIPLIER = re.compile(r"\b\d+\s?x\b|\b\d+x\b", re.IGNORECASE)
RE_NUMBER_GENERIC = re.compile(r"\b\d{1,3}(?:[,.\s]\d{3})+\b|\b\d+(\.\d+)?\b")  # raw numbers

SENT_SPLIT_RE = re.compile(r'(?<=[\.\?\n])\s+')

# Weights & caps (tuned)
WEIGHT_VERB = 0.45
WEIGHT_METRIC = 1.2
WEIGHT_ACHIEVEMENT = 2.5
WEIGHT_NOUN_DENSITY = 6.0

CAP_VERB = 6.0
CAP_METRIC = 7.0
CAP_ACHIEVEMENT = 5.0

# small stopword-like tokens to ignore if matched accidentally
COMMON_STOP_TOKENS = set([
    "be","do","go","get","have","make","use","like","know","need","work","say","see","take",
    "time","one","two","new","many","may","also","even","right","left","end"
])

def load_json_safe(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_domain_banks():
    verbs = {}
    nouns = {}
    for d in DOMAINS:
        verbs_list = [v for v in load_json_safe(f"{d}_verbs.json")]
        # normalize: keep tokens length >=3, remove obvious stop tokens, lowercase
        verbs_list = [v.lower() for v in verbs_list if isinstance(v, str) and len(v.strip()) >= 3]
        verbs_list = [v for v in verbs_list if v not in COMMON_STOP_TOKENS]
        verbs[d] = set(verbs_list)

        nouns_list = [n for n in load_json_safe(f"{d}_nouns.json")]
        nouns_list = [n.lower() for n in nouns_list if isinstance(n, str) and len(n.strip()) >= 3]
        nouns[d] = set(nouns_list)
    return verbs, nouns

def extract_sentences(text):
    parts = SENT_SPLIT_RE.split(text)
    return [p.strip() for p in parts if p.strip()]

def is_phone_like(token):
    # phone numbers are long digit strings, often 7+ digits (or include country code)
    digits = re.sub(r"[^\d]", "", token)
    return len(digits) >= 7

def is_year_like(token):
    # treat 1900-2105 as likely a year (low-value metric)
    try:
        val = int(re.sub(r"[^\d]", "", token))
        return 1900 <= val <= 2105
    except:
        return False

def find_metrics_filtered(text):
    raw = []
    for r in (RE_PERCENT, RE_CURRENCY, RE_MULTIPLIER, RE_NUMBER_GENERIC):
        for m in r.finditer(text):
            raw.append(m.group(0))
    # dedupe preserving order
    seen = set()
    out = []
    for h in raw:
        hh = h.strip()
        key = hh.lower()
        if key in seen:
            continue
        seen.add(key)
        # filter phone-like numbers out
        if is_phone_like(hh):
            continue
        # if it's a year-like token, **treat as low-value** by storing but marking
        out.append(hh)
    return out

# whole-word match helper
def whole_word_in_text(token, text):
    # token may contain spaces (multiword); use regex word boundaries
    token = re.escape(token)
    pattern = r'\b' + token + r'\b'
    return re.search(pattern, text, flags=re.IGNORECASE) is not None

def detect_domain_by_lexicon(text, verbs_banks, nouns_banks):
    text_low = text.lower()
    scores = {}
    for d in DOMAINS:
        v_matches = 0
        n_matches = 0
        for v in verbs_banks.get(d, []):
            # faster prefilter: skip tokens that are not in text by substring, then whole-word check
            if v in text_low and whole_word_in_text(v, text_low):
                v_matches += 1
        for n in nouns_banks.get(d, []):
            if n in text_low and whole_word_in_text(n, text_low):
                n_matches += 1
        scores[d] = v_matches * 1.0 + n_matches * 1.3
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        if any(k in text_low for k in ("python","java","sql","model","dataset","opencv","machine")):
            return "tech"
        if any(k in text_low for k in ("strategy","revenue","kpi","market","client")):
            return "business"
        return "business"
    return best

def analyze_text_impact(text, verbs_banks, nouns_banks, domain=None):
    text_low = text.lower()
    if not domain:
        domain = detect_domain_by_lexicon(text, verbs_banks, nouns_banks)

    domain_verbs = verbs_banks.get(domain, set())
    domain_nouns = nouns_banks.get(domain, set())

    # 1. verbs (whole-word)
    verb_hits = []
    for v in domain_verbs:
        if whole_word_in_text(v, text_low):
            # ignore tokens that are stop-like
            if len(v) < 3 or v in COMMON_STOP_TOKENS:
                continue
            verb_hits.append(v)

    # 2. metrics (filtered)
    metrics = find_metrics_filtered(text)

    # 3. achievement sentences: must contain domain verb (whole-word) + valid metric (not phone/year)
    sentences = extract_sentences(text)
    achievement_sentences = []
    for s in sentences:
        s_low = s.lower()
        verb_ok = any(whole_word_in_text(v, s_low) for v in domain_verbs)
        # find a metric in this sentence that is not phone-like and not pure year
        metric_ok = False
        for m in find_metrics_filtered(s):
            if not is_phone_like(m) and not is_year_like(m):
                metric_ok = True
                break
        if verb_ok and metric_ok:
            achievement_sentences.append(s.strip())

    # 4. noun density (whole-word)
    words = re.findall(r"\w+", text_low)
    word_count = max(1, len(words))
    noun_hits = []
    for n in domain_nouns:
        if whole_word_in_text(n, text_low):
            if len(n) < 3:
                continue
            noun_hits.append(n)
    noun_density = len(noun_hits) / word_count * 100
    density_norm = min(1.0, noun_density / 10.0)

    # scoring parts
    verb_points = min(CAP_VERB, len(verb_hits) * WEIGHT_VERB)
    metric_points = min(CAP_METRIC, len([m for m in metrics if not is_year_like(m)]) * WEIGHT_METRIC)
    achievement_points = min(CAP_ACHIEVEMENT, len(achievement_sentences) * WEIGHT_ACHIEVEMENT)
    noun_points = density_norm * WEIGHT_NOUN_DENSITY

    raw = verb_points + metric_points + achievement_points + noun_points

    # final normalization: scale raw (which should be within reasonable bound) to 0..25
    # avoid hard clipping by using a logistic-like squeeze if raw is slightly > max
    # Increased max_possible to make it harder to get a perfect score
    max_possible = (CAP_VERB + CAP_METRIC + CAP_ACHIEVEMENT + WEIGHT_NOUN_DENSITY) * 1.2
    # simple normalization
    impact_score = max(0.0, min(25.0, (raw / max_possible) * 25.0))

    result = {
        "domain": domain,
        "impact_score": round(impact_score, 2),
        "raw_points": round(raw, 3),
        "breakdown": {
            "verb_points": round(verb_points, 3),
            "metric_points": round(metric_points, 3),
            "achievement_points": round(achievement_points, 3),
            "noun_points": round(noun_points, 3)
        },
        "counts": {
            "verbs_found": len(verb_hits),
            "verbs_list": sorted(list(set(verb_hits)))[:200],
            "metrics_found": len(metrics),
            "metrics_list": metrics[:100],
            "achievement_count": len(achievement_sentences),
            "achievement_sentences": achievement_sentences[:20],
            "noun_count": len(noun_hits),
            "noun_sample": sorted(list(set(noun_hits)))[:200]
        }
    }
    return result

def analyze_resume_impact(pdf_path):
    try:
        from utils.pdf_reader import extract_text_from_pdf
    except Exception as e:
        raise RuntimeError("pdf_reader.py missing or failed to import.") from e

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(pdf_path)

    text = extract_text_from_pdf(pdf_path)
    verbs_banks, nouns_banks = load_domain_banks()
    return analyze_text_impact(text, verbs_banks, nouns_banks, domain=None)

if __name__ == "__main__":
    import sys, json
    if len(sys.argv) < 2:
        print("Usage: python domain_impact_analyzer_fixed.py resume.pdf")
        sys.exit(1)
    resume = sys.argv[1]
    out = analyze_resume_impact(resume)
    print(json.dumps(out, indent=2, ensure_ascii=False))
