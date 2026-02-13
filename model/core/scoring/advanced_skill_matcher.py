# advanced_skill_matcher.py
"""
Advanced Skill Matcher (Upgraded Module D)
- Uses semantic matching with sentence-transformers (intfloat/e5-base)
- Smarter candidate extraction (n-grams, token heuristics, domain banks)
- JD importance weighting (frequency + position)
- Outputs detailed matches, similarity scores, suggested skills and example lines
- Produces a final skill_score (0-45) and full ATS combined score if analyzers present

Usage:
    pip install -U sentence-transformers numpy scikit-learn
    python advanced_skill_matcher.py resume.pdf jd.txt

Optional flags:
    --fast    -> reduce candidate set and skip expensive expansions
"""

import re
import json
import os
import math
import argparse
from collections import Counter, defaultdict
import numpy as np

# try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
except Exception as e:
    raise RuntimeError("Install sentence-transformers: pip install sentence-transformers") from e

# ---- Config ----
EMBED_MODEL_NAME = "intfloat/e5-base"
EMBED_BATCH = 64
SIM_THRESHOLD = 0.72   # threshold to consider phrase-level semantic match
CANDIDATE_NGRAM_MAX = 4
MAX_CANDIDATES_RESUME = 1200
MAX_CANDIDATES_JD = 400
SKILL_SCORE_MAX = 45.0

# Basic skill bank (extend or replace with your large bank)
SKILL_BANK = {
    "hard": [
        "machine learning","deep learning","nlp","bert","xgboost","cnn","python","sql",
        "mongodb","react","javascript","api development","data structures","algorithms",
        "ocr","rag","vector database","tensorflow","pytorch","docker","kubernetes",
        "fastapi","rest api","mlops","feature engineering","model deployment"
    ],
    "tools": [
        "git","github","firebase","vs code","power bi","cursor","ollama",
        "numpy","pandas","sklearn","streamlit","mongodb","postgresql","mysql"
    ],
    "soft": [
        "communication","teamwork","leadership","problem solving","critical thinking","ownership"
    ]
}

STOPWORDS = set([
    "the","and","or","of","in","on","for","with","a","an","to","by","as","using","based","from",
    "at","is","are","be","was","were","this","that","which","it","its"
])

# ---- Utilities ----
def load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_resume_text(pdf_path):
    # lazy import so script doesn't fail if not used elsewhere
    from utils.pdf_reader import extract_text_from_pdf
    return extract_text_from_pdf(pdf_path)

def tokenize_simple(text):
    # keep alphanum and +.# tokens
    toks = re.findall(r"[A-Za-z0-9\+\#\.\-]+", text.lower())
    return toks

def ngrams(tokens, n):
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

def score_position_weight(index, total_len):
    # higher weight to top of document: positional bias
    # index ~ 0 -> weight near 1.0 ; index ~ end -> weight ~ 0.2
    if total_len <= 1:
        return 1.0
    frac = index / (total_len - 1)
    return 1.0 - 0.8 * frac  # linear decay 1.0 -> 0.2

# ---- Candidate extraction ----
def extract_candidates_from_text(text, domain_verbs=None, domain_nouns=None, max_candidates=800):
    """
    Heuristic extraction of candidate skill phrases from text:
    - collects tokens and ngrams (2..CANDIDATE_NGRAM_MAX)
    - retains phrases containing tech-like tokens (python, sql, api, ml, etc.)
    - retains phrases present in SKILL_BANK
    - filters stopwords, extremely short items
    - returns ranked list by frequency & lexical signal
    """
    t = text.lower()
    tokens = tokenize_simple(t)

    # collect ngrams
    cand_counter = Counter()

    # single tokens that look like skills: contain letters and digits or are in bank
    for tok in tokens:
        if len(tok) < 3:
            continue
        if tok in STOPWORDS:
            continue
        # heuristic: tokens with digits/plus/hash or common tech substrings
        if re.search(r"[0-9\+\#\.]", tok) or any(s in tok for s in ["python","sql","api","ml","nn","cnn","bert","xgboost","tensorflow","pytorch","docker","k8s","kube","rest","react","node","mongo","aws","gcp","azure","pip"]):
            cand_counter[tok] += 3
        # if token appears in skill bank add weight
        for cat, skills in SKILL_BANK.items():
            if tok in " ".join(skills):
                cand_counter[tok] += 2

    # ngrams
    max_n = CANDIDATE_NGRAM_MAX
    for n in range(2, max_n+1):
        for ng in ngrams(tokens, n):
            if any(w in STOPWORDS for w in ng.split()):
                # still allow if contains skill bank term
                if not any(s in ng for cat in SKILL_BANK.values() for s in cat):
                    continue
            # simple filter: must contain a letter
            if not re.search(r"[a-z]", ng):
                continue
            # boost if contains known skill bank items
            boost = 0
            for cat, skills in SKILL_BANK.items():
                for s in skills:
                    if s in ng:
                        boost += 4
            # boost if contains tech token
            if any(s in ng for s in ["machine","learning","model","api","pipeline","deployment","database","cloud","docker","kubernetes","tensorflow","pytorch","feature","engineering"]):
                boost += 2
            # count frequency
            cand_counter[ng] += 1 + boost

    # incorporate domain nouns/verbs if provided (give deterministic order)
    if domain_nouns:
        for n in domain_nouns:
            if len(n) < 3: continue
            if n in t:
                cand_counter[n] += 5
    if domain_verbs:
        for v in domain_verbs:
            if len(v) < 3: continue
            if v in t:
                cand_counter[v] += 1

    # Rank and prune
    candidates = [c for c, _ in cand_counter.most_common(max_candidates)]
    # normalize: remove extremely generic words
    filtered = []
    for c in candidates:
        words = c.split()
        if len(words) == 1 and len(c) <= 3:
            continue
        filtered.append(c)
    return filtered[:max_candidates]

