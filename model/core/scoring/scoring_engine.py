import json
import numpy as np
import os
from core.ontology.map_to_ontology import map_to_esco
from utils.extraction.skill_extractor import extract_candidates
from utils.pdf_reader import extract_text_from_pdf


def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def load_embeddings():
    base_path = os.path.dirname(os.path.abspath(__file__))
    embeddings_path = os.path.join(base_path, "../../utils/esco/skill_embeddings.json")
    with open(embeddings_path, "r", encoding="utf-8") as f:
        db = json.load(f)
    return db


def get_embedding_matrix(db):
    emb = np.array([np.array(item["embedding"]) for item in db])
    ids = [item["id"] for item in db]
    names = [item["name"] for item in db]
    return emb, ids, names


def evaluate_resume_against_jd(resume_pdf, jd_text):

    # STEP 1: load ESCO embeddings
    db = load_embeddings()
    emb_matrix, esco_ids, esco_names = get_embedding_matrix(db)

    # STEP 2: extract text from resume PDF
    resume_text = extract_text_from_pdf(resume_pdf)

    # STEP 3: extract candidate phrases
    resume_candidates = extract_candidates(resume_text)
    jd_candidates = extract_candidates(jd_text)

    # STEP 4: map resume skills to ESCO
    resume_skills = []
    for c in resume_candidates:
        m = map_to_esco(c)
        if m:
            resume_skills.append(m)

    # STEP 5: map JD skills to ESCO
    jd_skills = []
    for c in jd_candidates:
        m = map_to_esco(c)
        if m:
            jd_skills.append(m)

    # Build fast lookup
    resume_ids = set([s["esco_id"] for s in resume_skills])
    jd_ids = set([s["esco_id"] for s in jd_skills])

    # Create ID to embedding map
    id_to_emb = {id: emb for id, emb in zip(esco_ids, emb_matrix)}

    # STEP 6: Score calculation
    exact_matches = resume_ids.intersection(jd_ids)

    # similarity-based matches
    partial_matches = []
    missing_skills = []

    for jd_skill in jd_skills:
        if jd_skill["esco_id"] in exact_matches:
            continue

        best_sim = 0
        best_res = None

        jd_id = jd_skill["esco_id"]
        if jd_id in id_to_emb:
            jd_emb = id_to_emb[jd_id]

            # compare JD skill with all resume skills
            for r in resume_skills:
                r_id = r["esco_id"]
                if r_id in id_to_emb:
                    r_emb = id_to_emb[r_id]
                    sim = cosine(jd_emb, r_emb)

                    if sim > best_sim:
                        best_sim = sim
                        best_res = r

        if best_sim >= 0.70:
            partial_matches.append({
                "jd_skill": jd_skill["esco_name"],
                "matched_with": best_res["esco_name"],
                "similarity": float(best_sim)
            })
        else:
            missing_skills.append(jd_skill["esco_name"])

    # STEP 7: final score
    score = (
        len(exact_matches) * 2.0 +
        len(partial_matches) * 1.0 -
        len(missing_skills) * 1.5
    )

    score = max(0, min(100, score))  # normalize

    return {
        "score": score,
        "exact_matches": list(exact_matches),
        "partial_matches": partial_matches,
        "missing_skills": missing_skills
    }