# ---- JD extraction (similar) ----
def extract_jd_candidates(jd_text, max_candidates=400):
    toks = tokenize_simple(jd_text)
    # pick first 200 tokens/phrases for positional weighting
    candidates = extract_candidates_from_text(jd_text, max_candidates=max_candidates)
    # compute frequency & positional importance
    freq = Counter([c for c in candidates])
    # positional score: earlier candidates get higher base weight
    pos_weights = {}
    total_len = len(jd_text.splitlines()) or 1
    for i, line in enumerate(jd_text.splitlines()):
        for skill in SKILL_BANK.get("hard", []) + SKILL_BANK.get("tools", []) + SKILL_BANK.get("soft", []):
            if skill in line.lower():
                pos_weights[skill] = pos_weights.get(skill, 0) + score_position_weight(i, total_len)
    # return list (unique)
    uniq = []
    seen = set()
    for c in candidates:
        if c not in seen:
            uniq.append(c)
            seen.add(c)
    return uniq[:max_candidates], pos_weights

# ---- Embeddings & similarity ----
def embed_phrases(model, phrases, batch=EMBED_BATCH):
    vecs = []
    for i in range(0, len(phrases), batch):
        batch_phrases = phrases[i:i+batch]
        vecs_batch = model.encode(batch_phrases, normalize_embeddings=True)
        vecs.append(vecs_batch)
    if len(vecs) == 0:
        return np.zeros((0, model.get_sentence_embedding_dimension()))
    return np.vstack(vecs)

def compute_similarity_matrix(a_vecs, b_vecs):
    # cosine similarity via dot product (vectors are normalized)
    return np.dot(a_vecs, b_vecs.T)

# ---- Matching algorithm ----
def match_skills(model, resume_phrases, jd_phrases, jd_pos_weights=None, top_k=1, sim_threshold=SIM_THRESHOLD):
    if len(resume_phrases) == 0 or len(jd_phrases) == 0:
        return [], {}, 0.0

    r_vecs = embed_phrases(model, resume_phrases)
    j_vecs = embed_phrases(model, jd_phrases)

    sim_mat = compute_similarity_matrix(r_vecs, j_vecs)  # shape (R, J)

    matched = []
    jd_scores = defaultdict(float)
    resume_to_jd = {}
    for i in range(sim_mat.shape[0]):
        # find best JD match(s)
        j_idx = np.argmax(sim_mat[i])
        best_sim = float(sim_mat[i, j_idx])
        if best_sim >= sim_threshold:
            r_phrase = resume_phrases[i]
            j_phrase = jd_phrases[j_idx]
            matched.append({
                "resume_phrase": r_phrase,
                "jd_phrase": j_phrase,
                "similarity": round(best_sim, 4)
            })
            resume_to_jd[r_phrase] = (j_phrase, best_sim)
            # accumulate JD score weighted by pos weight if available
            weight = jd_pos_weights.get(j_phrase, 1.0) if jd_pos_weights else 1.0
            jd_scores[j_phrase] = max(jd_scores[j_phrase], best_sim * weight)

    # Also compute global semantic similarity (resume <-> JD full text)
    # This gives a usefulness bonus
    global_sim = None
    try:
        global_sim = float(np.dot(model.encode([" ".join(resume_phrases)], normalize_embeddings=True)[0],
                                  model.encode([" ".join(jd_phrases)], normalize_embeddings=True)[0]))
    except Exception:
        global_sim = 0.0

    return matched, jd_scores, global_sim

# ---- Skill scoring ----
def compute_skill_score(jd_scores, jd_phrases, max_score=SKILL_SCORE_MAX):
    """
    jd_scores: dict mapping jd_phrase -> score (0..1 weighted)
    jd_phrases: list of jd phrases (to compute coverage)
    We compute:
      - coverage fraction = matched_jd / total_jd
      - average jd match strength
      - then scale to max_score
    """
    if len(jd_phrases) == 0:
        return 0.0
    matched = [p for p, v in jd_scores.items() if v > 0]
    if not matched:
        return 0.0
    coverage = len(matched) / len(jd_phrases)
    avg_strength = sum(jd_scores[p] for p in matched) / len(matched)
    # Coverage is primary driver (70%), strength secondary (30%)
    raw = 0.7 * coverage + 0.3 * avg_strength
    return min(max_score, raw * max_score)

# ---- Suggestion generation ----
def suggest_additions(jd_phrases, jd_scores, resume_phrases):
    suggestions = []
    for p in jd_phrases:
        if jd_scores.get(p, 0) < SIM_THRESHOLD:
            # suggest if not matched; give an example line style
            example = f"• {p.title()} — demonstrated by implementing/using {p.split()[0]} in project X"
            suggestions.append({"skill": p, "suggested_line": example})
    return suggestions

# ---- Full pipeline ----
def advanced_score(resume_pdf, jd_input, fast=False):
    # load texts
    resume_text = extract_resume_text(resume_pdf)
    
    # Handle both file paths and raw text for JD
    if os.path.exists(jd_input) and os.path.isfile(jd_input):
        jd_text = load_text(jd_input)
    else:
        # Assume input is the raw text (e.g. from API)
        jd_text = jd_input

    # domain banks (if available)
    domain_verbs = []
    domain_nouns = []
    for d in ["tech","business","marketing","finance","operations","hr","design"]:
        vfile = f"{d}_verbs.json"
        nfile = f"{d}_nouns.json"
        if os.path.exists(vfile) and os.path.exists(nfile):
            # load and extend but keep small sets for heuristics
            try:
                with open(vfile, "r", encoding="utf-8") as f:
                    domain_verbs.extend(json.load(f)[:200])
                with open(nfile, "r", encoding="utf-8") as f:
                    domain_nouns.extend(json.load(f)[:300])
            except Exception:
                pass

    # extract candidates
    resume_cands = extract_candidates_from_text(resume_text, domain_verbs=domain_verbs, domain_nouns=domain_nouns,
                                               max_candidates=(400 if fast else MAX_CANDIDATES_RESUME))
    jd_cands, jd_pos_weights = extract_jd_candidates(jd_text, max_candidates=(200 if fast else MAX_CANDIDATES_JD))

    # ensure JD candidates include explicit bank skills
    for cat in SKILL_BANK.values():
        for s in cat:
            if s not in jd_cands and s in jd_text.lower():
                jd_cands.insert(0, s)

    # initialise embedder
    model = SentenceTransformer(EMBED_MODEL_NAME)

    # perform matching
    matched, jd_scores, global_sim = match_skills(model, resume_cands, jd_cands, jd_pos_weights, sim_threshold=SIM_THRESHOLD)

    # compute skill score
    skill_score = compute_skill_score(jd_scores, jd_cands, max_score=SKILL_SCORE_MAX)

    suggestions = suggest_additions(jd_cands, jd_scores, resume_cands)

    # build detailed response
    detail = {
        "resume_candidate_count": len(resume_cands),
        "jd_candidate_count": len(jd_cands),
        "global_resume_jd_similarity": round(global_sim, 4),
        "matched_pairs": matched,
        "jd_scores": {k: round(v, 4) for k, v in jd_scores.items()},
        "skill_score": round(skill_score, 2),
        "suggestions": suggestions[:40]
    }
    return detail

# ---- CLI + integration with other modules ----
def full_ats_with_advanced_skills(resume_pdf, jd_txt, output_json=None, fast=False):
    # compute advanced skill detail
    skill_detail = advanced_score(resume_pdf, jd_txt, fast=fast)
    skill_score = skill_detail["skill_score"]

    # try to reuse existing analyzers (safe import)
    try:
        from domain_impact_analyzer import analyze_resume_impact
        from preprocessing.structure_analyzer import analyze_structure
        from preprocessing.clarity_analyzer import analyze_clarity
        from utils.pdf_reader import extract_text_from_pdf
        text = extract_text_from_pdf(resume_pdf)
        impact = analyze_resume_impact(resume_pdf)
        structure = analyze_structure(text)
        clarity = analyze_clarity(text)
    except Exception:
        impact = {"impact_score": 0}
        structure = {"structure_score": 0}
        clarity = {"clarity_score": 0}

    final_score = impact.get("impact_score", 0) + structure.get("structure_score", 0) + clarity.get("clarity_score", 0) + skill_score
    final_score = round(max(0, min(100, final_score)), 2)

    out = {
        "final_ats_score": final_score,
        "impact_score": impact.get("impact_score", 0),
        "structure_score": structure.get("structure_score", 0),
        "clarity_score": clarity.get("clarity_score", 0),
        "skill_score": skill_score,
        "skill_detail": skill_detail,
        "impact_detail": impact,
        "structure_detail": structure,
        "clarity_detail": clarity
    }

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
    return out

# CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("resume", help="resume pdf path")
    parser.add_argument("jd", help="job description txt file")
    parser.add_argument("--out", help="output json file", default=None)
    parser.add_argument("--fast", action="store_true", help="faster, smaller candidate pools")
    args = parser.parse_args()

    res = full_ats_with_advanced_skills(args.resume, args.jd, output_json=args.out, fast=args.fast)
    print(json.dumps(res, indent=2, ensure_ascii=False))
